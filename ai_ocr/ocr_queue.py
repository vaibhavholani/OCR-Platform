import json
import os
import uuid
import base64
from datetime import datetime
from typing import Optional, Dict, List

class OCRQueue:
    """A persistent queue system for OCR processing results."""
    
    def __init__(self, queue_dir: str = "data/ocr_queue"):
        """Initialize the queue system.
        
        Args:
            queue_dir: Directory for queue storage (images and metadata)
        """
        # Convert to absolute path
        self.queue_dir = os.path.abspath(queue_dir)
        self.images_dir = os.path.join(self.queue_dir, "images")
        self.queue_file = os.path.join(self.queue_dir, "queue.json")
        
        # Create directories if they don't exist
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.queue_file), exist_ok=True)
        
        self.queue = self._load_queue()
        self._verify_queue()  # Verify and fix any issues
    
    def _load_queue(self) -> dict:
        """Load the queue metadata from disk."""
        try:
            try:
                with open(self.queue_file, 'r') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                # Initialize with empty queue if file doesn't exist or is empty
                initial_queue = {
                    "entries": [],
                    "stats": {
                        "total_processed": 0,
                        "total_pending": 0,
                        "last_processed": None
                    }
                }
                with open(self.queue_file, 'w') as f:
                    json.dump(initial_queue, f, indent=2)
                return initial_queue
        except Exception as e:
            print(f"Error loading queue: {str(e)}")
            return {
                "entries": [],
                "stats": {
                    "total_processed": 0,
                    "total_pending": 0,
                    "last_processed": None
                }
            }
    
    def _save_queue(self):
        """Save the queue to disk."""
        try:
            os.makedirs(os.path.dirname(self.queue_file), exist_ok=True)
            with open(self.queue_file, 'w') as f:
                json.dump(self.queue, f, indent=2)
        except Exception as e:
            print(f"Error saving queue: {str(e)}")
    
    def _update_stats(self):
        """Update queue statistics."""
        pending_count = len([e for e in self.queue["entries"] if e["status"] == "pending"])
        processed_count = len([e for e in self.queue["entries"] if e["status"] == "processed"])
        
        self.queue["stats"] = {
            "total_processed": processed_count,
            "total_pending": pending_count,
            "last_processed": datetime.now().isoformat() if processed_count > 0 else None
        }
    
    def _verify_queue(self):
        """Verify queue integrity and fix any issues."""
        fixed_entries = []
        for entry in self.queue["entries"]:
            if entry["status"] == "pending":
                # Convert to absolute path
                image_path = os.path.abspath(entry["image_path"])
                if os.path.exists(image_path):
                    entry["image_path"] = image_path
                    fixed_entries.append(entry)
                else:
                    print(f"Warning: Skipping entry {entry['id']} - missing image")
            else:
                # Keep processed entries
                fixed_entries.append(entry)
                
        self.queue["entries"] = fixed_entries
        self._update_stats()
        self._save_queue()
        
        # Clean up orphaned images
        self._cleanup_orphaned_images()
    
    def _cleanup_orphaned_images(self):
        """Remove image files that don't belong to any queue entry."""
        if not os.path.exists(self.images_dir):
            return
            
        for filename in os.listdir(self.images_dir):
            if not filename.endswith('.jpg'):
                continue
                
            file_path = os.path.join(self.images_dir, filename)
            entry_id = os.path.splitext(filename)[0]
            
            if not any(e["id"] == entry_id for e in self.queue["entries"]):
                try:
                    os.remove(file_path)
                    print(f"Removed orphaned image: {filename}")
                except Exception as e:
                    print(f"Error removing orphaned image {filename}: {str(e)}")
    
    def add_entries(self, entries: List[Dict]) -> List[str]:
        """Add multiple OCR results to queue.
        
        Args:
            entries: List of dictionaries containing OCR results and images
            
        Returns:
            List of entry IDs
        """
        entry_ids = []
        
        # Ensure images directory exists
        os.makedirs(self.images_dir, exist_ok=True)
        
        for entry in entries:
            entry_id = str(uuid.uuid4())
            image_path = os.path.join(self.images_dir, f"{entry_id}.jpg")
            
            try:
                # Save and verify image
                image_data = base64.b64decode(entry.get("image", ""))
                with open(image_path, "wb") as f:
                    f.write(image_data)
                
                # Verify image was saved
                if not os.path.exists(image_path):
                    raise Exception("Image file not created")
                
                # Verify image can be read
                with open(image_path, "rb") as f:
                    _ = f.read()
                
                # Store metadata in queue
                queue_entry = {
                    "id": entry_id,
                    "image_path": os.path.abspath(image_path),  # Store absolute path
                    "ocr_data": entry.get("ocr_data", {}),
                    "status": "pending",
                    "upload_time": datetime.now().isoformat()
                }
                self.queue["entries"].append(queue_entry)
                entry_ids.append(entry_id)
                
            except Exception as e:
                print(f"Error saving image for entry {entry_id}: {str(e)}")
                # Clean up if file was partially created
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except Exception as cleanup_error:
                        print(f"Error cleaning up image file: {str(cleanup_error)}")
                continue
        
        self._update_stats()
        self._save_queue()
        return entry_ids
    
    def get_next_entry(self) -> Optional[Dict]:
        """Get next pending entry from queue.
        
        Returns:
            Dictionary containing entry data or None if queue is empty
        """
        pending_entries = [e for e in self.queue["entries"] if e["status"] == "pending"]
        if not pending_entries:
            return None
        
        entry = pending_entries[0]
        
        try:
            # Verify image path is absolute
            image_path = os.path.abspath(entry["image_path"])
            
            # Load image from file
            try:
                with open(image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode()
            except Exception as e:
                print(f"Error loading image for entry {entry['id']}: {str(e)}")
                image_data = ""  # Return empty string if image can't be loaded
            
            # Convert to API format
            result = {
                "id": entry["id"],
                "image": image_data,
                "ocr_data": entry["ocr_data"],
                "status": entry["status"],
                "upload_time": entry["upload_time"]
            }
            return result
            
        except Exception as e:
            print(f"Error processing entry {entry['id']}: {str(e)}")
            # Skip this entry by marking it as processed
            self.mark_complete(entry["id"])
            # Try next entry recursively
            return self.get_next_entry()
    
    def mark_complete(self, entry_id: str):
        """Mark entry as processed and optionally cleanup image.
        
        Args:
            entry_id: ID of the entry to mark as complete
        """
        for entry in self.queue["entries"]:
            if entry["id"] == entry_id and entry["status"] == "pending":
                entry["status"] = "processed"
                entry["processed_time"] = datetime.now().isoformat()
                
                # Remove image file to save space
                try:
                    if os.path.exists(entry["image_path"]):
                        os.remove(entry["image_path"])
                except Exception as e:
                    print(f"Error removing image for entry {entry_id}: {str(e)}")
                break
                
        self._update_stats()
        self._save_queue()
    
    def get_status(self) -> Dict:
        """Get queue statistics.
        
        Returns:
            Dictionary containing queue statistics
        """
        self._update_stats()
        return self.queue["stats"]
    
    def clear_processed(self, days_old: int = 30):
        """Remove processed entries older than specified days.
        
        Args:
            days_old: Remove processed entries older than this many days
        """
        current_time = datetime.now()
        new_entries = []
        
        for entry in self.queue["entries"]:
            if entry["status"] != "processed":
                new_entries.append(entry)
                continue
                
            processed_time = datetime.fromisoformat(entry["processed_time"])
            age = (current_time - processed_time).days
            
            if age < days_old:
                new_entries.append(entry)
            else:
                # Remove image file if it exists
                try:
                    if "image_path" in entry and os.path.exists(entry["image_path"]):
                        os.remove(entry["image_path"])
                except Exception as e:
                    print(f"Error removing image for entry {entry.get('id')}: {str(e)}")
                    
        self.queue["entries"] = new_entries
        self._update_stats()
        self._save_queue()
