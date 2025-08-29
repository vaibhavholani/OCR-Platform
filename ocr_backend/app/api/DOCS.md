# API Documentation

This document provides a detailed overview of the API endpoints for the OCR platform.

## User Routes

**File:** `user_routes.py`

**Blueprint:** `/api/users`

This blueprint handles user management, including creation, retrieval, updating, deletion, and login.

---

### 1. Get All Users

*   **Endpoint:** `GET /api/users/`
*   **Description:** Retrieves a list of all registered users.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of user objects and the total count.

*   **Example Output (Success):**
    ```json
    {
        "users": [
            {
                "user_id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com"
            },
            {
                "user_id": 2,
                "name": "Jane Smith",
                "email": "jane.smith@example.com"
            }
        ],
        "count": 2
    }
    ```

---

### 2. Get User by ID

*   **Endpoint:** `GET /api/users/<user_id>`
*   **Description:** Retrieves a specific user by their unique ID.
*   **Payload:** None
*   **Returns:** A JSON object representing the user.

*   **Example Output (Success):**
    ```json
    {
        "user_id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
    ```

*   **Example Output (Not Found):**
    ```json
    {
        "error": "User not found"
    }
    ```

---

### 3. Create a New User

*   **Endpoint:** `POST /api/users/`
*   **Description:** Creates a new user account.
*   **Payload:** A JSON object with the user's name, email, and password.
    *   `name` (string, required): The user's full name.
    *   `email` (string, required): The user's email address.
    *   `password` (string, required): The user's password.

*   **Example Input:**
    ```json
    {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "securepassword123"
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "user_id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
    ```

*   **Example Output (Missing Fields):**
    ```json
    {
        "error": "Missing required fields"
    }
    ```

*   **Example Output (User Exists):**
    ```json
    {
        "error": "User with this email already exists"
    }
    ```

---

### 4. Update a User

*   **Endpoint:** `PUT /api/users/<user_id>`
*   **Description:** Updates a user's information.
*   **Payload:** A JSON object with the fields to update.
    *   `name` (string, optional): The user's new name.
    *   `email` (string, optional): The user's new email address.
    *   `password` (string, optional): The user's new password.

*   **Example Input:**
    ```json
    {
        "name": "Johnathan Doe"
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "user_id": 1,
        "name": "Johnathan Doe",
        "email": "john.doe@example.com"
    }
    ```

---

### 5. Delete a User

*   **Endpoint:** `DELETE /api/users/<user_id>`
*   **Description:** Deletes a user account.
*   **Payload:** None
*   **Returns:** A confirmation message.

*   **Example Output (Success):**
    ```json
    {
        "message": "User deleted successfully"
    }
    ```

---

### 6. Get User Documents

*   **Endpoint:** `GET /api/users/<user_id>/documents`
*   **Description:** Retrieves all documents associated with a specific user.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of document objects and the total count.

*   **Example Output (Success):**
    ```json
    {
        "documents": [
            {
                "doc_id": 101,
                "file_name": "invoice_123.pdf",
                "upload_date": "2025-08-27T10:00:00Z"
            }
        ],
        "count": 1
    }
    ```

---

### 7. Get User Templates

*   **Endpoint:** `GET /api/users/<user_id>/templates`
*   **Description:** Retrieves all templates created by a specific user.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of template objects and the total count.

*   **Example Output (Success):**
    ```json
    {
        "templates": [
            {
                "temp_id": 1,
                "name": "Default Invoice Template",
                "creation_date": "2025-08-27T10:00:00Z"
            }
        ],
        "count": 1
    }
    ```

---

### 8. Get User Template Names

*   **Endpoint:** `GET /api/users/<user_id>/templates/names`
*   **Description:** Retrieves only the names and IDs of templates created by a specific user.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of template names and IDs.

*   **Example Output (Success):**
    ```json
    {
        "templates": [
            {
                "temp_id": 1,
                "name": "Default Invoice Template"
            }
        ],
        "count": 1
    }
    ```

---

### 9. User Login

*   **Endpoint:** `POST /api/users/login`
*   **Description:** Authenticates a user and returns their information upon successful login.
*   **Payload:** A JSON object with the user's email and password.
    *   `email` (string, required): The user's email address.
    *   `password` (string, required): The user's password.

*   **Example Input:**
    ```json
    {
        "email": "john.doe@example.com",
        "password": "securepassword123"
    }
    ```

*   **Example Output (Invalid Credentials):**
    ```json
    {
        "error": "Invalid credentials"
    }
    ```



## Document Routes

**File:** `document_routes.py`

**Blueprint:** `/api/documents`

This blueprint handles document management, including creation, retrieval, updating, deletion, and OCR data handling.

---

### 1. Get All Documents

*   **Endpoint:** `GET /api/documents/`
*   **Description:** Retrieves a list of all documents.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of document objects and the total count.

*   **Example Output (Success):**
    ```json
    {
        "documents": [
            {
                "doc_id": 1,
                "user_id": 1,
                "file_path": "uploads/invoice.pdf",
                "original_filename": "invoice.pdf",
                "status": "PENDING",
                "created_at": "2025-08-27T12:00:00Z",
                "processed_at": null
            }
        ],
        "count": 1
    }
    ```

---

### 2. Get Document by ID

*   **Endpoint:** `GET /api/documents/<document_id>`
*   **Description:** Retrieves a specific document by its unique ID.
*   **Payload:** None
*   **Returns:** A JSON object representing the document.

*   **Example Output (Success):**
    ```json
    {
        "doc_id": 1,
        "user_id": 1,
        "file_path": "uploads/invoice.pdf",
        "original_filename": "invoice.pdf",
        "status": "PENDING",
        "created_at": "2025-08-27T12:00:00Z",
        "processed_at": null
    }
    ```

---

### 3. Download Document

*   **Endpoint:** `GET /api/documents/<document_id>/download`
*   **Description:** Downloads the original file for a document.
*   **Payload:** None
*   **Returns:** The document file as an attachment.

---

### 4. View Document

*   **Endpoint:** `GET /api/documents/<document_id>/view`
*   **Description:** Returns the document file for inline viewing in the browser.
*   **Payload:** None
*   **Returns:** The document file.

---

### 5. Create a New Document

*   **Endpoint:** `POST /api/documents/`
*   **Description:** Creates a new document. Supports both `multipart/form-data` for file uploads and traditional JSON payloads.
*   **Payload (multipart/form-data):**
    *   `file` (file, required): The document file to upload.
    *   `user_id` (integer, required): The ID of the user uploading the document.
    *   `template_id` (integer, optional): The ID of the template to use for OCR processing.
    *   `auto_process` (boolean, optional): If `true`, triggers OCR processing immediately after upload.
