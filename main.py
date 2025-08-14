#!/usr/bin/env python3
"""
Clover Desktop Mascot - Main Entry Point
A desktop mascot application based on Undertale Yellow's Clover character.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from core.mascot import DesktopMascot

def main():
    """Main entry point for the desktop mascot application."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running even when window is closed
    
    # Create and show the mascot
    mascot = DesktopMascot()
    mascot.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()