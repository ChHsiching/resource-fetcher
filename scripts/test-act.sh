#!/bin/bash
# scripts/test-act.sh
# Run GitHub Actions workflows locally using Act

set -e

echo "🔧 Running GitHub Actions workflows locally..."
echo ""

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo "❌ Act is not installed. Install it:"
    echo "  brew install act  # macOS"
    echo "  choco install act  # Windows"
    echo "  curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"
    exit 1
fi

# Run specific workflow
if [ -z "$1" ]; then
    echo "Running all workflows..."
    act -j test
else
    echo "Running workflow: $1"
    act -j "$1"
fi

echo ""
echo "✅ Local CI testing complete!"
