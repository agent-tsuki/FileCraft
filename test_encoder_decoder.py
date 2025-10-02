#!/usr/bin/env python3
"""
Comprehensive test for the encoder/decoder system.
"""
import requests
import json
import base64
import sys
import time
from pathlib import Path


class EncoderDecoderTester:
    """Test class for encoder/decoder system."""
    
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.codec_url = f"{base_url}/codec"
        self.passed = 0
        self.failed = 0
    
    def log(self, message, status="INFO"):
        """Log test messages."""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
    
    def test_api_endpoint(self, method, endpoint, **kwargs):
        """Test an API endpoint."""
        try:
            url = f"{self.codec_url}{endpoint}"
            self.log(f"Testing {method} {endpoint}")
            
            if method.upper() == "GET":
                response = requests.get(url, **kwargs)
            elif method.upper() == "POST":
                response = requests.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == 200:
                self.log(f"✅ {endpoint} - Status: {response.status_code}", "PASS")
                self.passed += 1
                return response.json()
            else:
                self.log(f"❌ {endpoint} - Status: {response.status_code}", "FAIL")
                self.log(f"Response: {response.text}", "ERROR")
                self.failed += 1
                return None
                
        except Exception as e:
            self.log(f"❌ {endpoint} - Exception: {str(e)}", "FAIL")
            self.failed += 1
            return None
    
    def test_base64_encoder(self):
        """Test Base64 encoder functionality."""
        self.log("=== Testing Base64 Encoder ===")
        
        # Test text encoding
        test_text = "Hello, World! 🌍"
        response = self.test_api_endpoint(
            "POST", 
            "/encode/base64/text",
            data={"text": test_text}
        )
        
        if response:
            encoded = response.get("encoded")
            if encoded:
                # Verify we can decode it back
                try:
                    decoded = base64.b64decode(encoded).decode('utf-8')
                    if decoded == test_text:
                        self.log("✅ Base64 encoding/decoding verification passed", "PASS")
                        self.passed += 1
                    else:
                        self.log("❌ Base64 encoding/decoding verification failed", "FAIL")
                        self.failed += 1
                except Exception as e:
                    self.log(f"❌ Base64 verification error: {e}", "FAIL")
                    self.failed += 1
        
        # Test encoder info
        self.test_api_endpoint("GET", "/encode/base64/info")
    
    def test_base64_decoder(self):
        """Test Base64 decoder functionality."""
        self.log("=== Testing Base64 Decoder ===")
        
        # Test text decoding
        test_text = "Hello, Base64 Decoder!"
        encoded_text = base64.b64encode(test_text.encode('utf-8')).decode('ascii')
        
        response = self.test_api_endpoint(
            "POST",
            "/decode/base64/text", 
            data={"encoded_text": encoded_text}
        )
        
        if response and response.get("decoded") == test_text:
            self.log("✅ Base64 decoder verification passed", "PASS")
            self.passed += 1
        else:
            self.log("❌ Base64 decoder verification failed", "FAIL")
            self.failed += 1
        
        # Test validation
        self.test_api_endpoint(
            "POST",
            "/decode/base64/validate",
            data={"encoded_text": encoded_text}
        )
        
        # Test decoder info
        self.test_api_endpoint("GET", "/decode/base64/info")
    
    def test_jwt_encoder(self):
        """Test JWT encoder functionality."""
        self.log("=== Testing JWT Encoder ===")
        
        # Test payload encoding
        test_payload = '{"user": "test", "role": "admin"}'
        response = self.test_api_endpoint(
            "POST",
            "/encode/jwt/payload",
            data={
                "payload": test_payload,
                "secret": "test-secret-key",
                "exp_minutes": 60
            }
        )
        
        if response and "token" in response:
            self.log("✅ JWT token generation successful", "PASS")
            self.passed += 1
            
            # Store token for decoder test
            self.test_jwt_token = response["token"]
        else:
            self.log("❌ JWT token generation failed", "FAIL")
            self.failed += 1
            self.test_jwt_token = None
        
        # Test text encoding
        self.test_api_endpoint(
            "POST",
            "/encode/jwt/text",
            data={
                "text": "Test JWT content",
                "secret": "test-secret"
            }
        )
        
        # Test algorithms list
        self.test_api_endpoint("GET", "/encode/jwt/algorithms")
        
        # Test encoder info
        self.test_api_endpoint("GET", "/encode/jwt/info")
    
    def test_jwt_decoder(self):
        """Test JWT decoder functionality."""
        self.log("=== Testing JWT Decoder ===")
        
        if hasattr(self, 'test_jwt_token') and self.test_jwt_token:
            # Test token decoding
            response = self.test_api_endpoint(
                "POST",
                "/decode/jwt/token",
                data={
                    "token": self.test_jwt_token,
                    "secret": "test-secret-key",
                    "verify": True
                }
            )
            
            if response and "payload" in response:
                self.log("✅ JWT token decoding successful", "PASS") 
                self.passed += 1
            else:
                self.log("❌ JWT token decoding failed", "FAIL")
                self.failed += 1
            
            # Test token inspection without verification
            self.test_api_endpoint(
                "POST",
                "/decode/jwt/inspect",
                data={"token": self.test_jwt_token}
            )
            
            # Test header decoding
            self.test_api_endpoint(
                "POST", 
                "/decode/jwt/header",
                data={"token": self.test_jwt_token}
            )
        else:
            self.log("❌ No JWT token available for decoder testing", "FAIL")
            self.failed += 1
        
        # Test decoder info
        self.test_api_endpoint("GET", "/decode/jwt/info")
    
    def test_url_encoder(self):
        """Test URL encoder functionality."""
        self.log("=== Testing URL Encoder ===")
        
        # Test text encoding
        test_text = "Hello World! Special chars: @#$%^&*()"
        self.test_api_endpoint(
            "POST",
            "/encode/url/text",
            data={"text": test_text}
        )
        
        # Test parameter encoding
        test_params = '{"name": "John Doe", "email": "john@example.com", "message": "Hello & welcome!"}'
        self.test_api_endpoint(
            "POST",
            "/encode/url/params",
            data={"params": test_params}
        )
        
        # Test component encoding
        self.test_api_endpoint(
            "POST",
            "/encode/url/component",
            data={"component": "path/with spaces/and&special=chars"},
            params={"component_type": "path"}
        )
        
        # Test character info
        self.test_api_endpoint("GET", "/encode/url/chars")
        
        # Test encoder info
        self.test_api_endpoint("GET", "/encode/url/info")
    
    def test_url_decoder(self):
        """Test URL decoder functionality."""
        self.log("=== Testing URL Decoder ===")
        
        # Test text decoding
        encoded_text = "Hello%20World%21%20Special%20chars%3A%20%40%23%24%25%5E%26%2A%28%29"
        self.test_api_endpoint(
            "POST",
            "/decode/url/text",
            data={"encoded_text": encoded_text}
        )
        
        # Test parameter decoding
        query_string = "name=John%20Doe&email=john%40example.com&message=Hello%20%26%20welcome%21"
        self.test_api_endpoint(
            "POST",
            "/decode/url/params", 
            data={"query_string": query_string}
        )
        
        # Test URL parsing
        test_url = "https://example.com:8080/path/to/resource?param1=value1&param2=value%202#fragment"
        self.test_api_endpoint(
            "POST",
            "/decode/url/parse",
            data={"url": test_url}
        )
        
        # Test content analysis
        self.test_api_endpoint(
            "POST",
            "/decode/url/analyze",
            data={"encoded_text": encoded_text}
        )
        
        # Test decoder info
        self.test_api_endpoint("GET", "/decode/url/info")
    
    def test_hex_encoder(self):
        """Test Hex encoder functionality."""
        self.log("=== Testing Hex Encoder ===")
        
        # Test text encoding
        test_text = "Hello Hex!"
        self.test_api_endpoint(
            "POST",
            "/encode/hex/text",
            data={"text": test_text},
            params={"separator": " ", "uppercase": True}
        )
        
        # Test ASCII encoding
        self.test_api_endpoint(
            "POST",
            "/encode/hex/ascii", 
            data={"ascii_text": "ASCII"},
            params={"separator": ":", "prefix": "0x"}
        )
        
        # Test length-prefixed encoding
        self.test_api_endpoint(
            "POST",
            "/encode/hex/with_length",
            data={"data": "Test data"}
        )
        
        # Test format examples
        self.test_api_endpoint("GET", "/encode/hex/formats")
        
        # Test encoder info
        self.test_api_endpoint("GET", "/encode/hex/info")
    
    def test_hex_decoder(self):
        """Test Hex decoder functionality."""
        self.log("=== Testing Hex Decoder ===")
        
        # Test text decoding
        hex_text = "48656c6c6f2048657821"  # "Hello Hex!"
        response = self.test_api_endpoint(
            "POST",
            "/decode/hex/text",
            data={"hex_text": hex_text},
            params={"output_format": "text"}
        )
        
        if response and response.get("decoded") == "Hello Hex!":
            self.log("✅ Hex decoder verification passed", "PASS")
            self.passed += 1
        else:
            self.log("❌ Hex decoder verification failed", "FAIL")
            self.failed += 1
        
        # Test direct text decoding
        self.test_api_endpoint(
            "POST",
            "/decode/hex/to_text",
            data={"hex_text": hex_text}
        )
        
        # Test content analysis
        self.test_api_endpoint(
            "POST",
            "/decode/hex/analyze",
            data={"hex_text": "48 65 6c 6c 6f 20 57 6f 72 6c 64"}
        )
        
        # Test decoder info
        self.test_api_endpoint("GET", "/decode/hex/info")
    
    def test_hash_encoder(self):
        """Test Hash encoder functionality."""
        self.log("=== Testing Hash Encoder ===")
        
        # Test text hashing
        test_text = "Hello Hash!"
        response = self.test_api_endpoint(
            "POST",
            "/encode/hash/text",
            data={"text": test_text},
            params={"algorithm": "sha256"}
        )
        
        if response and "hash" in response:
            self.log("✅ Hash generation successful", "PASS")
            self.passed += 1
            
            # Test hash verification
            generated_hash = response["hash"]
            verify_response = self.test_api_endpoint(
                "POST", 
                "/encode/hash/verify",
                data={
                    "data": test_text,
                    "expected_hash": generated_hash
                },
                params={"algorithm": "sha256"}
            )
            
            if verify_response and verify_response.get("is_valid"):
                self.log("✅ Hash verification successful", "PASS")
                self.passed += 1
            else:
                self.log("❌ Hash verification failed", "FAIL") 
                self.failed += 1
        else:
            self.log("❌ Hash generation failed", "FAIL")
            self.failed += 1
        
        # Test HMAC generation
        self.test_api_endpoint(
            "POST",
            "/encode/hash/hmac",
            data={
                "data": "Test HMAC data",
                "key": "secret-key"
            },
            params={"algorithm": "sha256"}
        )
        
        # Test algorithm list
        self.test_api_endpoint("GET", "/encode/hash/algorithms")
        
        # Test specific algorithm info
        self.test_api_endpoint("GET", "/encode/hash/algorithm/sha256")
        
        # Test encoder info
        self.test_api_endpoint("GET", "/encode/hash/info")
    
    def test_system_overview(self):
        """Test system overview endpoints."""
        self.log("=== Testing System Overview ===")
        
        # Test main overview
        self.test_api_endpoint("GET", "/")
        
        # Test supported formats
        self.test_api_endpoint("GET", "/formats")
    
    def run_all_tests(self):
        """Run all encoder/decoder tests."""
        self.log("🚀 Starting Encoder/Decoder System Tests")
        start_time = time.time()
        
        try:
            # Test system overview
            self.test_system_overview()
            
            # Test Base64
            self.test_base64_encoder()
            self.test_base64_decoder()
            
            # Test JWT
            self.test_jwt_encoder() 
            self.test_jwt_decoder()
            
            # Test URL
            self.test_url_encoder()
            self.test_url_decoder()
            
            # Test Hex
            self.test_hex_encoder()
            self.test_hex_decoder()
            
            # Test Hash
            self.test_hash_encoder()
            
        except KeyboardInterrupt:
            self.log("Tests interrupted by user", "WARN")
        except Exception as e:
            self.log(f"Unexpected error during testing: {e}", "ERROR")
        
        # Print summary
        end_time = time.time()
        duration = end_time - start_time
        total_tests = self.passed + self.failed
        
        self.log("=" * 50)
        self.log("🏁 TEST SUMMARY")
        self.log(f"Total Tests: {total_tests}")
        self.log(f"Passed: {self.passed} ✅")
        self.log(f"Failed: {self.failed} ❌")
        self.log(f"Success Rate: {(self.passed/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        self.log(f"Duration: {duration:.2f} seconds")
        
        if self.failed == 0:
            self.log("🎉 ALL TESTS PASSED!", "SUCCESS")
            return True
        else:
            self.log("⚠️  SOME TESTS FAILED", "WARN")
            return False


def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test encoder/decoder system")
    parser.add_argument(
        "--url", 
        default="http://localhost:8080",
        help="Base URL of the FileCraft server (default: http://localhost:8080)"
    )
    parser.add_argument(
        "--wait", 
        action="store_true",
        help="Wait for server to be ready before testing"
    )
    
    args = parser.parse_args()
    
    # Wait for server if requested
    if args.wait:
        print("⏳ Waiting for server to be ready...")
        import time
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{args.url}/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Server is ready!")
                    break
            except requests.exceptions.RequestException:
                pass
            
            if attempt == max_attempts - 1:
                print("❌ Server not ready after 30 attempts")
                sys.exit(1)
            
            time.sleep(1)
    
    # Run tests
    tester = EncoderDecoderTester(args.url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()