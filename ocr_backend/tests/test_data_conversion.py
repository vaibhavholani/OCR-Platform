"""
Tests for data type conversion functionality in OCR processing.

These tests verify that OCR extracted values are properly converted to the correct
Python data types based on field configurations.
"""

import os
import sys
import pytest
from datetime import datetime
from decimal import Decimal

# Ensure the package root (ocr_backend) is on sys.path so `import app` works when pytest
# is executed from the repository root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.utils.data_conversion import (
    convert_template_field_value,
    convert_sub_template_field_value,
    safe_convert_template_field_value,
    safe_convert_sub_template_field_value,
    parse_date_string,
    parse_currency_string,
    parse_boolean_string,
    DataConversionError
)
from app.utils.enums import FieldType, DataType


@pytest.fixture
def app():
    # Create a fresh app for testing
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


class TestTemplateFieldConversion:
    """Test conversion of template field values"""

    def test_text_field_conversion(self, app):
        result = convert_template_field_value("Hello World", FieldType.TEXT)
        assert result == "Hello World"
        assert isinstance(result, str)

    def test_select_field_conversion(self, app):
        result = convert_template_field_value("Option A", FieldType.SELECT)
        assert result == "Option A"
        assert isinstance(result, str)

    def test_number_field_integer_conversion(self, app):
        result = convert_template_field_value("42", FieldType.NUMBER)
        assert result == 42
        assert isinstance(result, int)

    def test_number_field_float_conversion(self, app):
        result = convert_template_field_value("42.5", FieldType.NUMBER)
        assert result == 42.5
        assert isinstance(result, float)

    def test_number_field_with_commas(self, app):
        result = convert_template_field_value("1,234", FieldType.NUMBER)
        assert result == 1234
        assert isinstance(result, int)

    def test_date_field_conversion(self, app):
        result = convert_template_field_value("2024-01-15", FieldType.DATE)
        assert isinstance(result, str)
        assert result == "15/01/2024"  # Should return formatted date string
        
        # Test different date formats all return same result
        test_dates = ["15/01/2024", "2024-01-15", "January 15, 2024", "15-Jan-2024"]
        for test_date in test_dates:
            result = convert_template_field_value(test_date, FieldType.DATE)
            assert result == "15/01/2024"
            
        # Test the problematic format from user issue
        result = convert_template_field_value("24-Jun-2025", FieldType.DATE)
        assert result == "24/06/2025"

    def test_email_field_conversion(self, app):
        result = convert_template_field_value("user@example.com", FieldType.EMAIL)
        assert result == "user@example.com"
        assert isinstance(result, str)

    def test_email_field_invalid(self, app):
        with pytest.raises(DataConversionError):
            convert_template_field_value("invalid-email", FieldType.EMAIL)

    def test_currency_field_conversion(self, app):
        result = convert_template_field_value("$1,234.56", FieldType.CURRENCY)
        assert isinstance(result, Decimal)
        assert result == Decimal('1234.56')

    def test_null_value_conversion(self, app):
        result = convert_template_field_value(None, FieldType.TEXT)
        assert result is None

    def test_empty_string_conversion(self, app):
        result = convert_template_field_value("", FieldType.TEXT)
        assert result is None


class TestSubTemplateFieldConversion:
    """Test conversion of sub-template field values"""

    def test_string_data_type(self, app):
        result = convert_sub_template_field_value("Hello", DataType.STRING)
        assert result == "Hello"
        assert isinstance(result, str)

    def test_integer_data_type(self, app):
        result = convert_sub_template_field_value("42", DataType.INTEGER)
        assert result == 42
        assert isinstance(result, int)

    def test_float_data_type(self, app):
        result = convert_sub_template_field_value("42.5", DataType.FLOAT)
        assert result == 42.5
        assert isinstance(result, float)

    def test_date_data_type(self, app):
        result = convert_sub_template_field_value("2024-01-15", DataType.DATE)
        assert isinstance(result, str)
        assert result == "15/01/2024"  # Should return formatted date string

    def test_boolean_data_type_true(self, app):
        result = convert_sub_template_field_value("true", DataType.BOOLEAN)
        assert result is True
        assert isinstance(result, bool)

    def test_boolean_data_type_false(self, app):
        result = convert_sub_template_field_value("false", DataType.BOOLEAN)
        assert result is False
        assert isinstance(result, bool)

    def test_select_data_type(self, app):
        result = convert_sub_template_field_value("Option B", DataType.SELECT)
        assert result == "Option B"
        assert isinstance(result, str)


