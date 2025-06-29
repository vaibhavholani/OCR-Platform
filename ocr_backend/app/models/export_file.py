from datetime import datetime
from .. import db

class ExportFile(db.Model):
    __tablename__ = 'export_files'
    
    export_file_id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.ocr_id'), nullable=False)
    exp_id = db.Column(db.Integer, db.ForeignKey('exports.exp_id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'export_file_id': self.export_file_id,
            'document_id': self.document_id,
            'exp_id': self.exp_id,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ExportFile {self.export_file_id}>' 