from datetime import datetime
from .. import db

class OCRData(db.Model):
    __tablename__ = 'ocr_data'
    
    ocr_id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.ocr_id'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('template_fields.field_id'), nullable=False)
    predicted_value = db.Column(db.Text)
    actual_value = db.Column(db.Text)
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'ocr_id': self.ocr_id,
            'document_id': self.document_id,
            'field_id': self.field_id,
            'predicted_value': self.predicted_value,
            'actual_value': self.actual_value,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<OCRData {self.ocr_id}>' 