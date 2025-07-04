from flask import Blueprint, jsonify, request
from .. import db
from ..models import Export, ExportFile, Document
from ..utils.enums import ExportFormat

bp = Blueprint('exports', __name__, url_prefix='/api/exports')

@bp.route('/', methods=['GET'])
def get_exports():
    """Get all exports"""
    exports = Export.query.all()
    return jsonify({
        'exports': [export.to_dict() for export in exports],
        'count': len(exports)
    })

@bp.route('/<int:export_id>', methods=['GET'])
def get_export(export_id):
    """Get a specific export by ID"""
    export = Export.query.get_or_404(export_id)
    return jsonify(export.to_dict())

@bp.route('/', methods=['POST'])
def create_export():
    """Create a new export"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('user_id', 'document_id', 'format')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        export_format = ExportFormat(data['format'].lower())
    except ValueError as e:
        return jsonify({'error': f'Invalid export format: {str(e)}'}), 400
    
    export = Export(
        user_id=data['user_id'],
        document_id=data['document_id'],
        format=export_format,
        filename=data.get('filename'),
        file_path=data.get('file_path')
    )
    
    db.session.add(export)
    db.session.commit()
    
    return jsonify(export.to_dict()), 201

@bp.route('/<int:export_id>', methods=['DELETE'])
def delete_export(export_id):
    """Delete an export"""
    export = Export.query.get_or_404(export_id)
    db.session.delete(export)
    db.session.commit()
    return jsonify({'message': 'Export deleted successfully'})

@bp.route('/<int:export_id>/files', methods=['GET'])
def get_export_files(export_id):
    """Get all files for an export"""
    export = Export.query.get_or_404(export_id)
    files = export.export_files.all()
    return jsonify({
        'export_files': [file.to_dict() for file in files],
        'count': len(files)
    })

@bp.route('/<int:export_id>/files', methods=['POST'])
def create_export_file(export_id):
    """Create an export file"""
    export = Export.query.get_or_404(export_id)
    data = request.get_json()
    
    if not data or not all(k in data for k in ('document_id', 'file_path')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify document exists
    document = Document.query.get_or_404(data['document_id'])
    
    export_file = ExportFile(
        exp_id=export_id,
        document_id=data['document_id'],
        file_path=data['file_path']
    )
    
    db.session.add(export_file)
    db.session.commit()
    
    return jsonify(export_file.to_dict()), 201

@bp.route('/files/<int:file_id>', methods=['DELETE'])
def delete_export_file(file_id):
    """Delete an export file"""
    export_file = ExportFile.query.get_or_404(file_id)
    return jsonify({'message': 'Export file deleted successfully'})

@bp.route('/formats', methods=['GET'])
def get_export_formats():
    """Get available export formats"""
    formats = [format.value for format in ExportFormat]
    return jsonify({
        'formats': formats,
        'count': len(formats)
    }) 