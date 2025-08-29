# Tally Module Documentation

This document provides a detailed overview of the components within the `tally` module, which facilitates integration with Tally ERP.

## TallyConfig Class

**File:** `config.py`

The `TallyConfig` class provides configuration settings and utility methods for connecting to and interacting with Tally.

### Attributes:

*   **`DEFAULT_VERSION`** (str):
    *   **Description:** Default Tally API version to use ("legacy" or "latest").
    *   **Default:** `"legacy"`
*   **`DEV_HOST`** (str):
    *   **Description:** Development host URL for Tally.
    *   **Default:** `"http://localhost:9000"`
*   **`DEFAULT_HOST`** (str):
    *   **Description:** Default host URL for Tally.
    *   **Default:** `DEV_HOST`
*   **`DEFAULT_PORT`** (int):
    *   **Description:** Default port for Tally connection.
    *   **Default:** `80`
*   **`TUNNEL_DOMAIN`** (str):
    *   **Description:** Domain for the Tally tunnel service.
    *   **Default:** `"holanitunnel.net"`
*   **`TUNNEL_PROTOCOL`** (str):
    *   **Description:** Protocol for the Tally tunnel ("http" or "https").
    *   **Default:** `"http"`
*   **`ENABLE_FALLBACK_TO_DEFAULT`** (bool):
    *   **Description:** If `True`, falls back to `DEFAULT_HOST` if API key resolution fails.
    *   **Default:** `True`
*   **`LEGACY_LIB_DIR`** (str):
    *   **Description:** Directory containing DLLs for the legacy Tally API version.
*   **`LATEST_LIB_DIR`** (str):
    *   **Description:** Directory containing DLLs for the latest Tally API version.
*   **`DEFAULT_LIB_DIR`** (str):
    *   **Description:** Default library directory, currently set to `LEGACY_LIB_DIR`.
*   **`DEFAULT_LEDGER_GROUP`** (str):
    *   **Description:** Default ledger group for general ledgers.
    *   **Default:** `"Sundry Debtors"`
*   **`DEFAULT_SUPPLIER_GROUP`** (str):
    *   **Description:** Default ledger group for supplier ledgers.
    *   **Default:** `"Sundry Creditors"`
*   **`DEFAULT_STOCK_GROUP`** (str):
    *   **Description:** Default stock group for new stock items.
    *   **Default:** `"Primary"`
*   **`DEFAULT_UNIT`** (str):
    *   **Description:** Default unit of measure.
    *   **Default:** `"PCS"`
*   **`DEFAULT_GODOWN`** (str):
    *   **Description:** Default godown (location) for inventory.
    *   **Default:** `"Main Location"`
*   **`DEFAULT_BATCH`** (str):
    *   **Description:** Default batch name for inventory.
    *   **Default:** `"Primary Batch"`
*   **`COMMON_UNITS`** (dict):
    *   **Description:** A dictionary of common units of measure with their formal names and decimal places.
*   **`DEFAULT_SALES_LEDGER`** (str):
    *   **Description:** Default sales ledger account.
    *   **Default:** `"Sales Account"`
*   **`DEFAULT_PURCHASE_LEDGER`** (str):
    *   **Description:** Default purchase ledger account.
    *   **Default:** `"Imported Goods"`
*   **`DEFAULT_VOUCHER_VIEW`** (str):
    *   **Description:** Default voucher view type.
    *   **Default:** `"Invoice Voucher View"`

### Methods:

*   **`get_lib_dir(version: str = None) -> str`**:
    *   **Description:** Returns the appropriate library directory based on the specified Tally API version.
    *   **Parameters:**
        *   `version` (str, optional): The Tally API version ("legacy" or "latest"). Defaults to `DEFAULT_LIB_DIR`.
    *   **Returns:** `str` - The path to the library directory.
*   **`get_default_ledger_group(ledger_type: str = "customer") -> str`**:
    *   **Description:** Returns the default ledger group based on the specified ledger type.
    *   **Parameters:**
        *   `ledger_type` (str, optional): The type of ledger ("customer", "supplier", "vendor", "creditor"). Defaults to "customer".
    *   **Returns:** `str` - The default ledger group name.
*   **`resolve_host_from_api_key(api_key: str = None) -> str`**:
    *   **Description:** Resolves the Tally host URL from a given API key, potentially using a tunnel service.
    *   **Parameters:**
        *   `api_key` (str, optional): The user's API key (32-character hex string).
    *   **Returns:** `str` - The resolved host URL.
    *   **Raises:** `ValueError` if the API key is invalid and fallback is disabled.

## TallyConnector Class

**File:** `connector.py`

