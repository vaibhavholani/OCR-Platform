from datetime import datetime
from .. import db

class Template(db.Model):
    __tablename__ = 'templates'
    
    temp_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    ai_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    template_fields = db.relationship('TemplateField', backref='template', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'temp_id': self.temp_id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'ai_instructions': self.ai_instructions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'template_fields': [field.to_dict() for field in self.template_fields]
        }
    
    def __repr__(self):
        return f'<Template {self.name}>' 