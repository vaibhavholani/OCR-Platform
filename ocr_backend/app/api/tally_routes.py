from flask import Blueprint, jsonify, request, current_app
from .. import db
from ..models import Document, OCRData, OCRLineItem, OCRLineItemValue, Template, TemplateField, SubTemplateField
from ..utils.enums import DocumentStatus, FieldType
from ..tally import (
    TallyConnector,
    get_companies_list,
    get_ledgers_list,
    get_stock_items_list,
    get_units_list,
    find_ledger_by_name,
    find_stock_item_by_name,
    find_unit_by_name,
    create_ledger,
    create_stock_item,
    create_simple_unit,
    create_compound_unit,
    update_unit,
    normalize_party_name,
    TallyConfig
)
import os
from datetime import datetime
from decimal import Decimal
from typing import Dict
import logging
import re

logger = logging.getLogger(__name__)

bp = Blueprint('tally', __name__, url_prefix='/api/tally')

def get_document_ocr_data(document_id):
    """
    Get OCR data for a document in the same format as document_routes
    Reuses the logic from document_routes.py
    """
    document = Document.query.get_or_404(document_id)
    
    # Get OCR data with field information (non-table fields)
    ocr_data = db.session.query(OCRData, TemplateField).join(
        TemplateField, OCRData.field_id == TemplateField.field_id
    ).filter(OCRData.document_id == document_id).all()
    
    # Format extracted data (text fields)
    extracted_data = {}
    for ocr, field in ocr_data:
        extracted_data[field.field_name.value] = ocr.predicted_value or ocr.actual_value
    
    # Get formatted table data
    table_data = reconstruct_table_data_from_db(document_id)
    
    return {
        'document_id': document_id,
        'status': document.status.value,
        'original_filename': document.original_filename,
        'processed_at': document.processed_at.isoformat() if document.processed_at else None,
        'extracted_data': extracted_data,
        'table_data': table_data
    }

def reconstruct_table_data_from_db(document_id):
    """
    Reconstruct table data from stored OCRLineItem and OCRLineItemValue records
    Reused from document_routes.py
    """
    # Get all table fields for line items in this document
    table_fields_query = db.session.query(TemplateField).join(
        OCRLineItem, TemplateField.field_id == OCRLineItem.field_id
    ).filter(
        OCRLineItem.document_id == document_id,
        TemplateField.field_type == FieldType.TABLE
    ).distinct().all()
    
    formatted_tables = {}
    
    for table_field in table_fields_query:
        # Get sub-template fields (columns)
        sub_fields = SubTemplateField.query.filter_by(field_id=table_field.field_id).all()
        
        # Get line items for this table field
        line_items = OCRLineItem.query.filter_by(
            document_id=document_id,
            field_id=table_field.field_id
        ).order_by(OCRLineItem.row_index).all()
        
        # Reconstruct rows
        rows = []
        for line_item in line_items:
            row_data = {}
            for value in line_item.ocr_line_item_values:
                if value.sub_template_field:
                    row_data[value.sub_template_field.field_name.value] = value.predicted_value or value.actual_value
            rows.append(row_data)
        
        # Format columns info
        columns = []
        for sub_field in sub_fields:
            columns.append({
                'name': sub_field.field_name.value,
                'data_type': sub_field.data_type.value,
                'sub_temp_field_id': sub_field.sub_temp_field_id
            })
        
        # Add to formatted tables
        formatted_tables[table_field.field_name.value] = {
            'field_id': table_field.field_id,
            'field_type': 'table',
            'columns': columns,
            'rows': rows,
            'row_count': len(rows)
        }
    
    return formatted_tables

