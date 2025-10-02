#!/usr/bin/env python3
"""
Test file type validation for audio files.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.file_validation import FileValidationService
from app.core.config import get_config

def test_file_type_validation():
    """Test that audio files are correctly identified."""
    print("🔍 Testing File Type Validation")
    print("=" * 40)
    
    config = get_config()
    validator = FileValidationService(config)
    
    # Test various audio extensions
    audio_extensions = [
        "test.wav", "test.mp3", "test.flac", "test.aac", 
        "test.ogg", "test.m4a", "test.wma", "test.aiff"
    ]
    
    print("Testing audio file extensions:")
    all_correct = True
    
    for filename in audio_extensions:
        try:
            clean_name, file_type = validator.get_file_type(filename)
            if file_type == "audio":
                print(f"✅ {filename} -> {file_type}")
            else:
                print(f"❌ {filename} -> {file_type} (expected 'audio')")
                all_correct = False
        except Exception as e:
            print(f"❌ {filename} -> ERROR: {e}")
            all_correct = False
    
    print()
    
    # Test image extensions (should not be audio)
    print("Testing non-audio file extensions:")
    non_audio_extensions = [
        ("test.jpg", "img"), ("test.png", "img"), 
        ("test.pdf", "pdf"), ("test.txt", "docs")
    ]
    
    for filename, expected_type in non_audio_extensions:
        try:
            clean_name, file_type = validator.get_file_type(filename)
            if file_type == expected_type:
                print(f"✅ {filename} -> {file_type}")
            else:
                print(f"❌ {filename} -> {file_type} (expected '{expected_type}')")
                all_correct = False
        except Exception as e:
            print(f"❌ {filename} -> ERROR: {e}")
            all_correct = False
    
    print()
    
    if all_correct:
        print("🎉 File type validation working correctly!")
        print("✅ Audio files are properly identified as 'audio' type")
        print("✅ Non-audio files are properly identified")
        return True
    else:
        print("❌ File type validation has issues")
        return False

if __name__ == "__main__":
    success = test_file_type_validation()
    
    if success:
        print("\n✅ VALIDATION FIX SUCCESSFUL!")
        print("The audio processing system will now correctly identify audio files.")
        print("Audio processing still requires library installation:")
        print("  ./install_audio_libs.sh")
    else:
        print("\n❌ VALIDATION ISSUES REMAIN")
        sys.exit(1)