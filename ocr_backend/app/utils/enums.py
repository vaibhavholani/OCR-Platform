from enum import Enum

class DocumentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"

class FieldType(Enum):
    TEXT = "text"
    SELECT = "select"
    TABLE = "table"
    NUMBER = "number"
    DATE = "date"
    EMAIL = "email"

class DataType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"
    BOOLEAN = "boolean"

class ExportFormat(Enum):
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"

class FieldName(Enum):
    INVOICE_NUMBER = "invoice_number"
    INVOICE_DATE = "invoice_date"
    DUE_DATE = "due_date"
    VENDOR_NAME = "vendor_name"
    VENDOR_ADDRESS = "vendor_address"
    CUSTOMER_NAME = "customer_name"
    CUSTOMER_ADDRESS = "customer_address"
    SUBTOTAL = "subtotal"
    TAX_AMOUNT = "tax_amount"
    TOTAL_AMOUNT = "total_amount"
    ITEM_DESCRIPTION = "item_description"
    QUANTITY = "quantity"
    UNIT_PRICE = "unit_price"
    LINE_TOTAL = "line_total" 