The `TallyConnector` class provides a high-level interface for connecting to and performing operations with Tally. It acts as a wrapper around `TallySession` and handles connection management.

### Exceptions:

*   **`TallyConnectorError`**: Custom exception for Tally connector errors.

### Constructor:

*   **`__init__(self, lib_dir: Optional[str] = None, version: str = TallyConfig.DEFAULT_VERSION, host: str = TallyConfig.DEFAULT_HOST)`**:
    *   **Description:** Initializes the Tally connector.
    *   **Parameters:**
        *   `lib_dir` (str, optional): Path to TallyConnector library directory. If `None`, it uses `TallyConfig.get_lib_dir()`.
        *   `version` (str): TallyConnector version ("legacy" or "latest"). Defaults to `TallyConfig.DEFAULT_VERSION`.
        *   `host` (str): Tally host URL. Defaults to `TallyConfig.DEFAULT_HOST`.
    *   **Raises:** `TallyConnectorError` if `TallySession` is not available (e.g., `pythonnet` not installed or DLLs inaccessible).

### Context Manager Methods:

*   **`__enter__(self)`**:
    *   **Description:** Establishes a connection to Tally when entering a `with` statement.
    *   **Returns:** `self` (the `TallyConnector` instance).
*   **`__exit__(self, exc_type, exc_value, traceback)`**:
    *   **Description:** Closes the connection to Tally when exiting a `with` statement.

### Methods:

*   **`connect(self)`**:
    *   **Description:** Explicitly establishes a connection to Tally.
    *   **Raises:** `TallyConnectorError` if the connection fails.
*   **`disconnect(self)`**:
    *   **Description:** Explicitly closes the connection to Tally.
*   **`is_connected(self) -> bool`**:
    *   **Description:** Checks if the connector is currently connected to Tally.
    *   **Returns:** `bool` - `True` if connected, `False` otherwise.
*   **`session` (property) -> TallySession**:
    *   **Description:** Returns the underlying `TallySession` object.
    *   **Raises:** `TallyConnectorError` if not connected.
*   **`get_version_info(self) -> dict`**:
    *   **Description:** Retrieves information about the current Tally connector version.
    *   **Returns:** `dict` - Version information.
    *   **Raises:** `TallyConnectorError` if not connected or if there's an error retrieving info.
*   **`test_connection(self) -> bool`**:
    *   **Description:** Tests the connectivity to Tally by attempting a simple operation (getting companies list).
    *   **Returns:** `bool` - `True` if the connection is successful and a basic operation can be performed, `False` otherwise.

## Data Insertion Functions

**File:** `data_insertion.py`

This file contains functions responsible for inserting and updating various data entities within Tally, such as ledgers, stock items, and vouchers.

---

### `create_ledger(connector: TallyConnector, ledger_data: Dict) -> Dict`

*   **Description:** Adds a new customer or supplier ledger to Tally if it doesn't already exist.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `ledger_data` (`Dict`): A dictionary containing ledger information.
        *   **Required:** `name` (str)
        *   **Optional:** `group` (str), `alias` (str), `email` (str), `mobile` (str), `address` (str), `ledger_type` (str, e.g., "customer", "supplier").
*   **Returns:** `Dict` - A dictionary with the creation result and ledger details.
*   **Raises:** `TallyConnectorError` if creation fails.

---

### `update_ledger(connector: TallyConnector, ledger_name: str, updates: Dict) -> Dict`

*   **Description:** Updates an existing ledger's details in Tally.
    *   **Note:** Full ledger update functionality might be limited by the underlying Tally API; this function currently provides a placeholder.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `ledger_name` (str): The name of the ledger to update.
    *   `updates` (`Dict`): A dictionary containing fields to update.
*   **Returns:** `Dict` - A dictionary with the update result.
*   **Raises:** `TallyConnectorError` if update fails.

---

### `create_stock_item(connector: TallyConnector, item_data: Dict) -> Dict`

*   **Description:** Inserts a new inventory item identified in OCR data but not yet in Tally.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `item_data` (`Dict`): A dictionary containing stock item information.
        *   **Required:** `name` (str)
        *   **Optional:** `base_unit` (str), `stock_group` (str), `alias` (str).
*   **Returns:** `Dict` - A dictionary with the creation result and item details.
*   **Raises:** `TallyConnectorError` if creation fails.

---

### `create_sales_voucher(connector: TallyConnector, voucher_data: Dict) -> Dict`

*   **Description:** Posts a new sales voucher to Tally.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `voucher_data` (`Dict`): A dictionary containing sales voucher information.
        *   **Required:** `party_name` (str), `date` (str or `datetime`), `items` (List[Dict]).
        *   **Optional:** `voucher_number` (str), `narration` (str), `bill_ref` (str).
