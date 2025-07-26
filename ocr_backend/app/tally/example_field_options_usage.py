"""
Example Usage of Tally Field Options Helper Functions

This file demonstrates how to use the helper functions to load Tally data
as options for SELECT type template fields.
"""

from app.tally import (
    auto_load_tally_options,
    load_companies_as_options,
    load_ledgers_as_options,
    load_stock_items_as_options,
    load_customer_options,
    load_vendor_options,
    get_field_options_summary,
    refresh_field_options,
    TallyFieldOptionsError
)

def example_auto_load_options():
    """
    Example: Automatically detect and load appropriate options based on field name
    """
    field_id = 123  # Replace with actual field ID
    
    try:
        result = auto_load_tally_options(field_id)
        print(f"✅ Auto-loaded {result['options_count']} options for field {field_id}")
        print(f"   Message: {result['message']}")
        return result
    except TallyFieldOptionsError as e:
        print(f"❌ Error: {e}")
        return None

def example_load_specific_data_types():
    """
    Example: Load specific types of Tally data
    """
    vendor_field_id = 124    # Replace with actual field ID for vendor selection
    customer_field_id = 125  # Replace with actual field ID for customer selection
    product_field_id = 126   # Replace with actual field ID for product selection
    
    try:
        # Load vendor ledgers (Sundry Creditors)
        vendor_result = load_vendor_options(vendor_field_id)
        print(f"✅ Loaded {vendor_result['options_count']} vendor options")
        
        # Load customer ledgers (Sundry Debtors)
        customer_result = load_customer_options(customer_field_id)
        print(f"✅ Loaded {customer_result['options_count']} customer options")
        
        # Load all stock items
        product_result = load_stock_items_as_options(product_field_id)
        print(f"✅ Loaded {product_result['options_count']} product options")
        
        return {
            'vendors': vendor_result,
            'customers': customer_result,
            'products': product_result
        }
        
    except TallyFieldOptionsError as e:
        print(f"❌ Error loading specific data types: {e}")
        return None

def example_load_with_filters():
    """
    Example: Load data with specific filters
    """
    field_id = 127  # Replace with actual field ID
    
    try:
        # Load only ledgers from "Bank Accounts" group
        result = load_ledgers_as_options(
            field_id=field_id,
            ledger_group="Bank Accounts",
            clear_existing=True
        )
        print(f"✅ Loaded {result['options_count']} bank account options")
        
        # Load stock items from "Finished Goods" group
        stock_result = load_stock_items_as_options(
            field_id=field_id,
            stock_group="Finished Goods"
        )
        print(f"✅ Loaded {stock_result['options_count']} finished goods options")
        
        return result
        
    except TallyFieldOptionsError as e:
        print(f"❌ Error loading with filters: {e}")
        return None

def example_get_field_summary():
    """
    Example: Get current options summary for a field
    """
    field_id = 123  # Replace with actual field ID
    
    try:
        summary = get_field_options_summary(field_id)
        
        if 'error' in summary:
            print(f"❌ Error: {summary['error']}")
            return None
            
        print(f"📊 Field Summary:")
        print(f"   Field ID: {summary['field_id']}")
        print(f"   Field Name: {summary['field_name']}")
        print(f"   Field Type: {summary['field_type']}")
        print(f"   Options Count: {summary['options_count']}")
        print(f"   Last Updated: {summary['last_updated']}")
        
        # Show first few options
        if summary['options']:
            print(f"   Sample Options:")
            for i, option in enumerate(summary['options'][:5]):
                print(f"     - {option['option_label']} ({option['option_value']})")
            if len(summary['options']) > 5:
                print(f"     ... and {len(summary['options']) - 5} more")
        
        return summary
        
    except Exception as e:
        print(f"❌ Error getting field summary: {e}")
        return None

def example_refresh_options():
    """
    Example: Refresh field options by reloading from Tally
    """
    field_id = 123  # Replace with actual field ID
    
    try:
        print(f"🔄 Refreshing options for field {field_id}...")
        result = refresh_field_options(field_id)
        print(f"✅ Refreshed {result['options_count']} options")
        return result
        
    except TallyFieldOptionsError as e:
        print(f"❌ Error refreshing options: {e}")
        return None

def example_api_usage():
    """
    Example: How to use the API endpoints
    """
    print("🌐 API Endpoints Usage Examples:")
    print()
    
    print("1. Auto-load options:")
    print("   POST /api/ocr/field/123/load_tally_options")
    print('   Body: {"data_type": "auto"}')
    print()
    
    print("2. Load specific data type:")
    print("   POST /api/ocr/field/123/load_tally_options")
    print('   Body: {"data_type": "customers"}')
    print()
    
    print("3. Load with filter:")
    print("   POST /api/ocr/field/123/load_tally_options")
    print('   Body: {"data_type": "ledgers", "group_filter": "Bank Accounts"}')
    print()
    
    print("4. Get field options summary:")
    print("   GET /api/ocr/field/123/options")
    print()
    
    print("5. Refresh options:")
    print("   POST /api/ocr/field/123/refresh_options")
    print()
    
    print("6. Load customers:")
    print("   POST /api/ocr/field/123/load_customers")
    print()
    
    print("7. Load vendors:")
    print("   POST /api/ocr/field/123/load_vendors")

if __name__ == "__main__":
    print("🚀 Tally Field Options Helper Examples")
    print("=" * 50)
    
    # Run examples (uncomment to test with actual field IDs)
    # example_auto_load_options()
    # example_load_specific_data_types()
    # example_load_with_filters()
    # example_get_field_summary()
    # example_refresh_options()
    
    # Show API usage examples
    example_api_usage() 