*   **Payload (application/json):**
    *   `user_id` (integer, required): The ID of the user.
    *   `file_path` (string, required): The path to the document file.
    *   `original_filename` (string, required): The original name of the file.

*   **Example Input (multipart/form-data):**
    ```
    (form data with file and other fields)
    ```

*   **Example Output (Success):**
    ```json
    {
        "doc_id": 2,
        "user_id": 1,
        "file_path": "uploads/new_invoice.pdf",
        "original_filename": "new_invoice.pdf",
        "status": "PENDING",
        "created_at": "2025-08-27T13:00:00Z",
        "processed_at": null
    }
    ```

---

### 6. Update a Document

*   **Endpoint:** `PUT /api/documents/<document_id>`
*   **Description:** Updates a document's properties, such as its status or file path.
*   **Payload:** A JSON object with the fields to update.
    *   `status` (string, optional): The new status of the document (e.g., "PROCESSED").
    *   `filename` (string, optional): The new filename.
    *   `file_path` (string, optional): The new file path.

*   **Example Input:**
    ```json
    {
        "status": "PROCESSED"
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "doc_id": 1,
        "user_id": 1,
        "file_path": "uploads/invoice.pdf",
        "original_filename": "invoice.pdf",
        "status": "PROCESSED",
        "created_at": "2025-08-27T12:00:00Z",
        "processed_at": "2025-08-27T13:10:00Z"
    }
    ```

---

### 7. Delete a Document

*   **Endpoint:** `DELETE /api/documents/<document_id>`
*   **Description:** Deletes a document.
*   **Payload:** None
*   **Returns:** A confirmation message.

*   **Example Output (Success):**
    ```json
    {
        "message": "Document deleted successfully"
    }
    ```

---

### 8. Get Document OCR Data

*   **Endpoint:** `GET /api/documents/<document_id>/ocr-data`
*   **Description:** Retrieves the OCR data associated with a document.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of OCR data entries.

*   **Example Output (Success):**
    ```json
    {
        "ocr_data": [
            {
                "ocr_id": 1,
                "document_id": 1,
                "field_id": 10,
                "predicted_value": "12345",
                "actual_value": "12345",
                "confidence": 0.95
            }
        ],
        "count": 1
    }
    ```

---

### 9. Create OCR Data

*   **Endpoint:** `POST /api/documents/<document_id>/ocr-data`
*   **Description:** Creates a new OCR data entry for a document.
*   **Payload:**
    *   `field_id` (integer, required): The ID of the template field.
    *   `predicted_value` (string, required): The value predicted by the OCR.
    *   `actual_value` (string, optional): The corrected value.
    *   `confidence` (float, optional): The confidence score of the prediction.

*   **Example Input:**
    ```json
    {
        "field_id": 10,
        "predicted_value": "ABC Corp",
        "confidence": 0.88
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "ocr_id": 2,
        "document_id": 1,
        "field_id": 10,
        "predicted_value": "ABC Corp",
        "actual_value": null,
        "confidence": 0.88
    }
    ```

---

### 10. Get Document Line Items

*   **Endpoint:** `GET /api/documents/<document_id>/line-items`
*   **Description:** Retrieves line items (table rows) from a document's OCR data.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of line items.

---

### 11. Create a Line Item

*   **Endpoint:** `POST /api/documents/<document_id>/line-items`
*   **Description:** Creates a new line item for a document.
*   **Payload:**
    *   `field_id` (integer, required): The ID of the table field.
    *   `row_index` (integer, required): The index of the row.

---

### 12. Create a Line Item Value

*   **Endpoint:** `POST /api/documents/line-items/<line_item_id>/values`
*   **Description:** Creates a value for a specific cell within a line item.
*   **Payload:**
    *   `sub_temp_field_id` (integer, required): The ID of the sub-template field (column).
    *   `predicted_value` (string, required): The predicted value for the cell.

---

### 13. Get Document Status

*   **Endpoint:** `GET /api/documents/<document_id>/status`
*   **Description:** Retrieves the processing status and other metadata of a document.
*   **Payload:** None
*   **Returns:** A JSON object with document status information.

*   **Example Output (Success):**
    ```json
    {
        "document_id": 1,
        "status": "PROCESSED",
        "original_filename": "invoice.pdf",
        "created_at": "2025-08-27T12:00:00Z",
        "processed_at": "2025-08-27T13:10:00Z",
        "ocr_data_count": 5,
        "line_items_count": 3,
        "has_ocr_data": true
    }
    ```

---

### 14. Get Document OCR Results

*   **Endpoint:** `GET /api/documents/<document_id>/ocr-results`
*   **Description:** Retrieves the complete, formatted OCR results for a document, including both regular fields and table data.
*   **Payload:** None
*   **Returns:** A JSON object with the extracted data.

---

### 15. Reprocess Document

*   **Endpoint:** `POST /api/documents/<document_id>/reprocess`
*   **Description:** Reprocesses a document with a specified template, clearing old OCR data.
*   **Payload:**
    *   `template_id` (integer, required): The ID of the template to use for reprocessing.

---

### 16. Update Field Value

*   **Endpoint:** `POST /api/documents/<document_id>/update-field-value`
*   **Description:** Updates the `actual_value` of a single, non-table OCR field.
*   **Payload:**
    *   `field_name` (string, required): The name of the field to update.
    *   `value` (string, required): The new, corrected value.

---

### 17. Update Table Cell Value

*   **Endpoint:** `POST /api/documents/<document_id>/update-table-cell-value`
*   **Description:** Updates the `actual_value` of a single cell within a table.
*   **Payload:**
    *   `field_name` (string, required): The name of the table field.
    *   `row_index` (integer, required): The index of the row to update.
    *   `column_name` (string, required): The name of the column to update.
    *   `value` (string, required): The new, corrected value for the cell.

## Enum Routes

**File:** `enum_routes.py`

**Blueprint:** `/api/enums`

This blueprint provides endpoints to retrieve possible values for various enumerations used in the system.

---

### 1. Get All Enums

*   **Endpoint:** `GET /api/enums/`
*   **Description:** Retrieves all available enumerations and their values.
*   **Payload:** None
*   **Returns:** A JSON object containing all available enums.

*   **Example Output (Success):**
    ```json
    {
        "document_status": ["PENDING", "PROCESSED", "ERROR"],
        "field_types": ["TEXT", "NUMBER", "DATE", "TABLE"],
        "data_types": ["STRING", "INTEGER", "FLOAT", "DATE"],
        "export_formats": ["CSV", "JSON", "XML"],
        "field_names": ["InvoiceNumber", "InvoiceDate", "TotalAmount", "LineItems"]
    }
    ```

---

### 2. Get Document Status

*   **Endpoint:** `GET /api/enums/document-status`
*   **Description:** Retrieves the available statuses for a document.
*   **Payload:** None
*   **Returns:** A JSON object with a list of document statuses.