def convert_ocr_to_tally_format(ocr_data):
    """
    Convert OCR data format to Tally voucher format
    Handles the specific structure provided by the user
    """
    try:
        # Extract vendor information
        extracted_data = ocr_data.get('extracted_data', {})
        table_data = ocr_data.get('table_data', {})
        
        # Get vendor name (party name)
        vendor_name = extracted_data.get('vendor_name', '')
        if not vendor_name:
            raise ValueError("Vendor name is required")
        
        # Normalize party name
        party_name = normalize_party_name(vendor_name)
        
        # Get invoice details
        invoice_number = extracted_data.get('invoice_number', '')
        vendor_address = extracted_data.get('vendor_address', '')
        
        # Extract line items from table data
        line_items = []
        
        # Find the table with items (commonly named 'item_description' or similar)
        item_table = None
        for table_name, table_info in table_data.items():
            if 'item_description' in table_name.lower() or 'item' in table_name.lower():
                item_table = table_info
                break
        
        if not item_table:
            # Try to get the first table
            if table_data:
                item_table = list(table_data.values())[0]
        
        if item_table and 'rows' in item_table:
            for row in item_table['rows']:
                try:
                    # Extract item details from row
                    item_description = re.sub(r'\s+', ' ', row.get('item_description', '').strip())

                    if not item_description:
                        continue
                    
                    quantity = float(row.get('quantity', '0') or '0')
                    unit_price = float(row.get('unit_price', '0') or '0')
                    line_total = float(row.get('line_total', '0') or '0')
                    
                    
                    # Calculate amount if not provided or inconsistent
                    calculated_amount = quantity * unit_price
                    amount = line_total if line_total > 0 else calculated_amount
                    
                    line_item = {
                        'stock_item': item_description,
                        'quantity': quantity,
                        'rate': unit_price,
                        'amount': amount,
                        'unit': TallyConfig.DEFAULT_UNIT,  # Default unit
                        'godown': TallyConfig.DEFAULT_GODOWN,
                        'batch': TallyConfig.DEFAULT_BATCH,
                        'purchase_ledger': TallyConfig.DEFAULT_PURCHASE_LEDGER
                    }
                    
                    line_items.append(line_item)
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to process line item: {e}")
                    continue
        
        # TODO: WARNING: This is a temporary fix to remove duplicates from line_items TILL THE FROTNEND IS FIXED.
        # Remove duplicates from line_items (it's a list of dictionaries)
        line_items = [dict(t) for t in {tuple(sorted(d.items())) for d in line_items}]

        total_amount = sum(item['amount'] for item in line_items)


        if not line_items:
            raise ValueError("No valid line items found in OCR data")

        
        # Create voucher data structure
        voucher_data = {
            'voucher_type': 'Purchase',
            'party_name': party_name,
            'date': '2025-04-01',  
            'voucher_number': invoice_number,
            'narration': f'Purchase from {party_name}' + (f' - Invoice {invoice_number}' if invoice_number else ''),
            'bill_ref': invoice_number,
            'items': line_items,
            'total_amount': total_amount,
            'vendor_address': vendor_address
        }
        
        return voucher_data
        
    except Exception as e:
        logger.error(f"Failed to convert OCR data to Tally format: {e}")
        raise ValueError(f"OCR to Tally conversion failed: {e}")

def ensure_stock_item_exists(item_name, stock_group="Primary", base_unit="PCS"):
    """
    Ensure stock item exists in Tally, create if it doesn't exist
    Returns the result of the operation
    """
    try:
        # Step 1: Check if stock item exists using latest version
        with TallyConnector(version="latest") as tally_latest:
            existing_item = find_stock_item_by_name(tally_latest, item_name)
            
            if existing_item:
                return {
                    'success': True,
                    'already_exists': True,
                    'item_name': item_name,
                    'message': f"Stock item '{item_name}' already exists in Tally"
                }
        
        # Step 2: Ensure the unit exists before creating stock item
        unit_result = ensure_unit_exists(base_unit)
        if not unit_result['success']:
            return {
                'success': False,
                'already_exists': False,
                'item_name': item_name,
                'message': f"Failed to ensure unit '{base_unit}' exists: {unit_result['message']}"
            }
        
        # Step 3: Create stock item using default version if it doesn't exist
        with TallyConnector() as tally_default:
            item_data = {
                "name": item_name,
                "base_unit": base_unit,
                "stock_group": stock_group
            }
            
            create_result = create_stock_item(tally_default, item_data)
            
            if create_result['success']:
                return {
                    'success': True,
                    'already_exists': False,
                    'item_name': create_result['item_name'],
                    'message': f"Successfully created stock item '{item_name}' with base unit {base_unit}"
                }
            else:
                return {
                    'success': False,
                    'already_exists': False,
                    'item_name': item_name,
                    'message': f"Failed to create stock item: {create_result['message']}"
                }
    
    except Exception as e:
        error_msg = f"Error in ensure_stock_item_exists: {e}"
        logger.error(error_msg)
        return {
            'success': False,
            'already_exists': False,
            'item_name': item_name,
            'message': error_msg
        }

