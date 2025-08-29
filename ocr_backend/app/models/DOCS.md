# Model Documentation

This document provides a detailed overview of the database models used in the OCR platform.

## User Model

**File:** `user.py`

**Table Name:** `users`

The `User` model represents a user in the system, handling authentication and authorization.

### Attributes:

*   **`user_id`** (Integer):
    *   **Description:** Unique identifier for the user.
    *   **Constraints:** Primary Key
*   **`name`** (String(100)):
    *   **Description:** The full name of the user.
    *   **Constraints:** Not Null
*   **`email`** (String(120)):
    *   **Description:** The email address of the user. Used for login.
    *   **Constraints:** Unique, Not Null
*   **`password_hash`** (String(255)):
    *   **Description:** Hashed password for security.
    *   **Constraints:** Not Null
*   **`api_key`** (String(32)):
    *   **Description:** Unique API key for the user, automatically generated.
    *   **Constraints:** Unique, Not Null, Default (random hex token)
*   **`created_at`** (DateTime):
    *   **Description:** Timestamp when the user record was created.
    *   **Constraints:** Default (current UTC time)
*   **`updated_at`** (DateTime):
    *   **Description:** Timestamp when the user record was last updated.
    *   **Constraints:** Default (current UTC time), On Update (current UTC time)

### Relationships:

*   **`documents`**: One-to-Many relationship with `Document` model. A user can have multiple documents.
    *   `backref='user'`
    *   `lazy='dynamic'`
    *   `cascade='all, delete-orphan'` (documents are deleted if the user is deleted)
*   **`templates`**: One-to-Many relationship with `Template` model. A user can create multiple templates.
    *   `backref='user'`
    *   `lazy='dynamic'`
    *   `cascade='all, delete-orphan'` (templates are deleted if the user is deleted)

### Methods:

*   **`set_password(password)`**:
    *   **Description:** Hashes the provided plain-text password and stores it in `password_hash`.
    *   **Parameters:**
        *   `password` (string): The plain-text password.
*   **`check_password(password)`**:
    *   **Description:** Checks if the provided plain-text password matches the stored hashed password.
    *   **Parameters:**
        *   `password` (string): The plain-text password to check.
    *   **Returns:** `True` if passwords match, `False` otherwise.
*   **`to_dict()`**:
    *   **Description:** Converts the User object to a dictionary, suitable for JSON serialization.
    *   **Returns:** `dict` containing user's `user_id`, `name`, `email`, `api_key`, `created_at`, and `updated_at`. (Note: `password_hash` is not included directly for security, but a placeholder `_plain_password` might be present for debugging/demo purposes).
*   **`__repr__()`**:
    *   **Description:** Returns a string representation of the User object, primarily for debugging.
    *   **Returns:** `str` in the format `<User {email}>`.

## Document Model

**File:** `document.py`

**Table Name:** `documents`

The `Document` model represents a file uploaded by a user for OCR processing.

### Attributes:

*   **`doc_id`** (Integer):
    *   **Description:** Unique identifier for the document.
    *   **Constraints:** Primary Key
*   **`user_id`** (Integer):
    *   **Description:** Foreign key linking to the `User` who uploaded the document.
    *   **Constraints:** Foreign Key (`users.user_id`), Not Null
*   **`file_path`** (String(500)):
    *   **Description:** The path to the stored document file on the server.
    *   **Constraints:** Not Null
*   **`original_filename`** (String(255)):
    *   **Description:** The original name of the file when it was uploaded.
    *   **Constraints:** Not Null
*   **`status`** (Enum):
    *   **Description:** The current processing status of the document (e.g., PENDING, PROCESSING, PROCESSED, FAILED).
    *   **Constraints:** Not Null, Default (`DocumentStatus.PENDING`)
*   **`created_at`** (DateTime):
    *   **Description:** Timestamp when the document record was created.
    *   **Constraints:** Default (current UTC time)
*   **`updated_at`** (DateTime):
    *   **Description:** Timestamp when the document record was last updated.
    *   **Constraints:** Default (current UTC time), On Update (current UTC time)
*   **`processed_at`** (DateTime):
    *   **Description:** Timestamp when the document finished OCR processing.
    *   **Constraints:** Nullable

### Relationships:

