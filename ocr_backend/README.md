# OCR Platform Backend

A customizable and flexible OCR (Optical Character Recognition) platform that processes documents using AI-powered field extraction based on configurable templates.

## 🚀 Features

- **Document Upload & Management**: Upload documents with automatic file handling
- **Template-Based OCR**: Define custom templates with specific fields to extract
- **AI-Powered Extraction**: Uses Google Gemini for intelligent field extraction
- **Integrated Pipeline**: Seamless document → template → OCR → database storage flow
- **Status Tracking**: Real-time processing status updates
- **Multi-format Support**: Handle text fields, tables, dates, currencies, etc.
- **Auto-processing**: Optional automatic OCR processing on upload
- **Reprocessing**: Re-run OCR with different templates
- **Export Capabilities**: Export extracted data in multiple formats

## 📋 Pipeline Flow

```
Document Upload → Template Selection → OCR Processing → Database Storage → Results
```

### Detailed Flow:
1. **Document Upload** (`POST /api/documents/`)
   - Upload file with optional template_id and auto_process flag
   - Document saved to filesystem and database with PENDING status

2. **OCR Processing** (`POST /api/ocr/process_document`)
   - Document status updated to PROCESSING
   - Template fields retrieved
   - Gemini AI processes document based on field types
   - Results saved to OCRData and OCRLineItem tables
   - Document status updated to PROCESSED or FAILED

3. **Results Retrieval** (`GET /api/documents/{id}/ocr-results`)
   - Formatted extraction results with field mappings
   - Confidence scores and timestamps

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Setup
```bash
# Clone repository
cd ocr_backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your-gemini-api-key"
export DATABASE_URL="sqlite:///ocr_platform.db"  # Optional

# Initialize database
python seed.py

# Run application
python run.py
```

The application will start at `http://localhost:5000`

## 📚 API Endpoints

### Documents
- `GET /api/documents/` - List all documents
- `POST /api/documents/` - Upload document (supports auto-processing)
- `GET /api/documents/{id}` - Get specific document
- `GET /api/documents/{id}/status` - Get processing status
- `GET /api/documents/{id}/ocr-results` - Get extraction results
- `POST /api/documents/{id}/reprocess` - Reprocess with different template
- `PUT /api/documents/{id}` - Update document
- `DELETE /api/documents/{id}` - Delete document

### OCR Processing
- `POST /api/ocr/process_document` - Process document with template
- `POST /api/ocr/extract_fields` - Legacy extraction endpoint
- `GET /api/ocr/data` - List all OCR data
- CRUD operations for OCR data, line items, and values

### Templates
- `GET /api/templates/` - List all templates
- `POST /api/templates/` - Create template
- `GET /api/templates/{id}` - Get template with fields
- `POST /api/templates/{id}/fields` - Add fields to template
- CRUD operations for template fields and sub-fields

### Users & Exports
- `GET /api/users/` - User management
- `GET /api/exports/` - Export data management
- `GET /api/enums/` - Available enum values

## 🔧 Usage Examples

### 1. Upload Document with Auto-Processing
```bash
curl -X POST http://localhost:5000/api/documents/ \
  -F "file=@invoice.pdf" \
  -F "user_id=1" \
  -F "template_id=1" \
  -F "auto_process=true"
```

### 2. Manual OCR Processing
```bash
curl -X POST http://localhost:5000/api/ocr/process_document \
  -H "Content-Type: application/json" \
  -d '{"doc_id": 1, "template_id": 1}'
```

### 3. Get Processing Status
```bash
curl http://localhost:5000/api/documents/1/status
```

### 4. Get Extraction Results
```bash
curl http://localhost:5000/api/documents/1/ocr-results
```

### 5. Reprocess Document
```bash
curl -X POST http://localhost:5000/api/documents/1/reprocess \
  -H "Content-Type: application/json" \
  -d '{"template_id": 2}'
```

## 📊 Database Schema

### Key Models:
- **Document**: Stores uploaded files and processing status
- **Template**: Defines extraction templates
- **TemplateField**: Individual fields within templates
- **SubTemplateField**: Sub-fields for complex structures (tables)
- **OCRData**: Extracted field values
- **OCRLineItem**: Table row data
- **OCRLineItemValue**: Individual cell values in tables

### Field Types:
- `TEXT`: Simple text extraction
- `NUMBER`: Numeric values
- `DATE`: Date fields
- `EMAIL`: Email addresses
- `CURRENCY`: Monetary amounts
- `TABLE`: Tabular data
- `SELECT`: Dropdown/choice fields

### Document Status:
- `PENDING`: Awaiting processing
- `PROCESSING`: Currently being processed
- `PROCESSED`: Successfully completed
- `FAILED`: Processing failed

## ⚙️ Configuration

Environment variables:
- `GEMINI_API_KEY`: Required for OCR processing
- `DATABASE_URL`: Database connection (defaults to SQLite)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `SECRET_KEY`: Flask secret key

Application settings in `config.py`:
- Upload folder paths
- File size limits
- OCR confidence thresholds
- Retry attempts

## 🔍 Logging

Logs are written to:
- Console (development)
- `logs/ocr_platform.log` (production)

Log rotation with 10MB files, 10 backup files.

## 🚦 Error Handling

The system includes comprehensive error handling:
- Document validation
- Template validation
- OCR processing errors
- Database transaction rollbacks
- Status tracking for failed processes
- Detailed error messages and logging

## 🔄 Status Tracking

Document processing status is tracked throughout the pipeline:
1. **PENDING** → Document uploaded, awaiting processing
2. **PROCESSING** → OCR extraction in progress
3. **PROCESSED** → Successfully completed with results
4. **FAILED** → Processing failed with error details

## 📈 Monitoring

Check system health:
- Document processing status
- OCR extraction counts
- Error rates in logs
- Database performance

## 🛣️ Roadmap

- [ ] Batch processing capabilities
- [ ] Custom confidence thresholds per field
- [ ] Template auto-detection
- [ ] Advanced table extraction
- [ ] Real-time processing notifications
- [ ] Performance metrics dashboard

## 📝 License

This project is licensed under the MIT License.
