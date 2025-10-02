# FileCraft Encoder/Decoder System Documentation

## Overview

The FileCraft Encoder/Decoder System provides comprehensive encoding and decoding capabilities for various formats commonly used in web development, security, and data processing. The system is built with FastAPI and offers both synchronous and streaming APIs for handling data of any size.

## 🌟 Features

- **Multiple Format Support**: Base64, JWT, URL, Hex, Hash (MD5, SHA1, SHA256, SHA512, etc.)
- **Streaming Support**: Handle large files efficiently with streaming responses
- **Validation & Error Handling**: Robust input validation and comprehensive error messages
- **Security**: Secure handling of sensitive data with proper JWT verification
- **Performance**: Optimized for speed and memory efficiency
- **Flexibility**: Multiple output formats and configuration options

## 📚 API Endpoints

### System Overview
- `GET /codec/` - Get system overview and capabilities
- `GET /codec/formats` - List all supported formats

### Base64 Encoding/Decoding
**Encoding:**
- `POST /codec/encode/base64/text` - Encode text to Base64
- `POST /codec/encode/base64/file` - Encode file to Base64
- `GET /codec/encode/base64/info` - Get encoder information

**Decoding:**
- `POST /codec/decode/base64/text` - Decode Base64 text
- `POST /codec/decode/base64/file` - Decode Base64 file
- `POST /codec/decode/base64/validate` - Validate Base64 format
- `GET /codec/decode/base64/info` - Get decoder information

### JWT (JSON Web Token) Encoding/Decoding
**Encoding:**
- `POST /codec/encode/jwt/payload` - Create JWT from JSON payload
- `POST /codec/encode/jwt/text` - Create JWT from text
- `POST /codec/encode/jwt/file` - Create JWT from file
- `GET /codec/encode/jwt/algorithms` - List supported algorithms
- `GET /codec/encode/jwt/info` - Get encoder information

**Decoding:**
- `POST /codec/decode/jwt/token` - Decode and verify JWT
- `POST /codec/decode/jwt/file` - Decode JWT from file
- `POST /codec/decode/jwt/inspect` - Inspect token without verification
- `POST /codec/decode/jwt/header` - Decode JWT header only
- `POST /codec/decode/jwt/validate` - Validate JWT format
- `GET /codec/decode/jwt/info` - Get decoder information

### URL Encoding/Decoding
**Encoding:**
- `POST /codec/encode/url/text` - URL encode text
- `POST /codec/encode/url/file` - URL encode file content
- `POST /codec/encode/url/params` - Encode dictionary as URL parameters
- `POST /codec/encode/url/component` - Encode specific URL component
- `GET /codec/encode/url/chars` - Get encoding character information
- `GET /codec/encode/url/info` - Get encoder information

**Decoding:**
- `POST /codec/decode/url/text` - Decode URL encoded text
- `POST /codec/decode/url/file` - Decode URL encoded file
- `POST /codec/decode/url/params` - Parse URL query parameters
- `POST /codec/decode/url/parse` - Parse complete URL
- `POST /codec/decode/url/analyze` - Analyze URL content
- `GET /codec/decode/url/info` - Get decoder information

### Hexadecimal Encoding/Decoding
**Encoding:**
- `POST /codec/encode/hex/text` - Encode text to hex
- `POST /codec/encode/hex/file` - Encode file to hex
- `POST /codec/encode/hex/ascii` - Encode ASCII text to hex
- `POST /codec/encode/hex/with_length` - Encode with length prefix
- `GET /codec/encode/hex/formats` - Get hex format examples
- `GET /codec/encode/hex/info` - Get encoder information

**Decoding:**
- `POST /codec/decode/hex/text` - Decode hex text
- `POST /codec/decode/hex/file` - Decode hex file
- `POST /codec/decode/hex/to_text` - Decode hex directly to text
- `POST /codec/decode/hex/with_length` - Decode length-prefixed hex
- `POST /codec/decode/hex/analyze` - Analyze hex content
- `GET /codec/decode/hex/info` - Get decoder information

