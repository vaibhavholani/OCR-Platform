from flask import Blueprint, jsonify, request
from .. import db
from ..models import OCRData, OCRLineItem, OCRLineItemValue

bp = Blueprint('ocr', __name__, url_prefix='/api/ocr')

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