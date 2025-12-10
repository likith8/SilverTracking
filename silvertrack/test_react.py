"""
Test script to verify React app is being served correctly
Run this to check: python manage.py shell < test_react.py
"""
from django.test import Client
from pathlib import Path
from django.conf import settings

client = Client()
response = client.get('/')

print(f"Status Code: {response.status_code}")
print(f"Content-Type: {response.get('Content-Type')}")
print(f"Content Length: {len(response.content)} bytes")
print("\nFirst 500 characters of response:")
print(response.content[:500].decode('utf-8', errors='ignore'))

# Check if React HTML structure exists
content = response.content.decode('utf-8', errors='ignore')
if '<div id="root">' in content:
    print("\n✓ React app HTML structure found!")
else:
    print("\n✗ React app HTML structure NOT found!")
    
if '/assets/' in content:
    print("✓ Asset paths found in HTML")
else:
    print("✗ Asset paths NOT found in HTML")