### Hash Encoding
- `POST /codec/encode/hash/text` - Generate hash of text
- `POST /codec/encode/hash/file` - Generate hash of file
- `POST /codec/encode/hash/hmac` - Generate HMAC
- `POST /codec/encode/hash/verify` - Verify hash
- `GET /codec/encode/hash/algorithms` - List hash algorithms
- `GET /codec/encode/hash/algorithm/{name}` - Get algorithm info
- `GET /codec/encode/hash/info` - Get encoder information

## 🚀 Usage Examples

### Base64 Encoding
```bash
# Encode text to Base64
curl -X POST http://localhost:8000/codec/encode/base64/text \
  -d "text=Hello World!"

# Encode with URL-safe Base64
curl -X POST "http://localhost:8000/codec/encode/base64/text?url_safe=true" \
  -d "text=Hello World!"
```

### Base64 Decoding
```bash
# Decode Base64 text
curl -X POST http://localhost:8000/codec/decode/base64/text \
  -d "encoded_text=SGVsbG8gV29ybGQh"

# Validate Base64 format
curl -X POST http://localhost:8000/codec/decode/base64/validate \
  -d "encoded_text=SGVsbG8gV29ybGQh"
```

### JWT Operations
```bash
# Create JWT token
curl -X POST http://localhost:8000/codec/encode/jwt/payload \
  -d 'payload={"user": "john", "role": "admin"}' \
  -d "secret=my-secret-key" \
  -d "exp_minutes=60"

# Decode JWT token
curl -X POST http://localhost:8000/codec/decode/jwt/token \
  -d "token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -d "secret=my-secret-key"

# Inspect JWT without verification
curl -X POST http://localhost:8000/codec/decode/jwt/inspect \
  -d "token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### URL Encoding/Decoding
```bash
# URL encode text
curl -X POST http://localhost:8000/codec/encode/url/text \
  -d "text=Hello World! @#$%"

# URL decode text
curl -X POST http://localhost:8000/codec/decode/url/text \
  -d "encoded_text=Hello%20World%21%20%40%23%24%25"

# Parse URL parameters
curl -X POST http://localhost:8000/codec/decode/url/params \
  -d "query_string=name=John%20Doe&email=john%40example.com"
```

### Hexadecimal Operations
```bash
# Encode text to hex
curl -X POST "http://localhost:8000/codec/encode/hex/text?uppercase=true&separator= " \
  -d "text=Hello"

# Decode hex to text
curl -X POST http://localhost:8000/codec/decode/hex/text \
  -d "hex_text=48656c6c6f"
```

### Hash Generation
```bash
# Generate SHA256 hash
curl -X POST "http://localhost:8000/codec/encode/hash/text?algorithm=sha256" \
  -d "text=Hello World"

# Generate HMAC
curl -X POST "http://localhost:8000/codec/encode/hash/hmac?algorithm=sha256" \
  -d "data=Hello World" \
  -d "key=secret-key"

# Verify hash
curl -X POST "http://localhost:8000/codec/encode/hash/verify?algorithm=sha256" \
  -d "data=Hello World" \
  -d "expected_hash=a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