*   **Example Output (Success):**
    ```json
    {
        "document_status": ["PENDING", "PROCESSED", "ERROR"],
        "count": 3
    }
    ```

---

### 3. Get Field Types

*   **Endpoint:** `GET /api/enums/field-types`
*   **Description:** Retrieves the available types for a template field.
*   **Payload:** None
*   **Returns:** A JSON object with a list of field types.

*   **Example Output (Success):**
    ```json
    {
        "field_types": ["TEXT", "NUMBER", "DATE", "TABLE"],
        "count": 4
    }
    ```

---

### 4. Get Data Types

*   **Endpoint:** `GET /api/enums/data-types`
*   **Description:** Retrieves the available data types for a field.
*   **Payload:** None
*   **Returns:** A JSON object with a list of data types.

*   **Example Output (Success):**
    ```json
    {
        "data_types": ["STRING", "INTEGER", "FLOAT", "DATE"],
        "count": 4
    }
    ```

---

### 5. Get Export Formats

*   **Endpoint:** `GET /api/enums/export-formats`
*   **Description:** Retrieves the available formats for exporting data.
*   **Payload:** None
*   **Returns:** A JSON object with a list of export formats.

*   **Example Output (Success):**
    ```json
    {
        "export_formats": ["CSV", "JSON", "XML"],
        "count": 3
    }
    ```

---

### 6. Get Field Names

*   **Endpoint:** `GET /api/enums/field-names`
*   **Description:** Retrieves the available names for template fields.
*   **Payload:** None
*   **Returns:** A JSON object with a list of field names.

*   **Example Output (Success):**
    ```json
    {
        "field_names": ["InvoiceNumber", "InvoiceDate", "TotalAmount", "LineItems"],
        "count": 4
    }
    ```

## Export Routes

**File:** `export_routes.py`

**Blueprint:** `/api/exports`

This blueprint manages data exports, allowing users to create, retrieve, and manage export records and their associated files.

---

### 1. Get All Exports

*   **Endpoint:** `GET /api/exports/`
*   **Description:** Retrieves a list of all export records.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of export objects and the total count.

*   **Example Output (Success):**
    ```json
    {
        "exports": [
            {
                "exp_id": 1,
                "user_id": 1,
                "document_id": 101,
                "format": "CSV",
                "filename": "export_101.csv",
                "file_path": "/path/to/exports/export_101.csv",
                "created_at": "2025-08-27T14:00:00Z"
            }
        ],
        "count": 1
    }
    ```

---

### 2. Get Export by ID

*   **Endpoint:** `GET /api/exports/<export_id>`
*   **Description:** Retrieves a specific export record by its unique ID.
*   **Payload:** None
*   **Returns:** A JSON object representing the export record.

*   **Example Output (Success):**
    ```json
    {
        "exp_id": 1,
        "user_id": 1,
        "document_id": 101,
        "format": "CSV",
        "filename": "export_101.csv",
        "file_path": "/path/to/exports/export_101.csv",
        "created_at": "2025-08-27T14:00:00Z"
    }
    ```

---

### 3. Create a New Export

*   **Endpoint:** `POST /api/exports/`
*   **Description:** Creates a new export record.
*   **Payload:** A JSON object with the export details.
    *   `user_id` (integer, required): The ID of the user creating the export.
    *   `document_id` (integer, required): The ID of the document being exported.
    *   `format` (string, required): The desired export format (e.g., "CSV", "JSON", "XML").
    *   `filename` (string, optional): The desired filename for the export.
    *   `file_path` (string, optional): The path where the export file will be stored.

*   **Example Input:**
    ```json
    {
        "user_id": 1,
        "document_id": 101,
        "format": "CSV",
        "filename": "my_document_export.csv"
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "exp_id": 2,
        "user_id": 1,
        "document_id": 101,
        "format": "CSV",
        "filename": "my_document_export.csv",
        "file_path": null,
        "created_at": "2025-08-27T14:30:00Z"
    }
    ```

---

### 4. Delete an Export

*   **Endpoint:** `DELETE /api/exports/<export_id>`
*   **Description:** Deletes an export record.
*   **Payload:** None
*   **Returns:** A confirmation message.

*   **Example Output (Success):**
    ```json
    {
        "message": "Export deleted successfully"
    }
    ```

---

### 5. Get All Files for an Export

*   **Endpoint:** `GET /api/exports/<export_id>/files`
*   **Description:** Retrieves all files associated with a specific export record.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of export file objects and the total count.

*   **Example Output (Success):**
    ```json
    {
        "export_files": [
            {
                "exp_file_id": 1,
                "exp_id": 1,
                "document_id": 101,
                "file_path": "/path/to/exports/export_101.csv",
                "created_at": "2025-08-27T14:00:00Z"
            }
        ],
        "count": 1
    }
    ```

---

### 6. Create an Export File

*   **Endpoint:** `POST /api/exports/<export_id>/files`
*   **Description:** Creates a new file entry for an existing export record.
*   **Payload:** A JSON object with the export file details.
    *   `document_id` (integer, required): The ID of the document associated with this export file.
    *   `file_path` (string, required): The path to the generated export file.

*   **Example Input:**
    ```json
    {
        "document_id": 101,
        "file_path": "/path/to/exports/new_export_file.json"
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "exp_file_id": 2,
        "exp_id": 1,
        "document_id": 101,
        "file_path": "/path/to/exports/new_export_file.json",
        "created_at": "2025-08-27T14:45:00Z"
    }
    ```

---

### 7. Delete an Export File

*   **Endpoint:** `DELETE /api/exports/files/<file_id>`
*   **Description:** Deletes a specific export file entry.
*   **Payload:** None
*   **Returns:** A confirmation message.

*   **Example Output (Success):**
    ```json
    {
        "message": "Export file deleted successfully"
    }
    ```

---

### 8. Get Export Formats

*   **Endpoint:** `GET /api/exports/formats`
*   **Description:** Retrieves the available formats for data export.
*   **Payload:** None
*   **Returns:** A JSON object with a list of export formats.

*   **Example Output (Success):**
    ```json
    {
        "formats": ["CSV", "JSON", "XML"],
        "count": 3
    }
    ```

## OCR Routes

**File:** `ocr_routes.py`

**Blueprint:** `/api/ocr`

This blueprint handles OCR data management, document processing, and integration with Tally for field options.

---

### 1. Get All OCR Data

*   **Endpoint:** `GET /api/ocr/data`
*   **Description:** Retrieves all OCR data records.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of OCR data objects and the total count.

*   **Example Output (Success):**
    ```json
    {
        "ocr_data": [
            {
                "ocr_id": 1,
                "document_id": 101,
                "field_id": 1,
                "predicted_value": "Invoice 123",
                "actual_value": null,
                "confidence": 0.98
            }
        ],
        "count": 1
    }
    ```

