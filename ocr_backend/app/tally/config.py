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
    
    # Development Mode - Simple toggle
    DEV_MODE = os.environ.get("TALLY_DEV_MODE", "true").lower() == "true"
    
    # Tally Connection Settings
    DEFAULT_VERSION = "legacy"  # or "latest"
    DEV_HOST = "http://localhost"
    DEV_PORT = 9000
    HTTP_PORT = 80
    DEFAULT_HOST = DEV_HOST
    DEFAULT_PORT = DEV_PORT
    
    # Tunnel Configuration
    TUNNEL_DOMAIN = "holanitunnel.net"  # Configurable tunnel domain
    TUNNEL_PROTOCOL = "http"  # Can be http or https
    
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
    
    @classmethod
    def get_host_and_port(cls, api_key: str = None) -> tuple[str, int]:
        """
        Smart host/port resolution based on dev mode and user context.
        
        Parameters
        ----------
        api_key : str, optional
            User's API key (if not provided, tries to auto-detect from context)
            
        Returns
        -------
        tuple[str, int]
            (host, port)
            
        Raises
        ------
        ValueError
            If api_key is required but not available
        """
        
        if cls.DEV_MODE:
            return cls.DEV_HOST, cls.DEV_PORT
        else:
            # Try to get api_key from parameter, then try auto-detection
            effective_api_key = api_key or cls._try_get_user_api_key()
            
            if not effective_api_key:
                raise ValueError("API key is required when not in dev mode. Either provide api_key parameter or ensure user context is available.")
            
            host = f"{cls.TUNNEL_PROTOCOL}://{effective_api_key}.{cls.TUNNEL_DOMAIN}"
            return host, cls.HTTP_PORT

    @classmethod
    def _try_get_user_api_key(cls) -> str | None:
        """
        Try to automatically get API key from various sources.
        
        Returns
        -------
        str | None
            API key if found, None otherwise
        """
        try:
            # Try Flask application context
            from flask import has_app_context, g, request, session
            
            if has_app_context():
                # Option 1: Check Flask g object
                if hasattr(g, 'user') and hasattr(g.user, 'api_key'):
                    return g.user.api_key
                
                # Option 2: Check Flask g for api_key directly
                if hasattr(g, 'api_key'):
                    return g.api_key
                    
                # Option 3: Check request headers (common pattern)
                if request and 'X-API-Key' in request.headers:
                    return request.headers['X-API-Key']
                    
                # Option 4: Check session
                if session and 'api_key' in session:
                    return session['api_key']
                    
                # Option 5: Check session user
                if session and 'user' in session:
                    user_data = session['user']
                    if isinstance(user_data, dict) and 'api_key' in user_data:
                        return user_data['api_key']
        
        except (ImportError, RuntimeError):
            # Not in Flask context or Flask not available
            pass
        
        # Try environment variable as fallback
        return os.environ.get("TALLY_API_KEY")
