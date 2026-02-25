# Development Setup Script for Windows
# This script sets up the development environment for the Resource Fetcher GUI

Write-Host "Setting up Resource Fetcher GUI development environment..." -ForegroundColor Cyan

# Check if Node.js is installed
Write-Host "`nChecking Node.js installation..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if (-not $nodeVersion) {
    Write-Host "ERROR: Node.js is not installed!" -ForegroundColor Red
    Write-Host "Please install Node.js v20 or later from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host "Found Node.js: $nodeVersion" -ForegroundColor Green

# Check if nvm is installed (for Node version management)
Write-Host "`nChecking nvm installation..." -ForegroundColor Yellow
$nvmInstalled = Get-Command nvm -ErrorAction SilentlyContinue
if ($nvmInstalled) {
    Write-Host "nvm is installed. Checking .nvmrc..." -ForegroundColor Green
    $requiredVersion = Get-Content .nvmrc
    Write-Host "Required Node version: $requiredVersion" -ForegroundColor Cyan
    nvm install $requiredVersion
    nvm use $requiredVersion
} else {
    Write-Host "nvm not found. Using system Node.js." -ForegroundColor Yellow
}

# Check if Python is installed
Write-Host "`nChecking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>$null
if (-not $pythonVersion) {
    Write-Host "ERROR: Python is not installed!" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or later from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host "Found Python: $pythonVersion" -ForegroundColor Green

# Check if Rust is installed
Write-Host "`nChecking Rust installation..." -ForegroundColor Yellow
$cargoVersion = cargo --version 2>$null
if (-not $cargoVersion) {
    Write-Host "ERROR: Rust/Cargo is not installed!" -ForegroundColor Red
    Write-Host "Please install Rust from https://rustup.rs/" -ForegroundColor Yellow
    exit 1
}
Write-Host "Found: $cargoVersion" -ForegroundColor Green

# Check if venv exists, create if not
Write-Host "`nChecking Python virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "..\.venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv ..\.venv
    Write-Host "Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

# Activate venv and install Python dependencies
Write-Host "`nInstalling Python dependencies..." -ForegroundColor Yellow
& "..\.venv\Scripts\python.exe" -m pip install --upgrade pip
& "..\.venv\Scripts\python.exe" -m pip install -e ..\cli
& "..\.venv\Scripts\python.exe" -m pip install -e ..\gui
Write-Host "Python dependencies installed." -ForegroundColor Green

# Install Node dependencies
Write-Host "`nInstalling Node dependencies..." -ForegroundColor Yellow
npm install
Write-Host "Node dependencies installed." -ForegroundColor Green

# Run tests to verify setup
Write-Host "`nRunning tests to verify setup..." -ForegroundColor Yellow
npm run test -- --run

Write-Host "`n============================================" -ForegroundColor Green
Write-Host "Development environment setup complete!" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Green

Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  npm run dev          - Start development server" -ForegroundColor White
Write-Host "  npm run build        - Build for production" -ForegroundColor White
Write-Host "  npm run test         - Run unit tests" -ForegroundColor White
Write-Host "  npm run test:watch   - Run tests in watch mode" -ForegroundColor White
Write-Host "  npm run test:coverage - Run tests with coverage" -ForegroundColor White
Write-Host "  npm run tauri dev    - Start Tauri development" -ForegroundColor White
Write-Host "  npm run tauri build  - Build Tauri application" -ForegroundColor White
