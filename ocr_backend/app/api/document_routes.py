from flask import Blueprint, jsonify, request, current_app
from .. import db
from ..models import Document, OCRData, OCRLineItem, OCRLineItemValue, Template, TemplateField, SubTemplateField
from ..utils.enums import DocumentStatus, FieldType
import os
from werkzeug.utils import secure_filename

bp = Blueprint('documents', __name__, url_prefix='/api/documents')

def reconstruct_table_data_from_db(document_id):
    """
    Reconstruct table data from stored OCRLineItem and OCRLineItemValue records
    in the same format as the processing function
    """
    # Get all table fields for line items in this document
    table_fields_query = db.session.query(TemplateField).join(
        OCRLineItem, TemplateField.field_id == OCRLineItem.field_id
    ).filter(
        OCRLineItem.document_id == document_id,
        TemplateField.field_type == FieldType.TABLE
    ).distinct().all()
    
    formatted_tables = {}
    
    for table_field in table_fields_query:
        # Get sub-template fields (columns)
        sub_fields = SubTemplateField.query.filter_by(field_id=table_field.field_id).all()
        
        # Get line items for this table field
        line_items = OCRLineItem.query.filter_by(
            document_id=document_id,
            field_id=table_field.field_id
        ).order_by(OCRLineItem.row_index).all()
        
        # Reconstruct rows
        rows = []
        for line_item in line_items:
            row_data = {}
            for value in line_item.ocr_line_item_values:
                if value.sub_template_field:
                    row_data[value.sub_template_field.field_name.value] = value.predicted_value or value.actual_value
            rows.append(row_data)
        
        # Format columns info
        columns = []
        for sub_field in sub_fields:
            columns.append({
                'name': sub_field.field_name.value,
                'data_type': sub_field.data_type.value,
                'sub_temp_field_id': sub_field.sub_temp_field_id
            })
        
        # Add to formatted tables
        formatted_tables[table_field.field_name.value] = {
            'field_id': table_field.field_id,
            'field_type': 'table',
            'columns': columns,
            'rows': rows,
            'row_count': len(rows)
        }
    
    return formatted_tables

@bp.route('/', methods=['GET'])
def get_documents():
    """Get all documents"""
    documents = Document.query.all()
    return jsonify({
        'documents': [document.to_dict() for document in documents],
        'count': len(documents)
    })

@bp.route('/<int:document_id>', methods=['GET'])
def get_document(document_id):
    """Get a specific document by ID"""
    document = Document.query.get_or_404(document_id)
    return jsonify(document.to_dict())