*   **`ocr_data`**: One-to-Many relationship with `OCRData` model. Stores extracted data fields.
    *   `backref='document'`
    *   `lazy='dynamic'`
    *   `cascade='all, delete-orphan'`
*   **`ocr_line_items`**: One-to-Many relationship with `OCRLineItem` model. Stores extracted table line items.
    *   `backref='document'`
    *   `lazy='dynamic'`
    *   `cascade='all, delete-orphan'`
*   **`export_files`**: One-to-Many relationship with `ExportFile` model. Stores records of exported versions of this document.
    *   `backref='document'`
    *   `lazy='dynamic'`
    *   `cascade='all, delete-orphan'`

### Methods:

*   **`to_dict()`**:
    *   **Description:** Converts the Document object to a dictionary, suitable for JSON serialization.
    *   **Returns:** `dict` containing `doc_id`, `user_id`, `file_path`, `original_filename`, `status`, `created_at`, `updated_at`, and `processed_at`.
*   **`__repr__()`**:
    *   **Description:** Returns a string representation of the Document object.
    *   **Returns:** `str` in the format `<Document {original_filename}>`.

## Export Model

**File:** `export.py`

**Table Name:** `exports`

The `Export` model represents a record of a data export operation, specifying the format and associated files.

### Attributes:

*   **`exp_id`** (Integer):
    *   **Description:** Unique identifier for the export record.
    *   **Constraints:** Primary Key
*   **`format`** (Enum):
    *   **Description:** The format of the exported data (e.g., CSV, JSON, XML).
    *   **Constraints:** Not Null
*   **`export_time`** (DateTime):
    *   **Description:** Timestamp when the export operation was performed.
    *   **Constraints:** Default (current UTC time)
*   **`created_at`** (DateTime):
    *   **Description:** Timestamp when the export record was created.
    *   **Constraints:** Default (current UTC time)
*   **`updated_at`** (DateTime):
    *   **Description:** Timestamp when the export record was last updated.
    *   **Constraints:** Default (current UTC time), On Update (current UTC time)

### Relationships:

*   **`export_files`**: One-to-Many relationship with `ExportFile` model. Represents the individual files generated as part of this export.
    *   `backref='export'`
    *   `lazy='dynamic'`
    *   `cascade='all, delete-orphan'`

### Methods:

*   **`to_dict()`**:
    *   **Description:** Converts the Export object to a dictionary, suitable for JSON serialization. Includes a list of associated `export_files`.
    *   **Returns:** `dict` containing `exp_id`, `format`, `export_time`, `created_at`, `updated_at`, and `export_files`.
*   **`__repr__()`**:
    *   **Description:** Returns a string representation of the Export object.
    *   **Returns:** `str` in the format `<Export {exp_id}>`.

## ExportFile Model

**File:** `export_file.py`

**Table Name:** `export_files`

The `ExportFile` model represents a specific file generated as part of an export operation.

### Attributes:

*   **`export_file_id`** (Integer):
    *   **Description:** Unique identifier for the export file record.
    *   **Constraints:** Primary Key
*   **`document_id`** (Integer):
    *   **Description:** Foreign key linking to the `Document` that this export file is derived from.
    *   **Constraints:** Foreign Key (`documents.doc_id`), Not Null
*   **`exp_id`** (Integer):
    *   **Description:** Foreign key linking to the parent `Export` record.
    *   **Constraints:** Foreign Key (`exports.exp_id`), Not Null
*   **`file_path`** (String(500)):
    *   **Description:** The path to the generated export file on the server.
    *   **Constraints:** Not Null
*   **`created_at`** (DateTime):
    *   **Description:** Timestamp when the export file record was created.
    *   **Constraints:** Default (current UTC time)
*   **`updated_at`** (DateTime):
    *   **Description:** Timestamp when the export file record was last updated.
    *   **Constraints:** Default (current UTC time), On Update (current UTC time)

### Methods:

*   **`to_dict()`**:
    *   **Description:** Converts the ExportFile object to a dictionary, suitable for JSON serialization.
    *   **Returns:** `dict` containing `export_file_id`, `document_id`, `exp_id`, `file_path`, `created_at`, and `updated_at`.
*   **`__repr__()`**:
    *   **Description:** Returns a string representation of the ExportFile object.
    *   **Returns:** `str` in the format `<ExportFile {export_file_id}>`.

## FieldOption Model

