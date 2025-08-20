"""
Tally Field Options Helper

Functions for loading Tally data (companies, ledgers, stock items) 
as options for SELECT type template fields.
"""

import logging
from typing import Dict, List, Optional, Union
from datetime import datetime

from .. import db
from ..models import TemplateField, FieldOption, SubTemplateField, SubTemplateFieldOption
from ..utils.enums import FieldType, FieldName, DataType
from .connector import TallyConnector, TallyConnectorError
from .data_retrieval import get_companies_list, get_ledgers_list, get_stock_items_list

logger = logging.getLogger(__name__)


class TallyFieldOptionsError(Exception):
    """Custom exception for Tally field options operations"""
    pass


def load_companies_as_options(field_id: int, clear_existing: bool = True) -> Dict:
    """
    Load Tally companies as options for a SELECT field.
    
    Args:
        field_id: ID of the template field
        clear_existing: Whether to clear existing options before loading
        
    Returns:
        Dict with success status and loaded options count
        
    Raises:
        TallyFieldOptionsError: If loading fails
    """
    try:
        # Validate field exists and is SELECT type
        field = TemplateField.query.get(field_id)
        if not field:
            raise TallyFieldOptionsError(f"Field with ID {field_id} not found")
        
        if field.field_type != FieldType.SELECT:
            raise TallyFieldOptionsError(f"Field {field_id} is not a SELECT type field")
        
        # Clear existing options if requested
        if clear_existing:
            FieldOption.query.filter_by(field_id=field_id).delete()
            db.session.flush()
        
        # Connect to Tally and fetch companies
        with TallyConnector(version="latest") as tally:
            companies = get_companies_list(tally)
        
        # Create field options from companies
        options_created = 0
        for company in companies:
            # Skip inactive companies
            if not company.get('is_active', True):
                continue
                
            option = FieldOption(
                field_id=field_id,
                option_value=company['name'],  # Use name as value
                option_label=company['name']   # Use name as label
            )
            db.session.add(option)
            options_created += 1
        
        db.session.commit()
        
        logger.info(f"Loaded {options_created} company options for field {field_id}")
        return {
            'success': True,
            'message': f'Successfully loaded {options_created} company options',
            'options_count': options_created,
            'field_id': field_id
        }
        
    except TallyConnectorError as e:
        db.session.rollback()
        logger.error(f"Tally connection error while loading companies for field {field_id}: {e}")
        raise TallyFieldOptionsError(f"Failed to connect to Tally: {e}")
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error loading companies for field {field_id}: {e}")
        raise TallyFieldOptionsError(f"Failed to load companies: {e}")


def load_ledgers_as_options(field_id: int, ledger_group: Optional[str] = None, clear_existing: bool = True) -> Dict:
    """
    Load Tally ledgers as options for a SELECT field.
    
    Args:
        field_id: ID of the template field
        ledger_group: Optional filter by ledger group (e.g., "Sundry Debtors", "Sundry Creditors")
        clear_existing: Whether to clear existing options before loading
        
    Returns:
        Dict with success status and loaded options count
        
    Raises:
        TallyFieldOptionsError: If loading fails
    """
    try:
        # Validate field exists and is SELECT type
        field = TemplateField.query.get(field_id)
        if not field:
            raise TallyFieldOptionsError(f"Field with ID {field_id} not found")
        
        if field.field_type != FieldType.SELECT:
            raise TallyFieldOptionsError(f"Field {field_id} is not a SELECT type field")
        
        # Clear existing options if requested
        if clear_existing:
            FieldOption.query.filter_by(field_id=field_id).delete()
            db.session.flush()
        
        # Connect to Tally and fetch ledgers
        with TallyConnector(version="latest") as tally:

            ledgers = get_ledgers_list(tally)
        
        # Filter by group if specified
        if ledger_group:
            ledgers = [l for l in ledgers if l.get('group', '').lower() == ledger_group.lower()]
        
        # Create field options from ledgers
        options_created = 0
        for ledger in ledgers:
            # Skip inactive ledgers
            if not ledger.get('is_active', True):
                continue
                
            # Use alias if available, otherwise use name
            display_name = ledger.get('alias') or ledger['name']
            
            option = FieldOption(
                field_id=field_id,
                option_value=ledger['name'],    # Always use actual name as value
                option_label=display_name       # Use alias or name for display
            )
            db.session.add(option)
            options_created += 1
        
        db.session.commit()
        
        group_filter_msg = f" (filtered by group: {ledger_group})" if ledger_group else ""
        logger.info(f"Loaded {options_created} ledger options for field {field_id}{group_filter_msg}")
        
        return {
            'success': True,
            'message': f'Successfully loaded {options_created} ledger options{group_filter_msg}',
            'options_count': options_created,
            'field_id': field_id,
            'ledger_group': ledger_group
        }
        
    except TallyConnectorError as e:
        db.session.rollback()
        logger.error(f"Tally connection error while loading ledgers for field {field_id}: {e}")
        raise TallyFieldOptionsError(f"Failed to connect to Tally: {e}")
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error loading ledgers for field {field_id}: {e}")
        raise TallyFieldOptionsError(f"Failed to load ledgers: {e}")


