from .base_service import BaseService
from ..models import User, CreditTransaction, Document
from .. import db
from typing import Tuple, Optional, Dict, Any

class CreditService(BaseService):
    """Service for handling all credit-related operations"""
    
    DEFAULT_OCR_COST = 1
    
    @classmethod
    def check_user_credits(cls, user_id: int, required_amount: int = 1) -> Tuple[bool, str, Optional[Dict]]:
        """
        Check if user has sufficient credits
        
        Returns:
            Tuple[success, message, user_info]
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found", None
            
            user_info = {
                'user_id': user_id,
                'current_balance': user.credits_remaining,
                'plan_type': user.plan_type
            }
            
            if user.credits_remaining >= required_amount:
                return True, f"Sufficient credits available", user_info
            else:
                return False, f"Insufficient credits. Required: {required_amount}, Available: {user.credits_remaining}", user_info
                
        except Exception as e:
            cls.log_error("Error checking user credits", e)
            return False, "Error checking credits", None
    
    @classmethod
    def deduct_credits_for_ocr(cls, user_id: int, doc_id: int, cost: int = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        Deduct credits for OCR processing with full transaction tracking
        
        Returns:
            Tuple[success, message, transaction_info]
        """
        if cost is None:
            cost = cls.DEFAULT_OCR_COST
            
        try:
            user = User.query.get(user_id)
            document = Document.query.get(doc_id)
            
            if not user:
                return False, "User not found", None
            
            if not document:
                return False, "Document not found", None
            
            # Check if credits are sufficient
            if user.credits_remaining < cost:
                return False, f"Insufficient credits. Required: {cost}, Available: {user.credits_remaining}", None
            
            # Calculate new balance
            balance_before = user.credits_remaining
            new_balance = balance_before - cost
            
            # Create transaction record
            transaction = CreditTransaction(
                user_id=user_id,
                amount=-cost,  # Negative for deduction
                balance_before=balance_before,
                balance_after=new_balance,
                description=f"OCR processing for document: {document.original_filename}",
                reference_type='document',
                reference_id=doc_id
            )
            
            # Update user balance
            user.credits_remaining = new_balance
            
            # Save to database
            db.session.add(transaction)
            
            if cls.commit_or_rollback():
                cls.log_info(f"Credits deducted successfully. User: {user_id}, Document: {doc_id}, Amount: {cost}")
                
                return True, f"Successfully deducted {cost} credit(s)", {
                    'transaction_id': transaction.transaction_id,
                    'amount_deducted': cost,
                    'balance_before': balance_before,
                    'balance_after': new_balance,
                    'document_id': doc_id
                }
            else:
                return False, "Failed to save transaction", None
                
        except Exception as e:
            cls.log_error("Error deducting credits for OCR", e)
            return False, f"Error processing credit deduction: {str(e)}", None
    
    @classmethod
    def refund_credits_for_failed_ocr(cls, user_id: int, doc_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """
        Refund credits when OCR processing fails
        
        Returns:
            Tuple[success, message, refund_info]
        """
        try:
            # Find the original deduction transaction
            original_transaction = CreditTransaction.query.filter_by(
                user_id=user_id,
                reference_type='document',
                reference_id=doc_id
            ).filter(CreditTransaction.amount < 0).order_by(CreditTransaction.created_at.desc()).first()
            
            if not original_transaction:
                return False, "No deduction transaction found for this document", None
            
            user = User.query.get(user_id)
            document = Document.query.get(doc_id)
            
            if not user or not document:
                return False, "User or document not found", None
            
            # Calculate refund amount (absolute value of original deduction)
            refund_amount = abs(original_transaction.amount)
            balance_before = user.credits_remaining
            new_balance = balance_before + refund_amount
            
            # Create refund transaction
            refund_transaction = CreditTransaction(
                user_id=user_id,
                amount=refund_amount,  # Positive for refund
                balance_before=balance_before,
                balance_after=new_balance,
                description=f"Refund for failed OCR processing: {document.original_filename}",
                reference_type='document_refund',
                reference_id=doc_id
            )
            
            # Update user balance
            user.credits_remaining = new_balance
            
            # Save to database
            db.session.add(refund_transaction)
            
            if cls.commit_or_rollback():
                cls.log_info(f"Credits refunded successfully. User: {user_id}, Document: {doc_id}, Amount: {refund_amount}")
                
                return True, f"Successfully refunded {refund_amount} credit(s)", {
                    'transaction_id': refund_transaction.transaction_id,
                    'amount_refunded': refund_amount,
                    'balance_before': balance_before,
                    'balance_after': new_balance,
                    'original_transaction_id': original_transaction.transaction_id
                }
            else:
                return False, "Failed to save refund transaction", None
                
        except Exception as e:
            cls.log_error("Error refunding credits for failed OCR", e)
            return False, f"Error processing credit refund: {str(e)}", None
    
    @classmethod
    def add_credits_to_user(cls, user_id: int, amount: int, description: str = "Manual credit addition") -> Tuple[bool, str, Optional[Dict]]:
        """
        Add credits to user account
        
        Returns:
            Tuple[success, message, transaction_info]
        """
        try:
            if amount <= 0:
                return False, "Amount must be positive", None
            
            user = User.query.get(user_id)
            if not user:
                return False, "User not found", None
            
            balance_before = user.credits_remaining
            new_balance = balance_before + amount
            
            # Create transaction record
            transaction = CreditTransaction(
                user_id=user_id,
                amount=amount,  # Positive for addition
                balance_before=balance_before,
                balance_after=new_balance,
                description=description,
                reference_type='manual_addition'
            )
            
            # Update user balance
            user.credits_remaining = new_balance
            
            # Save to database
            db.session.add(transaction)
            
            if cls.commit_or_rollback():
                cls.log_info(f"Credits added successfully. User: {user_id}, Amount: {amount}")
                
                return True, f"Successfully added {amount} credit(s)", {
                    'transaction_id': transaction.transaction_id,
                    'amount_added': amount,
                    'balance_before': balance_before,
                    'balance_after': new_balance
                }
            else:
                return False, "Failed to save transaction", None
                
        except Exception as e:
            cls.log_error("Error adding credits to user", e)
            return False, f"Error adding credits: {str(e)}", None
    
    @classmethod
    def get_user_credit_summary(cls, user_id: int) -> Optional[Dict]:
        """
        Get comprehensive credit summary for user
        
        Returns:
            Dict with credit info or None if user not found
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            # Get recent transactions (last 20)
            recent_transactions = CreditTransaction.query.filter_by(
                user_id=user_id
            ).order_by(CreditTransaction.created_at.desc()).limit(20).all()
            
            # Calculate statistics
            total_added = sum(t.amount for t in user.credit_transactions if t.amount > 0)
            total_spent = abs(sum(t.amount for t in user.credit_transactions if t.amount < 0))
            total_refunded = sum(t.amount for t in user.credit_transactions if t.reference_type == 'document_refund')
            
            return {
                'user_info': {
                    'user_id': user_id,
                    'name': user.name,
                    'email': user.email,
                    'plan_type': user.plan_type
                },
                'credits': {
                    'current_balance': user.credits_remaining,
                    'total_added': total_added,
                    'total_spent': total_spent,
                    'total_refunded': total_refunded
                },
                'recent_transactions': [t.to_dict() for t in recent_transactions],
                'transaction_count': user.credit_transactions.count()
            }
            
        except Exception as e:
            cls.log_error("Error getting user credit summary", e)
            return None
    
    @classmethod
    def get_document_credit_usage(cls, doc_id: int) -> Optional[Dict]:
        """
        Get credit transactions related to a specific document
        
        Returns:
            Dict with transaction info or None if not found
        """
        try:
            transactions = CreditTransaction.query.filter_by(
                reference_id=doc_id
            ).filter(
                CreditTransaction.reference_type.in_(['document', 'document_refund'])
            ).order_by(CreditTransaction.created_at.asc()).all()
            
            if not transactions:
                return None
            
            # Calculate net cost for this document
            net_cost = sum(t.amount for t in transactions)
            
            return {
                'document_id': doc_id,
                'net_cost': abs(net_cost),  # Show as positive number
                'transactions': [t.to_dict() for t in transactions],
                'has_refund': any(t.reference_type == 'document_refund' for t in transactions)
            }
            
        except Exception as e:
            cls.log_error("Error getting document credit usage", e)
            return None