---

### 2. Get Specific OCR Data

*   **Endpoint:** `GET /api/ocr/data/<ocr_id>`
*   **Description:** Retrieves a specific OCR data record by its unique ID.
*   **Payload:** None
*   **Returns:** A JSON object representing the OCR data record.

*   **Example Output (Success):**
    ```json
    {
        "ocr_id": 1,
        "document_id": 101,
        "field_id": 1,
        "predicted_value": "Invoice 123",
        "actual_value": null,
        "confidence": 0.98
    }
    ```

---

### 3. Create New OCR Data

*   **Endpoint:** `POST /api/ocr/data`
*   **Description:** Creates a new OCR data record.
*   **Payload:** A JSON object with the OCR data details.
    *   `document_id` (integer, required): The ID of the document.
    *   `field_id` (integer, required): The ID of the template field.
    *   `predicted_value` (string, required): The value predicted by OCR.
    *   `actual_value` (string, optional): The actual (corrected) value.
    *   `confidence` (float, optional): The confidence score.

*   **Example Input:**
    ```json
    {
        "document_id": 101,
        "field_id": 2,
        "predicted_value": "2025-08-27",
        "confidence": 0.95
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "ocr_id": 2,
        "document_id": 101,
        "field_id": 2,
        "predicted_value": "2025-08-27",
        "actual_value": null,
        "confidence": 0.95
    }
    ```

---

### 4. Update OCR Data

*   **Endpoint:** `PUT /api/ocr/data/<ocr_id>`
*   **Description:** Updates an existing OCR data record.
*   **Payload:** A JSON object with fields to update.
    *   `predicted_value` (string, optional): New predicted value.
    *   `actual_value` (string, optional): New actual value.
    *   `confidence` (float, optional): New confidence score.

*   **Example Input:**
    ```json
    {
        "actual_value": "2025-08-28"
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "ocr_id": 2,
        "document_id": 101,
        "field_id": 2,
        "predicted_value": "2025-08-27",
        "actual_value": "2025-08-28",
        "confidence": 0.95
    }
    ```

---

### 5. Delete OCR Data

*   **Endpoint:** `DELETE /api/ocr/data/<ocr_id>`
*   **Description:** Deletes an OCR data record.
*   **Payload:** None
*   **Returns:** A confirmation message.

*   **Example Output (Success):**
    ```json
    {
        "message": "OCR data deleted successfully"
    }
    ```

---

### 6. Get All Line Items

*   **Endpoint:** `GET /api/ocr/line-items`
*   **Description:** Retrieves all OCR line item records.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of line item objects and the total count.

---

### 7. Get Specific Line Item

*   **Endpoint:** `GET /api/ocr/line-items/<line_item_id>`
*   **Description:** Retrieves a specific OCR line item record by its unique ID.
*   **Payload:** None
*   **Returns:** A JSON object representing the line item record.

---

### 8. Create New Line Item

*   **Endpoint:** `POST /api/ocr/line-items`
*   **Description:** Creates a new OCR line item record.
*   **Payload:**
    *   `document_id` (integer, required): The ID of the document.
    *   `field_id` (integer, required): The ID of the table field this line item belongs to.
    *   `row_index` (integer, required): The row index of the line item.

---

### 9. Update Line Item

*   **Endpoint:** `PUT /api/ocr/line-items/<line_item_id>`
*   **Description:** Updates an existing OCR line item record.
*   **Payload:**
    *   `row_index` (integer, optional): New row index.

---

### 10. Delete Line Item

*   **Endpoint:** `DELETE /api/ocr/line-items/<line_item_id>`
*   **Description:** Deletes an OCR line item record.
*   **Payload:** None
*   **Returns:** A confirmation message.

---

### 11. Get All Values for a Line Item

*   **Endpoint:** `GET /api/ocr/line-items/<line_item_id>/values`
*   **Description:** Retrieves all values (cells) for a specific OCR line item.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of line item value objects and the total count.

---

### 12. Create New Line Item Value

*   **Endpoint:** `POST /api/ocr/line-items/<line_item_id>/values`
*   **Description:** Creates a new value (cell) for a specific OCR line item.
*   **Payload:**
    *   `sub_temp_field_id` (integer, required): The ID of the sub-template field (column).
    *   `predicted_value` (string, required): The predicted value for the cell.
    *   `actual_value` (string, optional): The actual (corrected) value.
    *   `confidence` (float, optional): The confidence score.

---

### 13. Get Specific Line Item Value

*   **Endpoint:** `GET /api/ocr/line-items/values/<value_id>`
*   **Description:** Retrieves a specific OCR line item value record by its unique ID.
*   **Payload:** None
*   **Returns:** A JSON object representing the line item value record.

---

### 14. Update Line Item Value

*   **Endpoint:** `PUT /api/ocr/line-items/values/<value_id>`
*   **Description:** Updates an existing OCR line item value record.
*   **Payload:**
    *   `predicted_value` (string, optional): New predicted value.
    *   `actual_value` (string, optional): New actual value.
    *   `confidence` (float, optional): New confidence score.

---

### 15. Delete Line Item Value

*   **Endpoint:** `DELETE /api/ocr/line-items/values/<value_id>`
*   **Description:** Deletes an OCR line item value record.
*   **Payload:** None
*   **Returns:** A confirmation message.

---

### 16. Extract Fields (Manual Trigger)

*   **Endpoint:** `POST /api/ocr/extract_fields`
*   **Description:** Manually triggers OCR field extraction for a document using a specified template.
*   **Payload:**
    *   `doc_id` (integer, required): The ID of the document to process.
    *   `template_id` (integer, required): The ID of the template to use for extraction.

*   **Example Input:**
    ```json
    {
        "doc_id": 101,
        "template_id": 1
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "fields": {
            "InvoiceNumber": "INV-2025-001",
            "TotalAmount": "123.45"
        }
    }
    ```

---

### 17. Process Document (Full Pipeline)

*   **Endpoint:** `POST /api/ocr/process_document`
*   **Description:** Initiates the full OCR processing pipeline for a document, including extraction, data conversion, and database storage.
*   **Payload:**
    *   `doc_id` (integer, required): The ID of the document to process.
    *   `template_id` (integer, required): The ID of the template to use for processing.

*   **Example Input:**
    ```json
    {
        "doc_id": 101,
        "template_id": 1
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "success": true,
        "message": "Document processed successfully",
        "document_id": 101,
        "template_id": 1,
        "status": "PROCESSED",
        "extracted_data": {
            "InvoiceNumber": "INV-2025-001",
            "TotalAmount": 123.45
        },
        "table_data": {
            "LineItems": {
                "field_id": 5,
                "field_type": "table",
                "columns": [
                    {"name": "Description", "data_type": "STRING", "sub_temp_field_id": 10},
                    {"name": "Quantity", "data_type": "INTEGER", "sub_temp_field_id": 11}
                ],
                "rows": [
                    {"Description": "Item A", "Quantity": 1},
                    {"Description": "Item B", "Quantity": 2}
                ],
                "row_count": 2
            }
        },
        "ocr_records_created": 2,
        "line_items_created": 2
    }
    ```

