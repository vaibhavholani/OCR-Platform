from datetime import datetime
from .. import db
from ..utils.enums import FieldType, FieldName

class TemplateField(db.Model):
    __tablename__ = 'template_fields'
    
    field_id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('templates.temp_id'), nullable=False)
    field_name = db.Column(db.Enum(FieldName), nullable=False)
    field_order = db.Column(db.Integer, nullable=False)
    field_type = db.Column(db.Enum(FieldType), nullable=False)
    ai_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sub_template_fields = db.relationship('SubTemplateField', backref='template_field', lazy='dynamic', cascade='all, delete-orphan')
    field_options = db.relationship('FieldOption', backref='template_field', lazy='dynamic', cascade='all, delete-orphan')
    ocr_data = db.relationship('OCRData', backref='template_field', lazy='dynamic', cascade='all, delete-orphan')
    ocr_line_items = db.relationship('OCRLineItem', backref='template_field', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'field_id': self.field_id,
            'template_id': self.template_id,
            'field_name': self.field_name.value if self.field_name else None,
            'field_order': self.field_order,
            'field_type': self.field_type.value if self.field_type else None,
            'ai_instructions': self.ai_instructions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'sub_template_fields': [sub_field.to_dict() for sub_field in self.sub_template_fields],
            'field_options': [option.to_dict() for option in self.field_options]
        }
    
    def __repr__(self):
        return f'<TemplateField {self.field_name}>' 