import os
from google import genai
from google.genai import types
import json

def call_gemini_ocr(image_path, field_names):
    """
    Calls Gemini API to extract specified field names from a JPEG image.
    Returns the raw response text from Gemini.
    """
    # Initialize the client
    client = genai.Client()
    
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()

    prompt = (
        "You are an OCR extraction assistant. "
        "Extract the following fields from the provided document image. "
        "Return your answer as a JSON object mapping each field name to its value. "
        "Most of the below fields are in the Top Section of the document image."
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
    If parsing fails, returns the raw response.
    """
    try:
        data = json.loads(response_text)
        return {field: data.get(field, None) for field in field_names}
    except Exception:
        return {"raw_response": response_text} 