---

### 18. Load Tally Options for Field

*   **Endpoint:** `POST /api/ocr/field/<field_id>/load_tally_options`
*   **Description:** Loads data from Tally as options for a SELECT type field.
*   **Payload:**
    *   `data_type` (string, required): Type of data to load ("auto", "companies", "ledgers", "stock_items", "customers", "vendors", "all_ledgers").
    *   `group_filter` (string, optional): Filter by a specific group (for ledgers/stock items).
    *   `clear_existing` (boolean, optional): Whether to clear existing options before loading (defaults to true).

*   **Example Input:**
    ```json
    {
        "data_type": "ledgers",
        "group_filter": "Sundry Debtors"
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "success": true,
        "message": "Options loaded successfully",
        "options_count": 5
    }
    ```

---

### 19. Get Field Options Summary

*   **Endpoint:** `GET /api/ocr/field/<field_id>/options`
*   **Description:** Retrieves a summary of current options configured for a field.
*   **Payload:** None
*   **Returns:** A JSON object with options summary.

---

### 20. Refresh Field Tally Options

*   **Endpoint:** `POST /api/ocr/field/<field_id>/refresh_options`
*   **Description:** Refreshes options for a field by reloading them from Tally.
*   **Payload:** None
*   **Returns:** A JSON object with refresh status.

---

### 21. Load Customers for Field

*   **Endpoint:** `POST /api/ocr/field/<field_id>/load_customers`
*   **Description:** Loads customer ledgers from Tally as options for a field.
*   **Payload:** None
*   **Returns:** A JSON object with load status.

---

### 22. Load Vendors for Field

*   **Endpoint:** `POST /api/ocr/field/<field_id>/load_vendors`
*   **Description:** Loads vendor ledgers from Tally as options for a field.
*   **Payload:** None
*   **Returns:** A JSON object with load status.

---

### 23. Load Tally Options for Sub-Field

*   **Endpoint:** `POST /api/ocr/sub-field/<sub_field_id>/load_tally_options`
*   **Description:** Loads data from Tally as options for a SELECT type sub-template field (within a table).
*   **Payload:**
    *   `data_type` (string, required): Type of data to load ("auto", "stock_items", "ledgers").
    *   `group_filter` (string, optional): Filter by a specific group.
    *   `clear_existing` (boolean, optional): Whether to clear existing options before loading (defaults to true).

---

### 24. Load Stock Items for Sub-Field

*   **Endpoint:** `POST /api/ocr/sub-field/<sub_field_id>/load_stock_items`
*   **Description:** Loads stock items from Tally as options for a sub-template field.
*   **Payload:**
    *   `stock_group` (string, optional): Filter by a specific stock group.
    *   `clear_existing` (boolean, optional): Whether to clear existing options before loading (defaults to true).

---

### 25. Load Ledgers for Sub-Field

*   **Endpoint:** `POST /api/ocr/sub-field/<sub_field_id>/load_ledgers`
*   **Description:** Loads ledgers from Tally as options for a sub-template field.
*   **Payload:**
    *   `ledger_group` (string, optional): Filter by a specific ledger group.
    *   `clear_existing` (boolean, optional): Whether to clear existing options before loading (defaults to true).

## Tally Routes

**File:** `tally_routes.py`

**Blueprint:** `/api/tally`

This blueprint provides endpoints for interacting with Tally, including testing connection, retrieving master data (companies, ledgers, stock items, units), ensuring existence of entities, and creating purchase vouchers from OCR data.

---

### 1. Test Connection

*   **Endpoint:** `GET /api/tally/test_connection`
*   **Description:** Tests the connection to the configured Tally instance.
*   **Payload:** None
*   **Returns:** A JSON object indicating connection success and Tally version info.

*   **Example Output (Success):**
    ```json
    {
        "success": true,
        "message": "Connected to Tally successfully",
        "connection_test": "Connection successful",
        "version_info": {
            "Tally.ERP 9": "Release 6.6.3",
            "TallyPrime": "Release 2.1"
        }
    }
    ```

---

### 2. Get Companies

*   **Endpoint:** `GET /api/tally/companies`
*   **Description:** Retrieves a list of all companies from Tally.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of company names and the total count.

*   **Example Output (Success):**
    ```json
    {
        "success": true,
        "companies": ["My Company A", "My Company B"],
        "count": 2
    }
    ```

---

### 3. Get Ledgers

*   **Endpoint:** `GET /api/tally/ledgers`
*   **Description:** Retrieves a list of all ledgers from Tally.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of ledger names and the total count.

*   **Example Output (Success):**
    ```json
    {
        "success": true,
        "ledgers": ["Cash", "Bank Account", "Sales", "Purchases"],
        "count": 4
    }
    ```

---

### 4. Get Stock Items

*   **Endpoint:** `GET /api/tally/stock_items`
*   **Description:** Retrieves a list of all stock items from Tally.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of stock item names and the total count.

*   **Example Output (Success):**
    ```json
    {
        "success": true,
        "stock_items": ["Product A", "Product B"],
        "count": 2
    }
    ```

---

### 5. Ensure Stock Item Exists

*   **Endpoint:** `POST /api/tally/stock_items/ensure_exists`
*   **Description:** Checks if a stock item exists in Tally; if not, creates it.
*   **Payload:**
    *   `item_name` (string, required): The name of the stock item.
    *   `stock_group` (string, optional): The stock group for the item (defaults to "Primary").

*   **Example Input:**
    ```json
    {
        "item_name": "New Product C",
        "stock_group": "Raw Materials"
    }
    ```

*   **Example Output (Success - Created):**
    ```json
    {
        "success": true,
        "already_exists": false,
        "item_name": "New Product C",
        "message": "Successfully created stock item 'New Product C' with base unit PCS"
    }
    ```

*   **Example Output (Success - Already Exists):**
    ```json
    {
        "success": true,
        "already_exists": true,
        "item_name": "Product A",
        "message": "Stock item 'Product A' already exists in Tally"
    }
    ```

---

### 6. Create Purchase Voucher from Document

*   **Endpoint:** `POST /api/tally/document/<document_id>/create_purchase_voucher`
*   **Description:** Creates a purchase voucher in Tally using OCR data extracted from a processed document. This is a key integration endpoint.
*   **Payload:** None (document ID is in path)
*   **Returns:** A JSON object detailing the success/failure of voucher creation, including stock item and party ledger creation summaries.