def ensure_party_ledger_exists(party_name, ledger_group="Sundry Creditors"):
    """
    Ensure party ledger exists in Tally, create if it doesn't exist
    Returns the result of the operation
    """
    try:
        # Step 1: Check if ledger exists using latest version
        with TallyConnector(version="latest") as tally_latest:
            existing_ledger = find_ledger_by_name(tally_latest, party_name)
            
            if existing_ledger:
                return {
                    'success': True,
                    'already_exists': True,
                    'ledger_name': party_name,
                    'message': f"Party ledger '{party_name}' already exists in Tally"
                }
        
        # Step 2: Create ledger using default version if it doesn't exist
        with TallyConnector() as tally_default:
            ledger_data = {
                "name": party_name,
                "group": ledger_group,
                "ledger_type": "supplier",  # This will map to Sundry Creditors
                "alias": party_name
            }
            
            create_result = create_ledger(tally_default, ledger_data)
            
            if create_result['success']:
                return {
                    'success': True,
                    'already_exists': False,
                    'ledger_name': create_result['ledger_name'],
                    'message': f"Successfully created party ledger '{party_name}' as Sundry Creditor"
                }
            else:
                return {
                    'success': False,
                    'already_exists': False,
                    'ledger_name': party_name,
                    'message': f"Failed to create party ledger: {create_result['message']}"
                }
    
    except Exception as e:
        error_msg = f"Error in ensure_party_ledger_exists: {e}"
        logger.error(error_msg)
        return {
            'success': False,
            'already_exists': False,
            'ledger_name': party_name,
            'message': error_msg
        }

def ensure_unit_exists(unit_name: str, decimal_places: int = 0, unit_type: str = "simple") -> Dict:
    """
    Ensure unit exists in Tally, create if it doesn't exist
    Returns the result of the operation
    """
    try:
        # Step 1: Check if unit exists using legacy version
        with TallyConnector(version="legacy") as tally_latest:
            existing_unit = find_unit_by_name(tally_latest, unit_name)
            
            if existing_unit:
                return {
                    'success': True,
                    'already_exists': True,
                    'unit_name': unit_name,
                    'unit_type': 'simple' if existing_unit['is_simple_unit'] else 'compound',
                    'decimal_places': existing_unit['decimal_places'],
                    'message': f"Unit '{unit_name}' already exists in Tally"
                }
        
        # Step 2: Create unit using legacy version if it doesn't exist
        with TallyConnector(version="legacy") as tally_default:
            unit_data = {
                "name": unit_name,
                "decimal_places": decimal_places
            }
            
            # Import create_simple_unit function
            from ..tally.data_insertion import create_simple_unit
            create_result = create_simple_unit(tally_default, unit_data)
            
            if create_result['success']:
                return {
                    'success': True,
                    'already_exists': False,
                    'unit_name': create_result['unit_name'],
                    'unit_type': create_result['unit_type'],
                    'decimal_places': create_result['decimal_places'],
                    'message': f"Successfully created unit '{unit_name}' with {decimal_places} decimal places"
                }
            else:
                return {
                    'success': False,
                    'already_exists': False,
                    'unit_name': unit_name,
                    'message': f"Failed to create unit: {create_result.get('message', 'Unknown error')}"
                }
    
    except Exception as e:
        error_msg = f"Error in ensure_unit_exists: {e}"
        logger.error(error_msg)
        return {
            'success': False,
            'already_exists': False,
            'unit_name': unit_name,
            'message': error_msg
        }

