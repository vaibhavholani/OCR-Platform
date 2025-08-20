from datetime import datetime
from .. import db

class SubTemplateFieldOption(db.Model):
    __tablename__ = 'sub_template_field_options'
    
    sub_options_id = db.Column(db.Integer, primary_key=True)
    sub_temp_field_id = db.Column(db.Integer, db.ForeignKey('sub_template_fields.sub_temp_field_id'), nullable=False)
    option_value = db.Column(db.String(100), nullable=False)
    option_label = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'sub_options_id': self.sub_options_id,
            'sub_temp_field_id': self.sub_temp_field_id,
            'option_value': self.option_value,
            'option_label': self.option_label,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<SubTemplateFieldOption {self.option_label}>'
