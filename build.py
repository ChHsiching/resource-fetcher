#!/usr/bin/env python3
"""
Local build script for Resource Fetcher.

This script builds a standalone executable using PyInstaller.
Run locally to test the build process before pushing to GitHub.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(1)
    return result


def clean_dist() -> None:
    """Clean the dist directory."""
    dist_path = Path("dist")
    if dist_path.exists():
        print(f"Cleaning {dist_path}...")
        shutil.rmtree(dist_path)
    dist_path.mkdir(parents=True, exist_ok=True)


def build_binary() -> None:
    """Build the standalone executable."""
    print("Building standalone executable...")

    # Determine platform-specific settings
    if sys.platform == "win32":
        binary_name = "resource-fetcher.exe"
    else:
        binary_name = "resource-fetcher"

    # PyInstaller command
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",  # Create single executable
        "--name",
        binary_name,
        "--clean",  # Clean cache before building
        "packages/resource-fetcher-cli/src/resource_fetcher_cli/cli/main.py",
    ]

    run_command(pyinstaller_cmd)

    # Verify the binary was created
    binary_path = Path("dist") / binary_name
    if not binary_path.exists():
        print(f"Error: Binary not found at {binary_path}")
        sys.exit(1)

    print(f"✅ Binary created: {binary_path}")
    print(f"   Size: {binary_path.stat().st_size / (1024*1024):.2f} MB")


def run_tests() -> None:
    """Run tests before building."""
    print("Running tests...")
    run_command([sys.executable, "-m", "pytest", "tests/", "-v"])
    print("[OK] All tests passed!")


def main() -> None:
    """Main build process."""
    print("=" * 60)
    print("Resource Fetcher - Local Build Script")
    print("=" * 60)

    # Check if we're in the project root
    if not Path("pyproject.toml").exists():
        print("Error: pyproject.toml not found. Please run from project root.")
        sys.exit(1)

    # Step 1: Run tests
    run_tests()

    # Step 2: Clean
    clean_dist()

    # Step 3: Build
    build_binary()

    print("\n" + "=" * 60)
    print("[OK] Build completed successfully!")
    print("=" * 60)
    print("\nTo test the binary:")
    if sys.platform == "win32":
        print("  .\\dist\\resource-fetcher.exe --help")
    else:
        print("  ./dist/resource-fetcher --help")


if __name__ == "__main__":
    main()