*   **Example Output (Success):**
    ```json
    {
        "success": true,
        "message": "Purchase voucher created successfully (created 1 new stock item), created party ledger",
        "document_id": 101,
        "voucher_data": {
            "voucher_type": "Purchase",
            "party_name": "Vendor XYZ",
            "date": "2025-04-01",
            "voucher_number": "INV-001",
            "narration": "Purchase from Vendor XYZ - Invoice INV-001",
            "bill_ref": "INV-001",
            "items": [
                {"stock_item": "Product A", "quantity": 10.0, "rate": 50.0, "amount": 500.0, "unit": "PCS", "godown": "Main Location", "batch": "Default Batch", "purchase_ledger": "Purchases Account"}
            ],
            "total_amount": 500.0,
            "vendor_address": "123 Main St"
        },
        "voucher_result": {
            "success": true,
            "message": "Purchase voucher created successfully for Vendor XYZ",
            "voucher_type": "Purchase",
            "party_name": "Vendor XYZ",
            "date": "2025-04-01",
            "total_amount": 500.0,
            "items_count": 1,
            "tally_response": "Voucher created successfully"
        },
        "stock_item_summary": {
            "total_items": 1,
            "existing_items": 0,
            "created_items": 1,
            "failed_items": 0,
            "created_item_names": ["Product A"],
            "existing_item_names": [],
            "failed_item_details": []
        },
        "party_ledger_summary": {
            "party_name": "Vendor XYZ",
            "ledger_exists": false,
            "ledger_created": true,
            "ledger_result": {
                "success": true,
                "already_exists": false,
                "ledger_name": "Vendor XYZ",
                "message": "Successfully created party ledger 'Vendor XYZ' as Sundry Creditor"
            }
        },
        "stock_item_results": [
            {
                "item_name": "Product A",
                "result": {
                    "success": true,
                    "already_exists": false,
                    "item_name": "Product A",
                    "message": "Successfully created stock item 'Product A' with base unit PCS"
                }
            }
        ],
        "warnings": []
    }
    ```

---

### 7. Get Tally-Ready OCR Data

*   **Endpoint:** `GET /api/tally/document/<document_id>/ocr_data`
*   **Description:** Retrieves OCR data for a document formatted for direct conversion into a Tally voucher.
*   **Payload:** None
*   **Returns:** A JSON object containing the original OCR data and the converted Tally voucher data.

*   **Example Output (Success):**
    ```json
    {
        "success": true,
        "document_id": 101,
        "original_ocr_data": {
            "document_id": 101,
            "status": "PROCESSED",
            "original_filename": "invoice.pdf",
            "processed_at": "2025-08-27T15:00:00Z",
            "extracted_data": {
                "vendor_name": "Vendor XYZ",
                "invoice_number": "INV-001",
                "total_amount": "500.00"
            },
            "table_data": {
                "LineItems": {
                    "field_id": 5,
                    "field_type": "table",
                    "columns": [
                        {"name": "item_description", "data_type": "STRING", "sub_temp_field_id": 10},
                        {"name": "quantity", "data_type": "INTEGER", "sub_temp_field_id": 11},
                        {"name": "unit_price", "data_type": "FLOAT", "sub_temp_field_id": 12},
                        {"name": "line_total", "data_type": "FLOAT", "sub_temp_field_id": 13}
                    ],
                    "rows": [
                        {"item_description": "Product A", "quantity": "10", "unit_price": "50", "line_total": "500"}
                    ],
                    "row_count": 1
                }
            }
        },
        "tally_voucher_data": {
            "voucher_type": "Purchase",
            "party_name": "Vendor XYZ",
            "date": "2025-04-01",
            "voucher_number": "INV-001",
            "narration": "Purchase from Vendor XYZ - Invoice INV-001",
            "bill_ref": "INV-001",
            "items": [
                {"stock_item": "Product A", "quantity": 10.0, "rate": 50.0, "amount": 500.0, "unit": "PCS", "godown": "Main Location", "batch": "Default Batch", "purchase_ledger": "Purchases Account"}
            ],
            "total_amount": 500.0,
            "vendor_address": ""
        }
    }
    ```

---

### 8. Ensure Party Ledger Exists

*   **Endpoint:** `POST /api/tally/ledgers/ensure_exists`
*   **Description:** Checks if a party ledger exists in Tally; if not, creates it.
*   **Payload:**
    *   `party_name` (string, required): The name of the party ledger.
    *   `ledger_group` (string, optional): The ledger group (defaults to "Sundry Creditors").

*   **Example Input:**
    ```json
    {
        "party_name": "New Vendor ABC",
        "ledger_group": "Sundry Creditors"
    }
    ```

*   **Example Output (Success - Created):**
    ```json
    {
        "success": true,
        "already_exists": false,
        "ledger_name": "New Vendor ABC",
        "message": "Successfully created party ledger 'New Vendor ABC' as Sundry Creditor"
    }
    ```

---

### 9. Get Units of Measure

*   **Endpoint:** `GET /api/tally/units`
*   **Description:** Retrieves a list of all units of measure (UOM) from Tally.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of units and the total count.

---

### 10. Get Specific Unit of Measure

*   **Endpoint:** `GET /api/tally/units/<unit_name>`
*   **Description:** Retrieves a specific unit of measure by name from Tally.
*   **Payload:** None
*   **Returns:** A JSON object representing the unit.

---

### 11. Create Unit of Measure

*   **Endpoint:** `POST /api/tally/units`
*   **Description:** Creates a new simple or compound unit of measure in Tally.
*   **Payload (Simple Unit):**
    *   `name` (string, required): The name of the unit (e.g., "PCS", "NOS").
    *   `decimal_places` (integer, optional): Number of decimal places (0-4, defaults to 0).
*   **Payload (Compound Unit):**
    *   `name` (string, required): The name of the compound unit (e.g., "DZ").
    *   `base_unit` (string, required): The name of the base unit (e.g., "PCS").
    *   `conversion` (number, required): The conversion factor (e.g., 12 for a dozen).
    *   `decimal_places` (integer, optional): Number of decimal places (0-4, defaults to 0).

---

### 12. Update Unit of Measure

*   **Endpoint:** `PUT /api/tally/units/<unit_name>`
*   **Description:** Updates an existing unit of measure in Tally.
*   **Payload:** Fields to update (e.g., `decimal_places`, `conversion`).

---

### 13. Delete Unit of Measure

