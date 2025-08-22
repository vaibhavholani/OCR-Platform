#!/usr/bin/env python3

"""
Test script to demonstrate the auto ledger refresh functionality during document processing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import TemplateField, Template, FieldOption, Document
from app.utils.enums import FieldType, FieldName, DocumentStatus
from app.tally import auto_load_tally_options, TallyFieldOptionsError

def test_auto_refresh_in_process():
    """Test that auto refresh works for SELECT fields during document processing"""
    
    app = create_app()
    
    with app.app_context():
        print("=== Testing Auto Refresh During Document Processing ===")
        print()
        
        # Find a template with Unit_of_measurement SELECT field
        unit_field = TemplateField.query.filter_by(
            field_name=FieldName.UNIT_OF_MEASUREMENT,
            field_type=FieldType.SELECT
        ).first()
        
        if not unit_field:
            print("No Unit_of_measurement SELECT field found.")
            return
        
        print(f"Found unit field: ID {unit_field.field_id} in template {unit_field.template_id}")
        
        # Clear existing options to simulate first-time load
        FieldOption.query.filter_by(field_id=unit_field.field_id).delete()
        db.session.commit()
        
        print("Cleared existing options.")
        
        # Simulate the refresh that happens during document processing
        print("Simulating auto refresh during document processing...")
        
        try:
            result = auto_load_tally_options(unit_field.field_id, clear_existing=True)
            print(f"✅ Auto refresh result: {result}")
            
            # Check loaded options
            options = FieldOption.query.filter_by(field_id=unit_field.field_id).all()
            print(f"✅ Loaded {len(options)} unit options:")
            for option in options:
                print(f"    - {option.option_label}")
                
            # Verify these are units, not ledgers
            if options:
                # Units should be short names
                avg_length = sum(len(opt.option_value) for opt in options) / len(options)
                print(f"✅ Average option length: {avg_length:.1f} characters")
                
                if avg_length < 15:  # Units are typically short
                    print("✅ SUCCESS: Field is loading units, not ledgers!")
                else:
                    print("❌ WARNING: Options might still be ledgers (long names)")
            
        except TallyFieldOptionsError as e:
            print(f"❌ Tally error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_auto_refresh_in_process()
