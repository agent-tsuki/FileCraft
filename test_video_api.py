#!/usr/bin/env python3
"""
Video API comprehensive test script for FileCraft.

Tests all video processing endpoints with various scenarios.
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
import tempfile

# Base URL for the API
BASE_URL = "http://localhost:8000"

def create_test_video():
    """Create a simple test video using FFmpeg if available."""
    try:
        import subprocess
        
        # Create a simple 5-second test video
        test_video_path = "test_video.mp4"
        
        # Generate a simple test video with FFmpeg
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "testsrc=duration=5:size=320x240:rate=30",
            "-f", "lavfi", 
            "-i", "sine=frequency=1000:duration=5",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            test_video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ Created test video: {test_video_path}")
            return test_video_path
        else:
            print(f"❌ Failed to create test video: {result.stderr}")
            return None
            
    except (ImportError, subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  FFmpeg not available, skipping video creation")
        return None

def test_video_formats():
    """Test getting supported video formats."""
    print("\n🔍 Testing video formats endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/video/formats")
        if response.status_code == 200:
            data = response.json()
            print("✅ Video formats retrieved successfully")
            print(f"   - Input formats: {len(data.get('input_formats', []))}")
            print(f"   - Output formats: {len(data.get('output_formats', []))}")
            print(f"   - Codecs: {len(data.get('codecs', {}))}")
            return True
        else:
            print(f"❌ Failed to get video formats: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing video formats: {e}")
        return False

def test_video_conversion(video_file):
    """Test video format conversion."""
    print(f"\n🔄 Testing video conversion with {video_file}...")
    
    if not os.path.exists(video_file):
        print(f"❌ Test video file not found: {video_file}")
        return False
    
    try:
        with open(video_file, 'rb') as f:
            files = {'video': (video_file, f, 'video/mp4')}
            data = {
                'target_format': 'webm',
                'quality_preset': 'hd',
                'codec': 'vp9'
            }
            
            print("   Converting MP4 to WebM with VP9 codec...")
            response = requests.post(f"{BASE_URL}/video/convert", files=files, data=data)
            
            if response.status_code == 200:
                # Save converted video
                output_file = "test_converted.webm"
                with open(output_file, 'wb') as out_f:
                    out_f.write(response.content)
                
                print(f"✅ Video conversion successful")
                print(f"   - Output file: {output_file}")
                print(f"   - Output size: {len(response.content)} bytes")
                
                # Check headers
                headers = response.headers
                print(f"   - Content-Type: {headers.get('content-type')}")
                print(f"   - Original Format: {headers.get('x-original-format')}")
                print(f"   - Target Format: {headers.get('x-target-format')}")
                
                return True
            else:
                print(f"❌ Video conversion failed: {response.status_code}")
                if response.content:
                    try:
                        error_data = response.json()
                        print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                    except:
                        print(f"   Raw error: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing video conversion: {e}")
        return False

def test_audio_extraction(video_file):
    """Test audio extraction from video."""
    print(f"\n🎵 Testing audio extraction from {video_file}...")
    
    if not os.path.exists(video_file):
        print(f"❌ Test video file not found: {video_file}")
        return False
    
    try:
        with open(video_file, 'rb') as f:
            files = {'video': (video_file, f, 'video/mp4')}
            params = {
                'audio_format': 'mp3',
                'audio_bitrate': '192k'
            }
            
            response = requests.post(f"{BASE_URL}/video/extract-audio", files=files, params=params)
            
            if response.status_code == 200:
                # Save extracted audio
                output_file = "test_extracted_audio.mp3"
                with open(output_file, 'wb') as out_f:
                    out_f.write(response.content)
                
                print(f"✅ Audio extraction successful")
                print(f"   - Output file: {output_file}")
                print(f"   - Output size: {len(response.content)} bytes")
                print(f"   - Content-Type: {response.headers.get('content-type')}")
                
                return True
            else:
                print(f"❌ Audio extraction failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Raw error: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing audio extraction: {e}")
        return False

def test_thumbnail_generation(video_file):
    """Test video thumbnail generation."""
    print(f"\n🖼️ Testing thumbnail generation from {video_file}...")
    
    if not os.path.exists(video_file):
        print(f"❌ Test video file not found: {video_file}")
        return False
    
    try:
        with open(video_file, 'rb') as f:
            files = {'video': (video_file, f, 'video/mp4')}
            params = {
                'timestamp': '2.5',
                'width': '640',
                'height': '360',
                'image_format': 'jpg'
            }
            
            response = requests.post(f"{BASE_URL}/video/thumbnail", files=files, params=params)
            
            if response.status_code == 200:
                # Save thumbnail
                output_file = "test_thumbnail.jpg"
                with open(output_file, 'wb') as out_f:
                    out_f.write(response.content)
                
                print(f"✅ Thumbnail generation successful")
                print(f"   - Output file: {output_file}")
                print(f"   - Output size: {len(response.content)} bytes")
                print(f"   - Content-Type: {response.headers.get('content-type')}")
                print(f"   - Timestamp: {response.headers.get('x-timestamp')}s")
                print(f"   - Dimensions: {response.headers.get('x-dimensions')}")
                
                return True
            else:
                print(f"❌ Thumbnail generation failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Raw error: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing thumbnail generation: {e}")
        return False

def test_video_info(video_file):
    """Test video information analysis."""
    print(f"\n📊 Testing video information analysis...")
    
    if not os.path.exists(video_file):
        print(f"❌ Test video file not found: {video_file}")
        return False
    
    try:
        with open(video_file, 'rb') as f:
            files = {'video': (video_file, f, 'video/mp4')}
            
            response = requests.post(f"{BASE_URL}/video/info", files=files)
            
            if response.status_code == 200:
                info = response.json()
                print(f"✅ Video analysis successful")
                print(f"   - Filename: {info.get('filename')}")
                print(f"   - Format: {info.get('format')}")
                print(f"   - Duration: {info.get('duration')}s")
                print(f"   - Size: {info.get('size')} bytes")
                print(f"   - Bitrate: {info.get('bitrate')} bps")
                print(f"   - Streams: {info.get('streams')}")
                
                if 'video' in info:
                    video_info = info['video']
                    print(f"   - Video codec: {video_info.get('codec')}")
                    print(f"   - Resolution: {video_info.get('width')}x{video_info.get('height')}")
                    print(f"   - FPS: {video_info.get('fps')}")
                
                if 'audio' in info:
                    audio_info = info['audio']
                    print(f"   - Audio codec: {audio_info.get('codec')}")
                    print(f"   - Sample rate: {audio_info.get('sample_rate')} Hz")
                    print(f"   - Channels: {audio_info.get('channels')}")
                
                return True
            else:
                print(f"❌ Video analysis failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Raw error: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing video analysis: {e}")
        return False

def test_async_processing(video_file):
    """Test asynchronous video processing."""
    print(f"\n⚡ Testing async video processing...")
    
    if not os.path.exists(video_file):
        print(f"❌ Test video file not found: {video_file}")
        return False
    
    try:
        with open(video_file, 'rb') as f:
            files = {'video': (video_file, f, 'video/mp4')}
            data = {
                'target_format': 'mkv',
                'quality_preset': 'hd',
                'use_async': 'true'
            }
            
            response = requests.post(f"{BASE_URL}/video/convert", files=files, data=data)
            
            if response.status_code == 200:
                task_info = response.json()
                task_id = task_info.get('task_id')
                
                if task_id:
                    print(f"✅ Async task started: {task_id}")
                    print(f"   Status: {task_info.get('status')}")
                    
                    # Check task status
                    for i in range(5):  # Check for 5 seconds
                        time.sleep(1)
                        status_response = requests.get(f"{BASE_URL}/video/task/{task_id}")
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            print(f"   Task status check {i+1}: {status_data.get('state')}")
                            
                            if status_data.get('state') in ['SUCCESS', 'FAILURE']:
                                break
                        else:
                            print(f"   Failed to check task status: {status_response.status_code}")
                    
                    return True
                else:
                    print(f"❌ No task_id returned in async response")
                    return False
            else:
                print(f"❌ Async processing failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Raw error: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing async processing: {e}")
        return False

def check_api_health():
    """Check if the API is running and accessible."""
    print("🏥 Checking API health...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API is healthy and running")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print(f"   Make sure the server is running on {BASE_URL}")
        return False

def cleanup_test_files():
    """Clean up test files created during testing."""
    print("\n🧹 Cleaning up test files...")
    
    test_files = [
        "test_video.mp4",
        "test_converted.webm", 
        "test_extracted_audio.mp3",
        "test_thumbnail.jpg"
    ]
    
    for file in test_files:
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f"   Removed: {file}")
        except Exception as e:
            print(f"   Failed to remove {file}: {e}")

def main():
    """Run all video API tests."""
    print("🎬 FileCraft Video API Test Suite")
    print("=" * 50)
    
    # Check if API is running
    if not check_api_health():
        print("\n❌ Cannot proceed with tests. Please start the FileCraft server first:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Create test video
    test_video = create_test_video()
    
    if not test_video:
        print("\n⚠️  No test video available. Some tests will be skipped.")
        print("   To run all tests, install FFmpeg and ensure it's in your PATH.")
    
    # Run tests
    results = []
    
    # Test 1: Video formats
    results.append(("Video Formats", test_video_formats()))
    
    # Skip video processing tests if no test video
    if test_video:
        # Test 2: Video conversion
        results.append(("Video Conversion", test_video_conversion(test_video)))
        
        # Test 3: Audio extraction
        results.append(("Audio Extraction", test_audio_extraction(test_video)))
        
        # Test 4: Thumbnail generation
        results.append(("Thumbnail Generation", test_thumbnail_generation(test_video)))
        
        # Test 5: Video analysis
        results.append(("Video Analysis", test_video_info(test_video)))
        
        # Test 6: Async processing (may fail if Celery not running)
        results.append(("Async Processing", test_async_processing(test_video)))
    
    # Print results summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Video API is working correctly.")
        success_code = 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        success_code = 1
    
    # Cleanup
    if test_video:
        cleanup_test_files()
    
    return success_code

if __name__ == "__main__":
    sys.exit(main())