def ensure_compound_unit_exists(unit_name: str, base_unit: str, conversion: float, decimal_places: int = 0) -> Dict:
    """
    Ensure compound unit exists in Tally, create if it doesn't exist
    Returns the result of the operation
    """
    try:
        # Step 1: Check if unit exists
        with TallyConnector(version="legacy") as tally_latest:
            existing_unit = find_unit_by_name(tally_latest, unit_name)
            
            if existing_unit:
                return {
                    'success': True,
                    'already_exists': True,
                    'unit_name': unit_name,
                    'unit_type': 'simple' if existing_unit['is_simple_unit'] else 'compound',
                    'base_unit': existing_unit.get('base_unit', ''),
                    'conversion': existing_unit.get('conversion', 1.0),
                    'decimal_places': existing_unit['decimal_places'],
                    'message': f"Compound unit '{unit_name}' already exists in Tally"
                }
        
        # Step 2: Ensure base unit exists first
        base_unit_result = ensure_unit_exists(base_unit)
        if not base_unit_result['success']:
            return {
                'success': False,
                'already_exists': False,
                'unit_name': unit_name,
                'message': f"Failed to ensure base unit '{base_unit}' exists: {base_unit_result['message']}"
            }
        
        # Step 3: Create compound unit
        with TallyConnector(version="legacy") as tally_default:
            unit_data = {
                "name": unit_name,
                "base_unit": base_unit,
                "conversion": conversion,
                "decimal_places": decimal_places
            }
            
            # Import create_compound_unit function
            from ..tally.data_insertion import create_compound_unit
            create_result = create_compound_unit(tally_default, unit_data)
            
            if create_result['success']:
                return {
                    'success': True,
                    'already_exists': False,
                    'unit_name': create_result['unit_name'],
                    'unit_type': create_result['unit_type'],
                    'base_unit': create_result['base_unit'],
                    'conversion': create_result['conversion'],
                    'decimal_places': create_result['decimal_places'],
                    'message': f"Successfully created compound unit '{unit_name}' = {conversion} {base_unit}"
                }
            else:
                return {
                    'success': False,
                    'already_exists': False,
                    'unit_name': unit_name,
                    'message': f"Failed to create compound unit: {create_result.get('message', 'Unknown error')}"
                }
    
    except Exception as e:
        error_msg = f"Error in ensure_compound_unit_exists: {e}"
        logger.error(error_msg)
        return {
            'success': False,
            'already_exists': False,
            'unit_name': unit_name,
            'message': error_msg
        }

def create_purchase_voucher_in_tally(voucher_data):
    """
    Create purchase voucher in Tally using low-level model approach
    Based on the example_usage.py implementation
    """
    try:
        with TallyConnector() as tally:
            # Access the voucher classes and converters from the session
            if not tally.session._vouchers_available:
                raise Exception("Voucher functionality not available")
            
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
            
            # Parse date
            voucher_date = datetime.strptime(voucher_data['date'], '%Y-%m-%d')
            
            # ---------- Voucher shell ----------
            v = Voucher()
            v.PartyName = voucher_data['party_name']
            v.VoucherType = "Purchase"
            v.Date = TallyDate(DateTime(voucher_date.year, voucher_date.month, voucher_date.day))
            v.EffectiveDate = v.Date
            v.View = VoucherViewType.InvoiceVoucherView
            v.IsInvoice = TallyYesNo(True)
            v.Action = Action.Create
            
            if voucher_data.get('narration'):
                v.Narration = voucher_data['narration']
            
            # ---------- Party ledger (credit) ----------
            total_amount = voucher_data['total_amount']
            supp_ledger = VoucherLedger(v.PartyName, TallyAmount(Decimal(total_amount)))
            supp_ledger.IsPartyLedger = TallyYesNo(True)
            
            # Bill allocations
            bill = BillAllocations()
            bill.Name = voucher_data.get('bill_ref', 'Bill')
            bill.BillType = BillRefType.NewRef
            bill.Amount = TallyAmount(Decimal(total_amount))
            
            supp_ledger.BillAllocations = List[BillAllocations]()
            supp_ledger.BillAllocations.Add(bill)
            
            # ---------- Initialize ledgers and inventory lists ----------
            v.Ledgers = List[VoucherLedger]()
            v.Ledgers.Add(supp_ledger)
            
            v.InventoryAllocations = List[AllInventoryAllocations]()
            
            # ---------- Process each line item ----------
            for item_data in voucher_data['items']:
                # Stock entry (debit)
                inv = AllInventoryAllocations()
                inv.StockItemName = item_data['stock_item']
                
                quantity = Decimal(item_data['quantity'])
                rate = Decimal(item_data['rate'])
                amount = Decimal(item_data['amount'])
                
                inv.BilledQuantity = TallyQuantity(quantity, item_data.get('unit', 'PCS'))
                inv.ActualQuantity = TallyQuantity(quantity, item_data.get('unit', 'PCS'))
                inv.Rate = TallyRate(rate, item_data.get('unit', 'PCS'))
                inv.Amount = TallyAmount(-amount)  # negative in purchase
                
                # Batch allocation
                batch = BatchAllocations()
                batch.GodownName = item_data.get('godown', TallyConfig.DEFAULT_GODOWN)
                batch.BatchName = item_data.get('batch', TallyConfig.DEFAULT_BATCH)
                batch.BilledQuantity = inv.BilledQuantity
                batch.ActualQuantity = inv.ActualQuantity
                batch.Amount = inv.Amount
                
                inv.BatchAllocations = List[BatchAllocations]()
                inv.BatchAllocations.Add(batch)
                
                # Ledger inside inventory (debit side)
                item_ledger = BaseVoucherLedger()
                item_ledger.LedgerName = item_data.get('purchase_ledger', TallyConfig.DEFAULT_PURCHASE_LEDGER)
                item_ledger.Amount = inv.Amount  # negative amount
                
                inv.Ledgers = List[BaseVoucherLedger]()
                inv.Ledgers.Add(item_ledger)
                
                v.InventoryAllocations.Add(inv)
            
            # ---------- Post the voucher to Tally ----------
            response = tally.session._svc.PostVoucherAsync(v).Result.Response
            
            return {
                'success': True,
                'message': f"Purchase voucher created successfully for {voucher_data['party_name']}",
                'voucher_type': 'Purchase',
                'party_name': voucher_data['party_name'],
                'date': voucher_data['date'],
                'total_amount': total_amount,
                'items_count': len(voucher_data['items']),
                'tally_response': response
            }
            
    except Exception as e:
        logger.error(f"Failed to create purchase voucher in Tally: {e}")
        return {
            'success': False,
            'message': f"Failed to create purchase voucher: {str(e)}",
            'error': str(e)
        }