def load_stock_items_as_options(field_id: int, stock_group: Optional[str] = None, clear_existing: bool = True) -> Dict:
    """
    Load Tally stock items as options for a SELECT field.
    
    Args:
        field_id: ID of the template field
        stock_group: Optional filter by stock group
        clear_existing: Whether to clear existing options before loading
        
    Returns:
        Dict with success status and loaded options count
        
    Raises:
        TallyFieldOptionsError: If loading fails
    """
    try:
        # Validate field exists and is SELECT type
        field = TemplateField.query.get(field_id)
        if not field:
            raise TallyFieldOptionsError(f"Field with ID {field_id} not found")
        
        if field.field_type != FieldType.SELECT:
            raise TallyFieldOptionsError(f"Field {field_id} is not a SELECT type field")
        
        # Clear existing options if requested
        if clear_existing:
            FieldOption.query.filter_by(field_id=field_id).delete()
            db.session.flush()
        
        # Connect to Tally and fetch stock items
        with TallyConnector(version="latest") as tally:
            stock_items = get_stock_items_list(tally)
        
        # Filter by stock group if specified
        if stock_group:
            stock_items = [item for item in stock_items if item.get('stock_group', '').lower() == stock_group.lower()]
        
        # Create field options from stock items
        options_created = 0
        for item in stock_items:
            # Skip inactive items
            if not item.get('is_active', True):
                continue
                
            # Use alias if available, otherwise use name
            display_name = item.get('alias') or item['name']
            
            option = FieldOption(
                field_id=field_id,
                option_value=item['name'],      # Always use actual name as value
                option_label=display_name       # Use alias or name for display
            )
            db.session.add(option)
            options_created += 1
        
        db.session.commit()
        
        group_filter_msg = f" (filtered by stock group: {stock_group})" if stock_group else ""
        logger.info(f"Loaded {options_created} stock item options for field {field_id}{group_filter_msg}")
        
        return {
            'success': True,
            'message': f'Successfully loaded {options_created} stock item options{group_filter_msg}',
            'options_count': options_created,
            'field_id': field_id,
            'stock_group': stock_group
        }
        
    except TallyConnectorError as e:
        db.session.rollback()
        logger.error(f"Tally connection error while loading stock items for field {field_id}: {e}")
        raise TallyFieldOptionsError(f"Failed to connect to Tally: {e}")
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error loading stock items for field {field_id}: {e}")
        raise TallyFieldOptionsError(f"Failed to load stock items: {e}")


