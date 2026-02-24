#!/usr/bin/env python3
"""
Build script for Resource Fetcher - CLI and GUI.

Builds both CLI and GUI as separate standalone executables.
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


def build_cli() -> None:
    """Build CLI executable."""
    print("\n" + "=" * 60)
    print("Building CLI executable...")
    print("=" * 60)

    if sys.platform == "win32":
        binary_name = "resource-fetcher.exe"
    else:
        binary_name = "resource-fetcher"

    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "poetry",
        "run",
        "pyinstaller",
        "--onefile",
        "--name",
        binary_name,
        "--clean",
        "--distpath",
        "dist",
        "src/resource_fetcher/cli/main.py",
    ]

    run_command(pyinstaller_cmd)

    binary_path = Path("dist") / binary_name
    if not binary_path.exists():
        print(f"Error: CLI binary not found at {binary_path}")
        sys.exit(1)

    size_mb = binary_path.stat().st_size / (1024 * 1024)
    print(f"✅ CLI binary created: {binary_path}")
    print(f"   Size: {size_mb:.2f} MB")


def build_gui() -> None:
    """Build GUI executable."""
    print("\n" + "=" * 60)
    print("Building GUI executable...")
    print("=" * 60)

    if sys.platform == "win32":
        binary_name = "resource-fetcher-gui.exe"
    else:
        binary_name = "resource-fetcher-gui"

    # GUI needs windowed mode (no console)
    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "poetry",
        "run",
        "pyinstaller",
        "--onefile",
        "--name",
        binary_name,
        "--windowed",  # No console window for GUI
        "--clean",
        "--distpath",
        "dist",
        "--hidden-import",
        "tkinter",
        "--hidden-import",
        "ttkbootstrap",
        "--hidden-import",
        "pyperclip",
        "src/resource_fetcher/gui/main.py",
    ]

    run_command(pyinstaller_cmd)

    binary_path = Path("dist") / binary_name
    if not binary_path.exists():
        print(f"Error: GUI binary not found at {binary_path}")
        sys.exit(1)

    size_mb = binary_path.stat().st_size / (1024 * 1024)
    print(f"✅ GUI binary created: {binary_path}")
    print(f"   Size: {size_mb:.2f} MB")


def run_tests() -> None:
    """Run tests before building."""
    print("\n" + "=" * 60)
    print("Running tests...")
    print("=" * 60)
    run_command([sys.executable, "-m", "pytest", "tests/", "-v"])
    print("[OK] All tests passed!")


def main() -> None:
    """Main build process."""
    print("=" * 60)
    print("Resource Fetcher - Build CLI and GUI")
    print("=" * 60)

    if not Path("pyproject.toml").exists():
        print("Error: pyproject.toml not found. Please run from project root.")
        sys.exit(1)

    # Step 1: Run tests
    run_tests()

    # Step 2: Clean
    clean_dist()

    # Step 3: Build CLI
    build_cli()

    # Step 4: Build GUI
    build_gui()

    print("\n" + "=" * 60)
    print("[OK] Build completed successfully!")
    print("=" * 60)
    print("\nBinaries created in dist/:")

    if sys.platform == "win32":
        print("  - resource-fetcher.exe (CLI)")
        print("  - resource-fetcher-gui.exe (GUI)")
        print("\nTo test:")
        print("  CLI:  .\\dist\\resource-fetcher.exe --help")
        print("  GUI:  .\\dist\\resource-fetcher-gui.exe")
    else:
        print("  - resource-fetcher (CLI)")
        print("  - resource-fetcher-gui (GUI)")
        print("\nTo test:")
        print("  CLI:  ./dist/resource-fetcher --help")
        print("  GUI:  ./dist/resource-fetcher-gui")


if __name__ == "__main__":
    main()
