"""
Tally Data Retrieval Functions

Functions for retrieving data from Tally (Export operations).
Implements all the data retrieval requirements from the spec.
"""

import logging
from typing import Dict, List, Optional, Any
from webbrowser import get

from .connector import TallyConnector, TallyConnectorError

logger = logging.getLogger(__name__)


def get_companies_list(connector: TallyConnector) -> List[Dict]:
    """
    Retrieve the list of all companies.
    
    Args:
        connector: Active TallyConnector instance
        
    Returns:
        List of company dictionaries with Name and other properties
        
    Raises:
        TallyConnectorError: If retrieval fails
    """
    try:
        companies = connector.session.get_companies()
        result = []
        
        for company in companies:
            company_dict = {
                'name': getattr(company, 'Name', ''),
                'guid': getattr(company, 'GUID', ''),
                'alias': getattr(company, 'Alias', ''),
                'is_active': getattr(company, 'IsActive', True)
            }
            result.append(company_dict)
        
        logger.info(f"Retrieved {len(result)} companies")
        return result
        
    except Exception as e:
        logger.error(f"Failed to retrieve companies: {e}")
        raise TallyConnectorError(f"Companies retrieval failed: {e}")


def get_ledgers_list(connector: TallyConnector, company_name: Optional[str] = None) -> List[Dict]:
    """
    Fetch all ledgers to match customer or supplier names from OCR data.
    
    Args:
        connector: Active TallyConnector instance
        company_name: Optional company name filter
        
    Returns:
        List of ledger dictionaries
        
    Raises:
        TallyConnectorError: If retrieval fails
    """
    try:
        ledgers = connector.session.get_ledgers()
        result = []
        
        for ledger in ledgers:
            # Handle None values from Tally data
            name = getattr(ledger, 'Name', '') or ''
            alias = getattr(ledger, 'Alias', '') or ''
            group = getattr(ledger, 'Group', '') or ''
            email = getattr(ledger, 'Email', '') or ''
            mobile = getattr(ledger, 'Mobile', '') or ''
            address = getattr(ledger, 'Address', '') or ''
            guid = getattr(ledger, 'GUID', '') or ''
            
            ledger_dict = {
                'name': name,
                'alias': alias,
                'group': group,
                'opening_balance': getattr(ledger, 'OpeningBalance', 0),
                'is_active': getattr(ledger, 'IsActive', True),
                'email': email,
                'mobile': mobile,
                'address': address,
                'guid': guid
            }
            result.append(ledger_dict)
        
        logger.info(f"Retrieved {len(result)} ledgers")
        return result
        
    except Exception as e:
        logger.error(f"Failed to retrieve ledgers: {e}")
        raise TallyConnectorError(f"Ledgers retrieval failed: {e}")


def get_stock_items_list(connector: TallyConnector, company_name: Optional[str] = None) -> List[Dict]:
    """
    Retrieve the list of all inventory items to ensure products from OCR data exist in Tally.
    
    Args:
        connector: Active TallyConnector instance
        company_name: Optional company name filter
        
    Returns:
        List of stock item dictionaries
        
    Raises:
        TallyConnectorError: If retrieval fails
    """
    try:
        stock_items = connector.session.get_stock_items()
        result = []
        
        for item in stock_items:
            item_dict = {
                'name': getattr(item, 'Name', ''),
                'alias': getattr(item, 'Alias', ''),
                'group': getattr(item, 'Group', ''),
                'base_unit': getattr(item, 'BaseUnit', ''),
                'stock_group': getattr(item, 'StockGroup', ''),
                'is_active': getattr(item, 'IsActive', True),
                'opening_balance': getattr(item, 'OpeningBalance', 0),
                'opening_rate': getattr(item, 'OpeningRate', 0),
                'guid': getattr(item, 'GUID', '')
            }
            result.append(item_dict)
        
        logger.info(f"Retrieved {len(result)} stock items")
        return result
        
    except Exception as e:
        logger.error(f"Failed to retrieve stock items: {e}")
        raise TallyConnectorError(f"Stock items retrieval failed: {e}")