**File:** `field_option.py`

**Table Name:** `field_options`

The `FieldOption` model stores predefined options for `SELECT` type template fields, often used for dropdowns or controlled vocabularies.

### Attributes:

*   **`options_id`** (Integer):
    *   **Description:** Unique identifier for the field option.
    *   **Constraints:** Primary Key
*   **`field_id`** (Integer):
    *   **Description:** Foreign key linking to the `TemplateField` this option belongs to.
    *   **Constraints:** Foreign Key (`template_fields.field_id`), Not Null
*   **`option_value`** (String(100)):
    *   **Description:** The actual value associated with the option (e.g., a code, an ID).
    *   **Constraints:** Not Null
*   **`option_label`** (String(100)):
    *   **Description:** The human-readable label for the option (e.g., "Approved", "Pending").
    *   **Constraints:** Not Null
*   **`created_at`** (DateTime):
    *   **Description:** Timestamp when the option was created.
    *   **Constraints:** Default (current UTC time)
*   **`updated_at`** (DateTime):
    *   **Description:** Timestamp when the option was last updated.
    *   **Constraints:** Default (current UTC time), On Update (current UTC time)

### Methods:

*   **`to_dict()`**:
    *   **Description:** Converts the FieldOption object to a dictionary, suitable for JSON serialization.
    *   **Returns:** `dict` containing `options_id`, `field_id`, `option_value`, `option_label`, `created_at`, and `updated_at`.
*   **`__repr__()`**:
    *   **Description:** Returns a string representation of the FieldOption object.
    *   **Returns:** `str` in the format `<FieldOption {option_label}>`.

## OCRData Model

**File:** `ocr_data.py`

**Table Name:** `ocr_data`

The `OCRData` model stores the extracted data for individual fields from a document after OCR processing.

### Attributes:

*   **`ocr_id`** (Integer):
    *   **Description:** Unique identifier for the OCR data record.
    *   **Constraints:** Primary Key
*   **`document_id`** (Integer):
    *   **Description:** Foreign key linking to the `Document` from which this data was extracted.
    *   **Constraints:** Foreign Key (`documents.doc_id`), Not Null
*   **`field_id`** (Integer):
    *   **Description:** Foreign key linking to the `TemplateField` definition for this extracted data.
    *   **Constraints:** Foreign Key (`template_fields.field_id`), Not Null
*   **`predicted_value`** (Text):
    *   **Description:** The value extracted by the OCR engine.
    *   **Constraints:** Nullable
*   **`actual_value`** (Text):
    *   **Description:** The corrected or verified value, if different from `predicted_value`.
    *   **Constraints:** Nullable
*   **`confidence`** (Float):
    *   **Description:** The confidence score of the OCR prediction.
    *   **Constraints:** Nullable
*   **`created_at`** (DateTime):
    *   **Description:** Timestamp when the OCR data record was created.
    *   **Constraints:** Default (current UTC time)
*   **`updated_at`** (DateTime):
    *   **Description:** Timestamp when the OCR data record was last updated.
    *   **Constraints:** Default (current UTC time), On Update (current UTC time)

### Methods:

*   **`to_dict()`**:
    *   **Description:** Converts the OCRData object to a dictionary, suitable for JSON serialization.
    *   **Returns:** `dict` containing `ocr_id`, `document_id`, `field_id`, `predicted_value`, `actual_value`, `confidence`, `created_at`, and `updated_at`.
*   **`__repr__()`**:
    *   **Description:** Returns a string representation of the OCRData object.
    *   **Returns:** `str` in the format `<OCRData {ocr_id}>`.

## OCRLineItem Model

**File:** `ocr_line_item.py`

**Table Name:** `ocr_line_items`

The `OCRLineItem` model represents a single row within a table extracted from a document by OCR.

### Attributes:

*   **`ocr_items_id`** (Integer):
    *   **Description:** Unique identifier for the OCR line item record.
    *   **Constraints:** Primary Key
*   **`document_id`** (Integer):
    *   **Description:** Foreign key linking to the `Document` this line item belongs to.
    *   **Constraints:** Foreign Key (`documents.doc_id`), Not Null
*   **`field_id`** (Integer):
    *   **Description:** Foreign key linking to the `TemplateField` (of type TABLE) that this line item is part of.
    *   **Constraints:** Foreign Key (`template_fields.field_id`), Not Null
