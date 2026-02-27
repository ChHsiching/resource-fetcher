#!/usr/bin/env python3
"""
Local build script for Resource Fetcher.

This script builds standalone executables (CLI and GUI) using PyInstaller.
Run locally to test the build process before pushing to GitHub.

Usage:
    python build.py --cli       # Build CLI only
    python build.py --gui       # Build GUI only
    python build.py --all       # Build both (default)
"""

import argparse
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


def build_cli_binary() -> None:
    """Build the CLI standalone executable."""
    print("Building CLI standalone executable...")

    # Determine platform-specific settings
    if sys.platform == "win32":
        binary_name = "resource-fetcher.exe"
    else:
        binary_name = "resource-fetcher"

    # PyInstaller command - use python -m to ensure it's found
    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",  # Create single executable
        "--name",
        binary_name,
        "--clean",  # Clean cache before building
        "cli/src/resource_fetcher_cli/cli/main.py",
    ]

    run_command(pyinstaller_cmd)

    # Verify the binary was created
    binary_path = Path("dist") / binary_name
    if not binary_path.exists():
        print(f"Error: CLI binary not found at {binary_path}")
        sys.exit(1)

    print(f"[OK] CLI binary created: {binary_path}")
    print(f"   Size: {binary_path.stat().st_size / (1024*1024):.2f} MB")


def run_tests() -> None:
    """Run tests before building."""
    print("Running tests...")
    run_command([sys.executable, "-m", "pytest", "tests/", "-v"])
    print("[OK] All tests passed!")


def main() -> None:
    """Main build process."""
    parser = argparse.ArgumentParser(description="Build Resource Fetcher CLI binary")
    parser.add_argument("--no-test", action="store_true", help="Skip running tests")
    args = parser.parse_args()

    print("=" * 60)
    print("Resource Fetcher - Local Build Script")
    print("=" * 60)

    # Check if we're in the project root
    if not Path("pyproject.toml").exists():
        print("Error: pyproject.toml not found. Please run from project root.")
        sys.exit(1)

    # Step 1: Run tests
    if not args.no_test:
        run_tests()

    # Step 2: Clean
    clean_dist()

    # Step 3: Build CLI
    build_cli_binary()

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