class TestSafeConversion:
    """Test safe conversion functions that handle errors gracefully"""

    def test_safe_template_field_success(self, app):
        result, error = safe_convert_template_field_value("42", FieldType.NUMBER)
        assert result == 42
        assert error is None

    def test_safe_template_field_failure(self, app):
        result, error = safe_convert_template_field_value("not-a-number", FieldType.NUMBER)
        assert result == "not-a-number"  # Original value returned on error
        assert error is not None
        assert "Failed to convert" in error

    def test_safe_sub_template_field_success(self, app):
        result, error = safe_convert_sub_template_field_value("42", DataType.INTEGER)
        assert result == 42
        assert error is None

    def test_safe_sub_template_field_failure(self, app):
        result, error = safe_convert_sub_template_field_value("not-a-number", DataType.INTEGER)
        assert result == "not-a-number"  # Original value returned on error
        assert error is not None
        assert "Failed to convert" in error


class TestDateParsing:
    """Test various date format parsing"""

    def test_iso_date(self, app):
        result = parse_date_string("2024-01-15")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_dd_mm_yyyy(self, app):
        result = parse_date_string("15/01/2024")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_month_name(self, app):
        result = parse_date_string("January 15, 2024")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_invalid_date(self, app):
        with pytest.raises(DataConversionError):
            parse_date_string("not-a-date")


class TestCurrencyParsing:
    """Test currency parsing functionality"""

    def test_dollar_currency(self, app):
        result = parse_currency_string("$1,234.56")
        assert result == Decimal('1234.56')

    def test_rupee_currency(self, app):
        result = parse_currency_string("₹1,23,456.78")
        assert result == Decimal('123456.78')

    def test_plain_number(self, app):
        result = parse_currency_string("1234.56")
        assert result == Decimal('1234.56')

    def test_invalid_currency(self, app):
        with pytest.raises(DataConversionError):
            parse_currency_string("not-a-currency")


class TestBooleanParsing:
    """Test boolean parsing functionality"""

    def test_true_values(self, app):
        true_inputs = ['true', '1', 'yes', 'y', 'on', 'enable', 'enabled', 'active']
        for input_val in true_inputs:
            result = parse_boolean_string(input_val)
            assert result is True

    def test_false_values(self, app):
        false_inputs = ['false', '0', 'no', 'n', 'off', 'disable', 'disabled', 'inactive']
        for input_val in false_inputs:
            result = parse_boolean_string(input_val)
            assert result is False

    def test_case_insensitive(self, app):
        assert parse_boolean_string('TRUE') is True
        assert parse_boolean_string('FALSE') is False

    def test_invalid_boolean(self, app):
        with pytest.raises(DataConversionError):
            parse_boolean_string("maybe")


class TestIntegrationScenarios:
    """Test realistic OCR data conversion scenarios"""

    def test_invoice_number_as_integer(self, app):
        # Invoice numbers should be converted to integers if field type is NUMBER
        result = convert_template_field_value("INV-12345", FieldType.TEXT)
        assert result == "INV-12345"
        
        # But if we extract just the number part
        result = convert_template_field_value("12345", FieldType.NUMBER)
        assert result == 12345
        assert isinstance(result, int)

    def test_invoice_date_conversion(self, app):
        # Various date formats from OCR should all convert to consistent DD/MM/YYYY format
        date_formats = [
            "2024-01-15",
            "15/01/2024", 
            "January 15, 2024",
            "15 Jan 2024"
        ]
        
        for date_str in date_formats:
            result = convert_template_field_value(date_str, FieldType.DATE)
            assert isinstance(result, str)
            assert result == "15/01/2024"  # All formats should convert to DD/MM/YYYY

    def test_total_amount_as_currency(self, app):
        # Currency amounts from OCR  
        currency_values = [
            "$1,234.56",
            "₹1,23,456.78",
            "1234.56"  # Plain number
        ]
        
        results = [
            Decimal('1234.56'),
            Decimal('123456.78'), 
            Decimal('1234.56')
        ]
        
        for currency_str, expected in zip(currency_values, results):
            result = convert_template_field_value(currency_str, FieldType.CURRENCY)
            assert isinstance(result, Decimal)
            assert result == expected

    def test_quantity_as_float(self, app):
        # Table quantities might be floats
        result = convert_sub_template_field_value("12.5", DataType.FLOAT)
        assert result == 12.5
        assert isinstance(result, float)

    def test_item_code_as_string(self, app):
        # Item codes should remain as strings
        result = convert_sub_template_field_value("ITM-001", DataType.STRING)
        assert result == "ITM-001"
        assert isinstance(result, str)
