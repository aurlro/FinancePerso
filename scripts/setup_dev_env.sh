#!/bin/bash
# Setup Development Environment for FinancePerso
# Usage: ./scripts/setup_dev_env.sh

set -e

echo "🚀 Setting up FinancePerso development environment..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
REQUIRED_VERSION="3.12"

if ! python3 --version | grep -q "$REQUIRED_VERSION"; then
    echo -e "${RED}❌ Python $REQUIRED_VERSION+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
fi

# Activate and install
echo "📥 Installing dependencies..."
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create pre-commit hook
echo "🔗 Setting up git hooks..."
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Running pre-commit checks..."

# Run tests
python3 -m pytest tests/test_essential.py -q --tb=no
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Commit aborted."
    exit 1
fi

echo "✓ Pre-commit checks passed"
EOF

chmod +x .git/hooks/pre-commit
echo -e "${GREEN}✓ Git hooks configured${NC}"

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env and add your API keys${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. source .venv/bin/activate"
echo "  2. Edit .env with your API keys"
echo "  3. streamlit run app.py"
echo ""
echo "Useful commands:"
echo "  make test       # Run all tests"
echo "  make lint       # Run linter"
echo "  make format     # Format code"
