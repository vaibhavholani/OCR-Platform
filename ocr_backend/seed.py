#!/usr/bin/env python3
"""
Seed script to populate the OCR Platform database with sample data.
Run this script to initialize the database with test data.
"""

from app import create_app, db
from app.models import (
    User, Document, Template, TemplateField, SubTemplateField, 
    FieldOption, OCRData, OCRLineItem, OCRLineItemValue, Export, ExportFile
)
from app.utils.enums import (
    DocumentStatus, FieldType, FieldName, DataType, ExportFormat
)

def seed_database():
    """Seed the database with sample data"""
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        print("Creating sample data...")
        
        # Create users
        user1 = User(
            name="John Doe",
            email="john@example.com"
        )
        user1.set_password("password123")
        
        user2 = User(
            name="Jane Smith", 
            email="jane@example.com"
        )
        user2.set_password("password123")
        
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Create templates
        template1 = Template(
            user_id=user1.user_id,
            name="Invoice Template",
            description="Standard invoice extraction template",
            ai_instructions="Extract invoice number, date, vendor, amounts, and line items"
        )
        
        template2 = Template(
            user_id=user2.user_id,
            name="Receipt Template", 
            description="Receipt data extraction template",
            ai_instructions="Extract receipt date, vendor, total amount, and items"
        )
        
        db.session.add_all([template1, template2])
        db.session.commit()
        
        # Create template fields
        fields_data = [
            # Invoice template fields
            (template1.temp_id, FieldName.INVOICE_NUMBER, 1, FieldType.TEXT),
            (template1.temp_id, FieldName.INVOICE_DATE, 2, FieldType.DATE),
            (template1.temp_id, FieldName.VENDOR_NAME, 3, FieldType.TEXT),
            (template1.temp_id, FieldName.TOTAL_AMOUNT, 4, FieldType.NUMBER),
            (template1.temp_id, FieldName.ITEM_DESCRIPTION, 5, FieldType.TABLE),
            
            # Receipt template fields
            (template2.temp_id, FieldName.VENDOR_NAME, 1, FieldType.TEXT),
            (template2.temp_id, FieldName.INVOICE_DATE, 2, FieldType.DATE),
            (template2.temp_id, FieldName.TOTAL_AMOUNT, 3, FieldType.NUMBER),
        ]
        
        template_fields = []
        for template_id, field_name, order, field_type in fields_data:
            field = TemplateField(
                template_id=template_id,
                field_name=field_name,
                field_order=order,
                field_type=field_type,
                ai_instructions=f"Extract {field_name.value.replace('_', ' ')}"
            )
            template_fields.append(field)
        
        db.session.add_all(template_fields)
        db.session.commit()
        
        # Create sub-template fields for table (line items)
        table_field = next(f for f in template_fields if f.field_name == FieldName.ITEM_DESCRIPTION)
        sub_fields = [
            (table_field.field_id, FieldName.ITEM_DESCRIPTION, DataType.STRING),
            (table_field.field_id, FieldName.QUANTITY, DataType.INTEGER),
            (table_field.field_id, FieldName.UNIT_PRICE, DataType.FLOAT),
            (table_field.field_id, FieldName.LINE_TOTAL, DataType.FLOAT),
        ]
        
        sub_template_fields = []
        for field_id, field_name, data_type in sub_fields:
            sub_field = SubTemplateField(
                field_id=field_id,
                field_name=field_name,
                data_type=data_type,
                ai_instructions=f"Extract {field_name.value.replace('_', ' ')}"
            )
            sub_template_fields.append(sub_field)
        
        db.session.add_all(sub_template_fields)
        db.session.commit()
        
        # Create documents
        doc1 = Document(
            user_id=user1.user_id,
            file_path="/uploads/invoice_001.pdf",
            original_filename="invoice_001.pdf",
            status=DocumentStatus.PROCESSED
        )
        
        doc2 = Document(
            user_id=user2.user_id,
            file_path="/uploads/receipt_001.pdf", 
            original_filename="receipt_001.pdf",
            status=DocumentStatus.PROCESSED
        )
        
        db.session.add_all([doc1, doc2])
        db.session.commit()
        
        # Create OCR data
        ocr_data = []
        for doc in [doc1, doc2]:
            for field in template_fields:
                if field.template_id == doc.user_id:  # Simple mapping
                    ocr_data.append(OCRData(
                        document_id=doc.doc_id,
                        field_id=field.field_id,
                        predicted_value=f"Sample {field.field_name.value}",
                        actual_value=f"Actual {field.field_name.value}",
                        confidence=0.85
                    ))
        
        db.session.add_all(ocr_data)
        db.session.commit()
        
        # Create line items for invoice
        line_item = OCRLineItem(
            document_id=doc1.doc_id,
            field_id=table_field.field_id,
            row_index=1
        )
        db.session.add(line_item)
        db.session.commit()
        
        # Create line item values
        line_values = []
        for sub_field in sub_template_fields:
            line_values.append(OCRLineItemValue(
                ocr_items_id=line_item.ocr_items_id,
                sub_temp_field_id=sub_field.sub_temp_field_id,
                predicted_value=f"Sample {sub_field.field_name.value}",
                actual_value=f"Actual {sub_field.field_name.value}",
                confidence=0.90
            ))
        
        db.session.add_all(line_values)
        db.session.commit()
        
        # Create export
        export = Export(format=ExportFormat.PDF)
        db.session.add(export)
        db.session.commit()
        
        # Create export file
        export_file = ExportFile(
            document_id=doc1.doc_id,
            exp_id=export.exp_id,
            file_path="/exports/invoice_001_export.pdf"
        )
        db.session.add(export_file)
        db.session.commit()
        
        print("✅ Database seeded successfully!")
        print(f"Created: {User.query.count()} users")
        print(f"Created: {Template.query.count()} templates") 
        print(f"Created: {Document.query.count()} documents")
        print(f"Created: {OCRData.query.count()} OCR data entries")
        print(f"Created: {Export.query.count()} exports")

if __name__ == "__main__":
    seed_database() 