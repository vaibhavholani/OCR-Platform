import os
import google.generativeai as genai
import json

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def call_gemini_ocr(image_path, field_names):
    """
    Calls Gemini API to extract specified field names from a JPEG image.
    Returns the raw response text from Gemini.
    """
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()

    prompt = (
        "You are an OCR extraction assistant. "
        "Extract the following fields from the provided document image. "
        "Return your answer as a JSON object mapping each field name to its value. "
        f"Fields: {', '.join(field_names)}"
    )

    model = genai.GenerativeModel("gemini-pro-vision")
    response = model.generate_content([
        prompt,
        genai.types.content.ImageData(mime_type="image/jpeg", data=image_bytes)
    ])
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