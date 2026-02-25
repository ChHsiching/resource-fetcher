#!/bin/bash
# Build Script for Unix/Linux/macOS
# This script builds the Resource Fetcher GUI for distribution

set -e

RELEASE=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --release)
            RELEASE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Building Resource Fetcher GUI..."

# Parse build type
BUILD_TYPE="debug"
CARGO_FLAG=""
if [ "$RELEASE" = true ]; then
    BUILD_TYPE="release"
    CARGO_FLAG="--release"
fi

echo "Build type: $BUILD_TYPE"

# Clean previous builds
echo ""
echo "Cleaning previous builds..."
rm -rf dist target src-tauri/target

# Run tests
echo ""
echo "Running tests..."
npm run test -- --run
if [ $? -ne 0 ]; then
    echo "ERROR: Tests failed!"
    exit 1
fi

# Type check
echo ""
echo "Type checking..."
npm run build
if [ $? -ne 0 ]; then
    echo "ERROR: Type check failed!"
    exit 1
fi

# Build Tauri application
echo ""
echo "Building Tauri application..."
if [ "$VERBOSE" = true ]; then
    npm run tauri build -- $CARGO_FLAG --verbose
else
    npm run tauri build -- $CARGO_FLAG
fi

if [ $? -ne 0 ]; then
    echo "ERROR: Tauri build failed!"
    exit 1
fi

# Output location
BUNDLE_DIR="src-tauri/target/$BUILD_TYPE/bundle"

echo ""
echo "============================================"
echo "Build completed successfully!"
echo "============================================"
echo ""

echo "Output location: $BUNDLE_DIR"

# List generated files
echo ""
echo "Generated files:"
find "$BUNDLE_DIR" -type f | while read -r file; do
    echo "  - $file"
done

echo ""
echo "Build artifacts are ready for distribution!"
