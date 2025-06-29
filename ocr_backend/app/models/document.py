from datetime import datetime
from .. import db
from ..utils.enums import DocumentStatus

class Document(db.Model):
    __tablename__ = 'documents'
    
    ocr_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Relationships
    ocr_data = db.relationship('OCRData', backref='document', lazy='dynamic', cascade='all, delete-orphan')
    ocr_line_items = db.relationship('OCRLineItem', backref='document', lazy='dynamic', cascade='all, delete-orphan')
    export_files = db.relationship('ExportFile', backref='document', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'ocr_id': self.ocr_id,
            'user_id': self.user_id,
            'file_path': self.file_path,
            'original_filename': self.original_filename,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
    
    def __repr__(self):
        return f'<Document {self.original_filename}>' 