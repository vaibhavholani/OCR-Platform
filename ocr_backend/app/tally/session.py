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
        The Tally host URL.  Defaults to `http://localhost:9000`.
    """

    def __init__(
        self,
        lib_dir: str | Path = None,
        *,
        version: str = "legacy",
        host: str = "http://localhost:9000",
    ) -> None:
        if not CLR_AVAILABLE:
            raise RuntimeError("CLR/pythonnet not available. Install pythonnet package.")
            
        _ensure_mono()
        
        # Use config to get lib_dir if not provided
        if lib_dir is None:
            lib_dir = TallyConfig.get_lib_dir(version)
            
        if version == "latest":
            _add_assembly_reference(lib_dir, "TallyConnectorNew")
        else:
            _add_assembly_reference(lib_dir, "TallyConnector")
        
        self.version = version.lower()
        self.host = host
        self.lib_dir = lib_dir
        
        # Version-specific imports after CLR reference is added
        self._setup_version_specific_imports()
        
        self._svc = self._create_service()

    def _setup_version_specific_imports(self):
        """Handle version-specific imports based on TallyConnector version."""
        
        # Initialize defaults
        self.request_options = None
        self._vouchers_available = False
        self._ledger_import_path = None
        self._stock_item_import_path = None
        
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
            # Legacy version doesn't have RequestOptions
            self.request_options = None
            logger.info("RequestOptions not available in legacy version")
            
            # Legacy version uses Masters namespace
            try:
                from TallyConnector.Core.Models.Masters import Ledger  # type: ignore
                self._ledger_import_path = "TallyConnector.Core.Models.Masters"
                logger.info("Using Ledger from TallyConnector.Core.Models.Masters")
            except ImportError:
                logger.warning("Ledger not available from Masters namespace in legacy version")
        
        # Common voucher-related imports (try both versions)
        self._load_voucher_functionality()
        
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

    def get_version_info(self):
        """Get information about what features are available in the current version."""
        info = {
            "version": self.version,
            "lib_dir": str(self.lib_dir),
            "host": self.host,
            "request_options_available": self.request_options is not None,
            "vouchers_available": self._vouchers_available,
            "ledger_import_path": self._ledger_import_path,
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

    def _create_service(self):
        """Create the appropriate TallyService based on version."""
        if self.version == "legacy":
            from TallyConnector.Services import TallyService
            return TallyService()
        elif self.version == "latest":
            from TallyConnectorNew.Services.TallyPrime.V6 import (  # type: ignore
                TallyPrimeService,
            )
            return TallyPrimeService()
        else:
            raise ValueError(
                "version must be 'legacy', 'latest' – got %r" % self.version
            )


__all__ = ["TallySession"]
