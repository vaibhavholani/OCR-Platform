from datetime import datetime
from .. import db

class OCRLineItemValue(db.Model):
    __tablename__ = 'ocr_line_item_values'
    
    ocr_items_value_id = db.Column(db.Integer, primary_key=True)
    ocr_items_id = db.Column(db.Integer, db.ForeignKey('ocr_line_items.ocr_items_id'), nullable=False)
    sub_temp_field_id = db.Column(db.Integer, db.ForeignKey('sub_template_fields.sub_temp_field_id'), nullable=False)
    predicted_value = db.Column(db.Text)
    actual_value = db.Column(db.Text)
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'ocr_items_value_id': self.ocr_items_value_id,
            'ocr_items_id': self.ocr_items_id,
            'sub_temp_field_id': self.sub_temp_field_id,
            'predicted_value': self.predicted_value,
            'actual_value': self.actual_value,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<OCRLineItemValue {self.ocr_items_value_id}>' 