def get_vouchers_list(connector: TallyConnector, filters: Optional[Dict] = None) -> List[Dict]:
    """
    Pull existing vouchers for reconciliation or to check if similar entries exist.
    
    Args:
        connector: Active TallyConnector instance
        filters: Optional filters (voucher_type, date_from, date_to, etc.)
        
    Returns:
        List of voucher dictionaries
        
    Raises:
        TallyConnectorError: If retrieval fails
    """
    try:
        vouchers = connector.session.get_vouchers()
        result = []
        
        for voucher in vouchers:
            voucher_dict = {
                'voucher_number': getattr(voucher, 'VoucherNumber', ''),
                'voucher_type': getattr(voucher, 'VoucherType', ''),
                'date': getattr(voucher, 'Date', ''),
                'party_name': getattr(voucher, 'PartyName', ''),
                'amount': getattr(voucher, 'Amount', 0),
                'narration': getattr(voucher, 'Narration', ''),
                'reference': getattr(voucher, 'Reference', ''),
                'guid': getattr(voucher, 'GUID', ''),
                'is_invoice': getattr(voucher, 'IsInvoice', False)
            }
            result.append(voucher_dict)
        
        # Apply filters if provided
        if filters:
            result = _apply_voucher_filters(result, filters)
        
        logger.info(f"Retrieved {len(result)} vouchers")
        return result
        
    except Exception as e:
        logger.error(f"Failed to retrieve vouchers: {e}")
        raise TallyConnectorError(f"Vouchers retrieval failed: {e}")


def find_ledger_by_name(connector: TallyConnector, ledger_name: str) -> Optional[Dict]:
    """
    Find a specific ledger by name (case-insensitive).
    
    Args:
        connector: Active TallyConnector instance
        ledger_name: Name of the ledger to find
        
    Returns:
        Ledger dictionary if found, None otherwise
        
    Raises:
        TallyConnectorError: If search fails
    """
    try:
        ledgers = get_ledgers_list(connector)
        ledger_name_lower = ledger_name.lower().strip()
        
        for ledger in ledgers:
            # Safe handling of potential None values
            ledger_name_safe = (ledger['name'] or '').lower().strip()
            ledger_alias_safe = (ledger['alias'] or '').lower().strip()
            
            if (ledger_name_safe == ledger_name_lower or 
                ledger_alias_safe == ledger_name_lower):
                logger.info(f"Found ledger: {ledger['name']}")
                return ledger
        
        logger.info(f"Ledger not found: {ledger_name}")
        return None
        
    except Exception as e:
        logger.error(f"Failed to find ledger {ledger_name}: {e}")
        raise TallyConnectorError(f"Ledger search failed: {e}")


def find_stock_item_by_name(connector: TallyConnector, item_name: str) -> Optional[Dict]:
    """
    Find a specific stock item by name (case-insensitive).
    
    Args:
        connector: Active TallyConnector instance
        item_name: Name of the stock item to find
        
    Returns:
        Stock item dictionary if found, None otherwise
        
    Raises:
        TallyConnectorError: If search fails
    """
    try:
        stock_items = get_stock_items_list(connector)
        item_name_lower = item_name.lower().strip()

        for item in stock_items:
            if (item['name'] is not None and (item['name'].lower().strip() == item_name_lower) or 
                item['alias'] is not None and (item['alias'].lower().strip() == item_name_lower)):
                logger.info(f"Found stock item: {item['name']}")
                return item
        
        logger.info(f"Stock item not found: {item_name}")
        return None
        
    except Exception as e:
        logger.error(f"Failed to find stock item {item_name}: {e}")
        raise TallyConnectorError(f"Stock item search failed: {e}")


def _apply_voucher_filters(vouchers: List[Dict], filters: Dict) -> List[Dict]:
    """Apply filters to voucher list."""
    filtered = vouchers
    
    if 'voucher_type' in filters:
        voucher_type = filters['voucher_type'].lower()
        filtered = [v for v in filtered if v['voucher_type'].lower() == voucher_type]
    
    if 'party_name' in filters:
        party_name = filters['party_name'].lower()
        filtered = [v for v in filtered if party_name in v['party_name'].lower()]
    
    # Add more filters as needed (date ranges, amount ranges, etc.)
    
    return filtered


