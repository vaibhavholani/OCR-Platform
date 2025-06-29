from datetime import datetime
from .. import db
from ..utils.enums import ExportFormat

class Export(db.Model):
    __tablename__ = 'exports'
    
    exp_id = db.Column(db.Integer, primary_key=True)
    format = db.Column(db.Enum(ExportFormat), nullable=False)
    export_time = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    export_files = db.relationship('ExportFile', backref='export', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'exp_id': self.exp_id,
            'format': self.format.value if self.format else None,
            'export_time': self.export_time.isoformat() if self.export_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'export_files': [file.to_dict() for file in self.export_files]
        }
    
    def __repr__(self):
        return f'<Export {self.exp_id}>' 