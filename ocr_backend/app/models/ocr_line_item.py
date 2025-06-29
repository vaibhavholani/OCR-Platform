from datetime import datetime
from .. import db

class OCRLineItem(db.Model):
    __tablename__ = 'ocr_line_items'
    
    ocr_items_id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.ocr_id'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('template_fields.field_id'), nullable=False)
    row_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ocr_line_item_values = db.relationship('OCRLineItemValue', backref='ocr_line_item', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'ocr_items_id': self.ocr_items_id,
            'document_id': self.document_id,
            'field_id': self.field_id,
            'row_index': self.row_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'ocr_line_item_values': [value.to_dict() for value in self.ocr_line_item_values]
        }
    
    def __repr__(self):
        return f'<OCRLineItem {self.ocr_items_id}>' 