"""
Data Type Conversion Utilities

Functions for convertin        elif field_type == FieldType.DATE:
            # Parse to datetime but return as human-readable string for frontend
            parsed_date = parse_date_string(str_value)
            if parsed_date:
                # Return in DD/MM/YYYY format for frontend compatibility
                return parsed_date.strftime("%d/%m/%Y")
            return str_value  # Return original if parsing fails
            
        elif field_type == FieldType.NUMBER:R extracted values to their correct data types
based on field configurations in templates.
"""

import logging
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Union, Optional

from .enums import FieldType, DataType

logger = logging.getLogger(__name__)


class DataConversionError(Exception):
    """Custom exception for data conversion errors"""
    pass


def convert_template_field_value(value: Any, field_type: FieldType, field_name: str = "") -> Any:
    """
    Convert a value to the appropriate Python type based on TemplateField.field_type
    
    Args:
        value: The raw value from OCR (usually string)
        field_type: The FieldType enum value
        field_name: Optional field name for error messages
        
    Returns:
        Converted value in appropriate Python type
        
    Raises:
        DataConversionError: If conversion fails
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
        
    try:
        # Convert to string first for consistent processing
        str_value = str(value).strip()
        
        if field_type == FieldType.TEXT:
            return str_value
            
        elif field_type == FieldType.SELECT:
            # SELECT fields remain as strings (mapping is handled separately)
            return str_value
            
        elif field_type == FieldType.NUMBER:
            # Try integer first, then float
            if '.' in str_value or 'e' in str_value.lower():
                return float(str_value.replace(',', ''))
            else:
                return int(str_value.replace(',', ''))
                
        elif field_type == FieldType.DATE:
            # Parse to datetime but return as human-readable string for frontend
            parsed_date = parse_date_string(str_value)
            if parsed_date:
                # Return in DD/MM/YYYY format for frontend compatibility
                return parsed_date.strftime("%d/%m/%Y")
            return str_value  # Return original if parsing fails
            
        elif field_type == FieldType.EMAIL:
            # Validate basic email format
            if '@' not in str_value or '.' not in str_value:
                raise DataConversionError(f"Invalid email format: {str_value}")
            return str_value.lower()
            
        elif field_type == FieldType.CURRENCY:
            return parse_currency_string(str_value)
            
        elif field_type == FieldType.TABLE:
            # Tables are handled separately, return as-is
            return value
            
        else:
            logger.warning(f"Unknown field type {field_type}, returning as string")
            return str_value
            
    except (ValueError, TypeError, InvalidOperation) as e:
        error_msg = f"Failed to convert '{value}' to {field_type.value}"
        if field_name:
            error_msg += f" for field '{field_name}'"
        error_msg += f": {str(e)}"
        raise DataConversionError(error_msg)


def convert_sub_template_field_value(value: Any, data_type: DataType, field_name: str = "") -> Any:
    """
    Convert a value to the appropriate Python type based on SubTemplateField.data_type
    
    Args:
        value: The raw value from OCR (usually string)  
        data_type: The DataType enum value
        field_name: Optional field name for error messages
        
    Returns:
        Converted value in appropriate Python type
        
    Raises:
        DataConversionError: If conversion fails
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
        
    try:
        # Convert to string first for consistent processing
        str_value = str(value).strip()
        
        if data_type == DataType.STRING:
            return str_value
            
        elif data_type == DataType.SELECT:
            # SELECT fields remain as strings (mapping is handled separately)
            return str_value
            
        elif data_type == DataType.INTEGER:
            return int(str_value.replace(',', ''))
            
        elif data_type == DataType.FLOAT:
            return float(str_value.replace(',', ''))
            
        elif data_type == DataType.DATE:
            # Parse to datetime but return as human-readable string for frontend
            parsed_date = parse_date_string(str_value)
            if parsed_date:
                # Return in DD/MM/YYYY format for frontend compatibility
                return parsed_date.strftime("%d/%m/%Y")
            return str_value  # Return original if parsing fails
            
        elif data_type == DataType.BOOLEAN:
            return parse_boolean_string(str_value)
            
        else:
            logger.warning(f"Unknown data type {data_type}, returning as string")
            return str_value
            
    except (ValueError, TypeError, InvalidOperation) as e:
        error_msg = f"Failed to convert '{value}' to {data_type.value}"
        if field_name:
            error_msg += f" for field '{field_name}'"
        error_msg += f": {str(e)}"
        raise DataConversionError(error_msg)


