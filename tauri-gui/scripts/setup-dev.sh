#!/bin/bash
# Development Setup Script for Unix/Linux/macOS
# This script sets up the development environment for the Resource Fetcher GUI

set -e

echo "Setting up Resource Fetcher GUI development environment..."

# Check if Node.js is installed
echo ""
echo "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed!"
    echo "Please install Node.js v20 or later from https://nodejs.org/"
    exit 1
fi
NODE_VERSION=$(node --version)
echo "Found Node.js: $NODE_VERSION"

# Check if nvm is installed (for Node version management)
echo ""
echo "Checking nvm installation..."
if command -v nvm &> /dev/null || [ -f "$NVM_DIR/nvm.sh" ]; then
    echo "nvm is installed. Checking .nvmrc..."
    REQUIRED_VERSION=$(cat .nvmrc)
    echo "Required Node version: $REQUIRED_VERSION"
    source "$NVM_DIR/nvm.sh" 2>/dev/null || true
    nvm install "$REQUIRED_VERSION" || true
    nvm use "$REQUIRED_VERSION" || true
else
    echo "nvm not found. Using system Node.js."
fi

# Check if Python is installed
echo ""
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed!"
    echo "Please install Python 3.10 or later from https://www.python.org/"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "Found Python: $PYTHON_VERSION"

# Check if Rust is installed
echo ""
echo "Checking Rust installation..."
if ! command -v cargo &> /dev/null; then
    echo "ERROR: Rust/Cargo is not installed!"
    echo "Please install Rust from https://rustup.rs/"
    exit 1
fi
CARGO_VERSION=$(cargo --version)
echo "Found: $CARGO_VERSION"

# Check if venv exists, create if not
echo ""
echo "Checking Python virtual environment..."
if [ ! -d "../.venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv ../.venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate venv and install Python dependencies
echo ""
echo "Installing Python dependencies..."
source "../.venv/bin/activate"
pip install --upgrade pip
pip install -e ../cli
pip install -e ../gui
echo "Python dependencies installed."

# Install Node dependencies
echo ""
echo "Installing Node dependencies..."
npm install
echo "Node dependencies installed."

# Run tests to verify setup
echo ""
echo "Running tests to verify setup..."
npm run test -- --run

echo ""
echo "============================================"
echo "Development environment setup complete!"
echo "============================================"
echo ""

echo "Available commands:"
echo "  npm run dev          - Start development server"
echo "  npm run build        - Build for production"
echo "  npm run test         - Run unit tests"
echo "  npm run test:watch   - Run tests in watch mode"
echo "  npm run test:coverage - Run tests with coverage"
echo "  npm run tauri dev    - Start Tauri development"
echo "  npm run tauri build  - Build Tauri application"
