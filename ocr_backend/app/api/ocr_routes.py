from flask import Blueprint, jsonify, request, current_app
from .. import db
from ..models import OCRData, OCRLineItem, OCRLineItemValue, Document, TemplateField, SubTemplateField, Template
from ..utils.gemini_ocr import call_gemini_ocr, parse_gemini_response
from ..utils.enums import DocumentStatus, FieldType
from ..tally import (
    auto_load_tally_options, 
    load_companies_as_options, 
    load_ledgers_as_options, 
    load_stock_items_as_options,
    get_field_options_summary,
    refresh_field_options,
    load_customer_options,
    load_vendor_options,
    load_all_ledger_options,
    TallyFieldOptionsError
)
import os

bp = Blueprint('ocr', __name__, url_prefix='/api/ocr')

def build_comprehensive_text_prompt(template, text_fields):
    """
    Build comprehensive prompt combining template + field level AI instructions for text fields.
    
    Args:
        template: Template object with ai_instructions
        text_fields: List of TemplateField objects for text-based fields
        
    Returns:
        str: Enhanced prompt combining all instruction levels
    """
    parts = []
    
    # Template-level instructions
    if template.ai_instructions:
        parts.append(f"General Instructions: {template.ai_instructions}")
    
    # Field-specific instructions
    field_instructions = []
    for field in text_fields:
        if field.ai_instructions:
            field_instructions.append(f"- {field.field_name.value}: {field.ai_instructions}")
    
    if field_instructions:
        parts.append(f"Field-specific Instructions:\n" + "\n".join(field_instructions))
    
    # Base extraction request
    field_names = [f.field_name.value for f in text_fields]
    parts.append(f"Extract the following fields: {', '.join(field_names)}")
    parts.append("Return as JSON object mapping field names to values.")
    
    return "\n\n".join(parts)

def build_comprehensive_table_prompt(template, table_field, sub_fields):
    """
    Build comprehensive prompt combining template + table + sub-field level AI instructions.
    
    Args:
        template: Template object with ai_instructions
        table_field: TemplateField object for the table field
        sub_fields: List of SubTemplateField objects for table columns
        
    Returns:
        str: Enhanced prompt combining all instruction levels
    """
    parts = []
    
    # Template-level instructions
    if template.ai_instructions:
        parts.append(f"General Instructions: {template.ai_instructions}")
    
    # Table-level instructions
    if table_field.ai_instructions:
        parts.append(f"Table Instructions: {table_field.ai_instructions}")
    
    # Sub-field level instructions
    sub_field_instructions = []
    for sub_field in sub_fields:
        if sub_field.ai_instructions:
            sub_field_instructions.append(f"- {sub_field.field_name.value}: {sub_field.ai_instructions}")
    
    if sub_field_instructions:
        parts.append(f"Column-specific Instructions:\n" + "\n".join(sub_field_instructions))
    
    # Base table extraction request
    sub_field_names = [sf.field_name.value for sf in sub_fields]
    parts.append(f"Extract table data for {table_field.field_name.value} with columns: {', '.join(sub_field_names)}")
    parts.append("Return as JSON with 'rows' array containing objects for each row.")
    
    return "\n\n".join(parts)

def format_table_data_for_response(table_data_results):
    """
    Format table data for frontend consumption
    
    Args:
        table_data_results: {field_id: {field_name, field_type, sub_fields, table_data}}
    
    Returns:
        Formatted dict ready for frontend
    """
    formatted_tables = {}
    
    for field_id, data in table_data_results.items():
        field_name = data['field_name']
        sub_fields = data['sub_fields']
        table_data = data['table_data']
        
        # Format columns info
        columns = []
        for sub_field in sub_fields:
            columns.append({
                'name': sub_field.field_name.value,
                'data_type': sub_field.data_type.value,
                'sub_temp_field_id': sub_field.sub_temp_field_id
            })
        
        # Format table
        formatted_tables[field_name] = {
            'field_id': field_id,
            'field_type': 'table',
            'columns': columns,
            'rows': table_data['rows'],
            'row_count': len(table_data['rows'])
        }
    
    return formatted_tables

