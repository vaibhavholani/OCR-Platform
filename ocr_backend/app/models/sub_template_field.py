from datetime import datetime
from .. import db
from ..utils.enums import FieldName, DataType

class SubTemplateField(db.Model):
    __tablename__ = 'sub_template_fields'
    
    sub_temp_field_id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('template_fields.field_id'), nullable=False)
    field_name = db.Column(db.Enum(FieldName), nullable=False)
    data_type = db.Column(db.Enum(DataType), nullable=False)
    ai_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ocr_line_item_values = db.relationship('OCRLineItemValue', backref='sub_template_field', lazy='dynamic', cascade='all, delete-orphan')
    sub_field_options = db.relationship('SubTemplateFieldOption', backref='sub_template_field', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'sub_temp_field_id': self.sub_temp_field_id,
            'field_id': self.field_id,
            'field_name': self.field_name.value if self.field_name else None,
            'data_type': self.data_type.value if self.data_type else None,
            'ai_instructions': self.ai_instructions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'sub_field_options': [option.to_dict() for option in self.sub_field_options]
        }
    
    def __repr__(self):
        return f'<SubTemplateField {self.field_name}>' 