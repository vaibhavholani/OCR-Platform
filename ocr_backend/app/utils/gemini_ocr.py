import os
from google import genai
from google.genai import types
import json

def call_gemini_ocr(image_path, field_names, custom_prompt=None):
    """
    Calls Gemini API to extract specified field names from a JPEG image.
    Returns the raw response text from Gemini.
    
    Args:
        image_path: Path to the image file
        field_names: List of field names to extract
        custom_prompt: Optional custom prompt for specialized extraction (e.g., tables)
    """
    # Initialize the client
    client = genai.Client()
    
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()

    if custom_prompt:
        prompt = custom_prompt + f" Return your answer as a JSON object. Fields: {', '.join(field_names)}"
    else:
        prompt = (
            "You are an OCR extraction assistant. "
            "Extract the following fields from the provided document image. "
            "Return your answer as a JSON object mapping each field name to its value. "
            "Most of the below fields are in the Top Section of the document image. "
            "If extracting table data, structure it as {'rows': [{'col1': 'value1', 'col2': 'value2'}, ...]}. "
            f"Fields: {', '.join(field_names)}"
        )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            prompt,
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        ]
    )
    return response.text

def parse_gemini_response(response_text, field_names):
    """
    Parses Gemini's response text and returns a dict mapping field names to values.
    Enhanced to handle different data types and table structures.
    If parsing fails, returns the raw response.
    """
    try:
        # Clean up the response text (remove markdown code blocks if present)
        cleaned_text = response_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        if cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]
        
        data = json.loads(cleaned_text.strip())
        
        # If it's table data with rows structure, return as-is
        if isinstance(data, dict) and 'rows' in data:
            return data
            
        # For regular field extraction, ensure all requested fields are included
        result = {}
        for field in field_names:
            value = data.get(field)
            if value is not None:
                result[field] = value
            else:
                # Try case-insensitive match
                for key, val in data.items():
                    if key.lower() == field.lower():
                        result[field] = val
                        break
                else:
                    result[field] = None
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response_text}")
        return {"raw_response": response_text, "parse_error": str(e)}
    except Exception as e:
        print(f"General parsing error: {e}")
        return {"raw_response": response_text, "parse_error": str(e)} 