def get_units_list(connector: TallyConnector, company_name: Optional[str] = None) -> List[Dict]:
    """
    Retrieve the list of all units of measure from Tally.
    
    Args:
        connector: Active TallyConnector instance
        company_name: Optional company name filter (not used currently)
        
    Returns:
        List of unit dictionaries
        
    Raises:
        TallyConnectorError: If retrieval fails
    """
    try:
        units = connector.session.get_units()
        result = []
        
        for unit in units:
            # Handle None values from Tally data
            name = getattr(unit, 'Name', '') or ''
            decimal_places = getattr(unit, 'DecimalPlaces', 0) or 0
            is_simple_unit = str(getattr(unit, 'IsSimpleUnit', '')).lower()
            base_unit = getattr(unit, 'BaseUnit', '') or ''
            conversion = getattr(unit, 'Conversion', 1.0) or 1.0
            guid = getattr(unit, 'GUID', '') or ''
            is_active = getattr(unit, 'IsActive', True)
            
            unit_dict = {
                'name': name,
                'decimal_places': decimal_places,
                'is_simple_unit': is_simple_unit == 'yes',  # Convert TallyYesNo to boolean
                'base_unit': base_unit,
                'conversion': float(conversion),
                'is_active': is_active,
                'guid': guid,
                'alter_id': getattr(unit, 'AlterId', 0) or 0,
                'master_id': getattr(unit, 'MasterId', 0) or 0
            }
            result.append(unit_dict)
        
        logger.info(f"Retrieved {len(result)} units")
        return result
        
    except Exception as e:
        logger.error(f"Failed to retrieve units: {e}")
        raise TallyConnectorError(f"Units retrieval failed: {e}")


def find_unit_by_name(connector: TallyConnector, unit_name: str) -> Optional[Dict]:
    """
    Find a specific unit by name (case-insensitive).
    
    Args:
        connector: Active TallyConnector instance
        unit_name: Name of the unit to find
        
    Returns:
        Unit dictionary if found, None otherwise
        
    Raises:
        TallyConnectorError: If search fails
    """
    try:
        # First try direct lookup using GetUnitAsync
        try:
            unit = connector.session.get_unit(unit_name)
            if unit:
                logger.info(f"Found unit: {getattr(unit, 'Name', 'Unknown')}")
                return {
                    'name': getattr(unit, 'Name', ''),
                    'decimal_places': getattr(unit, 'DecimalPlaces', 0) or 0,
                    'is_simple_unit': str(getattr(unit, 'IsSimpleUnit', '')).lower() == 'yes',
                    'base_unit': getattr(unit, 'BaseUnit', '') or '',
                    'conversion': float(getattr(unit, 'Conversion', 1.0) or 1.0),
                    'is_active': getattr(unit, 'IsActive', True),
                    'guid': getattr(unit, 'GUID', '') or '',
                    'alter_id': getattr(unit, 'AlterId', 0) or 0,
                    'master_id': getattr(unit, 'MasterId', 0) or 0
                }
        except Exception as direct_lookup_error:
            logger.debug(f"Direct lookup failed for unit '{unit_name}': {direct_lookup_error}")
            
        # Fallback to searching through all units
        units = get_units_list(connector)
        unit_name_lower = unit_name.lower().strip()
        
        for unit in units:
            # Safe handling of potential None values
            unit_name_safe = (unit['name'] or '').lower().strip()
            
            if unit_name_safe == unit_name_lower:
                logger.info(f"Found unit: {unit['name']}")
                return unit
        
        logger.info(f"Unit not found: {unit_name}")
        return None
        
    except Exception as e:
        logger.error(f"Failed to find unit {unit_name}: {e}")
        raise TallyConnectorError(f"Unit search failed: {e}")
