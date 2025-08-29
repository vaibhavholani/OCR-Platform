# Documentation for `utils`

Path: `/home/sarohy/upwork/vaibhav/OCR-Platform/ocr_backend/app/utils`

---

## Python files

### `data_conversion.py`

- Class: `DataConversionError`

  - Docstring:

    Custom exception for data conversion errors

- Function: `convert_template_field_value(value, field_type, field_name)`

  - Docstring:

    Convert a value to the appropriate Python type based on TemplateField.field_type

    Args:
        value: The raw value from OCR (usually string)
        field_type: The FieldType enum value
        field_name: Optional field name for error messages
    
    Returns:
        Converted value in appropriate Python type
    
    Raises:
        DataConversionError: If conversion fails

- Function: `convert_sub_template_field_value(value, data_type, field_name)`

  - Docstring:

    Convert a value to the appropriate Python type based on SubTemplateField.data_type

    Args:
        value: The raw value from OCR (usually string)  
        data_type: The DataType enum value
        field_name: Optional field name for error messages
    
    Returns:
        Converted value in appropriate Python type
    
    Raises:
        DataConversionError: If conversion fails

- Function: `parse_date_string(date_str)`

  - Docstring:

    Parse various date formats into datetime object

    Args:
        date_str: Date string in various formats
    
    Returns:
        datetime object
    
    Raises:
        DataConversionError: If date parsing fails

- Function: `parse_currency_string(currency_str)`

  - Docstring:

    Parse currency string into Decimal for precise monetary calculations

    Args:
        currency_str: Currency string (e.g., "$1,234.56", "₹1,23,456.78")
    
    Returns:
        Decimal value
    
    Raises:
        DataConversionError: If currency parsing fails

- Function: `parse_boolean_string(bool_str)`

  - Docstring:

    Parse string into boolean value

    Args:
        bool_str: String representation of boolean
    
    Returns:
        Boolean value
    
    Raises:
        DataConversionError: If boolean parsing fails

- Function: `safe_convert_template_field_value(value, field_type, field_name)`

  - Docstring:

    Safely convert a template field value, returning the converted value and any error message

    Args:
        value: The raw value from OCR
        field_type: The FieldType enum value
        field_name: Optional field name for error messages
    
    Returns:
        Tuple of (converted_value, error_message)
        If conversion succeeds: (converted_value, None)
        If conversion fails: (original_value, error_message)

- Function: `safe_convert_sub_template_field_value(value, data_type, field_name)`

  - Docstring:

    Safely convert a sub-template field value, returning the converted value and any error message

    Args:
        value: The raw value from OCR
        data_type: The DataType enum value
        field_name: Optional field name for error messages
    
    Returns:
        Tuple of (converted_value, error_message)
        If conversion succeeds: (converted_value, None)
        If conversion fails: (original_value, error_message)



### `enums.py`

- Class: `DocumentStatus`

- Class: `FieldType`

- Class: `DataType`

- Class: `ExportFormat`

- Class: `FieldName`



### `gemini_ocr.py`

- Function: `detect_file_type(file_path)`

  - Docstring:

    Intelligently detect the MIME type of a file using multiple methods.

    Args:
        file_path: Path to the file
    
    Returns:
        tuple: (mime_type, file_category) where file_category is 'image', 'video', 'audio', or 'document'
    
    Raises:
        ValueError: If file type is not supported by Gemini API

- Function: `generate_adaptive_prompt(field_names, file_category, custom_prompt)`

  - Docstring:

    Generate context-aware prompts based on the type of file being processed.

    Args:
        field_names: List of field names to extract
        file_category: Type of file ('image', 'video', 'audio', 'document')
        custom_prompt: Optional custom prompt override
    
    Returns:
        str: Optimized prompt for the specific file type

- Function: `call_gemini_ocr(file_path, field_names, custom_prompt)`

  - Docstring:

    Calls Gemini API to extract specified field names from any supported file type.
    Automatically detects file type and adapts processing accordingly.

    Args:
        file_path: Path to the file (images, PDFs, videos, audio, etc.)
        field_names: List of field names to extract
        custom_prompt: Optional custom prompt for specialized extraction
    
    Returns:
        str: Raw response text from Gemini
    
    Raises:
        ValueError: If file type is unsupported or API key is missing
        FileNotFoundError: If file doesn't exist

- Function: `parse_gemini_response(response_text, field_names)`

  - Docstring:

    Parses Gemini's response text and returns a dict mapping field names to values.
    Enhanced to handle different data types and table structures.
    If parsing fails, returns the raw response.


