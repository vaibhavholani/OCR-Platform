#!/usr/bin/env python3
"""
Main entry point for the OCR Platform Flask application.
Run this file to start the development server.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("🚀 Starting OCR Platform Backend...")
    print("📊 API will be available at: http://localhost:5000")
    print("📚 API Documentation:")
    print("   - Users: http://localhost:5000/api/users")
    print("   - Documents: http://localhost:5000/api/documents") 
    print("   - Exports: http://localhost:5000/api/exports")
    print("")
    app.run(debug=True, host='0.0.0.0', port=5000) 