"""
Tally Session Module

TallySession implementation integrated into the OCR backend.
Provides a clean interface to interact with Tally via the TallyConnector .NET SDK.
"""

from __future__ import annotations

import logging
import os
import sys
from contextlib import AbstractContextManager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import TallyConfig

# --- logging -----------------------------------------------------------------

logger = logging.getLogger(__name__)

# --- pythonnet / CLR bootstrap -----------------------------------------------

try:
    from pythonnet import load  # type: ignore
    # Load the CoreCLR runtime *once* at import‑time.
    load("coreclr")
    
    import clr  # noqa: E402  pylint: disable=import-error, wrong-import-position
    CLR_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import pythonnet/CLR: {e}")
    CLR_AVAILABLE = False
    clr = None

# -----------------------------------------------------------------------------


def _ensure_mono():
    """Set *MONO_PATH* on macOS so that the CLR can locate the Mono runtimes."""
    if sys.platform == "darwin":
        os.environ.setdefault(
            "MONO_PATH", "/Library/Frameworks/Mono.framework/Versions/Current"
        )


def _add_assembly_reference(lib_dir: Path | str, assembly_name: str = "TallyConnector"):
    """Append *lib_dir* to *sys.path* and register the assembly with *pythonnet*."""
    if not CLR_AVAILABLE:
        raise RuntimeError("CLR/pythonnet not available")
        
    lib_path = Path(lib_dir).expanduser().resolve()
    if not lib_path.exists():
        raise FileNotFoundError(f"lib_dir not found: {lib_path}")
    if str(lib_path) not in sys.path:
        sys.path.append(str(lib_path))

    try:
        clr.AddReference(assembly_name)
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to load %s from %s", assembly_name, lib_path)
        raise


