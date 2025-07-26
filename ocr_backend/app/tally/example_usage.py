"""
Tally Connector Library - Usage Examples

This file demonstrates how to use the Tally connector library with various scenarios.
Run this file to test the integration with your Tally setup.
"""

import logging
from datetime import datetime
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the Tally connector library
from . import (
    TallyConnector,
    TallyConfig,
    get_companies_list,
    get_ledgers_list,
    get_stock_items_list,
    get_vouchers_list,
    find_ledger_by_name,
    find_stock_item_by_name,
    create_ledger,
    create_stock_item,
    create_sales_voucher,
    create_purchase_voucher,
    ocr_data_to_voucher_format,
    validate_voucher_data,
    normalize_party_name,
    calculate_voucher_totals
)


def test_connection():
    """Test basic connection to Tally."""
    print("\n=== Testing Tally Connection ===")
    
    try:
        with TallyConnector() as tally:
            print(f"✓ Connected to Tally successfully")
            print(f"✓ Connection test: {tally.test_connection()}")
            print(f"✓ Version info: {tally.get_version_info()}")
            
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False
    
    return True


def test_data_retrieval():
    """Test data retrieval functions."""
    print("\n=== Testing Data Retrieval ===")
    
    try:
        with TallyConnector(version="latest") as tally:
            # Get companies
            companies = get_companies_list(tally)
            print(f"✓ Found {len(companies)} companies")
            if companies:
                print(f"  First company: {companies[0]['name']}")
            
            # Get ledgers
            ledgers = get_ledgers_list(tally)
            print(f"✓ Found {len(ledgers)} ledgers")
            if ledgers:
                print(f"  First ledger: {ledgers[0]['name']} ({ledgers[0]['group']})")
            
            # Get stock items
            stock_items = get_stock_items_list(tally)
            print(f"✓ Found {len(stock_items)} stock items")
            if stock_items:
                print(f"  First stock item: {stock_items[0]['name']}")
            
            # Get vouchers
            vouchers = get_vouchers_list(tally)
            print(f"✓ Found {len(vouchers)} vouchers")
            if vouchers:
                print(f"  First voucher: {vouchers[0]['voucher_type']} - {vouchers[0]['voucher_number']}")
            
    except Exception as e:
        print(f"✗ Data retrieval failed: {e}")
        return False
    
    return True


def test_search_functions():
    """Test search functions."""
    print("\n=== Testing Search Functions ===")
    
    try:
        with TallyConnector() as tally:
            # Search for a common ledger
            test_ledger_names = ["Cash", "Bank", "Sales Account", "Purchase Account"]
            
            for ledger_name in test_ledger_names:
                ledger = find_ledger_by_name(tally, ledger_name)
                if ledger:
                    print(f"✓ Found ledger: {ledger['name']}")
                    break
            else:
                print("✗ No common ledgers found")
            
            # Search for stock items
            test_item_names = ["Product", "Item", "Service"]
            
            for item_name in test_item_names:
                item = find_stock_item_by_name(tally, item_name)
                if item:
                    print(f"✓ Found stock item: {item['name']}")
                    break
            else:
                print("✗ No common stock items found")
            
    except Exception as e:
        print(f"✗ Search functions failed: {e}")
        return False
    
    return True


def test_data_creation():
    """Test data creation functions."""
    print("\n=== Testing Data Creation ===")
    
    try:
        with TallyConnector() as tally:
            # Test ledger creation
            ledger_data = {
                "name": "Test Customer OCR",
                "ledger_type": "customer",
                "email": "test@example.com",
                "mobile": "9876543210"
            }
            
            ledger_result = create_ledger(tally, ledger_data)
            if ledger_result['success']:
                print(f"✓ Created ledger: {ledger_result['ledger_name']}")
            else:
                print(f"✗ Ledger creation failed: {ledger_result['message']}")
            
    except Exception as e:
        print(f"✗ Data creation failed: {e}")
        return False
    
    return True


