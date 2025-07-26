"""
Tally Utility Functions

Helper functions for data transformation, validation, and mapping between OCR data and Tally formats.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from .config import TallyConfig

logger = logging.getLogger(__name__)


def ocr_data_to_voucher_format(ocr_data: Dict, document_type: str = "invoice") -> Dict:
    """
    Convert OCR extracted data to Tally voucher format.
    
    Args:
        ocr_data: Dictionary containing OCR extracted data
        document_type: Type of document ("invoice", "bill", "receipt")
        
    Returns:
        Dictionary formatted for Tally voucher creation
        
    Raises:
        ValueError: If required data is missing or invalid
    """
    try:
        # Determine voucher type based on document type
        voucher_type_map = {
            "invoice": "Sales",
            "bill": "Purchase", 
            "receipt": "Receipt",
            "payment": "Payment"
        }
        
        voucher_type = voucher_type_map.get(document_type.lower(), "Sales")
        
        # Extract basic voucher information
        voucher_data = {
            "voucher_type": voucher_type,
            "party_name": _extract_party_name(ocr_data),
            "date": _extract_date(ocr_data),
            "voucher_number": _extract_voucher_number(ocr_data),
            "narration": _extract_narration(ocr_data, document_type),
            "bill_ref": _extract_bill_reference(ocr_data),
            "items": _extract_line_items(ocr_data)
        }
        
        # Validate the extracted data
        is_valid, errors = validate_voucher_data(voucher_data)
        if not is_valid:
            raise ValueError(f"Invalid voucher data: {', '.join(errors)}")
        
        logger.info(f"Converted OCR data to {voucher_type} voucher format")
        return voucher_data
        
    except Exception as e:
        logger.error(f"Failed to convert OCR data to voucher format: {e}")
        raise


def validate_voucher_data(voucher_data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate voucher data before creation.
    
    Args:
        voucher_data: Dictionary containing voucher information
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields
    required_fields = ["party_name", "date", "items"]
    for field in required_fields:
        if not voucher_data.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Validate party name
    party_name = voucher_data.get("party_name", "")
    if party_name and len(party_name.strip()) < 2:
        errors.append("Party name must be at least 2 characters")
    
    # Validate date
    try:
        if voucher_data.get("date"):
            _parse_date_string(voucher_data["date"])
    except ValueError as e:
        errors.append(f"Invalid date format: {e}")
    
    # Validate items
    items = voucher_data.get("items", [])
    if not items:
        errors.append("At least one item is required")
    else:
        for i, item in enumerate(items):
            item_errors = _validate_item(item, i)
            errors.extend(item_errors)
    
    # Validate voucher type
    valid_types = ["Sales", "Purchase", "Receipt", "Payment"]
    if voucher_data.get("voucher_type") not in valid_types:
        errors.append(f"Invalid voucher type. Must be one of: {valid_types}")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def normalize_party_name(party_name: str) -> str:
    """
    Standardize party names for matching with existing ledgers.
    
    Args:
        party_name: Raw party name from OCR
        
    Returns:
        Normalized party name
    """
    if not party_name:
        return ""
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', party_name.strip())
    
    # Remove common prefixes/suffixes that might cause mismatches
    prefixes_to_remove = ['M/s', 'M/S', 'Ms.', 'Mr.', 'Mrs.']
    suffixes_to_remove = ['Pvt Ltd', 'Private Limited', 'Ltd', 'Inc', 'Corp']
    
    for prefix in prefixes_to_remove:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):].strip()
    
    for suffix in suffixes_to_remove:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()
    
    # Title case for consistency
    normalized = normalized.title()
    
    logger.debug(f"Normalized party name: '{party_name}' -> '{normalized}'")
    return normalized


def calculate_voucher_totals(line_items: List[Dict]) -> Dict:
    """
    Calculate totals from line items.
    
    Args:
        line_items: List of item dictionaries
        
    Returns:
        Dictionary containing calculated totals
    """
    totals = {
        "subtotal": 0.0,
        "tax_amount": 0.0,
        "discount_amount": 0.0,
        "total_amount": 0.0,
        "total_quantity": 0.0
    }
    
    for item in line_items:
        qty = float(item.get("qty", 0))
        rate = float(item.get("rate", 0))
        amount = float(item.get("amount", qty * rate))
        
        totals["subtotal"] += amount
        totals["total_quantity"] += qty
        
        # Add tax if present
        tax_amount = float(item.get("tax_amount", 0))
        totals["tax_amount"] += tax_amount
        
        # Add discount if present
        discount = float(item.get("discount", 0))
        totals["discount_amount"] += discount
    
    # Calculate final total
    totals["total_amount"] = totals["subtotal"] + totals["tax_amount"] - totals["discount_amount"]
    
    return totals


def _extract_party_name(ocr_data: Dict) -> str:
    """Extract party name from OCR data."""
    # Try different possible field names
    party_fields = ["party_name", "customer_name", "supplier_name", "vendor_name", "bill_to", "sold_to"]
    
    for field in party_fields:
        if field in ocr_data and ocr_data[field]:
            return normalize_party_name(str(ocr_data[field]))
    
    # If not found in direct fields, try nested structures
    if "header" in ocr_data:
        for field in party_fields:
            if field in ocr_data["header"] and ocr_data["header"][field]:
                return normalize_party_name(str(ocr_data["header"][field]))
    
    return ""


def _extract_date(ocr_data: Dict) -> str:
    """Extract date from OCR data."""
    date_fields = ["date", "invoice_date", "bill_date", "document_date", "issue_date"]
    
    for field in date_fields:
        if field in ocr_data and ocr_data[field]:
            return str(ocr_data[field])
    
    # Try nested structures
    if "header" in ocr_data:
        for field in date_fields:
            if field in ocr_data["header"] and ocr_data["header"][field]:
                return str(ocr_data["header"][field])
    
    # Default to current date if not found
    return datetime.now().strftime("%Y-%m-%d")


def _extract_voucher_number(ocr_data: Dict) -> Optional[str]:
    """Extract voucher/invoice number from OCR data."""
    number_fields = ["voucher_number", "invoice_number", "bill_number", "document_number", "ref_number"]
    
    for field in number_fields:
        if field in ocr_data and ocr_data[field]:
            return str(ocr_data[field])
    
    # Try nested structures
    if "header" in ocr_data:
        for field in number_fields:
            if field in ocr_data["header"] and ocr_data["header"][field]:
                return str(ocr_data["header"][field])
    
    return None


def _extract_narration(ocr_data: Dict, document_type: str) -> str:
    """Extract or generate narration for the voucher."""
    # Try to find existing narration
    narration_fields = ["narration", "description", "remarks", "notes"]
    
    for field in narration_fields:
        if field in ocr_data and ocr_data[field]:
            return str(ocr_data[field])
    
    # Generate default narration
    voucher_num = _extract_voucher_number(ocr_data)
    if voucher_num:
        return f"{document_type.title()} {voucher_num} - OCR Import"
    else:
        return f"{document_type.title()} - OCR Import"


def _extract_bill_reference(ocr_data: Dict) -> Optional[str]:
    """Extract bill reference for bill allocations."""
    ref_fields = ["bill_ref", "reference", "ref_number", "po_number"]
    
    for field in ref_fields:
        if field in ocr_data and ocr_data[field]:
            return str(ocr_data[field])
    
    # Use voucher number as bill reference if available
    return _extract_voucher_number(ocr_data)


def _extract_line_items(ocr_data: Dict) -> List[Dict]:
    """Extract line items from OCR data."""
    items = []
    
    # Try different possible structures for line items
    line_items_fields = ["items", "line_items", "products", "details"]
    
    for field in line_items_fields:
        if field in ocr_data and isinstance(ocr_data[field], list):
            for item in ocr_data[field]:
                processed_item = _process_line_item(item)
                if processed_item:
                    items.append(processed_item)
            break
    
    return items


def _process_line_item(item: Dict) -> Optional[Dict]:
    """Process individual line item."""
    try:
        # Extract item details
        stock_item = item.get("product_name") or item.get("item_name") or item.get("description", "")
        if not stock_item:
            return None
        
        qty = float(item.get("quantity") or item.get("qty", 1))
        rate = float(item.get("rate") or item.get("price") or item.get("unit_price", 0))
        unit = item.get("unit") or item.get("uom", TallyConfig.DEFAULT_UNIT)
        
        # Calculate amount if not provided
        amount = float(item.get("amount") or item.get("total", qty * rate))
        
        processed = {
            "stock_item": stock_item.strip(),
            "qty": qty,
            "rate": rate,
            "unit": unit,
            "amount": amount,
            "godown": item.get("godown", TallyConfig.DEFAULT_GODOWN),
            "batch": item.get("batch", TallyConfig.DEFAULT_BATCH)
        }
        
        # Add optional fields
        if "ledger" in item:
            processed["ledger"] = item["ledger"]
        
        return processed
        
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to process line item: {e}")
        return None


def _validate_item(item: Dict, index: int) -> List[str]:
    """Validate individual line item."""
    errors = []
    
    if not item.get("stock_item"):
        errors.append(f"Item {index + 1}: Missing stock item name")
    
    try:
        qty = float(item.get("qty", 0))
        if qty <= 0:
            errors.append(f"Item {index + 1}: Quantity must be greater than 0")
    except (ValueError, TypeError):
        errors.append(f"Item {index + 1}: Invalid quantity")
    
    try:
        rate = float(item.get("rate", 0))
        if rate < 0:
            errors.append(f"Item {index + 1}: Rate cannot be negative")
    except (ValueError, TypeError):
        errors.append(f"Item {index + 1}: Invalid rate")
    
    return errors


def _parse_date_string(date_str: str) -> datetime:
    """Parse date string with multiple format support."""
    if not date_str:
        raise ValueError("Empty date string")
    
    formats = [
        "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y",
        "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")