class TallySession(AbstractContextManager):
    """
    Context‑manager that handles Tally operations through TallyConnector.

    Parameters
    ----------
    lib_dir:
        Folder containing `TallyConnector.dll` and its dependencies.
    version:
        * "legacy" – Uses the classic `TallyConnector.Services.TallyService`
        * "latest" – Uses `TallyConnector.Services.TallyPrime.V6.TallyPrimeService`
    host:
        The Tally host URL. If not provided, will be resolved from api_key.
        Defaults to `http://localhost:9000` if neither host nor api_key is provided.
    api_key:
        User's API key for dynamic host resolution. If provided, host will be
        constructed as `http://{api_key}.holanitunnel.net`.
    port:
        Tally service port. Defaults to 80.
    """

    def __init__(
        self,
        lib_dir: str | Path = None,
        *,
        version: str = "legacy",
        host: str = None,
        api_key: str = None,
        port: int = None,
    ) -> None:
        if not CLR_AVAILABLE:
            raise RuntimeError("CLR/pythonnet not available. Install pythonnet package.")
            
        _ensure_mono()
        
        # Use config to get lib_dir if not provided
        if lib_dir is None:
            lib_dir = TallyConfig.get_lib_dir(version)
            
        # Use config to get port if not provided
        if port is None:
            port = TallyConfig.DEFAULT_PORT
            
        # Resolve host dynamically from API key or use provided host
        resolved_host = self._resolve_host(host, api_key)
            
        if version == "latest":
            _add_assembly_reference(lib_dir, "TallyConnectorNew")
        else:
            _add_assembly_reference(lib_dir, "TallyConnector")
        
        self.version = version.lower()
        self.host = resolved_host
        self.api_key = api_key
        self.port = port
        self.lib_dir = lib_dir
        
        # Version-specific imports after CLR reference is added
        self._setup_version_specific_imports()
        
        self._svc = self._create_service()

    def _setup_version_specific_imports(self):
        """Handle version-specific imports based on TallyConnector version."""
        
        # Initialize defaults
        self.request_options = None
        self.master_request_options = None
        self.post_request_options = None
        self._vouchers_available = False
        self._units_available = False
        self._ledger_import_path = None
        self._stock_item_import_path = None
        self._unit_import_path = None
        
        if self.version == "latest":
            # Latest version specific imports
            try:
                from TallyConnectorNew.Core.Models.Request import RequestOptions  # type: ignore
                self.request_options = RequestOptions()
                logger.info("RequestOptions available for latest version")
            except ImportError:
                logger.warning("RequestOptions not available in latest version")
                self.request_options = None
                
            # Try different import paths for latest version
            try:
                # In latest version, Ledger might be in a different namespace
                from TallyConnectorNew.Core.Models import Ledger  # type: ignore
                self._ledger_import_path = "TallyConnectorNew.Core.Models"
                logger.info("Using Ledger from TallyConnectorNew.Core.Models")
            except ImportError:
                logger.warning("Ledger not available from TallyConnectorNew.Core.Models in latest version")
                
        elif self.version == "legacy":
            # Legacy version RequestOptions setup
            self._setup_legacy_request_options()
            
            # Legacy version uses Masters namespace
            try:
                from TallyConnector.Core.Models.Masters import Ledger  # type: ignore
                self._ledger_import_path = "TallyConnector.Core.Models.Masters"
                logger.info("Using Ledger from TallyConnector.Core.Models.Masters")
            except ImportError:
                logger.warning("Ledger not available from Masters namespace in legacy version")
        
        # Common voucher-related imports (try both versions)
        self._load_voucher_functionality()
        
        # Load unit-related functionality
        self._load_unit_functionality()
        
    def _load_voucher_functionality(self):
        """Load voucher-related classes and converters."""
        try:
            from TallyConnector.Core.Models import (  # type: ignore
                Voucher,
                VoucherLedger, 
                BillAllocations,
                AllInventoryAllocations,
                BatchAllocations,
                BaseVoucherLedger,
                Action,
                VoucherViewType,
                BillRefType
            )
            from TallyConnector.Core.Converters.XMLConverterHelpers import (  # type: ignore
                TallyDate,
                TallyAmount,
                TallyQuantity,
                TallyRate,
                TallyYesNo,
            )
            from System import DateTime, Decimal  # type: ignore
            from System.Collections.Generic import List  # type: ignore
            
            # Store these as instance attributes for use in voucher creation
            self._voucher_classes = {
                'Voucher': Voucher,
                'VoucherLedger': VoucherLedger,
                'BillAllocations': BillAllocations,
                'AllInventoryAllocations': AllInventoryAllocations,
                'BatchAllocations': BatchAllocations,
                'BaseVoucherLedger': BaseVoucherLedger,
                'Action': Action,
                'VoucherViewType': VoucherViewType,
                'BillRefType': BillRefType
            }
            self._tally_converters = {
                'TallyDate': TallyDate,
                'TallyAmount': TallyAmount,
                'TallyQuantity': TallyQuantity,
                'TallyRate': TallyRate,
                'TallyYesNo': TallyYesNo
            }
            self._system_types = {
                'DateTime': DateTime,
                'Decimal': Decimal,
                'List': List
            }
            self._vouchers_available = True
            logger.info("Voucher functionality loaded successfully")
        except ImportError as e:
            logger.warning("Voucher classes not available: %s", e)
            self._vouchers_available = False

    def _setup_legacy_request_options(self):
        """Setup RequestOptions for legacy version."""
        try:
            from TallyConnector.Core.Models import (  # type: ignore
                RequestOptions,
                MasterRequestOptions,
                PostRequestOptions
            )
            
            self.request_options = RequestOptions()
            self.master_request_options = MasterRequestOptions()
            self.post_request_options = PostRequestOptions()
            logger.info("RequestOptions loaded for legacy version")
            
        except ImportError as e:
            logger.warning("RequestOptions not available in legacy version: %s", e)
            self.request_options = None
            self.master_request_options = None
            self.post_request_options = None

    def _load_unit_functionality(self):
        """Load unit-related classes and functionality."""
        try:
            from TallyConnector.Core.Models.Masters.Inventory import Unit  # type: ignore
            from TallyConnector.Core.Models import Action  # type: ignore
            from TallyConnector.Core.Converters.XMLConverterHelpers import TallyYesNo  # type: ignore
            
            # Store unit classes for use in unit creation
            self._unit_classes = {
                'Unit': Unit,
                'Action': Action,
                'TallyYesNo': TallyYesNo
            }
            
            # Set unit import path for dynamic imports
            self._unit_import_path = "TallyConnector.Core.Models.Masters.Inventory"
            self._units_available = True
            logger.info("Unit functionality loaded successfully")
            
        except ImportError as e:
            logger.warning("Unit classes not available: %s", e)
            self._units_available = False

    # --------------------------------------------------------------------- API

    # basic CRUD helpers -------------------------------------------------------

    def get_companies(self):
        """Return a .NET `IEnumerable<Company>` containing all companies."""
        return self._svc.GetCompaniesAsync().Result

    def get_ledgers(self, request_options: Any = None):
        """Get ledgers. Uses RequestOptions if available, otherwise uses default parameters."""
        if request_options is None and self.request_options is not None:
            request_options = self.request_options
        
        if request_options is not None:
            return self._svc.GetLedgersAsync(request_options).Result
        else:
            # For legacy version without RequestOptions
            return self._svc.GetLedgersAsync().Result

    def get_stock_items(self, request_options: Any = None):
        """Get stock items. Uses RequestOptions if available, otherwise uses default parameters."""
        if request_options is None and self.request_options is not None:
            request_options = self.request_options
            
        if request_options is not None:
            return self._svc.GetStockItemsAsync(request_options).Result
        else:
            # For legacy version without RequestOptions
            return self._svc.GetStockItemsAsync().Result

    def get_vouchers(self, request_options: Any = None):
        """Get vouchers. Uses RequestOptions if available, otherwise uses default parameters."""
        if request_options is None and self.request_options is not None:
            request_options = self.request_options
            
        if request_options is not None:
            return self._svc.GetVouchersAsync(request_options).Result
        else:
            # For legacy version without RequestOptions
            return self._svc.GetVouchersAsync().Result

    def get_units(self, request_options: Any = None):
        """Get units. Uses RequestOptions if available, otherwise uses default parameters."""
        if not self._units_available:
            raise RuntimeError("Unit functionality not available - check TallyConnector imports")
            
        if request_options is None and self.request_options is not None:
            request_options = self.request_options
            
        # Import the Unit class to use as generic type parameter
        Unit = self._unit_classes['Unit']
        
        if request_options is not None:
            # Call the generic method with Unit type parameter
            return self._svc.GetUnitsAsync[Unit](request_options).Result
        else:
            # Try calling without RequestOptions (should use default null)
            return self._svc.GetUnitsAsync[Unit]().Result

    def get_unit(self, unit_name: str, request_options: Any = None):
        """Get specific unit by name."""
        if not self._units_available:
            raise RuntimeError("Unit functionality not available - check TallyConnector imports")
            
        if request_options is None and self.master_request_options is not None:
            request_options = self.master_request_options
            
        if request_options is not None:
            # GetUnitAsync might also be generic, try with Unit type
            try:
                Unit = self._unit_classes['Unit']
                return self._svc.GetUnitAsync[Unit](unit_name, request_options).Result
            except Exception:
                # Fallback to non-generic call if the above fails
                return self._svc.GetUnitAsync(unit_name, request_options).Result
        else:
            raise RuntimeError("MasterRequestOptions required for GetUnitAsync")

    def create_ledger(
        self,
        name: str,
        *,
        group: str = "Sundry Debtors",
        alias: Optional[str] = None,
        **kwargs,
    ):
        """Create a new Ledger; returns the response from Tally."""
        if not self._ledger_import_path:
            raise RuntimeError(f"Ledger class not available for version '{self.version}'. Check TallyConnector installation.")
        
        # Dynamic import based on version
        if self._ledger_import_path == "TallyConnector.Core.Models.Masters":
            from TallyConnector.Core.Models.Masters import Ledger  # type: ignore
        elif self._ledger_import_path == "TallyConnector.Core.Models":
            from TallyConnector.Core.Models import Ledger  # type: ignore
        else:
            raise RuntimeError(f"Unknown ledger import path: {self._ledger_import_path}")


        ledger = Ledger()
        ledger.Name = name
        ledger.OldName = alias or name
        ledger.Group = group

        # apply extra fields via **kwargs (e.g. Email)
        for k, v in kwargs.items():
            if hasattr(ledger, k):
                setattr(ledger, k, v)
            else:
                logger.warning("Unknown Ledger attribute: %s", k)

        resp = self._svc.PostLedgerAsync(ledger).Result
        return resp.Response if hasattr(resp, "Response") else resp

    def create_voucher(
        self,
        *,
        voucher_type: str,
        date: datetime,
        party_name: str,
        items: List[Dict],
        voucher_number: Optional[str] = None,
        narration: str = "",
        bill_ref: Optional[str] = None,
        post: bool = True,
    ):
        """
        Build (and optionally POST) a voucher to Tally.

        Parameters
        ----------
        voucher_type:
            E.g. "Sales", "Purchase", "Receipt", "Payment"
        date:
            Python datetime -> converts to TallyDate internally
        party_name:
            Ledger name of party
        items:
            List of dicts with keys:
                - stock_item (str): Name of stock item
                - qty (float): Quantity
                - rate (float): Rate per unit
                - unit (str, optional): Unit of measurement, defaults to "Nos"
                - amount (float, optional): Total amount, auto-calculated if not provided
                - ledger (str, optional): Sales/purchase ledger name
                - godown (str, optional): Godown name, defaults to "Main Location"
                - batch (str, optional): Batch name, defaults to "Primary Batch"
        voucher_number:
            Optional voucher number
        narration:
            Free text description
        bill_ref:
            Creates a Bill Allocation under party ledger
        post:
            If True – pushes to Tally and returns response;
            otherwise just returns the Voucher object for inspection.

        Returns
        -------
        Response from Tally if post=True, otherwise the Voucher object
        """
        if not self._vouchers_available:
            raise RuntimeError("Voucher functionality not available - check TallyConnector imports")

        # Get classes from stored imports
        Voucher = self._voucher_classes['Voucher']
        VoucherLedger = self._voucher_classes['VoucherLedger']
        BillAllocations = self._voucher_classes['BillAllocations']
        AllInventoryAllocations = self._voucher_classes['AllInventoryAllocations']
        BatchAllocations = self._voucher_classes['BatchAllocations']
        BaseVoucherLedger = self._voucher_classes['BaseVoucherLedger']
        Action = self._voucher_classes['Action']
        VoucherViewType = self._voucher_classes['VoucherViewType']
        BillRefType = self._voucher_classes['BillRefType']
        
        # Get converter functions
        TallyDate = self._tally_converters['TallyDate']
        TallyAmount = self._tally_converters['TallyAmount']
        TallyQuantity = self._tally_converters['TallyQuantity']
        TallyRate = self._tally_converters['TallyRate']
        TallyYesNo = self._tally_converters['TallyYesNo']

        # Create voucher
        voucher = Voucher()
        voucher.Action = Action.Create
        voucher.VoucherType = voucher_type
        voucher.Date = TallyDate(date)
        voucher.EffectiveDate = voucher.Date
        voucher.View = VoucherViewType.InvoiceVoucherView
        if voucher_number:
            voucher.VoucherNumber = str(voucher_number)
        voucher.IsInvoice = TallyYesNo(True)
        voucher.PartyName = party_name
        if narration:
            voucher.Narration = narration

        # Party ledger (Debit or Credit depending on voucher type)
        sign = -1 if voucher_type.lower() in ("sales", "receipt") else 1
        total_amount = sum(item.get("amount", item["rate"] * item["qty"]) for item in items)
        party_led = VoucherLedger(party_name, TallyAmount(sign * total_amount))
        party_led.IsPartyLedger = TallyYesNo(True)

        # Add bill allocation if specified
        if bill_ref:
            party_led.BillAllocations = []
            bill = BillAllocations()
            bill.Name = bill_ref
            bill.Amount = party_led.Amount
            bill.BillType = BillRefType.NewRef
            party_led.BillAllocations.Add(bill)

        voucher.Ledgers = []
        voucher.Ledgers.Add(party_led)

        # Inventory lines
        voucher.InventoryAllocations = []
        for item in items:
            stock_name = item["stock_item"]
            qty = item["qty"]
            unit = item.get("unit", "Nos")
            rate = item.get("rate", 0.0)
            amount = item.get("amount", rate * qty)

            inv = AllInventoryAllocations()
            inv.StockItemName = stock_name
            inv.BilledQuantity = TallyQuantity(qty, unit)
            inv.ActualQuantity = TallyQuantity(qty, unit)
            inv.Amount = TallyAmount(amount)
            inv.Rate = TallyRate(rate, unit)

            # Batch allocation (required if batch-wise inventory is enabled)
            batch = BatchAllocations()
            batch.GodownName = item.get("godown", "Main Location")
            batch.BatchName = item.get("batch", "Primary Batch")
            batch.BilledQuantity = inv.BilledQuantity
            batch.ActualQuantity = inv.ActualQuantity
            batch.Amount = inv.Amount
            inv.BatchAllocations = []
            inv.BatchAllocations.Add(batch)

            # Sales/Purchase ledger within inventory line
            if ledger := item.get("ledger"):
                led = BaseVoucherLedger()
                led.LedgerName = ledger
                led.Amount = inv.Amount
                inv.Ledgers = []
                inv.Ledgers.Add(led)

            voucher.InventoryAllocations.Add(inv)

        logger.debug("Voucher XML:\n%s", voucher.GetXML())

        if post:
            resp = self._svc.PostVoucherAsync(voucher).Result
            response = resp.Response if hasattr(resp, "Response") else resp
            logger.info("Posted voucher – response: %s", response)
            return response
        else:
            return voucher

    def create_stock_item(
        self,
        name: str,
        *,
        base_unit: str = "Nos",
        stock_group: Optional[str] = None,
        **kwargs,
    ):
        """
        Create a new Stock Item (mainly for legacy version).
        
        Parameters
        ----------
        name: str
            Name of the stock item
        base_unit: str
            Base unit of measurement (default: "Nos")
        stock_group: str, optional
            Stock group name (defaults to "Primary" if not specified)
        **kwargs:
            Additional stock item attributes
            
        Returns
        -------
        Response from Tally
        """
        if self.version == "legacy":
            try:
                from TallyConnector.Core.Models.Masters.Inventory import StockItem  # type: ignore
                from TallyConnector.Core.Models import Action  # type: ignore
                
                stock_item = StockItem()
                stock_item.Name = name
                stock_item.BaseUnit = base_unit
                stock_item.StockGroup = stock_group or TallyConfig.DEFAULT_STOCK_GROUP
                stock_item.Action = Action.Create
                
                # Apply extra fields via **kwargs
                for k, v in kwargs.items():
                    if hasattr(stock_item, k):
                        setattr(stock_item, k, v)
                    else:
                        logger.warning("Unknown StockItem attribute: %s", k)
                
                resp = self._svc.PostStockItemAsync(stock_item).Result
                return resp.Response if hasattr(resp, "Response") else resp
                
            except ImportError as e:
                raise RuntimeError(f"StockItem creation not available in legacy version: {e}")
        else:
            raise RuntimeError(f"StockItem creation not implemented for version '{self.version}'. Use legacy version.")

    def create_unit(
        self,
        name: str,
        *,
        decimal_places: int = 0,
        is_simple: bool = True,
        base_unit: Optional[str] = None,
        conversion: float = 1.0,
        **kwargs,
    ):
        """
        Create a new Unit of Measure.
        
        Parameters
        ----------
        name: str
            Name/Symbol of the unit (e.g., "kg", "litre", "pcs")
        decimal_places: int
            Number of decimal places (0 to 4, default: 0)
        is_simple: bool
            True for simple units, False for compound units (default: True)
        base_unit: str, optional
            Base unit for compound units (required if is_simple=False)
        conversion: float
            Conversion factor for compound units (default: 1.0)
        **kwargs:
            Additional unit attributes
            
        Returns
        -------
        Response from Tally
        """
        if not self._units_available:
            raise RuntimeError("Unit functionality not available - check TallyConnector imports")
            
        if self.version == "legacy":
            try:
                # Get classes from stored imports
                Unit = self._unit_classes['Unit']
                Action = self._unit_classes['Action']
                TallyYesNo = self._unit_classes['TallyYesNo']
                
                unit = Unit()
                unit.Name = name
                unit.DecimalPlaces = decimal_places
                unit.IsSimpleUnit = TallyYesNo(is_simple)
                unit.Action = Action.Create
                
                # For compound units
                if not is_simple:
                    if not base_unit:
                        raise ValueError("base_unit is required for compound units")
                    unit.BaseUnit = base_unit
                    unit.Conversion = conversion
                
                # Apply extra fields via **kwargs
                for k, v in kwargs.items():
                    if hasattr(unit, k):
                        # Convert boolean values to TallyYesNo if needed
                        if isinstance(v, bool) and k in ['IsGstExcluded']:
                            v = TallyYesNo(v)
                        setattr(unit, k, v)
                    else:
                        logger.warning("Unknown Unit attribute: %s", k)
                
                # Use PostRequestOptions if available
                post_options = self.post_request_options
                if post_options is not None:
                    # PostUnitAsync is also generic
                    resp = self._svc.PostUnitAsync[Unit](unit, post_options).Result
                else:
                    # Fallback without PostRequestOptions
                    resp = self._svc.PostUnitAsync[Unit](unit).Result
                    
                return resp.Response if hasattr(resp, "Response") else resp
                
            except ImportError as e:
                raise RuntimeError(f"Unit creation not available in legacy version: {e}")
        else:
            raise RuntimeError(f"Unit creation not implemented for version '{self.version}'. Use legacy version.")

    def get_version_info(self):
        """Get information about what features are available in the current version."""
        info = {
            "version": self.version,
            "lib_dir": str(self.lib_dir),
            "host": self.host,
            "port": self.port,
            "api_key": self.api_key[:8] + "..." if self.api_key else None,  # Only show first 8 chars for security
            "host_source": "api_key" if self.api_key else "explicit" if self.host != TallyConfig.DEFAULT_HOST else "default",
            "request_options_available": self.request_options is not None,
            "master_request_options_available": self.master_request_options is not None,
            "post_request_options_available": self.post_request_options is not None,
            "vouchers_available": self._vouchers_available,
            "units_available": self._units_available,
            "ledger_import_path": self._ledger_import_path,
            "unit_import_path": self._unit_import_path,
            "stock_item_available": self.version == "legacy"
        }
        return info

    # context mgmt -------------------------------------------------------------

    def __enter__(self):
        # sanity check connectivity
        # Note: Skipping connection check for now as it may cause issues
        # if not self._svc.CheckAsync().Result:
        #     raise ConnectionError(
        #         "Tally appears to be offline. Ensure Tally is running and ODBC is enabled."
        #     )
        logger.info("Connected to Tally at %s (version: %s)", self.host, self.version)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # the .NET service does not expose *IDisposable*, so nothing special
        logger.info("Disconnected from Tally (%s)", self.host)
        return False  # propagate exceptions

    # ------------------------------------------------------------------- internals

    def _resolve_host(self, host: str = None, api_key: str = None) -> str:
        """
        Resolve the appropriate host URL based on provided parameters.
        
        Parameters
        ----------
        host : str, optional
            Explicitly provided host URL
        api_key : str, optional
            User's API key for dynamic host resolution
            
        Returns
        -------
        str
            Resolved host URL
            
        Raises
        ------
        ValueError
            If neither host nor api_key is provided and fallback is disabled
        """
        # If host is explicitly provided, use it
        if host:
            logger.info("Using explicitly provided host: %s", host)
            return host
        
        # If api_key is provided, resolve host from it
        if api_key:
            try:
                resolved_host = TallyConfig.resolve_host_from_api_key(api_key)
                logger.info("Resolved host from API key: %s", resolved_host)
                return resolved_host
            except ValueError as e:
                logger.warning("Failed to resolve host from API key: %s", e)
                # If fallback is enabled, TallyConfig.resolve_host_from_api_key will return default
                # If not, it will raise the exception which we re-raise here
                raise
        
        # Neither host nor api_key provided - use default
        logger.info("No host or API key provided, using default host: %s", TallyConfig.DEFAULT_HOST)
        return TallyConfig.DEFAULT_HOST

    def _create_service(self):
        """Create the appropriate TallyService based on version."""
        if self.version == "legacy":
            from TallyConnector.Services import TallyService
            tally = TallyService()
            tally.Setup(self.host, self.port)
            return tally
        elif self.version == "latest":
            from TallyConnectorNew.Services.TallyPrime.V6 import (  # type: ignore
                TallyPrimeService,
            )
            tally = TallyPrimeService()
            tally.SetupTallyService(self.host, self.port) 
            return tally
        else:
            raise ValueError(
                "version must be 'legacy', 'latest' – got %r" % self.version
            )


    @classmethod
    def from_user(cls, user, **kwargs):
        """
        Create a TallySession instance from a User object.
        
        Parameters
        ----------
        user : User
            User model instance with api_key attribute
        **kwargs
            Additional parameters to pass to TallySession constructor
            
        Returns
        -------
        TallySession
            Configured TallySession instance
            
        Raises
        ------
        AttributeError
            If user object doesn't have api_key attribute
        """
        if not hasattr(user, 'api_key'):
            raise AttributeError("User object must have an 'api_key' attribute")
        
        return cls(api_key=user.api_key, **kwargs)


__all__ = ["TallySession"]
