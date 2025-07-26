"""
Tally Connector Library

A pure function library for integrating with Tally ERP through the TallyConnector .NET SDK.
Provides data retrieval and insertion capabilities for OCR-to-Tally workflows.

Usage:
    from app.tally import TallyConnector, get_companies_list, create_sales_voucher
    
    with TallyConnector() as tally:
        companies = get_companies_list(tally)
        result = create_sales_voucher(tally, voucher_data)
"""

from .connector import TallyConnector
from .config import TallyConfig
from .data_retrieval import (
    get_companies_list,
    get_ledgers_list,
    get_stock_items_list,
    get_vouchers_list,
    find_ledger_by_name,
    find_stock_item_by_name
)
from .data_insertion import (
    create_ledger,
    update_ledger,
    create_stock_item,
    create_sales_voucher,
    create_purchase_voucher,
    create_payment_voucher
)
from .utils import (
    ocr_data_to_voucher_format,
    validate_voucher_data,
    normalize_party_name,
    calculate_voucher_totals
)
from .tally_field_options import (
    load_companies_as_options,
    load_ledgers_as_options,
    load_stock_items_as_options,
    auto_load_tally_options,
    refresh_field_options,
    get_field_options_summary,
    load_customer_options,
    load_vendor_options,
    load_all_ledger_options,
    TallyFieldOptionsError
)

__all__ = [
    'TallyConnector',
    'TallyConfig',
    # Data Retrieval
    'get_companies_list',
    'get_ledgers_list', 
    'get_stock_items_list',
    'get_vouchers_list',
    'find_ledger_by_name',
    'find_stock_item_by_name',
    # Data Insertion
    'create_ledger',
    'update_ledger',
    'create_stock_item',
    'create_sales_voucher',
    'create_purchase_voucher',
    'create_payment_voucher',
    # Utilities
    'ocr_data_to_voucher_format',
    'validate_voucher_data',
    'normalize_party_name',
    'calculate_voucher_totals',
    # Field Options
    'load_companies_as_options',
    'load_ledgers_as_options',
    'load_stock_items_as_options',
    'auto_load_tally_options',
    'refresh_field_options',
    'get_field_options_summary',
    'load_customer_options',
    'load_vendor_options',
    'load_all_ledger_options',
    'TallyFieldOptionsError'
]
