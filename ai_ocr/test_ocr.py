#!/usr/bin/env python3
"""
Test script for the AI OCR system.
This script tests the complete OCR pipeline with the sample image.
"""

import os
import sys
import base64
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parse_register_entry_v2 import parse_register_entry, encode_image

def test_ocr_system():
    """Test the complete OCR system."""
    
    # Load environment variables
    load_dotenv()
    
    # Check if OpenAI API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ Error: OPENAI_API_KEY not set in .env file")
        print("Please copy env_example.txt to .env and add your OpenAI API key")
        return False
    
    # Check if sample image exists
    sample_image_path = "Sample.jpg"
    if not os.path.exists(sample_image_path):
        print(f"❌ Error: Sample image not found at {sample_image_path}")
        return False
    
    try:
        print("🚀 Starting AI OCR System Test...")
        print("=" * 50)
        
        # Encode the sample image
        print("📷 Encoding sample image...")
        encoded_image = encode_image(sample_image_path)
        print(f"✅ Image encoded successfully (size: {len(encoded_image)} characters)")
        
        # Parse the invoice
        print("\n🔍 Parsing invoice with AI...")
        result = parse_register_entry(encoded_image)
        
        # Display results
        print("\n📋 OCR Results:")
        print("=" * 30)
        print(f"Supplier Name: {result.get('supplier_name', 'Not found')}")
        print(f"Matched Supplier: {result.get('supplier_name_matched', 'Not matched')}")
        print(f"Party Name: {result.get('party_name', 'Not found')}")
        print(f"Matched Party: {result.get('party_name_matched', 'Not matched')}")
        print(f"Date: {result.get('date', 'Not found')}")
        print(f"Bill Number: {result.get('bill_number', 'Not found')}")
        print(f"Amount: {result.get('amount', 'Not found')}")
        
        if 'queue_entry_id' in result:
            print(f"Queue Entry ID: {result['queue_entry_id']}")
        
        print("\n✅ AI OCR System Test Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_name_matching():
    """Test the name matching functionality."""
    try:
        print("\n🔍 Testing Name Matching...")
        from name_matcher import NameMatcher
        
        matcher = NameMatcher()
        
        # Test supplier matching
        test_supplier = "rachit fashion"
        result = matcher.find_match(test_supplier, 'supplier')
        print(f"Supplier match for '{test_supplier}': {result}")
        
        # Test party matching
        test_party = "retail store"
        result = matcher.find_match(test_party, 'party')
        print(f"Party match for '{test_party}': {result}")
        
        # Get cache stats
        stats = matcher.get_cache_stats()
        print(f"Cache stats: {stats}")
        
        print("✅ Name Matching Test Completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in name matching test: {str(e)}")
        return False

def test_queue_system():
    """Test the OCR queue system."""
    try:
        print("\n📋 Testing OCR Queue System...")
        from ocr_queue import OCRQueue
        
        queue = OCRQueue()
        
        # Get initial status
        status = queue.get_status()
        print(f"Initial queue status: {status}")
        
        # Test adding an entry (with dummy data)
        dummy_entry = {
            "image": base64.b64encode(b"dummy_image_data").decode(),
            "ocr_data": {
                "supplier_name": "Test Supplier",
                "amount": 1000,
                "date": "2024-01-01"
            }
        }
        
        entry_ids = queue.add_entries([dummy_entry])
        print(f"Added entry with ID: {entry_ids[0]}")
        
        # Get updated status
        status = queue.get_status()
        print(f"Updated queue status: {status}")
        
        # Get next entry
        next_entry = queue.get_next_entry()
        if next_entry:
            print(f"Retrieved entry: {next_entry['id']}")
            queue.mark_complete(next_entry['id'])
            print("Entry marked as complete")
        
        print("✅ OCR Queue Test Completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in queue test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 AI OCR System Test Suite")
    print("=" * 40)
    
    # Run all tests
    tests = [
        ("OCR System", test_ocr_system),
        ("Name Matching", test_name_matching),
        ("Queue System", test_queue_system)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "="*50)
    print("📊 Test Summary:")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The AI OCR system is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.") 