"""
Tally Data Insertion Functions

Functions for creating and updating data in Tally (Import operations).
Implements all the data insertion requirements from the spec.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from .connector import TallyConnector, TallyConnectorError
from .config import TallyConfig

logger = logging.getLogger(__name__)


def create_ledger(connector: TallyConnector, ledger_data: Dict) -> Dict:
    """
    Add new customer or supplier ledger if it doesn't already exist.
    
    Args:
        connector: Active TallyConnector instance
        ledger_data: Dictionary containing ledger information
            Required: name
            Optional: group, alias, email, mobile, address, ledger_type
            
    Returns:
        Dictionary with creation result and ledger details
        
    Raises:
        TallyConnectorError: If creation fails
    """
    try:
        # Validate required fields
        if 'name' not in ledger_data:
            raise ValueError("Ledger name is required")
        
        name = ledger_data['name']
        ledger_type = ledger_data.get('ledger_type', 'customer')
        group = ledger_data.get('group', TallyConfig.get_default_ledger_group(ledger_type))
        alias = ledger_data.get('alias', name)
        
        # Create ledger using TallySession
        response = connector.session.create_ledger(
            name=name,
            group=group,
            alias=alias,
            Email=ledger_data.get('email', ''),
            Mobile=ledger_data.get('mobile', ''),
            Address=ledger_data.get('address', '')
        )
        
        result = {
            'success': True,
            'message': f"Ledger '{name}' created successfully",
            'ledger_name': name,
            'group': group,
            'response': response
        }
        
        logger.info(f"Created ledger: {name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create ledger {ledger_data.get('name', 'Unknown')}: {e}")
        raise TallyConnectorError(f"Ledger creation failed: {e}")


def update_ledger(connector: TallyConnector, ledger_name: str, updates: Dict) -> Dict:
    """
    Update existing ledger details based on OCR data.
    
    Args:
        connector: Active TallyConnector instance
        ledger_name: Name of the ledger to update
        updates: Dictionary containing fields to update
        
    Returns:
        Dictionary with update result
        
    Raises:
        TallyConnectorError: If update fails
    """
    try:
        # Note: TallyConnector doesn't have a direct update method
        # This would typically require recreating the ledger with updated data
        # For now, we'll return a placeholder implementation
        
        logger.warning(f"Ledger update not fully implemented for: {ledger_name}")
        
        result = {
            'success': False,
            'message': f"Ledger update not implemented. Consider recreating ledger '{ledger_name}'",
            'ledger_name': ledger_name,
            'updates': updates
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to update ledger {ledger_name}: {e}")
        raise TallyConnectorError(f"Ledger update failed: {e}")


def create_stock_item(connector: TallyConnector, item_data: Dict) -> Dict:
    """
    Insert new inventory item identified in OCR data but not yet in Tally.
    
    Args:
        connector: Active TallyConnector instance
        item_data: Dictionary containing stock item information
            Required: name
            Optional: base_unit, stock_group, alias
            
    Returns:
        Dictionary with creation result and item details
        
    Raises:
        TallyConnectorError: If creation fails
    """
    try:
        # Validate required fields
        if 'name' not in item_data:
            raise ValueError("Stock item name is required")
        
        name = item_data['name']
        base_unit = item_data.get('base_unit', TallyConfig.DEFAULT_UNIT)
        stock_group = item_data.get('stock_group', TallyConfig.DEFAULT_STOCK_GROUP)
        
        # Create stock item using TallySession
        response = connector.session.create_stock_item(
            name=name,
            base_unit=base_unit,
            stock_group=stock_group
        )
        
        result = {
            'success': True,
            'message': f"Stock item '{name}' created successfully",
            'item_name': name,
            'base_unit': base_unit,
            'stock_group': stock_group,
            'response': response
        }
        
        # breakpoint()  # Debugging point to inspect response
        
        logger.info(f"Created stock item: {name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create stock item {item_data.get('name', 'Unknown')}: {e}")
        raise TallyConnectorError(f"Stock item creation failed: {e}")


def create_sales_voucher(connector: TallyConnector, voucher_data: Dict) -> Dict:
    """
    Post new sales voucher for invoices extracted by OCR.
    
    Args:
        connector: Active TallyConnector instance
        voucher_data: Dictionary containing voucher information
            Required: party_name, date, items
            Optional: voucher_number, narration, bill_ref
            
    Returns:
        Dictionary with creation result and voucher details
        
    Raises:
        TallyConnectorError: If creation fails
    """
    try:
        # Validate required fields
        required_fields = ['party_name', 'date', 'items']
        for field in required_fields:
            if field not in voucher_data:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Parse date
        date = _parse_date(voucher_data['date'])
        
        # Prepare voucher data
        voucher_params = {
            'voucher_type': 'Sales',
            'date': date,
            'party_name': voucher_data['party_name'],
            'items': voucher_data['items'],
            'voucher_number': voucher_data.get('voucher_number'),
            'narration': voucher_data.get('narration', 'Sales voucher from OCR'),
            'bill_ref': voucher_data.get('bill_ref'),
            'post': True
        }
        
        # Create voucher using TallySession
        response = connector.session.create_voucher(**voucher_params)
        
        result = {
            'success': True,
            'message': f"Sales voucher created for {voucher_data['party_name']}",
            'voucher_type': 'Sales',
            'party_name': voucher_data['party_name'],
            'date': date.isoformat(),
            'response': response
        }
        
        logger.info(f"Created sales voucher for: {voucher_data['party_name']}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create sales voucher: {e}")
        raise TallyConnectorError(f"Sales voucher creation failed: {e}")


def create_purchase_voucher(connector: TallyConnector, voucher_data: Dict) -> Dict:
    """
    Create purchase voucher for bills from suppliers.
    
    Args:
        connector: Active TallyConnector instance
        voucher_data: Dictionary containing voucher information
            Required: party_name, date, items
            Optional: voucher_number, narration, bill_ref
            
    Returns:
        Dictionary with creation result and voucher details
        
    Raises:
        TallyConnectorError: If creation fails
    """
    try:
        # Validate required fields
        required_fields = ['party_name', 'date', 'items']
        for field in required_fields:
            if field not in voucher_data:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Parse date
        date = _parse_date(voucher_data['date'])
        
        # Prepare voucher data
        voucher_params = {
            'voucher_type': 'Purchase',
            'date': date,
            'party_name': voucher_data['party_name'],
            'items': voucher_data['items'],
            'voucher_number': voucher_data.get('voucher_number'),
            'narration': voucher_data.get('narration', 'Purchase voucher from OCR'),
            'bill_ref': voucher_data.get('bill_ref'),
            'post': True
        }
        
        # Create voucher using TallySession
        response = connector.session.create_voucher(**voucher_params)
        
        result = {
            'success': True,
            'message': f"Purchase voucher created for {voucher_data['party_name']}",
            'voucher_type': 'Purchase',
            'party_name': voucher_data['party_name'],
            'date': date.isoformat(),
            'response': response
        }
        
        logger.info(f"Created purchase voucher for: {voucher_data['party_name']}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create purchase voucher: {e}")
        raise TallyConnectorError(f"Purchase voucher creation failed: {e}")


def create_payment_voucher(connector: TallyConnector, voucher_data: Dict) -> Dict:
    """
    Add payment voucher if OCR data includes payment details.
    
    Args:
        connector: Active TallyConnector instance
        voucher_data: Dictionary containing payment information
            Required: party_name, date, amount
            Optional: voucher_number, narration, payment_method
            
    Returns:
        Dictionary with creation result and voucher details
        
    Raises:
        TallyConnectorError: If creation fails
    """
    try:
        # Validate required fields
        required_fields = ['party_name', 'date', 'amount']
        for field in required_fields:
            if field not in voucher_data:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Parse date
        date = _parse_date(voucher_data['date'])
        
        # Prepare payment voucher data
        # Note: Payment vouchers typically don't have inventory items
        # They involve cash/bank and party ledgers
        
        result = {
            'success': False,
            'message': "Payment voucher creation not fully implemented",
            'voucher_type': 'Payment',
            'party_name': voucher_data['party_name'],
            'amount': voucher_data['amount'],
            'date': date.isoformat()
        }
        
        logger.warning(f"Payment voucher creation not implemented for: {voucher_data['party_name']}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create payment voucher: {e}")
        raise TallyConnectorError(f"Payment voucher creation failed: {e}")


def _parse_date(date_input: Any) -> datetime:
    """Parse date from various input formats."""
    if isinstance(date_input, datetime):
        return date_input
    elif isinstance(date_input, str):
        # Try common date formats
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']
        for fmt in formats:
            try:
                return datetime.strptime(date_input, fmt)
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {date_input}")
    else:
        raise ValueError(f"Invalid date type: {type(date_input)}")


def create_simple_unit(connector: TallyConnector, unit_data: Dict) -> Dict:
    """
    Create a simple unit of measure in Tally.
    
    Args:
        connector: Active TallyConnector instance
        unit_data: Dictionary containing unit information
            Required: name
            Optional: decimal_places (default: 0)
            
    Returns:
        Dictionary with creation result and unit details
        
    Raises:
        TallyConnectorError: If creation fails
    """
    try:
        # Validate required fields
        if 'name' not in unit_data:
            raise ValueError("Unit name is required")
        
        name = unit_data['name']
        decimal_places = unit_data.get('decimal_places', 0)
        
        # Validate decimal places (0-4 allowed in Tally)
        if not isinstance(decimal_places, int) or decimal_places < 0 or decimal_places > 4:
            raise ValueError("Decimal places must be an integer between 0 and 4")
        
        # Create unit using TallySession
        response = connector.session.create_unit(
            name=name,
            decimal_places=decimal_places,
            is_simple=True
        )
        
        result = {
            'success': True,
            'message': f"Simple unit '{name}' created successfully",
            'unit_name': name,
            'unit_type': 'simple',
            'decimal_places': decimal_places,
            'response': response
        }
        
        logger.info(f"Created simple unit: {name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create simple unit {unit_data.get('name', 'Unknown')}: {e}")
        raise TallyConnectorError(f"Simple unit creation failed: {e}")


def create_compound_unit(connector: TallyConnector, unit_data: Dict) -> Dict:
    """
    Create a compound unit of measure in Tally.
    
    Args:
        connector: Active TallyConnector instance
        unit_data: Dictionary containing compound unit information
            Required: name, base_unit, conversion
            Optional: decimal_places (default: 0)
            
    Returns:
        Dictionary with creation result and unit details
        
    Raises:
        TallyConnectorError: If creation fails
    """
    try:
        # Validate required fields
        required_fields = ['name', 'base_unit', 'conversion']
        for field in required_fields:
            if field not in unit_data:
                raise ValueError(f"Required field '{field}' is missing")
        
        name = unit_data['name']
        base_unit = unit_data['base_unit']
        conversion = unit_data['conversion']
        decimal_places = unit_data.get('decimal_places', 0)
        
        # Validate fields
        if not isinstance(decimal_places, int) or decimal_places < 0 or decimal_places > 4:
            raise ValueError("Decimal places must be an integer between 0 and 4")
            
        if not isinstance(conversion, (int, float)) or conversion <= 0:
            raise ValueError("Conversion factor must be a positive number")
        
        # Verify base unit exists (simple validation)
        from .data_retrieval import find_unit_by_name
        base_unit_exists = find_unit_by_name(connector, base_unit)
        if not base_unit_exists:
            logger.warning(f"Base unit '{base_unit}' not found. Creating compound unit anyway.")
        
        # Create compound unit using TallySession
        response = connector.session.create_unit(
            name=name,
            decimal_places=decimal_places,
            is_simple=False,
            base_unit=base_unit,
            conversion=float(conversion)
        )
        
        result = {
            'success': True,
            'message': f"Compound unit '{name}' created successfully ({conversion} {base_unit})",
            'unit_name': name,
            'unit_type': 'compound',
            'base_unit': base_unit,
            'conversion': float(conversion),
            'decimal_places': decimal_places,
            'response': response
        }
        
        logger.info(f"Created compound unit: {name} = {conversion} {base_unit}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create compound unit {unit_data.get('name', 'Unknown')}: {e}")
        raise TallyConnectorError(f"Compound unit creation failed: {e}")


def create_unit(connector: TallyConnector, unit_data: Dict) -> Dict:
    """
    Create a unit of measure in Tally (auto-detects simple vs compound).
    
    Args:
        connector: Active TallyConnector instance
        unit_data: Dictionary containing unit information
            Required: name
            Optional: decimal_places, base_unit, conversion
            
    Returns:
        Dictionary with creation result and unit details
        
    Raises:
        TallyConnectorError: If creation fails
    """
    try:
        # Auto-detect unit type based on provided data
        has_base_unit = 'base_unit' in unit_data and unit_data['base_unit']
        has_conversion = 'conversion' in unit_data and unit_data['conversion']
        
        if has_base_unit and has_conversion:
            # This is a compound unit
            return create_compound_unit(connector, unit_data)
        else:
            # This is a simple unit
            return create_simple_unit(connector, unit_data)
            
    except Exception as e:
        logger.error(f"Failed to create unit {unit_data.get('name', 'Unknown')}: {e}")
        raise TallyConnectorError(f"Unit creation failed: {e}")


def update_unit(connector: TallyConnector, unit_name: str, updates: Dict) -> Dict:
    """
    Update an existing unit in Tally.
    
    Args:
        connector: Active TallyConnector instance
        unit_name: Name of the unit to update
        updates: Dictionary containing fields to update
        
    Returns:
        Dictionary with update result
        
    Raises:
        TallyConnectorError: If update fails
    """
    try:
        # First check if unit exists
        from .data_retrieval import find_unit_by_name
        existing_unit = find_unit_by_name(connector, unit_name)
        
        if not existing_unit:
            raise ValueError(f"Unit '{unit_name}' not found")
        
        # Prepare update data
        unit_data = {
            'name': unit_name,
            'decimal_places': updates.get('decimal_places', existing_unit['decimal_places']),
        }
        
        # Handle unit type changes (not recommended but possible)
        if 'base_unit' in updates or 'conversion' in updates:
            unit_data['base_unit'] = updates.get('base_unit', existing_unit['base_unit'])
            unit_data['conversion'] = updates.get('conversion', existing_unit['conversion'])
        
        # Use create_unit with Action.Alter (handled automatically by session)
        response = connector.session.create_unit(
            name=unit_name,
            decimal_places=unit_data['decimal_places'],
            is_simple=existing_unit['is_simple_unit'],
            base_unit=unit_data.get('base_unit'),
            conversion=unit_data.get('conversion', 1.0)
        )
        
        result = {
            'success': True,
            'message': f"Unit '{unit_name}' updated successfully",
            'unit_name': unit_name,
            'updates_applied': updates,
            'response': response
        }
        
        logger.info(f"Updated unit: {unit_name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to update unit {unit_name}: {e}")
        raise TallyConnectorError(f"Unit update failed: {e}")