# ======================== API ROUTES ========================

@bp.route('/test_connection', methods=['GET'])
def test_connection():
    """Test basic connection to Tally."""
    try:
        with TallyConnector() as tally:
            test_result = tally.test_connection()
            version_info = tally.get_version_info()
            
            return jsonify({
                'success': True,
                'message': 'Connected to Tally successfully',
                'connection_test': test_result,
                'version_info': version_info
            })
            
    except Exception as e:
        logger.error(f"Tally connection test failed: {e}")
        return jsonify({
            'success': False,
            'message': f'Connection failed: {str(e)}',
            'error': str(e)
        }), 500

@bp.route('/companies', methods=['GET'])
def get_companies():
    """Get list of companies from Tally."""
    try:
        with TallyConnector(version="latest") as tally:
            companies = get_companies_list(tally)
            return jsonify({
                'success': True,
                'companies': companies,
                'count': len(companies)
            })
            
    except Exception as e:
        logger.error(f"Failed to get companies: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get companies: {str(e)}',
            'error': str(e)
        }), 500

@bp.route('/ledgers', methods=['GET'])
def get_ledgers():
    """Get list of ledgers from Tally."""
    try:
        with TallyConnector(version="latest") as tally:
            ledgers = get_ledgers_list(tally)
            return jsonify({
                'success': True,
                'ledgers': ledgers,
                'count': len(ledgers)
            })
            
    except Exception as e:
        logger.error(f"Failed to get ledgers: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get ledgers: {str(e)}',
            'error': str(e)
        }), 500

@bp.route('/stock_items', methods=['GET'])
def get_stock_items():
    """Get list of stock items from Tally."""
    try:
        with TallyConnector(version="latest") as tally:
            stock_items = get_stock_items_list(tally)
            return jsonify({
                'success': True,
                'stock_items': stock_items,
                'count': len(stock_items)
            })
            
    except Exception as e:
        logger.error(f"Failed to get stock items: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get stock items: {str(e)}',
            'error': str(e)
        }), 500

@bp.route('/stock_items/ensure_exists', methods=['POST'])
def ensure_stock_item():
    """Ensure stock item exists in Tally, create if it doesn't exist."""
    try:
        data = request.get_json()
        
        if not data or 'item_name' not in data:
            return jsonify({'error': 'item_name is required'}), 400
        
        item_name = data['item_name']
        stock_group = data.get('stock_group', 'Primary')
        
        result = ensure_stock_item_exists(item_name, stock_group)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Failed to ensure stock item exists: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to ensure stock item exists: {str(e)}',
            'error': str(e)
        }), 500

