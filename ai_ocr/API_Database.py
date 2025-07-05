"""
Database API module for retrieving supplier and party information.
This is a simplified version that can be extended to connect to your actual database.
"""

import json
import os
from typing import List, Tuple, Dict, Any

class DatabaseAPI:
    """Database API class for managing supplier and party data."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the database API.
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = data_dir
        self.suppliers_file = os.path.join(data_dir, "suppliers.json")
        self.parties_file = os.path.join(data_dir, "parties.json")
        
        # Create data directory and initialize files if they don't exist
        os.makedirs(data_dir, exist_ok=True)
        self._initialize_data_files()
    
    def _initialize_data_files(self):
        """Initialize data files with sample data if they don't exist."""
        # Initialize suppliers file
        if not os.path.exists(self.suppliers_file):
            sample_suppliers = [
                {"id": 1, "name": "Rachit Fashion", "type": "supplier"},
                {"id": 2, "name": "ABC Textiles", "type": "supplier"},
                {"id": 3, "name": "XYZ Fabrics", "type": "supplier"},
                {"id": 4, "name": "Fashion House Ltd", "type": "supplier"},
                {"id": 5, "name": "Textile World", "type": "supplier"}
            ]
            with open(self.suppliers_file, 'w') as f:
                json.dump(sample_suppliers, f, indent=2)
        
        # Initialize parties file
        if not os.path.exists(self.parties_file):
            sample_parties = [
                {"id": 1, "name": "Retail Store A", "type": "party"},
                {"id": 2, "name": "Fashion Boutique", "type": "party"},
                {"id": 3, "name": "Department Store", "type": "party"},
                {"id": 4, "name": "Online Retailer", "type": "party"},
                {"id": 5, "name": "Wholesale Buyer", "type": "party"}
            ]
            with open(self.parties_file, 'w') as f:
                json.dump(sample_parties, f, indent=2)
    
    def _load_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Load data from JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_data(self, file_path: str, data: List[Dict[str, Any]]):
        """Save data to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_all_names_ids(self, entity_type: str, dict_cursor: bool = False) -> List[Tuple[int, str]]:
        """
        Get all names and IDs for a given entity type.
        
        Args:
            entity_type: Type of entity ('supplier' or 'party')
            dict_cursor: Whether to return as dictionary (not used in this implementation)
            
        Returns:
            List of tuples containing (id, name)
        """
        if entity_type == 'supplier':
            data = self._load_data(self.suppliers_file)
        elif entity_type == 'party':
            data = self._load_data(self.parties_file)
        else:
            return []
        
        return [(item['id'], item['name']) for item in data]
    
    def add_entity(self, name: str, entity_type: str) -> int:
        """
        Add a new entity to the database.
        
        Args:
            name: Name of the entity
            entity_type: Type of entity ('supplier' or 'party')
            
        Returns:
            ID of the newly created entity
        """
        if entity_type == 'supplier':
            file_path = self.suppliers_file
            data = self._load_data(file_path)
        elif entity_type == 'party':
            file_path = self.parties_file
            data = self._load_data(file_path)
        else:
            raise ValueError(f"Invalid entity type: {entity_type}")
        
        # Generate new ID
        new_id = max([item['id'] for item in data], default=0) + 1
        
        # Add new entity
        new_entity = {
            "id": new_id,
            "name": name,
            "type": entity_type
        }
        data.append(new_entity)
        
        # Save back to file
        self._save_data(file_path, data)
        
        return new_id
    
    def search_entities(self, query: str, entity_type: str) -> List[Dict[str, Any]]:
        """
        Search for entities by name.
        
        Args:
            query: Search query
            entity_type: Type of entity ('supplier' or 'party')
            
        Returns:
            List of matching entities
        """
        if entity_type == 'supplier':
            data = self._load_data(self.suppliers_file)
        elif entity_type == 'party':
            data = self._load_data(self.parties_file)
        else:
            return []
        
        query_lower = query.lower()
        matches = [
            item for item in data 
            if query_lower in item['name'].lower()
        ]
        
        return matches

# Create a global instance
database_api = DatabaseAPI()

# Module-level functions for backward compatibility
def get_all_names_ids(entity_type: str, dict_cursor: bool = False) -> List[Tuple[int, str]]:
    """Get all names and IDs for a given entity type."""
    return database_api.get_all_names_ids(entity_type, dict_cursor)

def add_entity(name: str, entity_type: str) -> int:
    """Add a new entity to the database."""
    return database_api.add_entity(name, entity_type)

def search_entities(query: str, entity_type: str) -> List[Dict[str, Any]]:
    """Search for entities by name."""
    return database_api.search_entities(query, entity_type) 