#!/usr/bin/env python3
"""
Test script for the enhanced image converter API.
"""
import requests
import io
from PIL import Image
import json

# Create a simple test image
def create_test_image():
    """Create a simple test image."""
    img = Image.new('RGB', (300, 200), color=(255, 0, 0))  # Red image
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def test_image_formats_endpoint():
    """Test the formats endpoint."""
    print("Testing /images/formats endpoint...")
    response = requests.get('http://localhost:8080/images/formats')
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Formats endpoint works! Found {len(data['input_formats'])} input formats")
        print(f"   Output formats: {', '.join(data['output_formats'][:5])}...")
        return True
    else:
        print(f"❌ Formats endpoint failed: {response.status_code}")
        return False

def test_image_conversion():
    """Test basic image conversion."""
    print("\nTesting /images/convert endpoint...")
    
    # Create test image
    test_img = create_test_image()
    
    # Prepare files and data
    files = {'image': ('test.png', test_img, 'image/png')}
    data = {
        'target_format': 'jpeg',
        'quality': 90,
        'optimization_level': 'medium'
    }
    
    try:
        response = requests.post(
            'http://localhost:8080/images/convert',
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            print("✅ Image conversion successful!")
            print(f"   Content-Type: {response.headers.get('content-type')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Image conversion failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Image conversion error: {e}")
        return False

def test_image_info():
    """Test image info endpoint."""
    print("\nTesting /images/info endpoint...")
    
    # Create test image
    test_img = create_test_image()
    
    files = {'image': ('test.png', test_img, 'image/png')}
    
    try:
        response = requests.post(
            'http://localhost:8080/images/info',
            files=files
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Image info endpoint works!")
            print(f"   Format: {data.get('format')}")
            print(f"   Size: {data.get('size')}")
            print(f"   Megapixels: {data.get('megapixels')}")
            return True
        else:
            print(f"❌ Image info failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Image info error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing FileCraft Enhanced Image Converter API")
    print("=" * 50)
    
    tests = [
        test_image_formats_endpoint,
        test_image_conversion,
        test_image_info
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The enhanced image converter is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()