```

## 🔐 Security Considerations

### JWT Security
- Always use strong secret keys (minimum 256 bits for HS256)
- Set appropriate expiration times
- Verify tokens on the server side
- Use HTTPS in production
- Rotate keys regularly

### Hash Security
- Use SHA-256 or higher for cryptographic purposes
- Avoid MD5 and SHA-1 for security applications
- Use salts for password hashing
- Consider HMAC for message authentication

### General Security
- Validate all inputs
- Use appropriate encoding for context
- Handle sensitive data carefully
- Implement rate limiting for APIs

## 📝 Response Formats

All endpoints return JSON responses with consistent structure:

### Success Response
```json
{
  "input": "original input data",
  "encoded/decoded": "result",
  "algorithm": "algorithm used",
  "additional_info": "..."
}
```

### Error Response
```json
{
  "detail": "Error description"
}
```

### Streaming Responses
For file operations, responses may be:
- `text/plain` for text-based encodings
- `application/octet-stream` for binary data
- `application/json` for JSON data
- `application/jwt` for JWT tokens

## 🔧 Configuration Options

### Base64
- `url_safe`: Use URL-safe encoding (- and _ instead of + and /)
- `validate`: Validate format before decoding

### JWT
- `algorithm`: Signing algorithm (HS256, HS384, HS512, RS256, ES256)
- `exp_minutes`: Expiration time in minutes
- `issuer`: JWT issuer claim
- `audience`: JWT audience claim
- `subject`: JWT subject claim

### URL
- `safe`: Characters to not encode
- `encoding`: Character encoding (default: utf-8)
- `plus_encoding`: Use + for spaces

### Hex
- `uppercase`: Use uppercase hex digits
- `separator`: Separator between bytes
- `prefix`: Prefix for hex values
- `ignore_whitespace`: Ignore whitespace when decoding
- `ignore_separators`: Ignore separators when decoding

### Hash
- `algorithm`: Hash algorithm (md5, sha1, sha256, sha512, etc.)
- `output_format`: Output format (hex, base64, bytes)
- `salt`: Salt for hashing
- `hmac_key`: Key for HMAC generation

## 🎯 Use Cases

### Base64
- File transmission over text protocols
- Embedding images in HTML/CSS
- API data serialization
- Email attachments (MIME encoding)

### JWT
- Authentication tokens
- API authorization
- Secure data exchange
- Single sign-on (SSO)
- Microservices communication

### URL
- Query parameters in URLs
- Form data submission
- Path components encoding
- API endpoint parameters

### Hex
- Binary file analysis
- Debugging binary data
- Protocol analysis
- Memory dumps
- Cryptographic key display

### Hash
- Data integrity verification
- Password storage (with salt)
- Digital signatures
- Blockchain applications
- File checksums
- Message authentication (HMAC)

## 🚀 Performance Tips

1. **Use Streaming**: For large files, use streaming endpoints
2. **Choose Right Algorithm**: Balance security needs with performance
3. **Validate Input**: Use validation endpoints before processing
4. **Cache Results**: Cache frequently computed hashes
5. **Batch Operations**: Process multiple items when possible

## 🛠️ Development

### Running Tests
```bash
python test_encoder_decoder.py --wait
```

### Adding New Encoders/Decoders
1. Create service class extending `BaseEncoderService` or `BaseDecoderService`
2. Implement required abstract methods
3. Create router with endpoints
4. Add to main router
5. Update documentation

## 📊 API Testing Results

The comprehensive test suite covers:
- ✅ System overview endpoints
- ✅ Base64 encoding/decoding
- ✅ JWT token operations
- ✅ URL encoding/decoding  
- ✅ Hexadecimal operations
- ✅ Hash generation and verification

All tests pass successfully, demonstrating the system's reliability and completeness.

## 🤝 Contributing

1. Follow the existing code structure
2. Add comprehensive tests for new features
3. Update documentation
4. Ensure security best practices
5. Test with various input sizes and formats

## 📚 References

- [RFC 4648 - Base64 Encoding](https://tools.ietf.org/html/rfc4648)
- [RFC 7519 - JSON Web Token](https://tools.ietf.org/html/rfc7519)
- [RFC 3986 - URI Generic Syntax](https://tools.ietf.org/html/rfc3986)
- [FIPS 180-4 - Secure Hash Standard](https://csrc.nist.gov/publications/detail/fips/180/4/final)
- [RFC 2104 - HMAC](https://tools.ietf.org/html/rfc2104)

---

*FileCraft Encoder/Decoder System v1.0.0 - Built with FastAPI*