*   **Returns:** `Dict` - A dictionary with the creation result and voucher details.
*   **Raises:** `TallyConnectorError` if creation fails.

---

### `create_purchase_voucher(connector: TallyConnector, voucher_data: Dict) -> Dict`

*   **Description:** Posts a new purchase voucher to Tally.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `voucher_data` (`Dict`): A dictionary containing purchase voucher information.
        *   **Required:** `party_name` (str), `date` (str or `datetime`), `items` (List[Dict]).
        *   **Optional:** `voucher_number` (str), `narration` (str), `bill_ref` (str).
*   **Returns:** `Dict` - A dictionary with the creation result and voucher details.
*   **Raises:** `TallyConnectorError` if creation fails.

---

### `create_payment_voucher(connector: TallyConnector, voucher_data: Dict) -> Dict`

*   **Description:** Adds a payment voucher to Tally.
    *   **Note:** This function is currently a placeholder and not fully implemented.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `voucher_data` (`Dict`): A dictionary containing payment information.
        *   **Required:** `party_name` (str), `date` (str or `datetime`), `amount` (float or Decimal).
        *   **Optional:** `voucher_number` (str), `narration` (str), `payment_method` (str).
*   **Returns:** `Dict` - A dictionary with the creation result and voucher details.
*   **Raises:** `TallyConnectorError` if creation fails.

---

### `create_simple_unit(connector: TallyConnector, unit_data: Dict) -> Dict`

*   **Description:** Creates a simple unit of measure in Tally.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `unit_data` (`Dict`): A dictionary containing unit information.
        *   **Required:** `name` (str)
        *   **Optional:** `decimal_places` (int, default: 0, range: 0-4).
*   **Returns:** `Dict` - A dictionary with the creation result and unit details.
*   **Raises:** `TallyConnectorError` if creation fails.

---

### `create_compound_unit(connector: TallyConnector, unit_data: Dict) -> Dict`

*   **Description:** Creates a compound unit of measure in Tally.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `unit_data` (`Dict`): A dictionary containing compound unit information.
        *   **Required:** `name` (str), `base_unit` (str), `conversion` (float or int).
        *   **Optional:** `decimal_places` (int, default: 0, range: 0-4).
*   **Returns:** `Dict` - A dictionary with the creation result and unit details.
*   **Raises:** `TallyConnectorError` if creation fails.

---

### `create_unit(connector: TallyConnector, unit_data: Dict) -> Dict`

*   **Description:** Creates a unit of measure in Tally (auto-detects simple vs compound).
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `unit_data` (`Dict`): A dictionary containing unit information.
        *   **Required:** `name` (str)
        *   **Optional:** `decimal_places` (int), `base_unit` (str), `conversion` (float or int).
*   **Returns:** `Dict` - A dictionary with the creation result and unit details.
*   **Raises:** `TallyConnectorError` if creation fails.

---

### `update_unit(connector: TallyConnector, unit_name: str, updates: Dict) -> Dict`

*   **Description:** Updates an existing unit in Tally.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `unit_name` (str): The name of the unit to update.
    *   `updates` (`Dict`): A dictionary containing fields to update.
*   **Returns:** `Dict` - A dictionary with the update result.
*   **Raises:** `TallyConnectorError` if update fails.

## Data Retrieval Functions

**File:** `data_retrieval.py`

This file contains functions for retrieving various master data and transaction records from Tally.

---

### `get_companies_list(connector: TallyConnector) -> List[Dict]`

*   **Description:** Retrieves a list of all companies available in Tally.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
*   **Returns:** `List[Dict]` - A list of dictionaries, each representing a company with keys like `name`, `guid`, `alias`, `is_active`.
*   **Raises:** `TallyConnectorError` if retrieval fails.

---

### `get_ledgers_list(connector: TallyConnector, company_name: Optional[str] = None) -> List[Dict]`

*   **Description:** Fetches all ledgers from Tally. Can be used to match customer or supplier names from OCR data.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `company_name` (str, optional): An optional company name to filter ledgers (currently not used in implementation).
*   **Returns:** `List[Dict]` - A list of dictionaries, each representing a ledger with keys like `name`, `alias`, `group`, `email`, `mobile`, `address`, `guid`.
*   **Raises:** `TallyConnectorError` if retrieval fails.

---

### `get_stock_items_list(connector: TallyConnector, company_name: Optional[str] = None) -> List[Dict]`

