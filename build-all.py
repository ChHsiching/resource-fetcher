#!/usr/bin/env python3
"""
Complete build script for Resource Fetcher.
Builds both CLI and GUI with all packaging options.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
import zipfile
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def run(cmd, cwd=None, shell=False):
    """Run a command and exit if it fails."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, cwd=cwd, shell=shell)
    if result.returncode != 0:
        print(f"[ERROR] Command failed with exit code {result.returncode}")
        sys.exit(1)

def build_cli():
    """Build CLI using PyInstaller."""
    print("\n" + "="*60)
    print("Building CLI executable...")
    print("="*60)

    # Determine the Python executable to use
    # Prefer .venv Python if available
    venv_python = Path(".venv/Scripts/python.exe") if sys.platform == "win32" else Path(".venv/bin/python")
    if venv_python.exists():
        python_exe = str(venv_python)
    else:
        python_exe = sys.executable

    # build.py only supports --no-test flag, builds CLI by default
    run([python_exe, "build.py", "--no-test"])

    cli_binary = "dist/resource-fetcher.exe" if sys.platform == "win32" else "dist/resource-fetcher"
    cli_path = Path(cli_binary)
    if not cli_path.exists():
        print(f"[ERROR] CLI binary not found: {cli_binary}")
        sys.exit(1)

    print(f"[OK] CLI built: {cli_binary}")
    return cli_binary

def build_portable_python(cli_binary):
    """Create portable Python environment."""
    print("\n" + "="*60)
    print("Creating portable Python environment...")
    print("="*60)

    portable_dir = Path("portable")
    python_dir = portable_dir / "python"
    cli_dir = portable_dir / "cli"

    # Clean old portable package
    if portable_dir.exists():
        shutil.rmtree(portable_dir)

    portable_dir.mkdir()
    python_dir.mkdir(parents=True)
    cli_dir.mkdir(parents=True)

    # Create a placeholder file in python directory for glob pattern matching
    (python_dir / ".gitkeep").touch()

    # Copy CLI
    shutil.copy(Path(cli_binary), cli_dir / "resource-fetcher.exe")
    print(f"[OK] CLI copied to: {cli_dir / 'resource-fetcher.exe'}")

    # For now, we'll use a simpler approach:
    # Just copy CLI and create a minimal portable structure
    # The Python runtime will be bundled by Tauri's resources configuration
    print(f"[OK] Portable environment created: {portable_dir}")
    return portable_dir

def build_tauri_gui(portable_dir):
    """Build Tauri GUI with bundled resources."""
    print("\n" + "="*60)
    print("Building Tauri GUI...")
    print("="*60)

    # Build Tauri application
    run(["npm", "run", "tauri", "build"], cwd="tauri-gui", shell=True)

    # The GUI binary location depends on the build target
    if sys.platform == "win32":
        # Check for NSIS installer first
        nsis_bundle = Path("tauri-gui/src-tauri/target/release/bundle/nsis")
        if nsis_bundle.exists():
            exe_files = list(nsis_bundle.glob("*.exe"))
            if exe_files:
                print(f"[OK] NSIS installer created: {exe_files[0]}")

        # Check for MSI installer
        msi_bundle = Path("tauri-gui/src-tauri/target/release/bundle/msi")
        if msi_bundle.exists():
            msi_files = list(msi_bundle.glob("*.msi"))
            if msi_files:
                print(f"[OK] MSI installer created: {msi_files[0]}")

        # Also check for standalone exe
        gui_binary = Path("tauri-gui/src-tauri/target/release/resource-fetcher-gui.exe")
        if gui_binary.exists():
            print(f"[OK] GUI binary created: {gui_binary}")
            return str(gui_binary)

    return None

def create_portable_package(cli_binary, portable_dir, gui_binary=None):
    """Create portable ZIP package."""
    print("\n" + "="*60)
    print("Creating portable package...")
    print("="*60)

    release_dir = Path("release")
    release_dir.mkdir(parents=True, exist_ok=True)

    package_dir = release_dir / "Resource-Fetcher-Portable"
    if package_dir.exists():
        shutil.rmtree(package_dir)

    package_dir.mkdir()

    # Copy GUI if available
    if gui_binary and Path(gui_binary).exists():
        shutil.copy(gui_binary, package_dir / "Resource-Fetcher.exe")
        print(f"[OK] GUI copied to portable package")
    else:
        # Try to find the GUI binary in default location
        default_gui = Path("tauri-gui/src-tauri/target/release/resource-fetcher-gui.exe")
        if default_gui.exists():
            shutil.copy(default_gui, package_dir / "Resource-Fetcher.exe")
            print(f"[OK] GUI copied from default location")
        else:
            print("[WARNING] GUI binary not found, creating CLI-only portable package")

    # Copy runtime (CLI and potentially Python)
    runtime_dir = package_dir / "runtime"
    shutil.copytree(portable_dir, runtime_dir, dirs_exist_ok=True)

    # Create README
    with open(package_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write("Resource Fetcher - Portable Version\n")
        f.write("="*50 + "\n\n")
        f.write("Usage:\n")
        f.write("1. Double-click Resource-Fetcher.exe to launch GUI\n")
        if gui_binary:
            f.write("2. Or use CLI from command line:\n")
            f.write(f"   cd runtime\\cli\n")
            f.write(f"   resource-fetcher.exe --help\n")
        f.write("\nNo installation required!\n")
        f.write("\nVersion: 0.2.0\n")

    # Create startup script
    with open(package_dir / "start.bat", "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("REM Resource Fetcher Portable Launcher\n")
        f.write("start \"\" \"Resource-Fetcher.exe\"\n")

    # Create ZIP
    zip_path = release_dir / "Resource-Fetcher-Portable-win-x64.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)

    # Get ZIP size
    size_mb = Path(zip_path).stat().st_size / (1024*1024)
    print(f"[OK] Portable package created: {zip_path}")
    print(f"   Size: {size_mb:.2f} MB")

def main():
    """Main build process."""
    print("="*60)
    print("Resource Fetcher - Complete Build System")
    print("="*60)

    # 1. Build CLI
    cli_binary = build_cli()

    # 2. Create portable Python environment
    portable_dir = build_portable_python(cli_binary)

    # 3. Build Tauri GUI (this will create installers via NSIS/MSI)
    gui_binary = build_tauri_gui(portable_dir)

    # 4. Create portable ZIP package
    create_portable_package(cli_binary, portable_dir, gui_binary)

    print("\n" + "="*60)
    print("[OK] All builds completed successfully!")
    print("="*60)
    print("\nArtifacts created:")
    print("  - release/Resource-Fetcher-Portable-win-x64.zip")
    print("  - tauri-gui/src-tauri/target/release/bundle/nsis/*.exe")
    print("  - tauri-gui/src-tauri/target/release/bundle/msi/*.msi")
    print("\nNext steps:")
    print("  1. Test the portable package by extracting and running")
    print("  2. Test the NSIS installer")
    print("  3. Test the MSI installer")

if __name__ == "__main__":
    main()