@bp.route('/data', methods=['GET'])
def get_all_ocr_data():
    """Get all OCR data"""
    ocr_data = OCRData.query.all()
    return jsonify({
        'ocr_data': [data.to_dict() for data in ocr_data],
        'count': len(ocr_data)
    })

@bp.route('/data/<int:ocr_id>', methods=['GET'])
def get_ocr_data(ocr_id):
    """Get specific OCR data"""
    ocr_data = OCRData.query.get_or_404(ocr_id)
    return jsonify(ocr_data.to_dict())

@bp.route('/data', methods=['POST'])
def create_ocr_data():
    """Create new OCR data"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('document_id', 'field_id', 'predicted_value')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    ocr_data = OCRData(
        document_id=data['document_id'],
        field_id=data['field_id'],
        predicted_value=data['predicted_value'],
        actual_value=data.get('actual_value'),
        confidence=data.get('confidence', 0.0)
    )
    
    db.session.add(ocr_data)
    db.session.commit()
    
    return jsonify(ocr_data.to_dict()), 201

@bp.route('/data/<int:ocr_id>', methods=['PUT'])
def update_ocr_data(ocr_id):
    """Update OCR data"""
    ocr_data = OCRData.query.get_or_404(ocr_id)
    data = request.get_json()
    
    if 'predicted_value' in data:
        ocr_data.predicted_value = data['predicted_value']
    if 'actual_value' in data:
        ocr_data.actual_value = data['actual_value']
    if 'confidence' in data:
        ocr_data.confidence = data['confidence']
    
    db.session.commit()
    return jsonify(ocr_data.to_dict())

@bp.route('/data/<int:ocr_id>', methods=['DELETE'])
def delete_ocr_data(ocr_id):
    """Delete OCR data"""
    ocr_data = OCRData.query.get_or_404(ocr_id)
    db.session.delete(ocr_data)
    db.session.commit()
    return jsonify({'message': 'OCR data deleted successfully'})

@bp.route('/line-items', methods=['GET'])
def get_all_line_items():
    """Get all line items"""
    line_items = OCRLineItem.query.all()
    return jsonify({
        'line_items': [item.to_dict() for item in line_items],
        'count': len(line_items)
    })

@bp.route('/line-items/<int:line_item_id>', methods=['GET'])
def get_line_item(line_item_id):
    """Get specific line item"""
    line_item = OCRLineItem.query.get_or_404(line_item_id)
    return jsonify(line_item.to_dict())

@bp.route('/line-items', methods=['POST'])
def create_line_item():
    """Create new line item"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('document_id', 'field_id', 'row_index')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    line_item = OCRLineItem(
        document_id=data['document_id'],
        field_id=data['field_id'],
        row_index=data['row_index']
    )
    
    db.session.add(line_item)
    db.session.commit()
    
    return jsonify(line_item.to_dict()), 201

@bp.route('/line-items/<int:line_item_id>', methods=['PUT'])
def update_line_item(line_item_id):
    """Update line item"""
    line_item = OCRLineItem.query.get_or_404(line_item_id)
    data = request.get_json()
    
    if 'row_index' in data:
        line_item.row_index = data['row_index']
    
    db.session.commit()
    return jsonify(line_item.to_dict())

@bp.route('/line-items/<int:line_item_id>', methods=['DELETE'])
def delete_line_item(line_item_id):
    """Delete line item"""
    line_item = OCRLineItem.query.get_or_404(line_item_id)
    db.session.delete(line_item)
    db.session.commit()
    return jsonify({'message': 'Line item deleted successfully'})

@bp.route('/line-items/<int:line_item_id>/values', methods=['GET'])
def get_line_item_values(line_item_id):
    """Get all values for a line item"""
    line_item = OCRLineItem.query.get_or_404(line_item_id)
    values = line_item.ocr_line_item_values.all()
    return jsonify({
        'line_item_values': [value.to_dict() for value in values],
        'count': len(values)
    })