def parse_date_string(date_str: str) -> datetime:
    """
    Parse various date formats into datetime object
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        datetime object
        
    Raises:
        DataConversionError: If date parsing fails
    """
    # Clean the date string
    date_str = date_str.strip()
    
    # Common date formats to try
    date_formats = [
        '%Y-%m-%d',          # 2024-01-15
        '%d/%m/%Y',          # 15/01/2024
        '%m/%d/%Y',          # 01/15/2024
        '%d-%m-%Y',          # 15-01-2024
        '%m-%d-%Y',          # 01-15-2024
        '%d-%b-%Y',          # 24-Jun-2025
        '%d-%B-%Y',          # 24-June-2025
        '%d.%m.%Y',          # 15.01.2024
        '%Y/%m/%d',          # 2024/01/15
        '%B %d, %Y',         # January 15, 2024
        '%b %d, %Y',         # Jan 15, 2024
        '%d %B %Y',          # 15 January 2024
        '%d %b %Y',          # 15 Jan 2024
        '%Y-%m-%d %H:%M:%S', # 2024-01-15 14:30:00
        '%d/%m/%Y %H:%M',    # 15/01/2024 14:30
    ]
    
    for date_format in date_formats:
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            continue
    
    # Try to parse ISO format with timezone
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        pass
    
    raise DataConversionError(f"Unable to parse date: '{date_str}'")


def parse_currency_string(currency_str: str) -> Decimal:
    """
    Parse currency string into Decimal for precise monetary calculations
    
    Args:
        currency_str: Currency string (e.g., "$1,234.56", "₹1,23,456.78")
        
    Returns:
        Decimal value
        
    Raises:
        DataConversionError: If currency parsing fails
    """
    # Remove currency symbols and whitespace
    clean_str = re.sub(r'[^\d,.-]', '', currency_str.strip())
    
    # Handle different number formats
    # Remove commas (thousand separators)
    clean_str = clean_str.replace(',', '')
    
    try:
        return Decimal(clean_str)
    except InvalidOperation:
        raise DataConversionError(f"Unable to parse currency: '{currency_str}'")


def parse_boolean_string(bool_str: str) -> bool:
    """
    Parse string into boolean value
    
    Args:
        bool_str: String representation of boolean
        
    Returns:
        Boolean value
        
    Raises:
        DataConversionError: If boolean parsing fails
    """
    clean_str = bool_str.strip().lower()
    
    true_values = {'true', '1', 'yes', 'y', 'on', 'enable', 'enabled', 'active'}
    false_values = {'false', '0', 'no', 'n', 'off', 'disable', 'disabled', 'inactive'}
    
    if clean_str in true_values:
        return True
    elif clean_str in false_values:
        return False
    else:
        raise DataConversionError(f"Unable to parse boolean: '{bool_str}'")


def safe_convert_template_field_value(value: Any, field_type: FieldType, field_name: str = "") -> tuple[Any, Optional[str]]:
    """
    Safely convert a template field value, returning the converted value and any error message
    
    Args:
        value: The raw value from OCR
        field_type: The FieldType enum value
        field_name: Optional field name for error messages
        
    Returns:
        Tuple of (converted_value, error_message)
        If conversion succeeds: (converted_value, None)
        If conversion fails: (original_value, error_message)
    """
    try:
        converted_value = convert_template_field_value(value, field_type, field_name)
        return converted_value, None
    except DataConversionError as e:
        logger.warning(f"Data conversion failed: {str(e)}")
        return value, str(e)


def safe_convert_sub_template_field_value(value: Any, data_type: DataType, field_name: str = "") -> tuple[Any, Optional[str]]:
    """
    Safely convert a sub-template field value, returning the converted value and any error message
    
    Args:
        value: The raw value from OCR
        data_type: The DataType enum value
        field_name: Optional field name for error messages
        
    Returns:
        Tuple of (converted_value, error_message)
        If conversion succeeds: (converted_value, None)
        If conversion fails: (original_value, error_message)
    """
    try:
        converted_value = convert_sub_template_field_value(value, data_type, field_name)
        return converted_value, None
    except DataConversionError as e:
        logger.warning(f"Data conversion failed: {str(e)}")
        return value, str(e)