*   **Description:** Retrieves a list of all inventory stock items from Tally. Useful for ensuring products from OCR data exist in Tally.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `company_name` (str, optional): An optional company name to filter stock items (currently not used in implementation).
*   **Returns:** `List[Dict]` - A list of dictionaries, each representing a stock item with keys like `name`, `alias`, `group`, `base_unit`, `stock_group`, `is_active`, `opening_balance`, `opening_rate`, `guid`.
*   **Raises:** `TallyConnectorError` if retrieval fails.

---

### `get_vouchers_list(connector: TallyConnector, filters: Optional[Dict] = None) -> List[Dict]`

*   **Description:** Pulls existing vouchers from Tally. Can be used for reconciliation or to check if similar entries exist.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `filters` (`Dict`, optional): Optional filters to apply to the voucher list (e.g., `voucher_type`, `date_from`, `date_to`, etc.).
*   **Returns:** `List[Dict]` - A list of dictionaries, each representing a voucher.
*   **Raises:** `TallyConnectorError` if retrieval fails.

---

### `find_ledger_by_name(connector: TallyConnector, ledger_name: str) -> Optional[Dict]`

*   **Description:** Finds a specific ledger by its name (case-insensitive) or alias.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `ledger_name` (str): The name or alias of the ledger to find.
*   **Returns:** `Optional[Dict]` - A dictionary representing the ledger if found, `None` otherwise.
*   **Raises:** `TallyConnectorError` if the search operation fails.

---

### `find_stock_item_by_name(connector: TallyConnector, item_name: str) -> Optional[Dict]`

*   **Description:** Finds a specific stock item by its name (case-insensitive) or alias.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `item_name` (str): The name or alias of the stock item to find.
*   **Returns:** `Optional[Dict]` - A dictionary representing the stock item if found, `None` otherwise.
*   **Raises:** `TallyConnectorError` if the search operation fails.

---

### `get_units_list(connector: TallyConnector, company_name: Optional[str] = None) -> List[Dict]`

*   **Description:** Retrieves a list of all units of measure (UOM) from Tally.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `company_name` (str, optional): An optional company name filter (currently not used).
*   **Returns:** `List[Dict]` - A list of dictionaries, each representing a unit.
*   **Raises:** `TallyConnectorError` if retrieval fails.

---

### `find_unit_by_name(connector: TallyConnector, unit_name: str) -> Optional[Dict]`

*   **Description:** Finds a specific unit of measure by its name (case-insensitive). It first attempts a direct lookup and then falls back to searching through all units.
*   **Parameters:**
    *   `connector` (`TallyConnector`): An active instance of `TallyConnector`.
    *   `unit_name` (str): The name of the unit to find.
*   **Returns:** `Optional[Dict]` - A dictionary representing the unit if found, `None` otherwise.
*   **Raises:** `TallyConnectorError` if the search operation fails.

---

### `_apply_voucher_filters(vouchers: List[Dict], filters: Dict) -> List[Dict]`

*   **Description:** Internal helper function to apply filters to a list of voucher dictionaries.
*   **Parameters:**
    *   `vouchers` (`List[Dict]`): The list of voucher dictionaries to filter.
    *   `filters` (`Dict`): A dictionary of filters to apply (e.g., `voucher_type`, `party_name`).
*   **Returns:** `List[Dict]` - The filtered list of voucher dictionaries.

## Tally Session Module

**File:** `session.py`

The `TallySession` class provides the core functionality for interacting with Tally via the TallyConnector .NET SDK. It acts as a context manager to handle connection and disconnection.

### Exceptions:

*   **`RuntimeError`**: Raised if `CLR/pythonnet` is not available.

### Constructor:

*   **`__init__(self, lib_dir: str | Path = None, *, version: str = "legacy", host: str = None, api_key: str = None, port: int = None)`**:
    *   **Description:** Initializes a Tally session.
    *   **Parameters:**
        *   `lib_dir` (str | Path, optional): Folder containing `TallyConnector.dll` and its dependencies. If `None`, uses `TallyConfig.get_lib_dir()`.
        *   `version` (str): TallyConnector version ("legacy" or "latest"). Defaults to "legacy".
        *   `host` (str, optional): The Tally host URL. If `None`, it's resolved from `api_key`. Defaults to `http://localhost:9000` if neither host nor api_key is provided.
        *   `api_key` (str, optional): User's API key for dynamic host resolution. If provided, host will be constructed as `http://{api_key}.holanitunnel.net`.
        *   `port` (int, optional): Tally service port. Defaults to `TallyConfig.DEFAULT_PORT`.
    *   **Raises:** `RuntimeError` if `CLR/pythonnet` is not available.

### Context Manager Methods:

*   **`__enter__(self)`**:
    *   **Description:** Establishes the connection to Tally. Logs connection information.
    *   **Returns:** `self` (the `TallySession` instance).
*   **`__exit__(self, exc_type, exc_value, traceback)`**:
    *   **Description:** Closes the connection to Tally. Logs disconnection information.

### Methods:

*   **`get_companies(self)`**:
    *   **Description:** Retrieves a list of all companies from Tally.
    *   **Returns:** A .NET `IEnumerable<Company>` object.
*   **`get_ledgers(self, request_options: Any = None)`**:
    *   **Description:** Retrieves ledgers from Tally.
    *   **Parameters:**
        *   `request_options` (Any, optional): Request options for the Tally API call.
    *   **Returns:** A .NET object containing ledger data.
*   **`get_stock_items(self, request_options: Any = None)`**:
    *   **Description:** Retrieves stock items from Tally.
    *   **Parameters:**
        *   `request_options` (Any, optional): Request options for the Tally API call.
    *   **Returns:** A .NET object containing stock item data.
*   **`get_vouchers(self, request_options: Any = None)`**:
    *   **Description:** Retrieves vouchers from Tally.
    *   **Parameters:**
        *   `request_options` (Any, optional): Request options for the Tally API call.
    *   **Returns:** A .NET object containing voucher data.
*   **`get_units(self, request_options: Any = None)`**:
    *   **Description:** Retrieves units of measure from Tally.
    *   **Parameters:**
        *   `request_options` (Any, optional): Request options for the Tally API call.
    *   **Returns:** A .NET object containing unit data.
    *   **Raises:** `RuntimeError` if unit functionality is not available.
*   **`get_unit(self, unit_name: str, request_options: Any = None)`**:
    *   **Description:** Retrieves a specific unit of measure by name from Tally.
    *   **Parameters:**
        *   `unit_name` (str): The name of the unit.
        *   `request_options` (Any, optional): Request options for the Tally API call.
    *   **Returns:** A .NET object representing the unit.
    *   **Raises:** `RuntimeError` if unit functionality is not available or `MasterRequestOptions` are required but not provided.
*   **`create_ledger(self, name: str, *, group: str = "Sundry Debtors", alias: Optional[str] = None, **kwargs)`**:
    *   **Description:** Creates a new Ledger in Tally; returns the response from Tally.
    *   **Parameters:**
        *   `name` (str): Name of the ledger.
        *   `group` (str, optional): Group the ledger belongs to. Defaults to "Sundry Debtors".
        *   `alias` (str, optional): Alias for the ledger.
        *   `**kwargs`: Additional ledger attributes (e.g., `Email`, `Mobile`).
    *   **Returns:** Response from Tally.
    *   **Raises:** `RuntimeError` if Ledger class is not available for the current version.
*   **`create_voucher(self, *, voucher_type: str, date: datetime, party_name: str, items: List[Dict], voucher_number: Optional[str] = None, narration: str = "", bill_ref: Optional[str] = None, post: bool = True)`**:
    *   **Description:** Builds and optionally POSTs a voucher to Tally.
    *   **Parameters:**
        *   `voucher_type` (str): E.g. "Sales", "Purchase", "Receipt", "Payment".
        *   `date` (`datetime`): Python datetime -> converts to TallyDate internally.
        *   `party_name` (str): Ledger name of party.
        *   `items` (`List[Dict]`): List of dicts with keys: `stock_item`, `qty`, `rate`, `unit`, `amount`, `ledger`, `godown`, `batch`.
        *   `voucher_number` (str, optional): Optional voucher number.
        *   `narration` (str, optional): Free text description.
        *   `bill_ref` (str, optional): Creates a Bill Allocation under party ledger.
        *   `post` (bool): If True – pushes to Tally and returns response; otherwise just returns the Voucher object for inspection.
    *   **Returns:** Response from Tally if `post=True`, otherwise the Voucher object.
    *   **Raises:** `RuntimeError` if voucher functionality is not available.
*   **`create_stock_item(self, name: str, *, base_unit: str = "Nos", stock_group: Optional[str] = None, **kwargs)`**:
    *   **Description:** Create a new Stock Item (mainly for legacy version).
    *   **Parameters:**
        *   `name` (str): Name of the stock item.
        *   `base_unit` (str): Base unit of measurement (default: "Nos").
        *   `stock_group` (str, optional): Stock group name (defaults to "Primary" if not specified).
        *   `**kwargs`: Additional stock item attributes.
    *   **Returns:** Response from Tally.
    *   **Raises:** `RuntimeError` if StockItem creation is not available in legacy version.