*   **`row_index`** (Integer):
    *   **Description:** The 0-based index of the row within the table.
    *   **Constraints:** Not Null
*   **`created_at`** (DateTime):
    *   **Description:** Timestamp when the line item record was created.
    *   **Constraints:** Default (current UTC time)
*   **`updated_at`** (DateTime):
    *   **Description:** Timestamp when the line item record was last updated.
    *   **Constraints:** Default (current UTC time), On Update (current UTC time)

### Relationships:

*   **`ocr_line_item_values`**: One-to-Many relationship with `OCRLineItemValue` model. Stores the individual cell values for this row.
    *   `backref='ocr_line_item'`
    *   `lazy='dynamic'`
    *   `cascade='all, delete-orphan'`

### Methods:

*   **`to_dict()`**:
    *   **Description:** Converts the OCRLineItem object to a dictionary, suitable for JSON serialization. Includes a list of associated `ocr_line_item_values`.
    *   **Returns:** `dict` containing `ocr_items_id`, `document_id`, `field_id`, `row_index`, `created_at`, `updated_at`, and `ocr_line_item_values`.
*   **`__repr__()`**:
    *   **Description:** Returns a string representation of the OCRLineItem object.
    *   **Returns:** `str` in the format `<OCRLineItem {ocr_items_id}>`.

## OCRLineItemValue Model

**File:** `ocr_line_item_value.py`

**Table Name:** `ocr_line_item_values`

The `OCRLineItemValue` model stores the extracted data for a single cell within an OCR line item (i.e., a column value for a specific row in a table).

### Attributes:

*   **`ocr_items_value_id`** (Integer):
    *   **Description:** Unique identifier for the OCR line item value record.
    *   **Constraints:** Primary Key
*   **`ocr_items_id`** (Integer):
    *   **Description:** Foreign key linking to the parent `OCRLineItem` (the row).
    *   **Constraints:** Foreign Key (`ocr_line_items.ocr_items_id`), Not Null
*   **`sub_temp_field_id`** (Integer):
    *   **Description:** Foreign key linking to the `SubTemplateField` definition for this column.
    *   **Constraints:** Foreign Key (`sub_template_fields.sub_temp_field_id`), Not Null
*   **`predicted_value`** (Text):
    *   **Description:** The value extracted by the OCR engine for this cell.
    *   **Constraints:** Nullable
*   **`actual_value`** (Text):
    *   **Description:** The corrected or verified value for this cell, if different from `predicted_value`.
    *   **Constraints:** Nullable
*   **`confidence`** (Float):
    *   **Description:** The confidence score of the OCR prediction for this cell.
    *   **Constraints:** Nullable
*   **`created_at`** (DateTime):
    *   **Description:** Timestamp when the record was created.
    *   **Constraints:** Default (current UTC time)
*   **`updated_at`** (DateTime):
    *   **Description:** Timestamp when the record was last updated.
    *   **Constraints:** Default (current UTC time), On Update (current UTC time)

### Methods:

*   **`to_dict()`**:
    *   **Description:** Converts the OCRLineItemValue object to a dictionary, suitable for JSON serialization.
    *   **Returns:** `dict` containing `ocr_items_value_id`, `ocr_items_id`, `sub_temp_field_id`, `predicted_value`, `actual_value`, `confidence`, `created_at`, and `updated_at`.
*   **`__repr__()`**:
    *   **Description:** Returns a string representation of the OCRLineItemValue object.
    *   **Returns:** `str` in the format `<OCRLineItemValue {ocr_items_value_id}>`.

## SubTemplateField Model

**File:** `sub_template_field.py`

**Table Name:** `sub_template_fields`

The `SubTemplateField` model defines a column within a `TABLE` type `TemplateField`.

### Attributes:

*   **`sub_temp_field_id`** (Integer):
    *   **Description:** Unique identifier for the sub-template field.
    *   **Constraints:** Primary Key
*   **`field_id`** (Integer):
    *   **Description:** Foreign key linking to the parent `TemplateField` (the table).
    *   **Constraints:** Foreign Key (`template_fields.field_id`), Not Null
*   **`field_name`** (Enum):
    *   **Description:** The name of the sub-field (e.g., "ItemDescription", "Quantity").
    *   **Constraints:** Not Null
