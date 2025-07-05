class DataError(Exception):
    """Custom exception for data processing errors."""
    
    def __init__(self, error_data):
        """
        Initialize the DataError with error information.
        
        Args:
            error_data: Dictionary containing error details
        """
        self.error_data = error_data
        super().__init__(str(error_data))
    
    def get_error_data(self):
        """Get the error data dictionary."""
        return self.error_data 