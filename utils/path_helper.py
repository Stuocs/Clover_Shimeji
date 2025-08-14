#!/usr/bin/env python3
"""
Path Helper - Utilities for managing file paths
"""

import os
import sys

def get_base_path():
    """Get the base path of the application."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_resource_path():
    """Get the path to bundled resources (for PyInstaller)."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - use PyInstaller's temp directory
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        else:
            return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_assets_path():
    """Get the path to the assets directory."""
    return os.path.join(get_base_path(), 'assets')

def get_sprites_path():
    """Get the path to the sprites directory."""
    # For bundled resources (PyInstaller), use resource path
    resource_path = get_resource_path()
    sprites_path = os.path.join(resource_path, 'Sprites')
    if os.path.exists(sprites_path):
        return sprites_path
    
    # Fallback to base path for development/non-bundled
    base_path = get_base_path()
    sprites_path = os.path.join(base_path, 'Sprites')
    if os.path.exists(sprites_path):
        return sprites_path
    
    # Fallback to new assets structure
    assets_sprites = os.path.join(get_assets_path(), 'sprites')
    if os.path.exists(assets_sprites):
        return assets_sprites
    
    # If neither exists, return the resource path for compatibility
    return os.path.join(resource_path, 'Sprites')

def get_sprite_category_path(category):
    """Get the path to a specific sprite category."""
    return os.path.join(get_sprites_path(), category)

def ensure_directory_exists(path):
    """Ensure a directory exists, create if it doesn't."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path

def get_config_path():
    """Get the path for configuration files."""
    config_dir = os.path.join(get_base_path(), 'config')
    return ensure_directory_exists(config_dir)

def normalize_path(path):
    """Normalize a path for the current operating system."""
    return os.path.normpath(path)

def join_path(*args):
    """Join path components safely."""
    return os.path.join(*args)

def file_exists(filepath):
    """Check if a file exists."""
    return os.path.isfile(filepath)

def directory_exists(dirpath):
    """Check if a directory exists."""
    return os.path.isdir(dirpath)

def get_file_extension(filepath):
    """Get the file extension from a filepath."""
    return os.path.splitext(filepath)[1].lower()

def is_image_file(filepath):
    """Check if a file is an image based on its extension."""
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    return get_file_extension(filepath) in image_extensions