*   **`data_type`** (Enum):
    *   **Description:** The data type of the sub-field (e.g., "STRING", "INTEGER", "FLOAT", "SELECT").
    *   **Constraints:** Not Null
*   **`ai_instructions`** (Text):
    *   **Description:** Specific AI instructions for extracting this sub-field.
    *   **Constraints:** Nullable
*   **`created_at`** (DateTime):
    *   **Description:** Timestamp when the sub-field was created.
    *   **Constraints:** Default (current UTC time)
*   **`updated_at`** (DateTime):
    *   **Description:** Timestamp when the sub-field was last updated.
    *   **Constraints:** Default (current UTC time), On Update (current UTC time)

### Relationships:

*   **`ocr_line_item_values`**: One-to-Many relationship with `OCRLineItemValue` model. Stores the extracted values for this sub-field across different rows.
    *   `backref='sub_template_field'`
    *   `lazy='dynamic'`
    *   `cascade='all, delete-orphan'`
*   **`sub_field_options`**: One-to-Many relationship with `SubTemplateFieldOption` model. Stores predefined options for `SELECT` type sub-fields.
    *   `backref='sub_template_field'`
    *   `lazy='dynamic'`
    *   `cascade='all, delete-orphan'`

### Methods:

*   **`to_dict()`**:
    *   **Description:** Converts the SubTemplateField object to a dictionary, suitable for JSON serialization. Includes a list of associated `sub_field_options`.
    *   **Returns:** `dict` containing `sub_temp_field_id`, `field_id`, `field_name`, `data_type`, `ai_instructions`, `created_at`, `updated_at`, and `sub_field_options`.
*   **`__repr__()`**:
    *   **Description:** Returns a string representation of the SubTemplateField object.
    *   **Returns:** `str` in the format `<SubTemplateField {field_name}>`.

## SubTemplateFieldOption Model

**File:** `sub_template_field_option.py`

**Table Name:** `sub_template_field_options`

The `SubTemplateFieldOption` model stores predefined options for `SELECT` type sub-template fields (i.e., options for columns within a table).

### Attributes:

*   **`sub_options_id`** (Integer):
    *   **Description:** Unique identifier for the sub-template field option.
    *   **Constraints:** Primary Key
*   **`sub_temp_field_id`** (Integer):
    *   **Description:** Foreign key linking to the `SubTemplateField` this option belongs to.
    *   **Constraints:** Foreign Key (`sub_template_fields.sub_temp_field_id`), Not Null
*   **`option_value`** (String(100)):
    *   **Description:** The actual value associated with the option.
    *   **Constraints:** Not Null
*   **`option_label`** (String(100)):
    *   **Description:** The human-readable label for the option.
    *   **Constraints:** Not Null
*   **`created_at`** (DateTime):
    *   **Description:** Timestamp when the option was created.
    *   **Constraints:** Default (current UTC time)
*   **`updated_at`** (DateTime):
    *   **Description:** Timestamp when the option was last updated.
    *   **Constraints:** Default (current UTC time), On Update (current UTC time)

### Methods:

*   **`to_dict()`**:
    *   **Description:** Converts the SubTemplateFieldOption object to a dictionary, suitable for JSON serialization.
    *   **Returns:** `dict` containing `sub_options_id`, `sub_temp_field_id`, `option_value`, `option_label`, `created_at`, and `updated_at`.
*   **`__repr__()`**:
    *   **Description:** Returns a string representation of the SubTemplateFieldOption object.
    *   **Returns:** `str` in the format `<SubTemplateFieldOption {option_label}>`.

## TemplateField Model

**File:** `template_field.py`

**Table Name:** `template_fields`

The `TemplateField` model defines a specific field that needs to be extracted from a document using OCR, as part of a larger `Template`.

### Attributes:

*   **`field_id`** (Integer):
    *   **Description:** Unique identifier for the template field.
    *   **Constraints:** Primary Key
*   **`template_id`** (Integer):
    *   **Description:** Foreign key linking to the parent `Template`.
    *   **Constraints:** Foreign Key (`templates.temp_id`), Not Null
*   **`field_name`** (Enum):
    *   **Description:** The name of the field (e.g., "InvoiceNumber", "TotalAmount", "LineItems").
    *   **Constraints:** Not Null