@bp.route('/document/<int:document_id>/create_purchase_voucher', methods=['POST'])
def create_purchase_voucher_from_document(document_id):
    """
    Create purchase voucher in Tally from OCR data of a document.
    This is the main endpoint for converting OCR data to Tally purchase vouchers.
    """
    try:
        # Get document and validate
        document = Document.query.get_or_404(document_id)
        
        if document.status != DocumentStatus.PROCESSED:
            return jsonify({
                'success': False,
                'message': 'Document must be processed before creating Tally vouchers'
            }), 400
        
        # Get OCR data
        ocr_data = get_document_ocr_data(document_id)
        
        if not ocr_data['extracted_data'] and not ocr_data['table_data']:
            return jsonify({
                'success': False,
                'message': 'No OCR data found for this document'
            }), 400
        
        # Convert OCR data to Tally voucher format
        voucher_data = convert_ocr_to_tally_format(ocr_data)
        
                 # Ensure all stock items exist in Tally (create them if they don't exist)
        stock_item_results = []
        created_items = []
        existing_items = []
        failed_items = []
        
        for item in voucher_data['items']:
            result = ensure_stock_item_exists(item['stock_item'])
            stock_item_results.append({
                'item_name': item['stock_item'],
                'result': result
            })
            
            if result['success']:
                if result['already_exists']:
                    existing_items.append(item['stock_item'])
                else:
                    created_items.append(item['stock_item'])
            else:
                failed_items.append({
                    'item_name': item['stock_item'],
                    'error': result['message']
                })
        
        # Log the results for tracking
        if created_items:
            logger.info(f"Created {len(created_items)} new stock items: {', '.join(created_items)}")
        if existing_items:
            logger.info(f"Found {len(existing_items)} existing stock items: {', '.join(existing_items)}")
        if failed_items:
            logger.warning(f"Failed to create {len(failed_items)} stock items: {[item['item_name'] for item in failed_items]}")
        
        # Only fail if ALL stock items failed to be created/found
        if len(failed_items) == len(voucher_data['items']):
            return jsonify({
                'success': False,
                'message': 'Failed to ensure any stock items exist - cannot create voucher',
                'failed_items': failed_items,
                'stock_item_results': stock_item_results
            }), 500
        
        # If some items failed but others succeeded, proceed with a warning
        proceed_with_warnings = len(failed_items) > 0
        
        # Ensure party ledger exists
        party_result = ensure_party_ledger_exists(voucher_data['party_name'])
        
        if not party_result['success']:
            logger.warning(f"Failed to ensure party ledger exists: {party_result['message']}")
            # Continue with warning rather than failing completely
            proceed_with_warnings = True
        else:
            if party_result['already_exists']:
                logger.info(f"Found existing party ledger: {voucher_data['party_name']}")
            else:
                logger.info(f"Created new party ledger: {voucher_data['party_name']}")
        
        # Create purchase voucher in Tally
        voucher_result = create_purchase_voucher_in_tally(voucher_data)
        
        if voucher_result['success']:
            # Prepare success message with stock item and party ledger details
            message = 'Purchase voucher created successfully'
            if created_items and not failed_items:
                message += f' (created {len(created_items)} new stock items)'
            elif created_items and failed_items:
                message += f' (created {len(created_items)} new stock items, {len(failed_items)} items failed)'
            elif failed_items:
                message += f' (warning: {len(failed_items)} stock items could not be created)'
            
            # Add party ledger info to message
            if party_result['success'] and not party_result['already_exists']:
                message += f', created party ledger'
            elif party_result['success'] and party_result['already_exists']:
                message += f', using existing party ledger'
            elif not party_result['success']:
                message += f', warning: party ledger creation failed'
            
            warnings = []
            if len(failed_items) > 0:
                warnings.append('Some stock items could not be created')
            if not party_result['success']:
                warnings.append('Party ledger could not be created')
            
            return jsonify({
                'success': True,
                'message': message,
                'document_id': document_id,
                'voucher_data': voucher_data,
                'voucher_result': voucher_result,
                'stock_item_summary': {
                    'total_items': len(voucher_data['items']),
                    'existing_items': len(existing_items),
                    'created_items': len(created_items),
                    'failed_items': len(failed_items),
                    'created_item_names': created_items,
                    'existing_item_names': existing_items,
                    'failed_item_details': failed_items
                },
                'party_ledger_summary': {
                    'party_name': voucher_data['party_name'],
                    'ledger_exists': party_result['already_exists'],
                    'ledger_created': not party_result['already_exists'] and party_result['success'],
                    'ledger_result': party_result
                },
                'stock_item_results': stock_item_results,
                'warnings': warnings
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create purchase voucher',
                'voucher_result': voucher_result,
                'stock_item_summary': {
                    'total_items': len(voucher_data['items']),
                    'existing_items': len(existing_items),
                    'created_items': len(created_items),
                    'failed_items': len(failed_items),
                    'created_item_names': created_items,
                    'existing_item_names': existing_items,
                    'failed_item_details': failed_items
                },
                'party_ledger_summary': {
                    'party_name': voucher_data['party_name'],
                    'ledger_exists': party_result['already_exists'],
                    'ledger_created': not party_result['already_exists'] and party_result['success'],
                    'ledger_result': party_result
                },
                'stock_item_results': stock_item_results
            }), 500
            
    except Exception as e:
        logger.error(f"Failed to create purchase voucher from document {document_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to create purchase voucher: {str(e)}',
            'error': str(e)
        }), 500