@bp.route('/line-items/<int:line_item_id>/values', methods=['POST'])
def create_line_item_value(line_item_id):
    """Create new line item value"""
    line_item = OCRLineItem.query.get_or_404(line_item_id)
    data = request.get_json()
    
    if not data or not all(k in data for k in ('sub_temp_field_id', 'predicted_value')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    value = OCRLineItemValue(
        ocr_items_id=line_item_id,
        sub_temp_field_id=data['sub_temp_field_id'],
        predicted_value=data['predicted_value'],
        actual_value=data.get('actual_value'),
        confidence=data.get('confidence', 0.0)
    )
    
    db.session.add(value)
    db.session.commit()
    
    return jsonify(value.to_dict()), 201

@bp.route('/line-items/values/<int:value_id>', methods=['GET'])
def get_line_item_value(value_id):
    """Get specific line item value"""
    value = OCRLineItemValue.query.get_or_404(value_id)
    return jsonify(value.to_dict())

@bp.route('/line-items/values/<int:value_id>', methods=['PUT'])
def update_line_item_value(value_id):
    """Update line item value"""
    value = OCRLineItemValue.query.get_or_404(value_id)
    data = request.get_json()
    
    if 'predicted_value' in data:
        value.predicted_value = data['predicted_value']
    if 'actual_value' in data:
        value.actual_value = data['actual_value']
    if 'confidence' in data:
        value.confidence = data['confidence']
    
    db.session.commit()
    return jsonify(value.to_dict())

@bp.route('/line-items/values/<int:value_id>', methods=['DELETE'])
def delete_line_item_value(value_id):
    """Delete line item value"""
    value = OCRLineItemValue.query.get_or_404(value_id)
    db.session.delete(value)
    db.session.commit()
    return jsonify({'message': 'Line item value deleted successfully'})

@bp.route('/extract_fields', methods=['POST'])
def extract_fields():
    print("DB URI:", current_app.config['SQLALCHEMY_DATABASE_URI'])
    data = request.get_json()
    doc_id = data.get('doc_id')
    template_id = data.get('template_id')

    print("doc_id received:", doc_id)
    doc = Document.query.get(doc_id)
    print("Document found:", doc is not None)
    if doc:
        print("file_path from DB:", doc.file_path)
        print("Absolute file path:", os.path.abspath(doc.file_path))
        print("File exists:", os.path.exists(doc.file_path))

    if not doc:
        return jsonify({'error': 'Document not found'}), 404

    # 2. Fetch field names
    fields = TemplateField.query.filter_by(template_id=template_id).all()
    field_names = [f.field_name.value for f in fields]

    # 3. Call Gemini API
    image_path = doc.file_path
    gemini_response = call_gemini_ocr(image_path, field_names)

    # 4. Parse response
    extracted = parse_gemini_response(gemini_response, field_names)

    return jsonify({'fields': extracted}) 

def process_document_internal(doc_id, template_id):
    """
    Internal function for OCR processing that can be called from other modules.
    Returns a dict with success status, message, and extracted data.
    """
    try:
        # 1. Get document and validate
        doc = Document.query.get(doc_id)
        if not doc:
            return {'success': False, 'message': 'Document not found'}

        # 2. Get template and validate
        template = Template.query.get(template_id)
        if not template:
            return {'success': False, 'message': 'Template not found'}

        # 3. Update document status to PROCESSING
        doc.status = DocumentStatus.PROCESSING
        db.session.commit()

        # 4. Check if file exists
        if not os.path.exists(doc.file_path):
            doc.status = DocumentStatus.FAILED
            db.session.commit()
            return {'success': False, 'message': 'Document file not found'}

        # 5. Get template fields
        template_fields = TemplateField.query.filter_by(template_id=template_id).all()
        if not template_fields:
            doc.status = DocumentStatus.FAILED
            db.session.commit()
            return {'success': False, 'message': 'No fields defined for this template'}

        # 6. Process different field types
        extracted_data = {}
        ocr_data_records = []
        line_item_records = []
        table_data_results = {} # New dictionary to store table data results

        # Separate fields by type
        text_fields = [f for f in template_fields if f.field_type in [FieldType.TEXT, FieldType.SELECT, FieldType.NUMBER, FieldType.DATE, FieldType.EMAIL, FieldType.CURRENCY]]
        table_fields = [f for f in template_fields if f.field_type == FieldType.TABLE]

        # 7. Process text-based fields
        if text_fields:
            # Build enhanced prompt with hierarchical AI instructions
            enhanced_prompt = build_comprehensive_text_prompt(template, text_fields)
            field_names = [f.field_name.value for f in text_fields]
            
            # Call Gemini OCR with enhanced prompt
            gemini_response = call_gemini_ocr(doc.file_path, field_names, custom_prompt=enhanced_prompt)
            extracted_fields = parse_gemini_response(gemini_response, field_names)
            
            # Check for parsing errors
            if 'parse_error' in extracted_fields:
                doc.status = DocumentStatus.FAILED
                db.session.commit()
                return {'success': False, 'message': f'OCR parsing failed: {extracted_fields["parse_error"]}'}
            
            # Save to OCRData table
            for field in text_fields:
                field_value = extracted_fields.get(field.field_name.value)
                if field_value is not None:
                    ocr_data = OCRData(
                        document_id=doc_id,
                        field_id=field.field_id,
                        predicted_value=str(field_value),
                        confidence=0.8  # Default confidence, can be improved
                    )
                    ocr_data_records.append(ocr_data)
                    extracted_data[field.field_name.value] = field_value

        # 8. Process table fields
        for table_field in table_fields:
            # Get sub-template fields for this table
            sub_fields = SubTemplateField.query.filter_by(field_id=table_field.field_id).all()
            if sub_fields:
                sub_field_names = [sf.field_name.value for sf in sub_fields]
                
                # Create enhanced table prompt with hierarchical AI instructions
                enhanced_table_prompt = build_comprehensive_table_prompt(template, table_field, sub_fields)
                table_response = call_gemini_ocr(doc.file_path, sub_field_names, custom_prompt=enhanced_table_prompt)
                table_data = parse_gemini_response(table_response, sub_field_names)
                
                # Check for parsing errors
                if 'parse_error' in table_data:
                    # log the error
                    current_app.logger.error(f"Table parsing error: {table_data['parse_error']}")
                    
                    continue  # Skip this table but don't fail the entire process
                
                # Handle table data (assuming it returns a list of rows)
                if isinstance(table_data, dict) and 'rows' in table_data:
                    # Store table data for response
                    table_data_results[table_field.field_id] = {
                        'field_name': table_field.field_name.value,
                        'sub_fields': sub_fields,
                        'table_data': table_data
                    }
                    
                    # Store in database
                    for row_index, row_data in enumerate(table_data['rows']):
                        # Create line item
                        line_item = OCRLineItem(
                            document_id=doc_id,
                            field_id=table_field.field_id,
                            row_index=row_index
                        )
                        db.session.add(line_item)
                        db.session.flush()  # Get the ID
                        
                        # Create line item values
                        for sub_field in sub_fields:
                            value = row_data.get(sub_field.field_name.value)
                            if value is not None:
                                line_item_value = OCRLineItemValue(
                                    ocr_items_id=line_item.ocr_items_id,
                                    sub_temp_field_id=sub_field.sub_temp_field_id,
                                    predicted_value=str(value),
                                    confidence=0.8
                                )
                                db.session.add(line_item_value)
                        
                        line_item_records.append(line_item)

        # 9. Save all OCR data to database
        for ocr_data in ocr_data_records:
            db.session.add(ocr_data)

        # 10. Update document status to PROCESSED
        doc.status = DocumentStatus.PROCESSED
        from datetime import datetime
        doc.processed_at = datetime.utcnow()
        
        # 11. Commit all changes
        db.session.commit()

        # 12. Return success result
        formatted_table_data = format_table_data_for_response(table_data_results)
        
        return {
            'success': True,
            'message': 'Document processed successfully',
            'document_id': doc_id,
            'template_id': template_id,
            'status': doc.status.value,
            'extracted_data': extracted_data,
            'table_data': formatted_table_data,  # Formatted table data for frontend
            'ocr_records_created': len(ocr_data_records),
            'line_items_created': len(line_item_records)
        }

    except Exception as e:
        # Update document status to FAILED on any error
        try:
            if 'doc' in locals():
                doc.status = DocumentStatus.FAILED
                db.session.commit()
        except:
            pass
        
        return {'success': False, 'message': f'OCR processing failed: {str(e)}'}

@bp.route('/process_document', methods=['POST'])
def process_document():
    """
    Integrated OCR processing endpoint that handles the full pipeline:
    document → template → OCR → database storage
    """
    data = request.get_json()
    doc_id = data.get('doc_id')
    template_id = data.get('template_id')

    if not doc_id or not template_id:
        return jsonify({'error': 'Missing required fields: doc_id and template_id'}), 400

    result = process_document_internal(doc_id, template_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify({'error': result['message']}), 500 

@bp.route('/field/<int:field_id>/load_tally_options', methods=['POST'])
def load_field_tally_options(field_id):
    """
    Load Tally data as options for a SELECT field.
    
    Request Body:
    {
        "data_type": "auto|companies|ledgers|stock_items|customers|vendors|all_ledgers",
        "group_filter": "optional_group_name",
        "clear_existing": true
    }
    """
    try:
        data = request.get_json() or {}
        data_type = data.get('data_type', 'auto')
        group_filter = data.get('group_filter')
        clear_existing = data.get('clear_existing', True)
        
        if data_type == 'auto':
            result = auto_load_tally_options(field_id, clear_existing)
        elif data_type == 'companies':
            result = load_companies_as_options(field_id, clear_existing)
        elif data_type == 'ledgers':
            result = load_ledgers_as_options(field_id, group_filter, clear_existing)
        elif data_type == 'stock_items':
            result = load_stock_items_as_options(field_id, group_filter, clear_existing)
        elif data_type == 'customers':
            result = load_customer_options(field_id)
        elif data_type == 'vendors':
            result = load_vendor_options(field_id)
        elif data_type == 'all_ledgers':
            result = load_all_ledger_options(field_id)
        else:
            return jsonify({'error': 'Invalid data_type. Valid options: auto, companies, ledgers, stock_items, customers, vendors, all_ledgers'}), 400
            
        return jsonify(result)
        
    except TallyFieldOptionsError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error loading Tally options for field {field_id}: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@bp.route('/field/<int:field_id>/options', methods=['GET'])
def get_field_options(field_id):
    """Get current options summary for a field"""
    try:
        summary = get_field_options_summary(field_id)
        
        if 'error' in summary:
            return jsonify(summary), 404
            
        return jsonify(summary)
        
    except Exception as e:
        current_app.logger.error(f"Error getting field options for field {field_id}: {e}")
        return jsonify({'error': f'Failed to get field options: {str(e)}'}), 500

@bp.route('/field/<int:field_id>/refresh_options', methods=['POST'])
def refresh_field_tally_options(field_id):
    """Refresh field options by reloading from Tally"""
    try:
        result = refresh_field_options(field_id)
        return jsonify(result)
        
    except TallyFieldOptionsError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error refreshing options for field {field_id}: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@bp.route('/field/<int:field_id>/load_customers', methods=['POST'])
def load_field_customers(field_id):
    """Load customer ledgers as options for a field"""
    try:
        result = load_customer_options(field_id)
        return jsonify(result)
        
    except TallyFieldOptionsError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error loading customers for field {field_id}: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@bp.route('/field/<int:field_id>/load_vendors', methods=['POST'])
def load_field_vendors(field_id):
    """Load vendor ledgers as options for a field"""
    try:
        result = load_vendor_options(field_id)
        return jsonify(result)
        
    except TallyFieldOptionsError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error loading vendors for field {field_id}: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500 