*   **`create_unit(self, name: str, *, decimal_places: int = 0, is_simple: bool = True, base_unit: Optional[str] = None, conversion: float = 1.0, **kwargs)`**:
    *   **Description:** Create a new Unit of Measure.
    *   **Parameters:**
        *   `name` (str): Name/Symbol of the unit (e.g., "kg", "litre", "pcs").
        *   `decimal_places` (int): Number of decimal places (0 to 4, default: 0).
        *   `is_simple` (bool): True for simple units, False for compound units (default: True).
        *   `base_unit` (str, optional): Base unit for compound units (required if is_simple=False).
        *   `conversion` (float): Conversion factor for compound units (default: 1.0).
        *   `**kwargs`: Additional unit attributes.
    *   **Returns:** Response from Tally.
    *   **Raises:** `RuntimeError` if unit functionality is not available or unit creation is not implemented for the current version.
*   **`get_version_info(self)`**:
    *   **Description:** Get information about what features are available in the current version.
    *   **Returns:** `dict` - Version and feature information.
*   **`from_user(cls, user, **kwargs)` (classmethod)**:
    *   **Description:** Create a TallySession instance from a User object.
    *   **Parameters:**
        *   `user` (`User`): User model instance with api_key attribute.
        *   `**kwargs`: Additional parameters to pass to TallySession constructor.
    *   **Returns:** `TallySession` - Configured TallySession instance.
    *   **Raises:** `AttributeError` if user object doesn't have api_key attribute.

## Tally Field Options Helper Functions

**File:** `tally_field_options.py`

This file provides functions for dynamically loading data from Tally (companies, ledgers, stock items, units) and populating them as options for `SELECT` type template fields and sub-template fields.

### Exceptions:

*   **`TallyFieldOptionsError`**: Custom exception for Tally field options operations.

---

### `load_companies_as_options(field_id: int, clear_existing: bool = True) -> Dict`

*   **Description:** Loads Tally companies as options for a `SELECT` field.
*   **Parameters:**
    *   `field_id` (int): ID of the template field.
    *   `clear_existing` (bool, optional): Whether to clear existing options before loading. Defaults to `True`.
*   **Returns:** `Dict` - A dictionary with success status and loaded options count.
*   **Raises:** `TallyFieldOptionsError` if loading fails.

---

### `load_ledgers_as_options(field_id: int, ledger_group: Optional[str] = None, clear_existing: bool = True) -> Dict`

*   **Description:** Loads Tally ledgers as options for a `SELECT` field.
*   **Parameters:**
    *   `field_id` (int): ID of the template field.
    *   `ledger_group` (str, optional): Optional filter by ledger group (e.g., "Sundry Debtors", "Sundry Creditors").
    *   `clear_existing` (bool, optional): Whether to clear existing options before loading. Defaults to `True`.
*   **Returns:** `Dict` - A dictionary with success status and loaded options count.
*   **Raises:** `TallyFieldOptionsError` if loading fails.

---

### `load_stock_items_as_options(field_id: int, stock_group: Optional[str] = None, clear_existing: bool = True) -> Dict`

*   **Description:** Loads Tally stock items as options for a `SELECT` field.
*   **Parameters:**
    *   `field_id` (int): ID of the template field.
    *   `stock_group` (str, optional): Optional filter by stock group.
    *   `clear_existing` (bool, optional): Whether to clear existing options before loading. Defaults to `True`.
*   **Returns:** `Dict` - A dictionary with success status and loaded options count.
*   **Raises:** `TallyFieldOptionsError` if loading fails.

---

### `load_units_as_options(field_id: int, clear_existing: bool = True) -> Dict`

*   **Description:** Loads Tally units of measure as options for a `SELECT` field.
*   **Parameters:**
    *   `field_id` (int): ID of the template field.
    *   `clear_existing` (bool, optional): Whether to clear existing options before loading. Defaults to `True`.
*   **Returns:** `Dict` - A dictionary with success status and loaded options count.
*   **Raises:** `TallyFieldOptionsError` if loading fails.

---

### `auto_load_tally_options(field_id: int, clear_existing: bool = True) -> Dict`

*   **Description:** Automatically determines what type of Tally data to load (companies, ledgers, stock items, units) based on the field name and populates options for a `SELECT` field.
*   **Parameters:**
    *   `field_id` (int): ID of the template field.
    *   `clear_existing` (bool, optional): Whether to clear existing options before loading. Defaults to `True`.
*   **Returns:** `Dict` - A dictionary with success status and loaded options count.
*   **Raises:** `TallyFieldOptionsError` if loading fails or field type cannot be determined.

---

