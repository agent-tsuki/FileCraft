"""
Hash encoder router.
"""

from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional

from app.services.encoders.hash_encoder import (
    HashEncoderService,
    get_hash_encoder_service,
)

hash_encoder_router = APIRouter(prefix="/encode/hash", tags=["Hash Encoder"])


@hash_encoder_router.post(
    "/text",
    summary="Generate hash of text",
    description="Generate cryptographic hash of text string",
)
async def hash_text(
    text: str = Form(..., description="Text to hash"),
    algorithm: str = Query(default="sha256", description="Hash algorithm"),
    output_format: str = Query(
        default="hex", enum=["hex", "base64", "bytes"], description="Output format"
    ),
    salt: Optional[str] = Query(default=None, description="Salt for hashing"),
    encoding: str = Query(default="utf-8", description="Text encoding"),
    service: HashEncoderService = Depends(get_hash_encoder_service),
) -> JSONResponse:
    """
    Generate hash of text.

    - **text**: Text to hash
    - **algorithm**: Hash algorithm (md5, sha1, sha256, sha512, etc.)
    - **output_format**: Output format (hex, base64, bytes)
    - **salt**: Optional salt for hashing
    - **encoding**: Text encoding

    Returns hash of the text.
    """
    try:
        # Encode text with specified encoding
        byte_data = text.encode(encoding)

        hash_result = await service.encode(
            byte_data, algorithm=algorithm, output_format=output_format, salt=salt
        )

        # Get algorithm info
        algo_info = service.get_algorithm_info(algorithm)

        return JSONResponse(
            content={
                "input": text[:100] + "..." if len(text) > 100 else text,
                "input_length": len(text),
                "hash": hash_result,
                "algorithm": algorithm,
                "output_format": output_format,
                "salt_used": salt is not None,
                "encoding": encoding,
                "algorithm_info": algo_info,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hashing failed: {str(e)}")


@hash_encoder_router.post(
    "/file",
    summary="Generate hash of file",
    description="Generate cryptographic hash of file content",
)
async def hash_file(
    file: UploadFile = File(...),
    algorithm: str = Query(default="sha256", description="Hash algorithm"),
    output_format: str = Query(
        default="hex", enum=["hex", "base64", "bytes"], description="Output format"
    ),
    salt: Optional[str] = Query(default=None, description="Salt for hashing"),
    use_streaming: bool = Query(
        default=True, description="Use streaming for large files"
    ),
    service: HashEncoderService = Depends(get_hash_encoder_service),
) -> JSONResponse:
    """
    Generate hash of file content.

    - **file**: File to hash
    - **algorithm**: Hash algorithm
    - **output_format**: Output format (hex, base64, bytes)
    - **salt**: Optional salt for hashing
    - **use_streaming**: Use streaming for large files

    Returns hash of the file.
    """
    try:
        if use_streaming:
            # Use streaming for large files
            hash_stream = service.encode_stream(
                file, algorithm=algorithm, output_format=output_format, salt=salt
            )
            # Get the result from stream
            hash_result = b""
            async for chunk in hash_stream:
                hash_result += chunk
            hash_result = hash_result.decode("utf-8")
        else:
            hash_result = await service.encode_file(
                file, algorithm=algorithm, output_format=output_format, salt=salt
            )

        # Get algorithm info
        algo_info = service.get_algorithm_info(algorithm)

        return JSONResponse(
            content={
                "filename": file.filename,
                "file_size": file.size if hasattr(file, "size") else "unknown",
                "content_type": file.content_type,
                "hash": hash_result,
                "algorithm": algorithm,
                "output_format": output_format,
                "salt_used": salt is not None,
                "streaming_used": use_streaming,
                "algorithm_info": algo_info,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File hashing failed: {str(e)}")


@hash_encoder_router.post(
    "/hmac",
    summary="Generate HMAC",
    description="Generate HMAC (Hash-based Message Authentication Code)",
)
async def generate_hmac(
    data: str = Form(..., description="Data to generate HMAC for"),
    key: str = Form(..., description="Secret key for HMAC"),
    algorithm: str = Query(default="sha256", description="Hash algorithm"),
    output_format: str = Query(
        default="hex", enum=["hex", "base64", "bytes"], description="Output format"
    ),
    encoding: str = Query(default="utf-8", description="Text encoding"),
    service: HashEncoderService = Depends(get_hash_encoder_service),
) -> JSONResponse:
    """
    Generate HMAC.

    - **data**: Data to generate HMAC for
    - **key**: Secret key for HMAC
    - **algorithm**: Hash algorithm
    - **output_format**: Output format (hex, base64, bytes)
    - **encoding**: Text encoding

    Returns HMAC of the data.
    """
    try:
        hmac_result = await service.encode(
            data,
            algorithm=algorithm,
            output_format=output_format,
            hmac_key=key,
            encoding=encoding,
        )

        return JSONResponse(
            content={
                "data": data[:100] + "..." if len(data) > 100 else data,
                "hmac": hmac_result,
                "algorithm": algorithm,
                "output_format": output_format,
                "key_provided": True,
                "encoding": encoding,
                "type": "HMAC",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HMAC generation failed: {str(e)}")


@hash_encoder_router.post(
    "/verify", summary="Verify hash", description="Verify data against expected hash"
)
async def verify_hash(
    data: str = Form(..., description="Data to verify"),
    expected_hash: str = Form(..., description="Expected hash value"),
    algorithm: str = Query(default="sha256", description="Hash algorithm"),
    output_format: str = Query(
        default="hex", enum=["hex", "base64", "bytes"], description="Hash format"
    ),
    salt: Optional[str] = Query(default=None, description="Salt used in original hash"),
    encoding: str = Query(default="utf-8", description="Text encoding"),
    service: HashEncoderService = Depends(get_hash_encoder_service),
) -> JSONResponse:
    """
    Verify data against expected hash.

    - **data**: Data to verify
    - **expected_hash**: Expected hash value
    - **algorithm**: Hash algorithm used
    - **output_format**: Format of the hash
    - **salt**: Salt used in original hash
    - **encoding**: Text encoding

    Returns verification result.
    """
    try:
        # Generate hash of the data
        computed_hash = await service.encode(
            data,
            algorithm=algorithm,
            output_format=output_format,
            salt=salt,
            encoding=encoding,
        )

        # Verify hashes match
        is_valid = await service.verify_hash(
            data,
            expected_hash,
            algorithm=algorithm,
            output_format=output_format,
            salt=salt,
            encoding=encoding,
        )

        return JSONResponse(
            content={
                "data": data[:100] + "..." if len(data) > 100 else data,
                "expected_hash": expected_hash,
                "computed_hash": computed_hash,
                "is_valid": is_valid,
                "algorithm": algorithm,
                "output_format": output_format,
                "salt_used": salt is not None,
                "encoding": encoding,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Hash verification failed: {str(e)}"
        )


@hash_encoder_router.get(
    "/algorithms",
    summary="List hash algorithms",
    description="Get list of available hash algorithms",
)
async def list_hash_algorithms(
    service: HashEncoderService = Depends(get_hash_encoder_service),
) -> JSONResponse:
    """
    List available hash algorithms.

    Returns list of supported hash algorithms.
    """
    try:
        algorithms = service.list_algorithms()

        # Get info for common algorithms
        common_info = {}
        for algo in algorithms["common"]:
            try:
                info = service.get_algorithm_info(algo)
                common_info[algo] = info
            except:
                common_info[algo] = {"error": "Info unavailable"}

        return JSONResponse(
            content={
                "algorithms": algorithms,
                "common_algorithm_info": common_info,
                "recommendations": {
                    "general_purpose": "sha256",
                    "high_security": "sha512",
                    "legacy_compatibility": "sha1",
                    "fast_checksums": "md5",
                    "cryptographic": ["sha256", "sha384", "sha512"],
                    "avoid_for_security": ["md5", "sha1"],
                },
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Algorithm listing failed: {str(e)}"
        )


@hash_encoder_router.get(
    "/algorithm/{algorithm_name}",
    summary="Get algorithm information",
    description="Get detailed information about specific hash algorithm",
)
async def get_algorithm_info(
    algorithm_name: str, service: HashEncoderService = Depends(get_hash_encoder_service)
) -> JSONResponse:
    """
    Get information about specific hash algorithm.

    - **algorithm_name**: Name of the hash algorithm

    Returns detailed algorithm information.
    """
    try:
        info = service.get_algorithm_info(algorithm_name)

        # Add additional context
        security_notes = {
            "md5": "Cryptographically broken, avoid for security purposes",
            "sha1": "Deprecated for security, use SHA-2 family instead",
            "sha256": "Secure, widely recommended",
            "sha512": "More secure, larger output",
            "sha3_256": "Latest SHA-3 standard, quantum-resistant",
            "sha3_512": "SHA-3 with maximum security",
        }

        use_cases = {
            "md5": ["File integrity checks", "Non-security checksums"],
            "sha1": ["Legacy systems", "Git commits"],
            "sha256": ["Digital signatures", "Password hashing", "Blockchain"],
            "sha512": ["High-security applications", "Server certificates"],
            "sha3_256": ["Future-proof applications", "Post-quantum cryptography"],
            "blake2b": ["High-performance hashing", "Cryptographic applications"],
        }

        info["security_notes"] = security_notes.get(
            algorithm_name.lower(), "No specific notes"
        )
        info["common_use_cases"] = use_cases.get(
            algorithm_name.lower(), ["General hashing"]
        )

        return JSONResponse(content=info)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Algorithm info failed: {str(e)}")


@hash_encoder_router.get(
    "/info",
    summary="Get hash encoder information",
    description="Get information about hash encoding",
)
async def get_hash_encoder_info(
    service: HashEncoderService = Depends(get_hash_encoder_service),
) -> JSONResponse:
    """
    Get hash encoder information.

    Returns information about hash encoding capabilities.
    """
    return JSONResponse(
        content={
            "encoder": "Cryptographic Hash Functions",
            "description": "Generate cryptographic hashes for data integrity and security",
            "hash_types": {
                "MD5": "128-bit hash, fast but cryptographically broken",
                "SHA-1": "160-bit hash, deprecated for security",
                "SHA-2": "Family including SHA-256, SHA-512 - currently secure",
                "SHA-3": "Latest standard, quantum-resistant",
                "BLAKE2": "High-performance alternative to SHA-2",
            },
            "features": [
                "Multiple hash algorithms",
                "Various output formats (hex, base64, bytes)",
                "Salt support for enhanced security",
                "HMAC generation",
                "Hash verification",
                "Streaming for large files",
            ],
            "security_considerations": [
                "Use SHA-256 or higher for security applications",
                "Avoid MD5 and SHA-1 for cryptographic purposes",
                "Use salts for password hashing",
                "Consider HMAC for message authentication",
                "Verify hashes to ensure data integrity",
            ],
            "use_cases": {
                "data_integrity": "Verify files haven't been modified",
                "password_storage": "Store password hashes (with salt)",
                "digital_signatures": "Part of digital signature process",
                "blockchain": "Block validation and proof-of-work",
                "checksums": "Quick data validation",
                "message_auth": "HMAC for message authentication",
            },
            "best_practices": [
                "Use appropriate algorithm for your security needs",
                "Always use salt for password hashing",
                "Verify hashes to detect tampering",
                "Use streaming for large files",
                "Keep hash algorithms up to date",
            ],
        }
    )
