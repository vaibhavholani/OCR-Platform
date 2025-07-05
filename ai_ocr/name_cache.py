import json
import os
import re
from typing import Optional, Dict
from rapidfuzz import distance

class NameMatchCache:
    """A persistent cache system for name matching results."""
    
    def __init__(self, cache_file: str = "data/name_match_cache.json"):
        """Initialize the cache system.
        
        Args:
            cache_file: Path to the JSON file for persistent storage
        """
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.hits = 0
        self.misses = 0
    
    def _load_cache(self) -> dict:
        """Load the cache from disk."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                # Initialize with empty dict if file doesn't exist or is empty
                with open(self.cache_file, 'w') as f:
                    json.dump({}, f)
                return {}
        except Exception as e:
            print(f"Error loading cache: {str(e)}")
            return {}
    
    def _save_cache(self):
        """Save the cache to disk."""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def _normalize_name(self, name: str) -> str:
        """Normalize a business name for consistent matching.
        
        Args:
            name: The business name to normalize
            
        Returns:
            Normalized version of the name
        """
        if not name:
            return ""
            
        # Convert to lowercase and remove punctuation
        normalized = re.sub(r'[^\w\s]', '', name.lower())
        
        # Split into words and filter out business suffixes
        words = normalized.split()
        words = [w for w in words if w not in ['pvt', 'ltd', 'limited', 'private']]
        
        # Join back together
        normalized = ''.join(words)
        
        return normalized
    
    def get(self, name: str, threshold: float = 0.95) -> Optional[str]:
        """Get a matched name from the cache.
        
        Args:
            name: The name to look up
            threshold: Minimum similarity score for fuzzy matching
            
        Returns:
            The matched name if found, None otherwise
        """
        if not name:
            return None
            
        normalized = self._normalize_name(name)
        if not normalized:
            return None
        
        # Try exact match first
        if normalized in self.cache:
            self.hits += 1
            return self.cache[normalized]
        
        # Try fuzzy matching with normalized cached names
        best_match = None
        best_score = 0
        for cached_key, cached_value in self.cache.items():
            score = distance.JaroWinkler.similarity(normalized, self._normalize_name(cached_key))
            if score > threshold and score > best_score and score > 0.95:
                best_score = score
                best_match = cached_value
        
        if best_match:
            self.hits += 1
            return best_match
        
        self.misses += 1
        return None
    
    def set(self, name: str, matched_name: str):
        """Store a new name match in the cache.
        
        Args:
            name: The original name
            matched_name: The correct matched name
        """
        if not name or not matched_name:
            return
            
        normalized = self._normalize_name(name)
        if normalized:
            self.cache[normalized] = matched_name
            self._save_cache()
    
    def get_stats(self) -> Dict[str, float]:
        """Get cache performance statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        total = self.hits + self.misses
        return {
            "total_entries": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": self.hits / total if total > 0 else 0
        }
    
    def update_mapping(self, original_name: str, corrected_name: str) -> None:
        """Update cache with a human-corrected mapping.
        
        This method is called when a user manually corrects an OCR prediction.
        These corrections take precedence over AI predictions.
        
        Args:
            original_name: The original OCR'd name
            corrected_name: The correct name selected by the user
        """
        if not original_name or not corrected_name:
            return
            
        normalized = self._normalize_name(original_name)
        if normalized:
            self.cache[normalized] = corrected_name
            self._save_cache()
            print(f"Cache updated: {original_name} -> {corrected_name}")
