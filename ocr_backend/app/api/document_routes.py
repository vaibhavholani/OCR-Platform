from flask import Blueprint, jsonify, request
from .. import db
from ..models import Document, OCRData, OCRLineItem, OCRLineItemValue, Template, TemplateField
from ..utils.enums import DocumentStatus

bp = Blueprint('documents', __name__, url_prefix='/api/documents')

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
    """Create a new document"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('user_id', 'filename')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    document = Document(
        user_id=data['user_id'],
        filename=data['filename'],
        file_path=data.get('file_path')
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