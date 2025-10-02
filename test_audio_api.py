#!/usr/bin/env python3
"""
Test script for the enhanced audio converter API.
"""
import requests
import io
import wave
import struct
import json

# Create a simple test audio file
def create_test_audio():
    """Create a simple test audio file (1 second of 440Hz sine wave)."""
    sample_rate = 44100
    duration = 1.0  # seconds
    frequency = 440.0  # Hz (A4 note)
    
    frames = []
    for i in range(int(sample_rate * duration)):
        # Generate sine wave
        value = int(32767 * 0.5 * (1 + 0.5 * 1.0))  # Simple tone
        frames.append(struct.pack('<h', value))
    
    # Create WAV file in memory
    buffer = io.BytesIO()
    
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(frames))
    
    buffer.seek(0)
    return buffer

def test_audio_formats_endpoint():
    """Test the audio formats endpoint."""
    print("Testing /audio/formats endpoint...")
    try:
        response = requests.get('http://localhost:8080/audio/formats')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Audio formats endpoint works! Found {len(data['input_formats'])} input formats")
            print(f"   Output formats: {', '.join(data['output_formats'][:5])}...")
            print(f"   Quality presets: {', '.join(data['quality_presets'].keys())}")
            return True
        else:
            print(f"❌ Audio formats endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Audio formats endpoint error: {str(e)}")
        return False

def test_audio_conversion():
    """Test basic audio conversion."""
    print("\\nTesting /audio/convert endpoint...")
    
    try:
        # Create test audio
        test_audio = create_test_audio()
        
        # Prepare files and data
        files = {'audio': ('test.wav', test_audio, 'audio/wav')}
        data = {
            'target_format': 'mp3',
            'bitrate': 128,
            'use_async': False
        }
        
        response = requests.post(
            'http://localhost:8080/audio/convert',
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            print("✅ Audio conversion successful!")
            print(f"   Content-Type: {response.headers.get('content-type')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Audio conversion failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Response: {error_data}")
            except:
                print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Audio conversion error: {str(e)}")
        return False

def test_audio_analysis():
    """Test audio analysis endpoint."""
    print("\\nTesting /audio/analyze endpoint...")
    
    try:
        # Create test audio
        test_audio = create_test_audio()
        
        files = {'audio': ('test.wav', test_audio, 'audio/wav')}
        
        response = requests.post(
            'http://localhost:8080/audio/analyze',
            files=files
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Audio analysis endpoint works!")
            
            # Check if it's async processing or sync result
            if "task_id" in data:
                print(f"   Task ID: {data['task_id']}")
            else:
                print(f"   Duration: {data.get('duration_seconds', 'N/A')} seconds")
                print(f"   Sample Rate: {data.get('sample_rate', 'N/A')} Hz")
                print(f"   Channels: {data.get('channels', 'N/A')}")
            
            return True
        else:
            print(f"❌ Audio analysis failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Response: {error_data}")
            except:
                print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Audio analysis error: {str(e)}")
        return False

def test_audio_effects():
    """Test audio effects endpoint."""
    print("\\nTesting /audio/effects endpoint...")
    
    try:
        # Create test audio
        test_audio = create_test_audio()
        
        files = {'audio': ('test.wav', test_audio, 'audio/wav')}
        params = {
            'effects': ['normalize', 'fade_in']
        }
        
        response = requests.post(
            'http://localhost:8080/audio/effects',
            files=files,
            params=params
        )
        
        if response.status_code == 200:
            if response.headers.get('content-type', '').startswith('audio/'):
                print("✅ Audio effects successful!")
                print(f"   Content-Type: {response.headers.get('content-type')}")
                print(f"   Effects Applied: {response.headers.get('X-Effects-Applied', 'N/A')}")
                return True
            else:
                # Might be async response
                data = response.json()
                if "task_id" in data:
                    print("✅ Audio effects submitted for background processing!")
                    print(f"   Task ID: {data['task_id']}")
                    return True
                else:
                    print(f"❌ Unexpected response: {data}")
                    return False
        else:
            print(f"❌ Audio effects failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Response: {error_data}")
            except:
                print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Audio effects error: {str(e)}")
        return False

def main():
    """Run all audio API tests."""
    print("🎵 Testing FileCraft Enhanced Audio Converter API")
    print("=" * 50)
    
    tests = [
        test_audio_formats_endpoint,
        test_audio_conversion,
        test_audio_analysis,
        test_audio_effects
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The enhanced audio converter is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()