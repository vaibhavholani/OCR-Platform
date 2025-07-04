from flask import Blueprint, jsonify
from ..utils.enums import DocumentStatus, FieldType, DataType, ExportFormat, FieldName

bp = Blueprint('enums', __name__, url_prefix='/api/enums')

@bp.route('/', methods=['GET'])
def get_all_enums():
    """Get all available enums"""
    return jsonify({
        'document_status': [status.value for status in DocumentStatus],
        'field_types': [field_type.value for field_type in FieldType],
        'data_types': [data_type.value for data_type in DataType],
        'export_formats': [format.value for format in ExportFormat],
        'field_names': [field_name.value for field_name in FieldName]
    })

@bp.route('/document-status', methods=['GET'])
def get_document_status():
    """Get available document status options"""
    statuses = [status.value for status in DocumentStatus]
    return jsonify({
        'document_status': statuses,
        'count': len(statuses)
    })

@bp.route('/field-types', methods=['GET'])
def get_field_types():
    """Get available field types"""
    types = [field_type.value for field_type in FieldType]
    return jsonify({
        'field_types': types,
        'count': len(types)
    })

@bp.route('/data-types', methods=['GET'])
def get_data_types():
    """Get available data types"""
    types = [data_type.value for data_type in DataType]
    return jsonify({
        'data_types': types,
        'count': len(types)
    })

@bp.route('/export-formats', methods=['GET'])
def get_export_formats():
    """Get available export formats"""
    formats = [format.value for format in ExportFormat]
    return jsonify({
        'export_formats': formats,
        'count': len(formats)
    })

@bp.route('/field-names', methods=['GET'])
def get_field_names():
    """Get available field names"""
    names = [field_name.value for field_name in FieldName]
    return jsonify({
        'field_names': names,
        'count': len(names)
    }) 