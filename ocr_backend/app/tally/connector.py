"""
Tally Connector

Main connector class that wraps the TallySession for clean integration.
"""

import logging
from typing import Optional

from .config import TallyConfig

try:
    from .session import TallySession
except ImportError as e:
    logging.error(f"Failed to import TallySession: {e}")
    TallySession = None


logger = logging.getLogger(__name__)


class TallyConnectorError(Exception):
    """Custom exception for Tally connector errors."""
    pass


class TallyConnector:
    """
    Main connector class for Tally operations.
    
    Provides a clean wrapper around TallySession with proper error handling
    and connection management.
    """
    
    def __init__(
        self, 
        lib_dir: Optional[str] = None,
        version: str = TallyConfig.DEFAULT_VERSION,
        host: str = TallyConfig.DEFAULT_HOST
    ):
        """
        Initialize Tally connector.
        
        Args:
            lib_dir: Path to TallyConnector library directory
            version: TallyConnector version ("legacy" or "latest")
            host: Tally host URL
        """
        if TallySession is None:
            raise TallyConnectorError(
                "TallySession not available. Ensure pythonnet is installed and TallyConnector DLLs are accessible."
            )
        
        self.lib_dir = lib_dir or TallyConfig.get_lib_dir(version)
        self.version = version
        self.host = host
        self._session = None
        self._is_connected = False
        
        logger.info(f"Initializing TallyConnector with version={version}, host={host}")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit."""
        self.disconnect()
        return False
    
    def connect(self):
        """Establish connection to Tally."""
        try:
            self._session = TallySession(
                lib_dir=self.lib_dir,
                version=self.version,
                host=self.host
            )
            self._session.__enter__()
            self._is_connected = True
            logger.info("Successfully connected to Tally")
        except Exception as e:
            logger.error(f"Failed to connect to Tally: {e}")
            raise TallyConnectorError(f"Connection failed: {e}")
    
    def disconnect(self):
        """Close connection to Tally."""
        if self._session and self._is_connected:
            try:
                self._session.__exit__(None, None, None)
                self._is_connected = False
                logger.info("Disconnected from Tally")
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
        self._session = None
    
    def is_connected(self) -> bool:
        """Check if connected to Tally."""
        return self._is_connected and self._session is not None
    
    @property
    def session(self) -> TallySession:
        """Get the underlying TallySession."""
        if not self.is_connected():
            raise TallyConnectorError("Not connected to Tally. Use 'with TallyConnector()' or call connect() first.")
        return self._session
    
    def get_version_info(self) -> dict:
        """Get information about the current Tally connector version."""
        if not self.is_connected():
            raise TallyConnectorError("Not connected to Tally")
        
        try:
            return self._session.get_version_info()
        except Exception as e:
            logger.error(f"Failed to get version info: {e}")
            raise TallyConnectorError(f"Version info error: {e}")
    
    def test_connection(self) -> bool:
        """Test the connection to Tally."""
        try:
            if not self.is_connected():
                return False
            
            # Try a simple operation to test connectivity
            companies = self._session.get_companies()
            return companies is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