### `load_stock_items_as_sub_field_options(sub_field_id: int, stock_group: Optional[str] = None, clear_existing: bool = True) -> Dict`

*   **Description:** Loads Tally stock items as options for a `SELECT` sub-template field.
*   **Parameters:**
    *   `sub_field_id` (int): ID of the sub-template field.
    *   `stock_group` (str, optional): Optional filter by stock group.
    *   `clear_existing` (bool, optional): Whether to clear existing options before loading. Defaults to `True`.
*   **Returns:** `Dict` - A dictionary with success status and loaded options count.
*   **Raises:** `TallyFieldOptionsError` if loading fails.

---

### `load_ledgers_as_sub_field_options(sub_field_id: int, ledger_group: Optional[str] = None, clear_existing: bool = True) -> Dict`

*   **Description:** Loads Tally ledgers as options for a `SELECT` sub-template field.
*   **Parameters:**
    *   `sub_field_id` (int): ID of the sub-template field.
    *   `ledger_group` (str, optional): Optional filter by ledger group.
    *   `clear_existing` (bool, optional): Whether to clear existing options before loading. Defaults to `True`.
*   **Returns:** `Dict` - A dictionary with success status and loaded options count.
*   **Raises:** `TallyFieldOptionsError` if loading fails.

---

### `load_units_as_sub_field_options(sub_field_id: int, clear_existing: bool = True) -> Dict`

*   **Description:** Loads Tally units of measure as options for a `SELECT` sub-template field.
*   **Parameters:**
    *   `sub_field_id` (int): ID of the sub-template field.
    *   `clear_existing` (bool, optional): Whether to clear existing options before loading. Defaults to `True`.
*   **Returns:** `Dict` - A dictionary with success status and loaded options count.
*   **Raises:** `TallyFieldOptionsError` if loading fails.

---

### `auto_load_tally_sub_field_options(sub_field_id: int, clear_existing: bool = True) -> Dict`

*   **Description:** Automatically determines what type of Tally data to load for a sub-field based on its name and populates options for a `SELECT` sub-field.
*   **Parameters:**
    *   `sub_field_id` (int): ID of the sub-template field.
    *   `clear_existing` (bool, optional): Whether to clear existing options before loading. Defaults to `True`.
*   **Returns:** `Dict` - A dictionary with success status and loaded options count.
*   **Raises:** `TallyFieldOptionsError` if loading fails or field type cannot be determined.

---

### `get_field_options_summary(field_id: int) -> Dict`

*   **Description:** Retrieves a summary of current options configured for a field.
*   **Parameters:**
    *   `field_id` (int): ID of the template field.
*   **Returns:** `Dict` - A dictionary with field information and options summary.

---

### `refresh_field_options(field_id: int) -> Dict`

*   **Description:** Refreshes field options by reloading them from Tally using auto-detection.
*   **Parameters:**
    *   `field_id` (int): ID of the template field.
*   **Returns:** `Dict` - A dictionary with success status and loaded options count.
*   **Raises:** `TallyFieldOptionsError` if refreshing fails.

---

### `load_customer_options(field_id: int) -> Dict`

*   **Description:** Loads customer ledgers (Sundry Debtors) as options for a `SELECT` field.
*   **Parameters:**
    *   `field_id` (int): ID of the template field.
*   **Returns:** `Dict` - A dictionary with success status and loaded options count.

---

### `load_vendor_options(field_id: int) -> Dict`

*   **Description:** Loads vendor ledgers (Sundry Creditors) as options for a `SELECT` field.
*   **Parameters:**
    *   `field_id` (int): ID of the template field.
*   **Returns:** `Dict` - A dictionary with success status and loaded options count.

---

### `load_all_ledger_options(field_id: int) -> Dict`

*   **Description:** Loads all ledgers (without group filter) as options for a `SELECT` field.
*   **Parameters:**
    *   `field_id` (int): ID of the template field.
*   **Returns:** `Dict` - A dictionary with success status and loaded options count.

## Utility Functions

**File:** `utils.py`

This file contains helper functions for data transformation, validation, and mapping between OCR extracted data and Tally formats.

---

### `ocr_data_to_voucher_format(ocr_data: Dict, document_type: str = "invoice") -> Dict`

*   **Description:** Converts OCR extracted data into a format suitable for Tally voucher creation.
*   **Parameters:**
    *   `ocr_data` (`Dict`): Dictionary containing OCR extracted data.
    *   `document_type` (str, optional): Type of document ("invoice", "bill", "receipt", "payment"). Defaults to "invoice".
*   **Returns:** `Dict` - A dictionary formatted for Tally voucher creation.
*   **Raises:** `ValueError` if required data is missing or invalid.