def auto_load_tally_options(field_id: int, clear_existing: bool = True) -> Dict:
    """
    Automatically determine what type of Tally data to load based on field name.
    
    Args:
        field_id: ID of the template field
        clear_existing: Whether to clear existing options before loading
        
    Returns:
        Dict with success status and loaded options count
        
    Raises:
        TallyFieldOptionsError: If loading fails or field type cannot be determined
    """
    try:
        # Get field information
        field = TemplateField.query.get(field_id)
        if not field:
            raise TallyFieldOptionsError(f"Field with ID {field_id} not found")
        
        if field.field_type != FieldType.SELECT:
            raise TallyFieldOptionsError(f"Field {field_id} is not a SELECT type field")
        
        field_name = field.field_name
        
        # Map field names to Tally data types
        field_mapping = {
            # Company-related fields
            FieldName.VENDOR_NAME: ('ledgers', 'Sundry Creditors'),
            FieldName.CUSTOMER_NAME: ('ledgers', 'Sundry Debtors'),
            
            # Stock item fields
            FieldName.ITEM_DESCRIPTION: ('stock_items', None),
        }
        
        if field_name in field_mapping:
            data_type, group_filter = field_mapping[field_name]
            
            if data_type == 'companies':
                return load_companies_as_options(field_id, clear_existing)
            elif data_type == 'ledgers':
                return load_ledgers_as_options(field_id, group_filter, clear_existing)
            elif data_type == 'stock_items':
                return load_stock_items_as_options(field_id, group_filter, clear_existing)
        
        # Fallback: check field name string for common patterns
        field_name_str = field_name.value.lower()
        
        if any(keyword in field_name_str for keyword in ['vendor', 'supplier', 'creditor']):
            return load_ledgers_as_options(field_id, 'Sundry Creditors', clear_existing)
        elif any(keyword in field_name_str for keyword in ['customer', 'client', 'debtor']):
            return load_ledgers_as_options(field_id, 'Sundry Debtors', clear_existing)
        elif any(keyword in field_name_str for keyword in ['item', 'product', 'stock']):
            return load_stock_items_as_options(field_id, None, clear_existing)
        elif 'company' in field_name_str:
            return load_companies_as_options(field_id, clear_existing)
        else:
            # Default to all ledgers if no specific pattern is found
            logger.warning(f"Could not determine Tally data type for field {field_name}, defaulting to all ledgers")
            return load_ledgers_as_options(field_id, None, clear_existing)
        
    except Exception as e:
        logger.error(f"Error in auto_load_tally_options for field {field_id}: {e}")
        raise TallyFieldOptionsError(f"Failed to auto-load options: {e}")


# Sub-Template Field Options Functions
def load_stock_items_as_sub_field_options(sub_field_id: int, stock_group: Optional[str] = None, clear_existing: bool = True) -> Dict:
    """
    Load Tally stock items as options for a SELECT sub-template field.
    
    Args:
        sub_field_id: ID of the sub-template field
        stock_group: Optional filter by stock group
        clear_existing: Whether to clear existing options before loading
        
    Returns:
        Dict with success status and loaded options count
        
    Raises:
        TallyFieldOptionsError: If loading fails
    """
    try:
        # Validate sub-field exists and is SELECT type
        sub_field = SubTemplateField.query.get(sub_field_id)
        if not sub_field:
            raise TallyFieldOptionsError(f"Sub-field with ID {sub_field_id} not found")
        
        if sub_field.data_type != DataType.SELECT:
            raise TallyFieldOptionsError(f"Sub-field {sub_field_id} is not a SELECT type field")
        
        # Clear existing options if requested
        if clear_existing:
            SubTemplateFieldOption.query.filter_by(sub_temp_field_id=sub_field_id).delete()
            db.session.flush()
        
        # Connect to Tally and fetch stock items
        with TallyConnector(version="latest") as tally:
            stock_items = get_stock_items_list(tally)
        
        # Filter by stock group if specified
        if stock_group:
            stock_items = [item for item in stock_items if item.get('stock_group', '').lower() == stock_group.lower()]
        
        # Create sub-field options from stock items
        options_created = 0
        for item in stock_items:
            # Skip inactive items
            if not item.get('is_active', True):
                continue
                
            # Use alias if available, otherwise use name
            display_name = item.get('alias') or item['name']
            
            option = SubTemplateFieldOption(
                sub_temp_field_id=sub_field_id,
                option_value=item['name'],      # Always use actual name as value
                option_label=display_name       # Use alias or name for display
            )
            db.session.add(option)
            options_created += 1
        
        db.session.commit()
        
        group_filter_msg = f" (filtered by stock group: {stock_group})" if stock_group else ""
        logger.info(f"Loaded {options_created} stock item options for sub-field {sub_field_id}{group_filter_msg}")
        
        return {
            'success': True,
            'message': f'Successfully loaded {options_created} stock item options{group_filter_msg}',
            'options_count': options_created,
            'sub_field_id': sub_field_id,
            'stock_group': stock_group
        }
        
    except TallyConnectorError as e:
        db.session.rollback()
        logger.error(f"Tally connection error while loading stock items for sub-field {sub_field_id}: {e}")
        raise TallyFieldOptionsError(f"Failed to connect to Tally: {e}")
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error loading stock items for sub-field {sub_field_id}: {e}")
        raise TallyFieldOptionsError(f"Failed to load stock items: {e}")


