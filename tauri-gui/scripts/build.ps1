# Build Script for Windows
# This script builds the Resource Fetcher GUI for distribution

param(
    [switch]$Release = $false,
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"

Write-Host "Building Resource Fetcher GUI..." -ForegroundColor Cyan

# Parse build type
$BuildType = if ($Release) { "release" } else { "debug" }
$CargoFlag = if ($Release) { "--release" } else { ""

}

Write-Host "Build type: $BuildType" -ForegroundColor Yellow

# Clean previous builds
Write-Host "`nCleaning previous builds..." -ForegroundColor Yellow
Remove-Item -Path "dist", "target" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "src-tauri/target" -Recurse -Force -ErrorAction SilentlyContinue

# Run tests
Write-Host "`nRunning tests..." -ForegroundColor Yellow
npm run test -- --run
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Tests failed!" -ForegroundColor Red
    exit 1
}

# Type check
Write-Host "`nType checking..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Type check failed!" -ForegroundColor Red
    exit 1
}

# Build Tauri application
Write-Host "`nBuilding Tauri application..." -ForegroundColor Yellow
if ($Verbose) {
    npm run tauri build -- $CargoFlag --verbose
} else {
    npm run tauri build -- $CargoFlag
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Tauri build failed!" -ForegroundColor Red
    exit 1
}

# Output location
$BundleDir = "src-tauri/target/$BuildType/bundle"

Write-Host "`n============================================" -ForegroundColor Green
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Green

Write-Host "Output location: $BundleDir" -ForegroundColor Cyan

# List generated files
Write-Host "`nGenerated files:" -ForegroundColor Yellow
Get-ChildItem -Path $BundleDir -Recurse -File | ForEach-Object {
    Write-Host "  - $($_.FullName)" -ForegroundColor White
}

Write-Host "`nBuild artifacts are ready for distribution!" -ForegroundColor Green