---

### `validate_voucher_data(voucher_data: Dict) -> Tuple[bool, List[str]]`

*   **Description:** Validates the structure and content of voucher data before it's sent to Tally.
*   **Parameters:**
    *   `voucher_data` (`Dict`): Dictionary containing voucher information.
*   **Returns:** `Tuple[bool, List[str]]` - A tuple where the first element is `True` if the data is valid, `False` otherwise, and the second element is a list of error messages.

---

### `normalize_party_name(party_name: str) -> str`

*   **Description:** Standardizes party names from OCR data for better matching with existing ledgers in Tally. Removes common prefixes/suffixes and normalizes spacing.
*   **Parameters:**
    *   `party_name` (str): Raw party name from OCR.
*   **Returns:** `str` - The normalized party name.

---

### `calculate_voucher_totals(line_items: List[Dict]) -> Dict`

*   **Description:** Calculates various totals (subtotal, tax, discount, grand total, total quantity) from a list of line items.
*   **Parameters:**
    *   `line_items` (`List[Dict]`): List of item dictionaries, each containing `qty`, `rate`, `amount`, `tax_amount`, `discount` (optional).
*   **Returns:** `Dict` - A dictionary containing calculated totals.

---

### `_extract_party_name(ocr_data: Dict) -> str`

*   **Description:** Internal helper to extract the party name from OCR data, trying various common field names.
*   **Parameters:**
    *   `ocr_data` (`Dict`): Dictionary containing OCR extracted data.
*   **Returns:** `str` - The extracted and normalized party name, or an empty string if not found.

---

### `_extract_date(ocr_data: Dict) -> str`

*   **Description:** Internal helper to extract a date from OCR data, trying various common field names. Defaults to the current date if no date is found.
*   **Parameters:**
    *   `ocr_data` (`Dict`): Dictionary containing OCR extracted data.
*   **Returns:** `str` - The extracted date string.

---

### `_extract_voucher_number(ocr_data: Dict) -> Optional[str]`

*   **Description:** Internal helper to extract a voucher or invoice number from OCR data.
*   **Parameters:**
    *   `ocr_data` (`Dict`): Dictionary containing OCR extracted data.
*   **Returns:** `Optional[str]` - The extracted number string, or `None` if not found.

---

### `_extract_narration(ocr_data: Dict, document_type: str) -> str`

*   **Description:** Internal helper to extract or generate a narration for the Tally voucher.
*   **Parameters:**
    *   `ocr_data` (`Dict`): Dictionary containing OCR extracted data.
    *   `document_type` (str): Type of document (e.g., "invoice", "bill").
*   **Returns:** `str` - The extracted or generated narration.

---

### `_extract_bill_reference(ocr_data: Dict) -> Optional[str]`

*   **Description:** Internal helper to extract a bill reference for Tally bill allocations. Falls back to the voucher number if no specific bill reference is found.
*   **Parameters:**
    *   `ocr_data` (`Dict`): Dictionary containing OCR extracted data.
*   **Returns:** `Optional[str]` - The extracted bill reference string, or `None`.

---

### `_extract_line_items(ocr_data: Dict) -> List[Dict]`

*   **Description:** Internal helper to extract line items (products/services) from OCR data, handling various possible structures.
*   **Parameters:**
    *   `ocr_data` (`Dict`): Dictionary containing OCR extracted data.
*   **Returns:** `List[Dict]` - A list of dictionaries, each representing a processed line item.

---

### `_process_line_item(item: Dict) -> Optional[Dict]`

*   **Description:** Internal helper to process an individual raw line item dictionary from OCR data, extracting and standardizing key fields like stock item, quantity, rate, and amount.
*   **Parameters:**
    *   `item` (`Dict`): A dictionary representing a single line item.
*   **Returns:** `Optional[Dict]` - A processed line item dictionary, or `None` if processing fails.

---

### `_validate_item(item: Dict, index: int) -> List[str]`

*   **Description:** Internal helper to validate an individual line item's data (e.g., presence of stock item name, valid quantity/rate).
*   **Parameters:**
    *   `item` (`Dict`): A dictionary representing a single line item.
    *   `index` (int): The 0-based index of the item in the list (for error reporting).
*   **Returns:** `List[str]` - A list of error messages for the item.

---

### `_parse_date_string(date_str: str) -> datetime`

*   **Description:** Internal helper to parse a date string, supporting multiple common date formats.
*   **Parameters:**
    *   `date_str` (str): The date string to parse.
*   **Returns:** `datetime` - The parsed datetime object.
*   **Raises:** `ValueError` if the date string cannot be parsed.