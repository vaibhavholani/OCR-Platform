from .base_service import BaseService
from .credit_service import CreditService
from ..models import Document
from ..utils.enums import DocumentStatus
from .. import db
from typing import Tuple, Optional, Dict

class OCRService(BaseService):
    """Service for handling OCR processing logic with credit management"""
    
    @classmethod
    def check_credits_before_processing(cls, doc_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """
        Check if user has sufficient credits before OCR processing
        
        Returns:
            Tuple[success, message, result_info]
        """
        try:
            document = Document.query.get(doc_id)
            if not document:
                return False, "Document not found", None
            
            # Check if user has sufficient credits
            credit_success, credit_message, credit_info = CreditService.check_user_credits(
                user_id=document.user_id,
                required_amount=1
            )
            
            return credit_success, credit_message, credit_info
            
        except Exception as e:
            cls.log_error("Error checking credits before processing", e)
            return False, f"Error checking credits: {str(e)}", None
    
    @classmethod
    def deduct_credits_for_processing(cls, doc_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """
        Deduct credits for OCR processing
        
        Returns:
            Tuple[success, message, transaction_info]
        """
        try:
            document = Document.query.get(doc_id)
            if not document:
                return False, "Document not found", None
            
            return CreditService.deduct_credits_for_ocr(
                user_id=document.user_id,
                doc_id=doc_id
            )
            
        except Exception as e:
            cls.log_error("Error deducting credits for processing", e)
            return False, f"Error deducting credits: {str(e)}", None
    
    @classmethod
    def refund_credits_for_failed_processing(cls, doc_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """
        Refund credits when OCR processing fails
        
        Returns:
            Tuple[success, message, refund_info]
        """
        try:
            document = Document.query.get(doc_id)
            if not document:
                return False, "Document not found", None
            
            return CreditService.refund_credits_for_failed_ocr(
                user_id=document.user_id,
                doc_id=doc_id
            )
            
        except Exception as e:
            cls.log_error("Error refunding credits for failed processing", e)
            return False, f"Error refunding credits: {str(e)}", None
    
    # TODO: Implement actual OCR processing methods later
    # These will include:
    # - process_document_with_template()
    # - _perform_ocr_processing()
    # - Integration with existing OCR pipeline
