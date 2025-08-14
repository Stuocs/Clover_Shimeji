#!/usr/bin/env python3
"""
Build script for creating standalone executable of Clover Desktop Mascot
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Carpetas que queremos incluir en el .exe
INCLUDE_DIRS = ["assets", "Sprites", "core", "utils", "watcher"]

def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller if not present."""
    print("Installing PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

def build_executable(debug=False):
    """Build the standalone executable."""
    print("Building Clover Desktop Mascot executable...")

    # Generar lista de --add-data para todas las carpetas que existan
    data_args = []
    for folder in INCLUDE_DIRS:
        if os.path.exists(folder):
            data_args.append(f"--add-data={folder};{folder}")

    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name=CloverMascot",
        "--distpath=dist",
        "--workpath=build",
        "--specpath=."
    ]

    # Modo ventana solo si no es debug
    if not debug:
        cmd.append("--windowed")

    # Icono si existe (prioritize the premium high-quality Clover icon)
    if os.path.exists("assets/clover_premium.ico"):
        cmd.append("--icon=assets/clover_premium.ico")

    # Agregar data_args
    cmd.extend(data_args)

    # Script principal
    cmd.append("main.py")

    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Build successful!")
        print(f"📁 Executable created in: {os.path.abspath('dist')}")
        print("🚀 You can now run CloverMascot.exe")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

    return True

def create_portable_package():
    """Create a portable package with the executable and assets."""
    exe_path = Path("dist") / "CloverMascot.exe"
    if not exe_path.exists():
        print("❌ Executable not found. Build first.")
        return

    print("Creating portable package...")

    portable_dir = Path("CloverMascot_Portable")
    if portable_dir.exists():
        shutil.rmtree(portable_dir)

    portable_dir.mkdir()

    shutil.copy2(exe_path, portable_dir)

    if os.path.exists("README.md"):
        shutil.copy2("README.md", portable_dir)

    print(f"✅ Portable package created: {portable_dir}/")

def clean_build_files():
    """Clean up build artifacts."""
    print("Cleaning build files...")

    dirs_to_remove = ["build", "__pycache__", "dist"]
    files_to_remove = ["CloverMascot.spec"]

    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed: {dir_name}/")

    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Removed: {file_name}")

    for root, dirs, _ in os.walk("."):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            shutil.rmtree(pycache_path)
            print(f"Removed: {pycache_path}")

def main():
    """Main build function."""
    print("Clover Desktop Mascot Build Script")
    print("=" * 40)

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "clean":
            clean_build_files()
            return
        elif command == "package":
            create_portable_package()
            return
        elif command == "debug":
            if not check_pyinstaller():
                try:
                    install_pyinstaller()
                except subprocess.CalledProcessError:
                    print("❌ Failed to install PyInstaller")
                    return
            build_executable(debug=True)
            return
        elif command == "help":
            print("Available commands:")
            print("  python build.py        - Build executable (windowed)")
            print("  python build.py debug  - Build executable with console for debugging")
            print("  python build.py clean  - Clean build files")
            print("  python build.py package - Create portable package")
            print("  python build.py help   - Show this help")
            return

    if not check_pyinstaller():
        try:
            install_pyinstaller()
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return

    build_executable(debug=False)

if __name__ == "__main__":
    main()