*   **`field_order`** (Integer):
    *   **Description:** The display order of the field within the template.
    *   **Constraints:** Not Null
*   **`field_type`** (Enum):
    *   **Description:** The type of data this field represents (e.g., "TEXT", "NUMBER", "DATE", "TABLE", "SELECT").
    *   **Constraints:** Not Null
*   **`ai_instructions`** (Text):
    *   **Description:** Specific AI instructions for extracting this field.
    *   **Constraints:** Nullable
*   **`created_at`** (DateTime):
    *   **Description:** Timestamp when the field was created.
    *   **Constraints:** Default (current UTC time)
*   **`updated_at`** (DateTime):
    *   **Description:** Timestamp when the field was last updated.
    *   **Constraints:** Default (current UTC time), On Update (current UTC time)

### Relationships:

*   **`sub_template_fields`**: One-to-Many relationship with `SubTemplateField` model. Used if `field_type` is `TABLE` to define columns.
    *   `backref='template_field'`
    *   `lazy='dynamic'`
    *   `cascade='all, delete-orphan'`
*   **`field_options`**: One-to-Many relationship with `FieldOption` model. Used if `field_type` is `SELECT` to define predefined options.
    *   `backref='template_field'`
    *   `lazy='dynamic'`
    *   `cascade='all, delete-orphan'`
*   **`ocr_data`**: One-to-Many relationship with `OCRData` model. Stores the extracted OCR data for this field.
    *   `backref='template_field'`
    *   `lazy='dynamic'`
    *   `cascade='all, delete-orphan'`
*   **`ocr_line_items`**: One-to-Many relationship with `OCRLineItem` model. Stores the extracted line items if `field_type` is `TABLE`.
    *   `backref='template_field'`
    *   `lazy='dynamic'`
    *   `cascade='all, delete-orphan'`

### Methods:

*   **`to_dict()`**:
    *   **Description:** Converts the TemplateField object to a dictionary, suitable for JSON serialization. Includes lists of associated `sub_template_fields` and `field_options`.
    *   **Returns:** `dict` containing `field_id`, `template_id`, `field_name`, `field_order`, `field_type`, `ai_instructions`, `created_at`, `updated_at`, `sub_template_fields`, and `field_options`.
*   **`__repr__()`**:
    *   **Description:** Returns a string representation of the TemplateField object.
    *   **Returns:** `str` in the format `<TemplateField {field_name}>`.

## Template Model

**File:** `template.py`

**Table Name:** `templates`

The `Template` model defines a reusable structure for OCR processing, specifying which fields to extract from documents.

### Attributes:

*   **`temp_id`** (Integer):
    *   **Description:** Unique identifier for the template.
    *   **Constraints:** Primary Key
*   **`user_id`** (Integer):
    *   **Description:** Foreign key linking to the `User` who created the template.
    *   **Constraints:** Foreign Key (`users.user_id`), Not Null
*   **`name`** (String(100)):
    *   **Description:** The name of the template.
    *   **Constraints:** Not Null
*   **`description`** (Text):
    *   **Description:** A detailed description of the template's purpose.
    *   **Constraints:** Nullable
*   **`ai_instructions`** (Text):
    *   **Description:** General AI instructions for processing documents with this template.
    *   **Constraints:** Nullable
*   **`created_at`** (DateTime):
    *   **Description:** Timestamp when the template was created.
    *   **Constraints:** Default (current UTC time)
*   **`updated_at`** (DateTime):
    *   **Description:** Timestamp when the template was last updated.
    *   **Constraints:** Default (current UTC time), On Update (current UTC time)

### Relationships:

*   **`template_fields`**: One-to-Many relationship with `TemplateField` model. Defines the fields to be extracted by this template.
    *   `backref='template'`
    *   `lazy='dynamic'`
    *   `cascade='all, delete-orphan'`

### Methods:

*   **`to_dict()`**:
    *   **Description:** Converts the Template object to a dictionary, suitable for JSON serialization. Includes a list of associated `template_fields`.
    *   **Returns:** `dict` containing `temp_id`, `user_id`, `name`, `description`, `ai_instructions`, `created_at`, `updated_at`, and `template_fields`.
*   **`__repr__()`**:
    *   **Description:** Returns a string representation of the Template object.
    *   **Returns:** `str` in the format `<Template {name}>`.