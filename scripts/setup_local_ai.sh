#!/bin/bash
"""
Setup script for Local AI (Llama 3.2 3B)
=======================================

This script sets up the environment for running local Small Language Models
using Unsloth with 4-bit quantization.

Requirements:
- NVIDIA GPU with CUDA support (6GB+ VRAM recommended)
- Python 3.10+
- CUDA Toolkit 11.8 or 12.1

Usage:
    chmod +x setup_local_ai.sh
    ./setup_local_ai.sh
"""

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  🤖 Setup Local AI - FinancePerso                               ║"
echo "║  Llama 3.2 3B with Unsloth (4-bit quantization)                 ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_error "macOS detected. Local SLM with Unsloth requires Linux with NVIDIA GPU."
    print_error "Please use the cloud providers (Gemini, OpenAI) on macOS."
    exit 1
fi

# Check for NVIDIA GPU
echo "📋 Checking system requirements..."
if ! command -v nvidia-smi &> /dev/null; then
    print_error "nvidia-smi not found. Please install NVIDIA drivers."
    exit 1
fi

print_status "NVIDIA GPU detected:"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

# Check CUDA version
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep "release" | sed -n 's/.*release \([0-9]\+\.[0-9]\+\).*/\1/p')
    print_status "CUDA version: $CUDA_VERSION"
else
    print_warning "nvcc not found. Make sure CUDA toolkit is installed."
fi

# Create virtual environment
VENV_NAME=".venv_ml"
echo
echo "📦 Creating virtual environment: $VENV_NAME"

if [ -d "$VENV_NAME" ]; then
    print_warning "Directory $VENV_NAME already exists."
    read -p "Do you want to remove it and create a new one? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_NAME"
        python3 -m venv "$VENV_NAME"
        print_status "Virtual environment recreated."
    else
        print_warning "Using existing virtual environment."
    fi
else
    python3 -m venv "$VENV_NAME"
    print_status "Virtual environment created."
fi

# Activate virtual environment
echo
echo "🔄 Activating virtual environment..."
source "$VENV_NAME/bin/activate"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install PyTorch with CUDA support
echo
echo "🔥 Installing PyTorch with CUDA support..."

# Detect CUDA version and install appropriate PyTorch
if [[ -n "$CUDA_VERSION" ]]; then
    if [[ "$CUDA_VERSION" == "12.1" ]] || [[ "$CUDA_VERSION" == "12.2" ]]; then
        print_status "Installing PyTorch for CUDA 12.1..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    elif [[ "$CUDA_VERSION" == "11.8" ]] || [[ "$CUDA_VERSION" == "11.7" ]]; then
        print_status "Installing PyTorch for CUDA 11.8..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    else
        print_warning "CUDA version $CUDA_VERSION not specifically supported. Trying CUDA 11.8..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    fi
else
    print_warning "CUDA version not detected. Installing CPU-only PyTorch..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Install xformers
echo
echo "⚡ Installing xformers (optimized attention)..."
pip install xformers --index-url https://download.pytorch.org/whl/cu121 2>/dev/null || \
pip install xformers

# Install Unsloth
echo
echo "🦥 Installing Unsloth (optimized LLM inference)..."
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

# Install other dependencies
echo
echo "📚 Installing additional dependencies..."
pip install transformers accelerate bitsandbytes scipy

# Create .env file with local AI configuration
echo
echo "📝 Setting up environment variables..."

if [ -f ".env" ]; then
    print_warning ".env file already exists."
    
    # Check if local AI vars already exist
    if grep -q "AI_PROVIDER=local" .env; then
        print_status "Local AI configuration already present in .env"
    else
        echo >> .env
        echo "# Local AI Configuration (added by setup_local_ai.sh)" >> .env
        echo "AI_PROVIDER=local" >> .env
        echo "LOCAL_SLM_MODEL=llama-3.2-3b" >> .env
        echo "LOCAL_SLM_FALLBACK=true" >> .env
        echo >> .env
        echo "# Fallback API Keys (optional)" >> .env
        echo "GEMINI_API_KEY=your_gemini_key_here" >> .env
        echo "DEEPSEEK_API_KEY=your_deepseek_key_here" >> .env
        print_status "Local AI configuration appended to .env"
    fi
else
    cat > .env << EOF
# FinancePerso Configuration
# Database
DATABASE_PATH=Data/finance.db

# AI Provider Configuration
# Options: gemini, openai, deepseek, kimi, local
AI_PROVIDER=local

# Local SLM Configuration
LOCAL_SLM_MODEL=llama-3.2-3b
LOCAL_SLM_FALLBACK=true

# API Keys (for fallback)
GEMINI_API_KEY=
DEEPSEEK_API_KEY=
OPENAI_API_KEY=
KIMI_API_KEY=

# Security
ENCRYPTION_KEY=your_encryption_key_here

# Optional: Sentry for error tracking
SENTRY_DSN=
EOF
    print_status ".env file created with local AI configuration."
fi

# Create activation script
cat > activate_local_ai.sh << 'EOF'
#!/bin/bash
# Activate local AI environment
source .venv_ml/bin/activate
export AI_PROVIDER=local
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
echo "🤖 Local AI environment activated!"
echo "   Provider: $(python3 -c "import os; print(os.getenv('AI_PROVIDER', 'not set'))")"
echo "   Python: $(which python3)"
echo ""
echo "Run demo: python demo_local_ai.py"
EOF
chmod +x activate_local_ai.sh

# Verification
echo
echo "🔍 Verifying installation..."
python3 << EOPYTHON
import sys
try:
    import torch
    print(f"✓ PyTorch {torch.__version__}")
    print(f"  CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  CUDA version: {torch.version.cuda}")
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
    
    import transformers
    print(f"✓ Transformers {transformers.__version__}")
    
    try:
        from unsloth import FastLanguageModel
        print(f"✓ Unsloth installed")
    except ImportError:
        print("⚠ Unsloth import failed (may need GPU)")
    
    print("\n✅ Installation successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOPYTHON

# Summary
echo
print_status "Setup complete!"
echo
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  Next Steps:                                                     ║"
echo "╠══════════════════════════════════════════════════════════════════╣"
echo "║  1. Activate environment: source activate_local_ai.sh            ║"
echo "║  2. Edit .env and add your fallback API keys (optional)          ║"
echo "║  3. Test installation: python demo_local_ai.py                   ║"
echo "║  4. Run app: streamlit run app.py                                ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo
print_warning "Note: First model download will take several minutes."
print_warning "      The model (~2GB) will be cached in ~/.cache/huggingface/"
echo
