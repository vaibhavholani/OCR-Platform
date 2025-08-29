from datetime import datetime
from .. import db

class CreditTransaction(db.Model):
    __tablename__ = 'credit_transactions'
    
    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Positive for add, negative for deduct
    balance_before = db.Column(db.Integer, nullable=False)  # Balance before this transaction
    balance_after = db.Column(db.Integer, nullable=False)  # Balance after this transaction
    description = db.Column(db.String(255), nullable=False)
    reference_type = db.Column(db.String(50))  # 'document', 'document_refund', 'manual_addition', etc.
    reference_id = db.Column(db.Integer)  # doc_id, purchase_id, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'user_id': self.user_id,
            'amount': self.amount,
            'balance_before': self.balance_before,
            'balance_after': self.balance_after,
            'description': self.description,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<CreditTransaction {self.transaction_id}: {self.amount} credits>'