*   **Endpoint:** `DELETE /api/tally/units/<unit_name>`
*   **Description:** Deletes a unit of measure from Tally. (Note: Tally typically doesn't support deleting units in use; this endpoint might suggest deactivation instead).
*   **Payload:** None
*   **Returns:** A message indicating success or if deletion is not supported.

---

### 14. Ensure Unit Exists

*   **Endpoint:** `POST /api/tally/units/ensure_exists`
*   **Description:** Checks if a unit exists in Tally; if not, creates it (simple or compound).
*   **Payload (Simple Unit):**
    *   `unit_name` (string, required): The name of the unit.
    *   `decimal_places` (integer, optional): Number of decimal places.
*   **Payload (Compound Unit):**
    *   `unit_name` (string, required): The name of the compound unit.
    *   `base_unit` (string, required): The base unit.
    *   `conversion` (number, required): The conversion factor.
    *   `decimal_places` (integer, optional): Number of decimal places.

---

### 15. Get Common Units

*   **Endpoint:** `GET /api/tally/units/common`
*   **Description:** Retrieves a list of common units predefined in the system.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of common units.

---

### 16. Create All Common Units

*   **Endpoint:** `POST /api/tally/units/common/create_all`
*   **Description:** Creates all predefined common units in Tally if they don't already exist.
*   **Payload:** None
*   **Returns:** A JSON object summarizing the creation results.

## Template Routes

**File:** `template_routes.py`

**Blueprint:** `/api/templates`

This blueprint manages OCR templates, including their creation, retrieval, updating, deletion, and the management of associated fields and field options.

---

### 1. Get All Templates

*   **Endpoint:** `GET /api/templates/`
*   **Description:** Retrieves a list of all OCR templates.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of template objects and the total count.

*   **Example Output (Success):**
    ```json
    {
        "templates": [
            {
                "temp_id": 1,
                "user_id": 1,
                "name": "Invoice Template",
                "description": "Standard invoice processing template",
                "ai_instructions": "Extract invoice details accurately.",
                "created_at": "2025-08-27T16:00:00Z"
            }
        ],
        "count": 1
    }
    ```

---

### 2. Get Template by ID

*   **Endpoint:** `GET /api/templates/<template_id>`
*   **Description:** Retrieves a specific template by its unique ID.
*   **Payload:** None
*   **Returns:** A JSON object representing the template.

*   **Example Output (Success):**
    ```json
    {
        "temp_id": 1,
        "user_id": 1,
        "name": "Invoice Template",
        "description": "Standard invoice processing template",
        "ai_instructions": "Extract invoice details accurately.",
        "created_at": "2025-08-27T16:00:00Z"
    }
    ```

---

### 3. Get Template Names and IDs

*   **Endpoint:** `GET /api/templates/names`
*   **Description:** Retrieves only the names and IDs of all templates.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of template names and IDs.

*   **Example Output (Success):**
    ```json
    {
        "templates": [
            {
                "temp_id": 1,
                "name": "Invoice Template"
            }
        ],
        "count": 1
    }
    ```

---

### 4. Create a New Template

*   **Endpoint:** `POST /api/templates/`
*   **Description:** Creates a new OCR template.
*   **Payload:** A JSON object with the template details.
    *   `user_id` (integer, required): The ID of the user creating the template.
    *   `name` (string, required): The name of the template.
    *   `description` (string, optional): A description for the template.
    *   `ai_instructions` (string, optional): Specific AI instructions for the template.

*   **Example Input:**
    ```json
    {
        "user_id": 1,
        "name": "Purchase Order Template",
        "description": "Template for purchase orders",
        "ai_instructions": "Focus on line items and total amount."
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "temp_id": 2,
        "user_id": 1,
        "name": "Purchase Order Template",
        "description": "Template for purchase orders",
        "ai_instructions": "Focus on line items and total amount.",
        "created_at": "2025-08-27T16:30:00Z"
    }
    ```

---

### 5. Update a Template

*   **Endpoint:** `PUT /api/templates/<template_id>`
*   **Description:** Updates an existing OCR template.
*   **Payload:** A JSON object with fields to update.
    *   `name` (string, optional): New name for the template.
    *   `description` (string, optional): New description.
    *   `ai_instructions` (string, optional): New AI instructions.

*   **Example Input:**
    ```json
    {
        "name": "Updated Invoice Template"
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "temp_id": 1,
        "user_id": 1,
        "name": "Updated Invoice Template",
        "description": "Standard invoice processing template",
        "ai_instructions": "Extract invoice details accurately.",
        "created_at": "2025-08-27T16:00:00Z"
    }
    ```

---

### 6. Delete a Template

*   **Endpoint:** `DELETE /api/templates/<template_id>`
*   **Description:** Deletes an OCR template.
*   **Payload:** None
*   **Returns:** A confirmation message.

*   **Example Output (Success):**
    ```json
    {
        "message": "Template deleted successfully"
    }
    ```

---

### 7. Get All Fields for a Template

*   **Endpoint:** `GET /api/templates/<template_id>/fields`
*   **Description:** Retrieves all fields associated with a specific template.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of template field objects and the total count.

*   **Example Output (Success):**
    ```json
    {
        "template_fields": [
            {
                "field_id": 1,
                "template_id": 1,
                "field_name": "InvoiceNumber",
                "field_order": 1,
                "field_type": "TEXT",
                "ai_instructions": null
            }
        ],
        "count": 1
    }
    ```

---

### 8. Create a Template Field

*   **Endpoint:** `POST /api/templates/<template_id>/fields`
*   **Description:** Creates a new field for a template.
*   **Payload:** A JSON object with the field details.
    *   `field_name` (string, required): The name of the field (e.g., "InvoiceNumber", "TotalAmount").
    *   `field_order` (integer, required): The display order of the field.
    *   `field_type` (string, required): The type of the field (e.g., "TEXT", "NUMBER", "DATE", "TABLE", "SELECT").
    *   `ai_instructions` (string, optional): Specific AI instructions for this field.

*   **Example Input:**
    ```json
    {
        "field_name": "TotalAmount",
        "field_order": 2,
        "field_type": "NUMBER",
        "ai_instructions": "Extract the grand total from the invoice."
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "field_id": 2,
        "template_id": 1,
        "field_name": "TotalAmount",
        "field_order": 2,
        "field_type": "NUMBER",
        "ai_instructions": "Extract the grand total from the invoice."
    }
    ```

---

### 9. Get Specific Template Field

*   **Endpoint:** `GET /api/templates/fields/<field_id>`
*   **Description:** Retrieves a specific template field by its unique ID.
*   **Payload:** None
*   **Returns:** A JSON object representing the template field.

---

### 10. Update Template Field

*   **Endpoint:** `PUT /api/templates/fields/<field_id>`
*   **Description:** Updates an existing template field.
*   **Payload:** A JSON object with fields to update.
    *   `field_name` (string, optional): New name for the field.
    *   `field_order` (integer, optional): New display order.
    *   `field_type` (string, optional): New field type.
    *   `ai_instructions` (string, optional): New AI instructions.

---

### 11. Delete Template Field

*   **Endpoint:** `DELETE /api/templates/fields/<field_id>`
*   **Description:** Deletes a template field.
*   **Payload:** None
*   **Returns:** A confirmation message.

---

### 12. Get Sub-Fields for a Template Field

*   **Endpoint:** `GET /api/templates/fields/<field_id>/sub-fields`
*   **Description:** Retrieves all sub-fields (columns) for a specific template field (typically for TABLE type fields).
*   **Payload:** None
*   **Returns:** A JSON object containing a list of sub-template field objects and the total count.

---

### 13. Create a Sub-Template Field

*   **Endpoint:** `POST /api/templates/fields/<field_id>/sub-fields`
*   **Description:** Creates a new sub-field for a template field.
*   **Payload:** A JSON object with the sub-field details.
    *   `field_name` (string, required): The name of the sub-field (e.g., "ItemDescription", "Quantity").
    *   `data_type` (string, required): The data type of the sub-field (e.g., "STRING", "INTEGER", "FLOAT", "SELECT").
    *   `ai_instructions` (string, optional): Specific AI instructions for this sub-field.

---

### 14. Get Options for a Template Field

*   **Endpoint:** `GET /api/templates/fields/<field_id>/options`
*   **Description:** Retrieves all predefined options for a SELECT type template field.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of field option objects and the total count.

---

### 15. Create a Field Option

*   **Endpoint:** `POST /api/templates/fields/<field_id>/options`
*   **Description:** Creates a new option for a SELECT type template field.
*   **Payload:**
    *   `option_value` (string, required): The actual value to be stored.
    *   `option_label` (string, required): The display label for the option.

---

### 16. Get Options for a Sub-Template Field

*   **Endpoint:** `GET /api/templates/sub-fields/<sub_field_id>/options`
*   **Description:** Retrieves all predefined options for a SELECT type sub-template field.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of sub-field option objects and the total count.

---

### 17. Create a Sub-Template Field Option

*   **Endpoint:** `POST /api/templates/sub-fields/<sub_field_id>/options`
*   **Description:** Creates a new option for a SELECT type sub-template field.
*   **Payload:**
    *   `option_value` (string, required): The actual value to be stored.
    *   `option_label` (string, required): The display label for the option.

---

### 18. Delete a Sub-Template Field Option

*   **Endpoint:** `DELETE /api/templates/sub-fields/options/<option_id>`
*   **Description:** Deletes a sub-template field option.
*   **Payload:** None
*   **Returns:** A confirmation message.

## User Routes

**File:** `user_routes.py`

**Blueprint:** `/api/users`

This blueprint handles user management, including creation, retrieval, updating, deletion, and login.

---

### 1. Get All Users

*   **Endpoint:** `GET /api/users/`
*   **Description:** Retrieves a list of all registered users.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of user objects and the total count.

*   **Example Output (Success):**
    ```json
    {
        "users": [
            {
                "user_id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com"
            },
            {
                "user_id": 2,
                "name": "Jane Smith",
                "email": "jane.smith@example.com"
            }
        ],
        "count": 2
    }
    ```

---

### 2. Get User by ID

*   **Endpoint:** `GET /api/users/<user_id>`
*   **Description:** Retrieves a specific user by their unique ID.
*   **Payload:** None
*   **Returns:** A JSON object representing the user.

*   **Example Output (Success):**
    ```json
    {
        "user_id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
    ```

*   **Example Output (Not Found):**
    ```json
    {
        "error": "User not found"
    }
    ```

---

### 3. Create a New User

*   **Endpoint:** `POST /api/users/`
*   **Description:** Creates a new user account.
*   **Payload:** A JSON object with the user's name, email, and password.
    *   `name` (string, required): The user's full name.
    *   `email` (string, required): The user's email address.
    *   `password` (string, required): The user's password.

*   **Example Input:**
    ```json
    {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "securepassword123"
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "user_id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
    ```

*   **Example Output (Missing Fields):**
    ```json
    {
        "error": "Missing required fields"
    }
    ```

*   **Example Output (User Exists):**
    ```json
    {
        "error": "User with this email already exists"
    }
    ```

---

### 4. Update a User

*   **Endpoint:** `PUT /api/users/<user_id>`
*   **Description:** Updates a user's information.
*   **Payload:** A JSON object with the fields to update.
    *   `name` (string, optional): The user's new name.
    *   `email` (string, optional): The user's new email address.
    *   `password` (string, optional): The user's new password.

*   **Example Input:**
    ```json
    {
        "name": "Johnathan Doe"
    }
    ```

*   **Example Output (Success):**
    ```json
    {
        "user_id": 1,
        "name": "Johnathan Doe",
        "email": "john.doe@example.com"
    }
    ```

---

### 5. Delete a User

*   **Endpoint:** `DELETE /api/users/<user_id>`
*   **Description:** Deletes a user account.
*   **Payload:** None
*   **Returns:** A confirmation message.

*   **Example Output (Success):**
    ```json
    {
        "message": "User deleted successfully"
    }
    ```

---

### 6. Get User Documents

*   **Endpoint:** `GET /api/users/<user_id>/documents`
*   **Description:** Retrieves all documents associated with a specific user.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of document objects and the total count.

*   **Example Output (Success):**
    ```json
    {
        "documents": [
            {
                "doc_id": 101,
                "file_name": "invoice_123.pdf",
                "upload_date": "2025-08-27T10:00:00Z"
            }
        ],
        "count": 1
    }
    ```

---

### 7. Get User Templates

*   **Endpoint:** `GET /api/users/<user_id>/templates`
*   **Description:** Retrieves all templates created by a specific user.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of template objects and the total count.

*   **Example Output (Success):**
    ```json
    {
        "templates": [
            {
                "temp_id": 1,
                "name": "Default Invoice Template",
                "creation_date": "2025-08-27T10:00:00Z"
            }
        ],
        "count": 1
    }
    ```

---

### 8. Get User Template Names

*   **Endpoint:** `GET /api/users/<user_id>/templates/names`
*   **Description:** Retrieves only the names and IDs of templates created by a specific user.
*   **Payload:** None
*   **Returns:** A JSON object containing a list of template names and IDs.

*   **Example Output (Success):**
    ```json
    {
        "templates": [
            {
                "temp_id": 1,
                "name": "Default Invoice Template"
            }
        ],
        "count": 1
    }
    ```

---

### 9. User Login

*   **Endpoint:** `POST /api/users/login`
*   **Description:** Authenticates a user and returns their information upon successful login.
*   **Payload:** A JSON object with the user's email and password.
    *   `email` (string, required): The user's email address.
    *   `password` (string, required): The user's password.

*   **Example Input:**
    ```json
    {
        "email": "john.doe@example.com",
        "password": "securepassword123"
    }
    ```

*   **Example Output (Invalid Credentials):**
    ```json
    {
        "error": "Invalid credentials"
    }
    ```