def load_ledgers_as_sub_field_options(sub_field_id: int, ledger_group: Optional[str] = None, clear_existing: bool = True) -> Dict:
    """
    Load Tally ledgers as options for a SELECT sub-template field.
    
    Args:
        sub_field_id: ID of the sub-template field
        ledger_group: Optional filter by ledger group (e.g., "Sundry Debtors", "Sundry Creditors")
        clear_existing: Whether to clear existing options before loading
        
    Returns:
        Dict with success status and loaded options count
        
    Raises:
        TallyFieldOptionsError: If loading fails
    """
    try:
        # Validate sub-field exists and is SELECT type
        sub_field = SubTemplateField.query.get(sub_field_id)
        if not sub_field:
            raise TallyFieldOptionsError(f"Sub-field with ID {sub_field_id} not found")
        
        if sub_field.data_type != DataType.SELECT:
            raise TallyFieldOptionsError(f"Sub-field {sub_field_id} is not a SELECT type field")
        
        # Clear existing options if requested
        if clear_existing:
            SubTemplateFieldOption.query.filter_by(sub_temp_field_id=sub_field_id).delete()
            db.session.flush()
        
        # Connect to Tally and fetch ledgers
        with TallyConnector(version="latest") as tally:
            ledgers = get_ledgers_list(tally)
        
        # Filter by group if specified
        if ledger_group:
            ledgers = [l for l in ledgers if l.get('group', '').lower() == ledger_group.lower()]
        
        # Create sub-field options from ledgers
        options_created = 0
        for ledger in ledgers:
            # Skip inactive ledgers
            if not ledger.get('is_active', True):
                continue
                
            # Use alias if available, otherwise use name
            display_name = ledger.get('alias') or ledger['name']
            
            option = SubTemplateFieldOption(
                sub_temp_field_id=sub_field_id,
                option_value=ledger['name'],    # Always use actual name as value
                option_label=display_name       # Use alias or name for display
            )
            db.session.add(option)
            options_created += 1
        
        db.session.commit()
        
        group_filter_msg = f" (filtered by group: {ledger_group})" if ledger_group else ""
        logger.info(f"Loaded {options_created} ledger options for sub-field {sub_field_id}{group_filter_msg}")
        
        return {
            'success': True,
            'message': f'Successfully loaded {options_created} ledger options{group_filter_msg}',
            'options_count': options_created,
            'sub_field_id': sub_field_id,
            'ledger_group': ledger_group
        }
        
    except TallyConnectorError as e:
        db.session.rollback()
        logger.error(f"Tally connection error while loading ledgers for sub-field {sub_field_id}: {e}")
        raise TallyFieldOptionsError(f"Failed to connect to Tally: {e}")
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error loading ledgers for sub-field {sub_field_id}: {e}")
        raise TallyFieldOptionsError(f"Failed to load ledgers: {e}")


