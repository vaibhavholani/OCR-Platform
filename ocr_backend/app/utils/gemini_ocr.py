import os
import mimetypes
from pathlib import Path
from google import genai
from google.genai import types
import json
from flask import current_app

# Comprehensive mapping of Gemini-supported file types
SUPPORTED_MIME_TYPES = {
    # Images
    'image/png': ['.png'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/webp': ['.webp'],
    
    # Videos
    'video/x-flv': ['.flv'],
    'video/quicktime': ['.mov'],
    'video/mpeg': ['.mpeg', '.mpg'],
    'video/mpegps': ['.mpegps'],
    'video/mp4': ['.mp4'],
    'video/webm': ['.webm'],
    'video/wmv': ['.wmv'],
    'video/3gpp': ['.3gp', '.3gpp'],
    
    # Audio
    'audio/aac': ['.aac'],
    'audio/flac': ['.flac'],
    'audio/mp3': ['.mp3'],
    'audio/m4a': ['.m4a'],
    'audio/mpeg': ['.mp3', '.mpeg'],
    'audio/mpga': ['.mpga'],
    'audio/mp4': ['.mp4'],
    'audio/opus': ['.opus'],
    'audio/pcm': ['.pcm'],
    'audio/wav': ['.wav'],
    'audio/webm': ['.webm'],
    
    # Documents
    'application/pdf': ['.pdf'],
    'text/plain': ['.txt']
}

# Reverse mapping for extension to MIME type lookup
EXTENSION_TO_MIME = {}
for mime_type, extensions in SUPPORTED_MIME_TYPES.items():
    for ext in extensions:
        EXTENSION_TO_MIME[ext.lower()] = mime_type

def detect_file_type(file_path):
    """
    Intelligently detect the MIME type of a file using multiple methods.
    
    Args:
        file_path: Path to the file
        
    Returns:
        tuple: (mime_type, file_category) where file_category is 'image', 'video', 'audio', or 'document'
        
    Raises:
        ValueError: If file type is not supported by Gemini API
    """
    file_path = Path(file_path)
    
    # Method 1: Check by file extension first (most reliable for our use case)
    extension = file_path.suffix.lower()
    if extension in EXTENSION_TO_MIME:
        mime_type = EXTENSION_TO_MIME[extension]
    else:
        # Method 2: Use Python's mimetypes module as fallback
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type not in SUPPORTED_MIME_TYPES:
            supported_extensions = [ext for exts in SUPPORTED_MIME_TYPES.values() for ext in exts]
            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported file types: {', '.join(sorted(set(supported_extensions)))}"
            )
    
    # Determine file category for adaptive prompting
    if mime_type.startswith('image/'):
        category = 'image'
    elif mime_type.startswith('video/'):
        category = 'video'
    elif mime_type.startswith('audio/'):
        category = 'audio'
    elif mime_type.startswith('application/') or mime_type.startswith('text/'):
        category = 'document'
    else:
        category = 'unknown'
    
    return mime_type, category

def generate_adaptive_prompt(field_names, file_category, custom_prompt=None):
    """
    Generate context-aware prompts based on the type of file being processed.
    
    Args:
        field_names: List of field names to extract
        file_category: Type of file ('image', 'video', 'audio', 'document')
        custom_prompt: Optional custom prompt override
        
    Returns:
        str: Optimized prompt for the specific file type
    """
    if custom_prompt:
        return custom_prompt + f" Return your answer as a JSON object. Fields: {', '.join(field_names)}"
    
    base_instruction = "You are an intelligent content analysis assistant. "
    
    if file_category == 'image':
        prompt = (
            base_instruction +
            "Analyze the provided image and extract the specified information. "
            "Look carefully at all text, objects, and visual elements in the image. "
            "For documents or forms, pay special attention to the header and top sections. "
            "Return your answer as a JSON object mapping each field name to its value. "
            f"Fields to extract: {', '.join(field_names)}"
        )
    elif file_category == 'video':
        prompt = (
            base_instruction +
            "Analyze the provided video content and extract the specified information. "
            "Consider both visual elements and any audio/speech content. "
            "Look for text overlays, spoken information, and visual cues throughout the video. "
            "Return your answer as a JSON object mapping each field name to its value. "
            f"Fields to extract: {', '.join(field_names)}"
        )
    elif file_category == 'audio':
        prompt = (
            base_instruction +
            "Analyze the provided audio content and extract the specified information. "
            "Transcribe and analyze any speech, identify speakers if relevant, and note audio characteristics. "
            "Return your answer as a JSON object mapping each field name to its value. "
            f"Fields to extract: {', '.join(field_names)}"
        )
    elif file_category == 'document':
        prompt = (
            base_instruction +
            "Analyze the provided document and extract the specified information. "
            "Carefully read through the entire document, paying attention to headers, sections, and formatted content. "
            "For forms or structured documents, focus on labeled fields and data entries. "
            "Return your answer as a JSON object mapping each field name to its value. "
            f"Fields to extract: {', '.join(field_names)}"
        )
    else:
        # Fallback for unknown file types
        prompt = (
            base_instruction +
            "Analyze the provided content and extract the specified information. "
            "Return your answer as a JSON object mapping each field name to its value. "
            f"Fields to extract: {', '.join(field_names)}"
        )
    
    return prompt

def call_gemini_ocr(file_path, field_names, custom_prompt=None):
    """
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
    """
    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Get API key from configuration
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in configuration. Please set it in your .env file.")
    
    # Detect file type and validate support
    try:
        mime_type, file_category = detect_file_type(file_path)
    except ValueError as e:
        raise ValueError(f"File type detection failed: {e}")
    
    # Initialize the client with API key
    client = genai.Client(api_key=api_key)
    
    # Read file as binary data
    with open(file_path, "rb") as file:
        file_bytes = file.read()
    
    # Generate appropriate prompt based on file type
    prompt = generate_adaptive_prompt(field_names, file_category, custom_prompt)
    
    # Make API call with detected MIME type
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            prompt,
            types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
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
        
        # Handle different response formats for table data
        if isinstance(data, list):
            # Direct array format: [{"col1": "val1", "col2": "val2"}, ...]
            return {"rows": data}
        elif isinstance(data, dict) and 'rows' in data:
            # Expected format: {"rows": [{"col1": "val1", "col2": "val2"}, ...]}
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