@bp.route('/', methods=['POST'])
def create_document():
    """Create a new document (supports file upload via multipart/form-data or JSON)"""
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        # Handle file upload
        if 'file' not in request.files or 'user_id' not in request.form:
            return jsonify({'error': 'Missing required fields (file, user_id)'}), 400
        
        file = request.files['file']
        user_id = request.form['user_id']
        template_id = request.form.get('template_id')  # Optional template_id
        auto_process = request.form.get('auto_process', 'false').lower() == 'true'
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        filename = secure_filename(file.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        rel_file_path = os.path.relpath(file_path, start=current_app.config['BASE_DIR'])
        
        document = Document(
            user_id=user_id,
            file_path=rel_file_path,
            original_filename=filename,
            status=DocumentStatus.PENDING
        )
        
        db.session.add(document)
        db.session.commit()
        
        # If template_id is provided and auto_process is True, trigger OCR processing
        if template_id and auto_process:
            try:
                # Import here to avoid circular imports
                from ..api.ocr_routes import process_document_internal
                result = process_document_internal(document.doc_id, int(template_id))
                
                return jsonify({
                    'document': document.to_dict(),
                    'ocr_processing': {
                        'status': 'completed' if result['success'] else 'failed',
                        'message': result['message'],
                        'extracted_data': result.get('extracted_data', {})
                    }
                }), 201
            except Exception as e:
                current_app.logger.error(f"Auto OCR processing failed: {str(e)}")
                return jsonify({
                    'document': document.to_dict(),
                    'ocr_processing': {
                        'status': 'failed',
                        'message': f'OCR processing failed: {str(e)}'
                    }
                }), 201
        
        return jsonify(document.to_dict()), 201
    else:
        # Fallback to old JSON-based logic
        data = request.get_json()
        if not data or not all(k in data for k in ('user_id', 'file_path', 'original_filename')):
            return jsonify({'error': 'Missing required fields'}), 400
        
        document = Document(
            user_id=data['user_id'],
            file_path=data['file_path'],
            original_filename=data['original_filename'],
            status=DocumentStatus.PENDING
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify(document.to_dict()), 201

@bp.route('/<int:document_id>', methods=['PUT'])
def update_document(document_id):
    """Update a document"""
    document = Document.query.get_or_404(document_id)
    data = request.get_json()
    
    try:
        if 'status' in data:
            document.status = DocumentStatus(data['status'].lower())
        if 'filename' in data:
            document.filename = data['filename']
        if 'file_path' in data:
            document.file_path = data['file_path']
    except ValueError as e:
        return jsonify({'error': f'Invalid status: {str(e)}'}), 400
    
    db.session.commit()
    return jsonify(document.to_dict())

@bp.route('/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document"""
    document = Document.query.get_or_404(document_id)
    db.session.delete(document)
    db.session.commit()
    return jsonify({'message': 'Document deleted successfully'})

@bp.route('/<int:document_id>/ocr-data', methods=['GET'])
def get_document_ocr_data(document_id):
    """Get OCR data for a document"""
    document = Document.query.get_or_404(document_id)
    ocr_data = document.ocr_data.all()
    return jsonify({
        'ocr_data': [data.to_dict() for data in ocr_data],
        'count': len(ocr_data)
    })

@bp.route('/<int:document_id>/ocr-data', methods=['POST'])
def create_ocr_data(document_id):
    """Create OCR data for a document"""
    document = Document.query.get_or_404(document_id)
    data = request.get_json()
    
    if not data or not all(k in data for k in ('field_id', 'predicted_value')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    ocr_data = OCRData(
        document_id=document_id,
        field_id=data['field_id'],
        predicted_value=data['predicted_value'],
        actual_value=data.get('actual_value'),
        confidence=data.get('confidence', 0.0)
    )
    
    db.session.add(ocr_data)
    db.session.commit()
    
    return jsonify(ocr_data.to_dict()), 201

@bp.route('/<int:document_id>/line-items', methods=['GET'])
def get_document_line_items(document_id):
    """Get line items for a document"""
    document = Document.query.get_or_404(document_id)
    line_items = document.ocr_line_items.all()
    return jsonify({
        'line_items': [item.to_dict() for item in line_items],
        'count': len(line_items)
    })

@bp.route('/<int:document_id>/line-items', methods=['POST'])
def create_line_item(document_id):
    """Create a line item for a document"""
    document = Document.query.get_or_404(document_id)
    data = request.get_json()
    
    if not data or not all(k in data for k in ('field_id', 'row_index')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    line_item = OCRLineItem(
        document_id=document_id,
        field_id=data['field_id'],
        row_index=data['row_index']
    )
    
    db.session.add(line_item)
    db.session.commit()
    
    return jsonify(line_item.to_dict()), 201

@bp.route('/line-items/<int:line_item_id>/values', methods=['POST'])
def create_line_item_value(line_item_id):
    """Create a value for a line item"""
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

@bp.route('/<int:document_id>/status', methods=['GET'])
def get_document_status(document_id):
    """Get document processing status"""
    try:
        document = Document.query.get_or_404(document_id)
        
        # Get OCR data count
        ocr_data_count = OCRData.query.filter_by(document_id=document_id).count()
        line_items_count = OCRLineItem.query.filter_by(document_id=document_id).count()
        
        return jsonify({
            'document_id': document_id,
            'status': document.status.value,
            'original_filename': document.original_filename,
            'created_at': document.created_at.isoformat() if document.created_at else None,
            'processed_at': document.processed_at.isoformat() if document.processed_at else None,
            'ocr_data_count': ocr_data_count,
            'line_items_count': line_items_count,
            'has_ocr_data': ocr_data_count > 0 or line_items_count > 0
        })
    except Exception as e:
        current_app.logger.error(f"Error getting document status: {str(e)}")
        return jsonify({'error': 'Failed to get document status'}), 500

@bp.route('/<int:document_id>/ocr-results', methods=['GET'])
def get_document_ocr_results(document_id):
    """Get complete OCR results for a document"""
    try:
        document = Document.query.get_or_404(document_id)
        
        # Get OCR data with field information (non-table fields)
        ocr_data = db.session.query(OCRData, TemplateField).join(
            TemplateField, OCRData.field_id == TemplateField.field_id
        ).filter(OCRData.document_id == document_id).all()
        
        # Format extracted data (text fields)
        extracted_data = {}
        for ocr, field in ocr_data:
            extracted_data[field.field_name.value] = ocr.predicted_value or ocr.actual_value
        
        # Get formatted table data
        table_data = reconstruct_table_data_from_db(document_id)
        
        return jsonify({
            'document_id': document_id,
            'status': document.status.value,
            'original_filename': document.original_filename,
            'processed_at': document.processed_at.isoformat() if document.processed_at else None,
            'extracted_data': extracted_data,  # Text fields in same format as processing
            'table_data': table_data  # Table data in same format as processing
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting OCR results: {str(e)}")
        return jsonify({'error': 'Failed to get OCR results'}), 500

@bp.route('/<int:document_id>/reprocess', methods=['POST'])
def reprocess_document(document_id):
    """Reprocess a document with a specific template"""
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        
        if not template_id:
            return jsonify({'error': 'Missing template_id'}), 400
        
        document = Document.query.get_or_404(document_id)
        
        # Clear existing OCR data
        OCRData.query.filter_by(document_id=document_id).delete()
        
        # Clear existing line items (cascade will handle values)
        OCRLineItem.query.filter_by(document_id=document_id).delete()
        
        db.session.commit()
        
        # Reset document status
        document.status = DocumentStatus.PENDING
        document.processed_at = None
        db.session.commit()
        
        # Trigger reprocessing
        from ..api.ocr_routes import process_document_internal
        result = process_document_internal(document_id, template_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['message']}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error reprocessing document: {str(e)}")
        return jsonify({'error': 'Failed to reprocess document'}), 500 