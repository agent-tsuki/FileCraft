#!/bin/bash
"""
FileCraft Audio Processing - Library Installation Script
"""

echo "🎵 Installing FileCraft Audio Processing Libraries..."
echo "=================================================="

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: Not in a virtual environment"
    echo "   Consider activating a virtual environment first:"
    echo "   python -m venv env && source env/bin/activate"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 1
    fi
fi

echo "🔧 Installing system dependencies..."

# Detect OS
if command -v apt-get &> /dev/null; then
    echo "   Detected: Ubuntu/Debian"
    sudo apt-get update
    sudo apt-get install -y \
        ffmpeg \
        libsndfile1-dev \
        libasound2-dev \
        libportaudio2 \
        libportaudiocpp0 \
        portaudio19-dev \
        libfftw3-dev \
        libavcodec-dev \
        libavformat-dev \
        libavutil-dev \
        pkg-config
        
elif command -v brew &> /dev/null; then
    echo "   Detected: macOS"
    brew install ffmpeg portaudio libsndfile fftw
    
elif command -v yum &> /dev/null; then
    echo "   Detected: RHEL/CentOS"
    sudo yum install -y \
        ffmpeg-devel \
        libsndfile-devel \
        alsa-lib-devel \
        portaudio-devel \
        fftw-devel
        
else
    echo "   ❌ Unknown system. Please install these manually:"
    echo "      - FFmpeg"
    echo "      - libsndfile"
    echo "      - PortAudio"
    echo "      - FFTW"
fi

echo ""
echo "📦 Installing Python audio processing libraries..."

# Core audio libraries
pip install --upgrade pip

echo "   Installing pydub (core audio manipulation)..."
pip install pydub==0.25.1

echo "   Installing librosa (audio analysis)..."
pip install librosa==0.10.1

echo "   Installing soundfile (high-quality I/O)..."
pip install soundfile==0.12.1

echo "   Installing numpy & scipy (signal processing)..."
pip install numpy==1.24.3 scipy==1.11.1

echo "   Installing audio enhancement libraries..."
pip install pyloudnorm==0.1.1
pip install noisereduce==3.0.0

# Optional advanced libraries
echo ""
echo "🔬 Installing advanced audio analysis libraries (optional)..."

echo "   Installing essentia (music analysis)..."
pip install essentia-tensorflow==2.1b6.dev1110 || {
    echo "   ⚠️  Essentia installation failed (this is optional)"
    echo "      You can continue without it"
}

echo "   Installing pyaudio (real-time audio)..."
pip install pyaudio==0.2.11 || {
    echo "   ⚠️  PyAudio installation failed (this is optional)"
    echo "      You can continue without it"
}

echo ""
echo "✅ Installation complete!"
echo ""
echo "🧪 Testing audio processing capabilities..."

# Test the installation
python -c "
import sys
success = True

try:
    from pydub import AudioSegment
    print('✅ pydub: Audio manipulation')
except ImportError:
    print('❌ pydub: Failed')
    success = False

try:
    import librosa
    print('✅ librosa: Audio analysis')
except ImportError:
    print('❌ librosa: Failed')
    success = False

try:
    import soundfile as sf
    print('✅ soundfile: High-quality I/O')
except ImportError:
    print('❌ soundfile: Failed')
    success = False

try:
    import numpy as np
    import scipy.signal
    print('✅ numpy/scipy: Signal processing')
except ImportError:
    print('❌ numpy/scipy: Failed')
    success = False

# Optional libraries
try:
    import essentia
    print('✅ essentia: Music analysis (optional)')
except ImportError:
    print('⚠️  essentia: Not available (optional)')

try:
    import pyaudio
    print('✅ pyaudio: Real-time audio (optional)')
except ImportError:
    print('⚠️  pyaudio: Not available (optional)')

if success:
    print('')
    print('🎉 All core libraries installed successfully!')
    print('   FileCraft Audio Processing is ready to use!')
else:
    print('')
    print('❌ Some core libraries failed to install.')
    print('   Please check the error messages above.')
    sys.exit(1)
"

echo ""
echo "🚀 Next steps:"
echo "1. Restart your FileCraft application"
echo "2. Test audio conversion: python test_audio_comprehensive.py"
echo "3. Check API docs: http://localhost:8080/docs"
echo ""
echo "📚 Documentation: README_AUDIO_PROCESSING.md"