@bp.route('/document/<int:document_id>/ocr_data', methods=['GET'])
def get_document_tally_ready_data(document_id):
    """
    Get OCR data formatted for Tally conversion.
    Useful for previewing what will be sent to Tally.
    """
    try:
        # Get document and validate
        document = Document.query.get_or_404(document_id)
        
        if document.status != DocumentStatus.PROCESSED:
            return jsonify({
                'success': False,
                'message': 'Document must be processed to get OCR data'
            }), 400
        
        # Get OCR data
        ocr_data = get_document_ocr_data(document_id)
        
        # Convert to Tally format
        voucher_data = convert_ocr_to_tally_format(ocr_data)
        
        return jsonify({
            'success': True,
            'document_id': document_id,
            'original_ocr_data': ocr_data,
            'tally_voucher_data': voucher_data
        })
        
    except Exception as e:
        logger.error(f"Failed to get Tally-ready data for document {document_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get Tally-ready data: {str(e)}',
            'error': str(e)
        }), 500

@bp.route('/ledgers/ensure_exists', methods=['POST'])
def ensure_party_ledger():
    """Ensure party ledger exists in Tally, create if it doesn't exist."""
    try:
        data = request.get_json()
        
        if not data or 'party_name' not in data:
            return jsonify({'error': 'party_name is required'}), 400
        
        party_name = data['party_name']
        ledger_group = data.get('ledger_group', 'Sundry Creditors')
        
        result = ensure_party_ledger_exists(party_name, ledger_group)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Failed to ensure party ledger exists: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to ensure party ledger exists: {str(e)}',
            'error': str(e)
        }), 500

# =============================================================================
# UNIT OF MEASURE (UOM) ROUTES
# =============================================================================

@bp.route('/units', methods=['GET'])
def get_units():
    """Get list of units of measure from Tally."""
    try:
        with TallyConnector(version="legacy") as tally:
            units = get_units_list(tally)
            return jsonify({
                'success': True,
                'units': units,
                'count': len(units)
            })
            
    except Exception as e:
        logger.error(f"Failed to get units: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get units: {str(e)}',
            'error': str(e)
        }), 500

@bp.route('/units/<string:unit_name>', methods=['GET'])
def get_unit(unit_name):
    """Get specific unit by name from Tally."""
    try:
        with TallyConnector(version="legacy") as tally:
            unit = find_unit_by_name(tally, unit_name)
            
            if unit:
                return jsonify({
                    'success': True,
                    'unit': unit
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Unit "{unit_name}" not found'
                }), 404
            
    except Exception as e:
        logger.error(f"Failed to get unit {unit_name}: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get unit: {str(e)}',
            'error': str(e)
        }), 500

@bp.route('/units', methods=['POST'])
def create_unit():
    """Create a new unit of measure in Tally."""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Unit name is required'}), 400
        
        # Validate decimal places
        decimal_places = data.get('decimal_places', 0)
        if not isinstance(decimal_places, int) or decimal_places < 0 or decimal_places > 4:
            return jsonify({'error': 'Decimal places must be an integer between 0 and 4'}), 400
        
        # Determine unit type
        is_compound = 'base_unit' in data and 'conversion' in data
        
        if is_compound:
            # Create compound unit
            required_fields = ['name', 'base_unit', 'conversion']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'{field} is required for compound units'}), 400
            
            if not isinstance(data['conversion'], (int, float)) or data['conversion'] <= 0:
                return jsonify({'error': 'Conversion must be a positive number'}), 400
            
            unit_data = {
                'name': data['name'],
                'base_unit': data['base_unit'],
                'conversion': data['conversion'],
                'decimal_places': decimal_places
            }
            
            with TallyConnector(version="legacy") as tally:
                result = create_compound_unit(tally, unit_data)
        else:
            # Create simple unit
            unit_data = {
                'name': data['name'],
                'decimal_places': decimal_places
            }
            
            with TallyConnector(version="legacy") as tally:
                result = create_simple_unit(tally, unit_data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Failed to create unit: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to create unit: {str(e)}',
            'error': str(e)
        }), 500