def auto_load_tally_sub_field_options(sub_field_id: int, clear_existing: bool = True) -> Dict:
    """
    Automatically determine what type of Tally data to load for a sub-field based on field name.
    
    Args:
        sub_field_id: ID of the sub-template field
        clear_existing: Whether to clear existing options before loading
        
    Returns:
        Dict with success status and loaded options count
        
    Raises:
        TallyFieldOptionsError: If loading fails or field type cannot be determined
    """
    try:
        # Get sub-field information
        sub_field = SubTemplateField.query.get(sub_field_id)
        if not sub_field:
            raise TallyFieldOptionsError(f"Sub-field with ID {sub_field_id} not found")
        
        if sub_field.data_type != DataType.SELECT:
            raise TallyFieldOptionsError(f"Sub-field {sub_field_id} is not a SELECT type field")
        
        field_name = sub_field.field_name
        
        # Map field names to Tally data types for sub-fields
        field_mapping = {
            # Stock item fields
            FieldName.ITEM_DESCRIPTION: ('stock_items', None),
            FieldName.ITEM_CODE: ('stock_items', None),
            
            # Vendor/Customer fields  
            FieldName.VENDOR_NAME: ('ledgers', 'Sundry Creditors'),
            FieldName.CUSTOMER_NAME: ('ledgers', 'Sundry Debtors'),
        }
        
        if field_name in field_mapping:
            data_type, group_filter = field_mapping[field_name]
            
            if data_type == 'ledgers':
                return load_ledgers_as_sub_field_options(sub_field_id, group_filter, clear_existing)
            elif data_type == 'stock_items':
                return load_stock_items_as_sub_field_options(sub_field_id, group_filter, clear_existing)
        
        # Fallback: check field name string for common patterns
        field_name_str = field_name.value.lower()
        
        if any(keyword in field_name_str for keyword in ['item', 'product', 'stock', 'description']):
            return load_stock_items_as_sub_field_options(sub_field_id, None, clear_existing)
        elif any(keyword in field_name_str for keyword in ['vendor', 'supplier', 'creditor']):
            return load_ledgers_as_sub_field_options(sub_field_id, 'Sundry Creditors', clear_existing)
        elif any(keyword in field_name_str for keyword in ['customer', 'client', 'debtor']):
            return load_ledgers_as_sub_field_options(sub_field_id, 'Sundry Debtors', clear_existing)
        else:
            # Default to stock items for unknown sub-fields
            logger.warning(f"Could not determine Tally data type for sub-field {field_name}, defaulting to stock items")
            return load_stock_items_as_sub_field_options(sub_field_id, None, clear_existing)
        
    except Exception as e:
        logger.error(f"Error in auto_load_tally_sub_field_options for sub-field {sub_field_id}: {e}")
        raise TallyFieldOptionsError(f"Failed to auto-load sub-field options: {e}")


def get_field_options_summary(field_id: int) -> Dict:
    """
    Get a summary of current options for a field.
    
    Args:
        field_id: ID of the template field
        
    Returns:
        Dict with field information and options summary
    """
    try:
        field = TemplateField.query.get(field_id)
        if not field:
            return {'error': f"Field with ID {field_id} not found"}
        
        options = FieldOption.query.filter_by(field_id=field_id).all()
        
        return {
            'field_id': field_id,
            'field_name': field.field_name.value,
            'field_type': field.field_type.value,
            'options_count': len(options),
            'options': [option.to_dict() for option in options],
            'last_updated': max([opt.updated_at for opt in options]).isoformat() if options else None
        }
        
    except Exception as e:
        logger.error(f"Error getting options summary for field {field_id}: {e}")
        return {'error': f"Failed to get options summary: {e}"}


def refresh_field_options(field_id: int) -> Dict:
    """
    Refresh field options by reloading from Tally using auto-detection.
    
    Args:
        field_id: ID of the template field
        
    Returns:
        Dict with success status and loaded options count
    """
    try:
        # Use auto-load to refresh options
        return auto_load_tally_options(field_id, clear_existing=True)
        
    except Exception as e:
        logger.error(f"Error refreshing options for field {field_id}: {e}")
        raise TallyFieldOptionsError(f"Failed to refresh field options: {e}")


def load_customer_options(field_id: int) -> Dict:
    """
    Load customer ledgers (Sundry Debtors) as options for a SELECT field.
    
    Args:
        field_id: ID of the template field
        
    Returns:
        Dict with success status and loaded options count
    """
    return load_ledgers_as_options(field_id, 'Sundry Debtors', clear_existing=True)


def load_vendor_options(field_id: int) -> Dict:
    """
    Load vendor ledgers (Sundry Creditors) as options for a SELECT field.
    
    Args:
        field_id: ID of the template field
        
    Returns:
        Dict with success status and loaded options count
    """
    return load_ledgers_as_options(field_id, 'Sundry Creditors', clear_existing=True)


def load_all_ledger_options(field_id: int) -> Dict:
    """
    Load all ledgers (no group filter) as options for a SELECT field.
    
    Args:
        field_id: ID of the template field
        
    Returns:
        Dict with success status and loaded options count
    """
    return load_ledgers_as_options(field_id, None, clear_existing=True)