def test_voucher_creation():
    """Test voucher creation using low-level Tally model approach."""
    print("\n=== Testing Voucher Creation (Low-Level Model Approach) ===")
    
    try:
        with TallyConnector() as tally:
            # Access the voucher classes and converters from the session
            if not tally.session._vouchers_available:
                print("✗ Voucher functionality not available")
                return False
            
            # Import the required classes and types from the session's stored imports
            Voucher = tally.session._voucher_classes['Voucher']
            VoucherLedger = tally.session._voucher_classes['VoucherLedger']
            BillAllocations = tally.session._voucher_classes['BillAllocations']
            BillRefType = tally.session._voucher_classes['BillRefType']
            AllInventoryAllocations = tally.session._voucher_classes['AllInventoryAllocations']
            BatchAllocations = tally.session._voucher_classes['BatchAllocations']
            BaseVoucherLedger = tally.session._voucher_classes['BaseVoucherLedger']
            Action = tally.session._voucher_classes['Action']
            VoucherViewType = tally.session._voucher_classes['VoucherViewType']
            
            TallyDate = tally.session._tally_converters['TallyDate']
            TallyAmount = tally.session._tally_converters['TallyAmount']
            TallyQuantity = tally.session._tally_converters['TallyQuantity']
            TallyRate = tally.session._tally_converters['TallyRate']
            TallyYesNo = tally.session._tally_converters['TallyYesNo']
            
            DateTime = tally.session._system_types['DateTime']
            Decimal = tally.session._system_types['Decimal']
            List = tally.session._system_types['List']
            
            print("✓ Imported all required Tally model classes and converters")
            
            # ---------- Voucher shell ----------
            v = Voucher()
            v.PartyName = "Pradyum Corp."
            v.VoucherType = "Purchase"
            v.Date = TallyDate(DateTime(2025, 4, 1))
            v.EffectiveDate = v.Date
            v.View = VoucherViewType.InvoiceVoucherView
            v.IsInvoice = TallyYesNo(True)
            v.Action = Action.Create
            
            print("✓ Created voucher shell for Purchase voucher")
            
            # ---------- Party ledger (credit) ----------
            supp_ledger = VoucherLedger(v.PartyName, TallyAmount(Decimal(4.65)))
            supp_ledger.IsPartyLedger = TallyYesNo(True)
            
            bill = BillAllocations()
            bill.Name = "First Bill"
            bill.BillType = BillRefType.NewRef
            bill.Amount = TallyAmount(Decimal(4.65))
            
            supp_ledger.BillAllocations = List[BillAllocations]()
            supp_ledger.BillAllocations.Add(bill)
            
            print("✓ Created party ledger with bill allocations")
            
            # ---------- Stock entry (debit) ----------
            inv = AllInventoryAllocations()
            inv.StockItemName = "Best Product"
            inv.BilledQuantity = TallyQuantity(Decimal(1), "Nos")
            inv.ActualQuantity = TallyQuantity(Decimal(1), "Nos")
            inv.Rate = TallyRate(Decimal(4.65), "Nos")
            inv.Amount = TallyAmount(Decimal(-4.65))  # negative in purchase
            
            # batch
            batch = BatchAllocations()
            batch.GodownName = "Main Location"
            batch.BatchName = "Primary Batch"
            batch.BilledQuantity = inv.BilledQuantity
            batch.ActualQuantity = inv.ActualQuantity
            batch.Amount = inv.Amount
            
            inv.BatchAllocations = List[BatchAllocations]()
            inv.BatchAllocations.Add(batch)
            
            # ledger inside inventory (debit side)
            item_ledger = BaseVoucherLedger()
            item_ledger.LedgerName = "Imported Goods"
            item_ledger.Amount = inv.Amount  # -4.65
            
            inv.Ledgers = List[BaseVoucherLedger]()
            inv.Ledgers.Add(item_ledger)
            
            print("✓ Created inventory allocation with batch and ledger details")
            
            # ---------- Assemble voucher ----------
            v.Ledgers = List[VoucherLedger]()
            v.Ledgers.Add(supp_ledger)
            
            v.InventoryAllocations = List[AllInventoryAllocations]()
            v.InventoryAllocations.Add(inv)
            
            print("✓ Assembled complete voucher structure")
            
            # ---------- Generate XML and post to Tally ----------
            # print("✓ Generated voucher XML:")
            # print(v.GetXML())
            
            # Post the voucher to Tally
            response = tally.session._svc.PostVoucherAsync(v).Result.Response
            print(f"✓ Posted voucher to Tally - Response: {response}")
            
            print("✓ Successfully created purchase voucher using low-level model approach")
            
    except Exception as e:
        print(f"✗ Voucher creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_ocr_data_conversion():
    """Test OCR data to voucher format conversion."""
    print("\n=== Testing OCR Data Conversion ===")
    
    try:
        # Sample OCR data structure
        sample_ocr_data = {
            "party_name": "ABC Corporation Pvt Ltd",
            "invoice_date": "2025-01-15",
            "invoice_number": "INV-2025-001",
            "items": [
                {
                    "product_name": "Widget A",
                    "quantity": 10,
                    "rate": 50.0,
                    "amount": 500.0,
                    "unit": "Nos"
                },
                {
                    "product_name": "Widget B", 
                    "quantity": 5,
                    "rate": 100.0,
                    "amount": 500.0,
                    "unit": "Nos"
                }
            ],
            "total_amount": 1000.0,
            "narration": "Sale of widgets as per order"
        }
        
        # Convert OCR data to voucher format
        voucher_data = ocr_data_to_voucher_format(sample_ocr_data, "invoice")
        print("✓ OCR data converted to voucher format")
        print(f"  Party: {voucher_data['party_name']}")
        print(f"  Date: {voucher_data['date']}")
        print(f"  Items: {len(voucher_data['items'])}")
        print(f"  Voucher Type: {voucher_data['voucher_type']}")
        
        # Test party name normalization
        normalized_name = normalize_party_name("M/s ABC Corporation Pvt Ltd")
        print(f"✓ Normalized party name: {normalized_name}")
        
        # Validate converted data
        is_valid, errors = validate_voucher_data(voucher_data)
        if is_valid:
            print("✓ Converted voucher data is valid")
        else:
            print(f"✗ Validation errors: {', '.join(errors)}")
        
    except Exception as e:
        print(f"✗ OCR data conversion failed: {e}")
        return False
    
    return True


def add_stock_item_if_not_exists(item_name: str, stock_group: str = "Primary"):
    """
    Sample function to add a stock item if it doesn't already exist.
    
    This function:
    1. First checks if the stock item exists using TallyConnector(version="latest")
    2. If not found, creates the item using TallyConnector() with base_unit "PCS"
    
    Args:
        item_name (str): Name of the stock item to check/create
        stock_group (str): Stock group for the item (default: "Primary")
    
    Returns:
        dict: Result of the operation with success status and message
    """
    print(f"\n=== Adding Stock Item: {item_name} ===")
    
    try:
        # Step 1: Check if stock item exists using latest version
        print("🔍 Checking if stock item exists...")
        with TallyConnector(version="latest") as tally_latest:
            existing_item = find_stock_item_by_name(tally_latest, item_name)

            if existing_item:
                print(f"✓ Stock item '{item_name}' already exists")
                return {
                    'success': True,
                    'already_exists': True,
                    'item_name': item_name,
                    'message': f"Stock item '{item_name}' already exists in Tally"
                }
        
        # Step 2: Create stock item using default version if it doesn't exist
        print(f"📦 Stock item '{item_name}' not found. Creating new stock item...")
        with TallyConnector() as tally_default:
            item_data = {
                "name": item_name,
                "base_unit": "PCS",
                "stock_group": stock_group
            }
            
            create_result = create_stock_item(tally_default, item_data)
            
            if create_result['success']:
                print(f"✓ Successfully created stock item: {create_result['item_name']}")
                return {
                    'success': True,
                    'already_exists': False,
                    'item_name': create_result['item_name'],
                    'message': f"Successfully created stock item '{item_name}' with base unit PCS"
                }
            else:
                print(f"✗ Failed to create stock item: {create_result['message']}")
                return {
                    'success': False,
                    'already_exists': False,
                    'item_name': item_name,
                    'message': f"Failed to create stock item: {create_result['message']}"
                }
    
    except Exception as e:
        error_msg = f"Error in add_stock_item_if_not_exists: {e}"
        print(f"✗ {error_msg}")
        return {
            'success': False,
            'already_exists': False,
            'item_name': item_name,
            'message': error_msg
        }


def test_add_stock_item_sample():
    """Test the add_stock_item_if_not_exists function."""
    print("\n=== Testing Add Stock Item Sample Function ===")
    
    try:
        # Test with a sample item name
        test_item_name = "Sample Widget PCS"
        result = add_stock_item_if_not_exists(test_item_name, "Primary")
        
        if result['success']:
            if result['already_exists']:
                print(f"✓ Function correctly identified existing item: {test_item_name}")
            else:
                print(f"✓ Function successfully created new item: {test_item_name}")
        else:
            print(f"✗ Function failed: {result['message']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def run_all_tests():
    """Run all test functions."""
    print("🚀 Starting Tally Connector Library Tests")
    print("=" * 50)
    
    tests = [
        ("Connection Test", test_connection),
        ("Data Retrieval Test", test_data_retrieval),
        # ("Voucher Creation Test", test_voucher_creation),
        ("Add Stock Item Sample Test", test_add_stock_item_sample),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Tally connector library is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")


if __name__ == "__main__":
    run_all_tests()