@bp.route('/units/<string:unit_name>', methods=['PUT'])
def update_unit_route(unit_name):
    """Update an existing unit of measure in Tally."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Update data is required'}), 400
        
        # Validate decimal places if provided
        if 'decimal_places' in data:
            decimal_places = data['decimal_places']
            if not isinstance(decimal_places, int) or decimal_places < 0 or decimal_places > 4:
                return jsonify({'error': 'Decimal places must be an integer between 0 and 4'}), 400
        
        # Validate conversion if provided
        if 'conversion' in data:
            if not isinstance(data['conversion'], (int, float)) or data['conversion'] <= 0:
                return jsonify({'error': 'Conversion must be a positive number'}), 400
        
        with TallyConnector(version="legacy") as tally:
            result = update_unit(tally, unit_name, data)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Failed to update unit {unit_name}: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to update unit: {str(e)}',
            'error': str(e)
        }), 500

@bp.route('/units/<string:unit_name>', methods=['DELETE'])
def delete_unit(unit_name):
    """Delete a unit of measure from Tally."""
    try:
        # Note: Tally typically doesn't support deleting units that are in use
        # This is a placeholder implementation
        return jsonify({
            'success': False,
            'message': 'Unit deletion is not supported in this version. Units should be made inactive instead.',
            'suggestion': 'Use PUT /units/{unit_name} with {"is_active": false} to deactivate the unit'
        }), 501  # Not Implemented
            
    except Exception as e:
        logger.error(f"Failed to delete unit {unit_name}: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to delete unit: {str(e)}',
            'error': str(e)
        }), 500

@bp.route('/units/ensure_exists', methods=['POST'])
def ensure_unit():
    """Ensure unit exists in Tally, create if it doesn't exist."""
    try:
        data = request.get_json()
        
        if not data or 'unit_name' not in data:
            return jsonify({'error': 'unit_name is required'}), 400
        
        unit_name = data['unit_name']
        decimal_places = data.get('decimal_places', 0)
        
        # Check if this is a compound unit request
        if 'base_unit' in data and 'conversion' in data:
            # Ensure compound unit
            base_unit = data['base_unit']
            conversion = data['conversion']
            
            if not isinstance(conversion, (int, float)) or conversion <= 0:
                return jsonify({'error': 'Conversion must be a positive number'}), 400
            
            result = ensure_compound_unit_exists(unit_name, base_unit, conversion, decimal_places)
        else:
            # Ensure simple unit
            result = ensure_unit_exists(unit_name, decimal_places)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Failed to ensure unit exists: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to ensure unit exists: {str(e)}',
            'error': str(e)
        }), 500

@bp.route('/units/common', methods=['GET'])
def get_common_units():
    """Get list of common units predefined in the system."""
    try:
        common_units = []
        for unit_name, properties in TallyConfig.COMMON_UNITS.items():
            common_units.append({
                'name': unit_name,
                'formal_name': properties['formal_name'],
                'decimal_places': properties['decimal_places'],
                'is_simple': True
            })
        
        return jsonify({
            'success': True,
            'common_units': common_units,
            'count': len(common_units)
        })
        
    except Exception as e:
        logger.error(f"Failed to get common units: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get common units: {str(e)}',
            'error': str(e)
        }), 500

@bp.route('/units/common/create_all', methods=['POST'])
def create_all_common_units():
    """Create all common units in Tally if they don't exist."""
    try:
        results = []
        success_count = 0
        error_count = 0
        
        for unit_name, properties in TallyConfig.COMMON_UNITS.items():
            try:
                result = ensure_unit_exists(unit_name, properties['decimal_places'])
                results.append({
                    'unit_name': unit_name,
                    'result': result
                })
                
                if result['success']:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                results.append({
                    'unit_name': unit_name,
                    'result': {
                        'success': False,
                        'message': str(e)
                    }
                })
        
        return jsonify({
            'success': error_count == 0,
            'message': f'Processed {len(TallyConfig.COMMON_UNITS)} units: {success_count} successful, {error_count} failed',
            'success_count': success_count,
            'error_count': error_count,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Failed to create common units: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to create common units: {str(e)}',
            'error': str(e)
        }), 500 