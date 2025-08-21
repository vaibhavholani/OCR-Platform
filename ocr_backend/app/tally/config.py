"""
Tally Configuration

Configuration settings for Tally connector library.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

class TallyConfig:
    """Configuration class for Tally connector settings."""
    
    # Tally Connection Settings
    DEFAULT_VERSION = "legacy"  # or "latest"
    DEFAULT_HOST = "http://localhost:9000"
    
    # Alternative library directories for different versions
    # _PARENT = Path(__file__).parent
    # prefer an explicit environment override, otherwise use this file's parent directory
    env_dir = os.environ.get("TALLY_PARENT_DIR")
    _PARENT = str(Path(env_dir).expanduser().resolve())


    LEGACY_LIB_DIR = os.path.join(_PARENT, "tally_dll_files", "lib")
    LATEST_LIB_DIR = os.path.join(_PARENT, "tally_dll_files", "lib_new_name_space")


    DEFAULT_LIB_DIR = LEGACY_LIB_DIR  # Default to legacy
    
    # Default values for entity creation
    DEFAULT_LEDGER_GROUP = "Sundry Debtors"
    DEFAULT_SUPPLIER_GROUP = "Sundry Creditors"
    DEFAULT_STOCK_GROUP = "Primary"
    DEFAULT_UNIT = "PCS"
    DEFAULT_GODOWN = "Main Location"
    DEFAULT_BATCH = "Primary Batch"
    
    # Common units and their properties for easy reference
    COMMON_UNITS = {
        'PCS': {'formal_name': 'Pieces', 'decimal_places': 0},
        'KG': {'formal_name': 'Kilogram', 'decimal_places': 3},
        'LITRE': {'formal_name': 'Litre', 'decimal_places': 2},
        'METER': {'formal_name': 'Meter', 'decimal_places': 2},
        'BOX': {'formal_name': 'Box', 'decimal_places': 0},
        'SET': {'formal_name': 'Set', 'decimal_places': 0},
        'PACK': {'formal_name': 'Pack', 'decimal_places': 0},
        'BOTTLE': {'formal_name': 'Bottle', 'decimal_places': 0},
        'GRAM': {'formal_name': 'Gram', 'decimal_places': 2},
        'TON': {'formal_name': 'Ton', 'decimal_places': 3}
    }
    
    # Sales and Purchase ledger defaults
    DEFAULT_SALES_LEDGER = "Sales Account"
    DEFAULT_PURCHASE_LEDGER = "Imported Goods"
    
    # Voucher defaults
    DEFAULT_VOUCHER_VIEW = "Invoice Voucher View"
    
    @classmethod
    def get_lib_dir(cls, version: str = None) -> str:
        """Get the appropriate library directory based on version."""
        if version == "latest":
            return cls.LATEST_LIB_DIR
        elif version == "legacy":
            return cls.LEGACY_LIB_DIR
        else:
            return cls.DEFAULT_LIB_DIR
    
    @classmethod
    def get_default_ledger_group(cls, ledger_type: str = "customer") -> str:
        """Get default ledger group based on type."""
        if ledger_type.lower() in ["supplier", "vendor", "creditor"]:
            return cls.DEFAULT_SUPPLIER_GROUP
        else:
            return cls.DEFAULT_LEDGER_GROUP
