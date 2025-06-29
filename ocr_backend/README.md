# OCR Platform Backend

A Flask-based backend API for an OCR (Optical Character Recognition) platform that handles document processing, template management, and data extraction.

## 🚀 Features

- **User Management**: Authentication and user profiles
- **Document Processing**: Upload and process documents with OCR
- **Template System**: Create custom extraction templates with AI instructions
- **Data Extraction**: Extract structured data from documents
- **Export System**: Export processed data in multiple formats
- **RESTful API**: Complete CRUD operations for all entities

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)

## 🛠️ Installation

1. **Clone the repository** (if not already done):

   ```bash
   cd ocr_backend
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**:

   ```bash
   python seed.py
   ```

4. **Run the application**:
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:5000`

## 📊 Database Schema

### Core Entities

- **Users**: Authentication and user management
- **Documents**: File uploads and processing status
- **Templates**: OCR extraction templates
- **Template Fields**: Individual fields within templates
- **OCR Data**: Extracted data from documents
- **Line Items**: Table row data for structured documents
- **Exports**: Export sessions and files

### Relationships

- Users have many Documents and Templates
- Templates have many Template Fields
- Documents have many OCR Data and Line Items
- Template Fields can have Sub Fields and Field Options

## 🔌 API Endpoints

### Users (`/api/users`)

| Method | Endpoint                    | Description          |
| ------ | --------------------------- | -------------------- |
| GET    | `/api/users/`               | Get all users        |
| GET    | `/api/users/<id>`           | Get specific user    |
| POST   | `/api/users/`               | Create new user      |
| PUT    | `/api/users/<id>`           | Update user          |
| DELETE | `/api/users/<id>`           | Delete user          |
| GET    | `/api/users/<id>/documents` | Get user's documents |
| GET    | `/api/users/<id>/templates` | Get user's templates |

### Documents (`/api/documents`)

| Method | Endpoint                         | Description             |
| ------ | -------------------------------- | ----------------------- |
| GET    | `/api/documents/`                | Get all documents       |
| GET    | `/api/documents/<id>`            | Get specific document   |
| POST   | `/api/documents/`                | Create new document     |
| PUT    | `/api/documents/<id>`            | Update document         |
| DELETE | `/api/documents/<id>`            | Delete document         |
| GET    | `/api/documents/<id>/ocr-data`   | Get document OCR data   |
| POST   | `/api/documents/<id>/ocr-data`   | Create OCR data         |
| GET    | `/api/documents/<id>/line-items` | Get document line items |
| POST   | `/api/documents/<id>/line-items` | Create line item        |

### Exports (`/api/exports`)

| Method | Endpoint                  | Description           |
| ------ | ------------------------- | --------------------- |
| GET    | `/api/exports/`           | Get all exports       |
| GET    | `/api/exports/<id>`       | Get specific export   |
| POST   | `/api/exports/`           | Create new export     |
| DELETE | `/api/exports/<id>`       | Delete export         |
| GET    | `/api/exports/<id>/files` | Get export files      |
| POST   | `/api/exports/<id>/files` | Create export file    |
| GET    | `/api/exports/formats`    | Get available formats |

## 📝 Sample Data

The seed script creates:

- **2 Users**: John Doe and Jane Smith
- **2 Templates**: Invoice and Receipt templates
- **8 Template Fields**: Various field types (text, date, number, table)
- **4 Sub Fields**: For table structure
- **2 Documents**: Sample invoice and receipt
- **OCR Data**: Extracted values with confidence scores
- **Line Items**: Table row data with values
- **1 Export**: Sample PDF export

### Test Credentials

- **User 1**: john@example.com / password123
- **User 2**: jane@example.com / password123

## 🔧 Configuration

The application uses SQLite by default. Configuration is in `app/config.py`:

- Database: SQLite (`ocr_platform.db`)
- Upload folder: `uploads/`
- Max file size: 16MB
- Debug mode: Enabled

## 🧪 Testing the API

### Get all users:

```bash
curl http://localhost:5000/api/users/
```

### Create a new user:

```bash
curl -X POST http://localhost:5000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "password123"}'
```

### Get all documents:

```bash
curl http://localhost:5000/api/documents/
```

## 📁 Project Structure

```
ocr_backend/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration settings
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── template.py
│   │   ├── template_field.py
│   │   ├── sub_template_field.py
│   │   ├── ocr_data.py
│   │   ├── ocr_line_item.py
│   │   ├── ocr_line_item_value.py
│   │   ├── field_option.py
│   │   ├── export.py
│   │   └── export_file.py
│   ├── api/                     # API routes
│   │   ├── __init__.py
│   │   ├── user_routes.py
│   │   ├── document_routes.py
│   │   └── export_routes.py
│   └── utils/
│       └── enums.py             # Enumeration classes
├── seed.py                      # Database seeding script
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Development

### Running in Development Mode

```bash
python run.py
```

### Seeding the Database

```bash
python seed.py
```

### Database Migrations

The application uses Flask-Migrate for database migrations:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 🔒 Security Notes

- Passwords are hashed using Werkzeug's security functions
- CORS is enabled for frontend integration
- Input validation is implemented on all endpoints
- SQL injection protection via SQLAlchemy ORM

## 📞 Support

For issues or questions, please check the API documentation or create an issue in the repository.

---

**Happy Coding! 🎉**
