#!/usr/bin/env python3
"""
Event Handler - Manages user interactions and input events
"""

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtGui import QCursor

class EventHandler(QObject):
    """Handles various events and user interactions for the mascot."""
    
    # Signals
    mouse_idle = pyqtSignal()  # Emitted when mouse hasn't moved for a while
    mouse_active = pyqtSignal()  # Emitted when mouse becomes active
    
    def __init__(self, mascot):
        super().__init__()
        self.mascot = mascot
        
        # Mouse tracking
        self.last_mouse_pos = QCursor.pos()
        self.mouse_idle_timer = QTimer()
        self.mouse_idle_timer.timeout.connect(self.on_mouse_idle)
        self.mouse_idle_timer.setSingleShot(True)
        
        # Mouse position check timer
        self.mouse_check_timer = QTimer()
        self.mouse_check_timer.timeout.connect(self.check_mouse_movement)
        self.mouse_check_timer.start(100)  # Check every 100ms
        
        # State tracking
        self.is_mouse_idle = False
        self.mouse_idle_threshold = 5000  # 5 seconds of no movement
        
    def check_mouse_movement(self):
        """Check if the mouse has moved and update idle state."""
        current_pos = QCursor.pos()
        
        if current_pos != self.last_mouse_pos:
            # Mouse moved
            self.last_mouse_pos = current_pos
            
            if self.is_mouse_idle:
                self.is_mouse_idle = False
                self.mouse_active.emit()
            
            # Reset idle timer
            self.mouse_idle_timer.stop()
            self.mouse_idle_timer.start(self.mouse_idle_threshold)
    
    def on_mouse_idle(self):
        """Called when mouse has been idle for the threshold time."""
        if not self.is_mouse_idle:
            self.is_mouse_idle = True
            self.mouse_idle.emit()
    
    def is_mouse_near_mascot(self, threshold=100):
        """Check if the mouse cursor is near the mascot."""
        mouse_pos = QCursor.pos()
        mascot_pos = self.mascot.pos()
        mascot_center = mascot_pos + self.mascot.rect().center()
        
        distance = ((mouse_pos.x() - mascot_center.x())**2 + 
                   (mouse_pos.y() - mascot_center.y())**2)**0.5
        
        return distance <= threshold
    
    def get_mouse_direction_from_mascot(self):
        """Get the direction of the mouse relative to the mascot."""
        mouse_pos = QCursor.pos()
        mascot_pos = self.mascot.pos()
        mascot_center = mascot_pos + self.mascot.rect().center()
        
        dx = mouse_pos.x() - mascot_center.x()
        dy = mouse_pos.y() - mascot_center.y()
        
        # Determine primary direction
        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'down' if dy > 0 else 'up'
    
    def get_distance_to_mouse(self):
        """Get the distance from mascot to mouse cursor."""
        mouse_pos = QCursor.pos()
        mascot_pos = self.mascot.pos()
        mascot_center = mascot_pos + self.mascot.rect().center()
        
        dx = mouse_pos.x() - mascot_center.x()
        dy = mouse_pos.y() - mascot_center.y()
        
        return (dx**2 + dy**2)**0.5
    
    def start_mouse_tracking(self):
        """Start tracking mouse movement."""
        if not self.mouse_check_timer.isActive():
            self.mouse_check_timer.start(100)
    
    def stop_mouse_tracking(self):
        """Stop tracking mouse movement."""
        self.mouse_check_timer.stop()
        self.mouse_idle_timer.stop()
    
    def set_mouse_idle_threshold(self, milliseconds):
        """Set the threshold for mouse idle detection."""
        self.mouse_idle_threshold = milliseconds
    
    def force_mouse_idle_check(self):
        """Force an immediate check for mouse idle state."""
        self.check_mouse_movement()
    
    def reset_mouse_idle_timer(self):
        """Reset the mouse idle timer."""
        self.mouse_idle_timer.stop()
        self.mouse_idle_timer.start(self.mouse_idle_threshold)
        if self.is_mouse_idle:
            self.is_mouse_idle = False
            self.mouse_active.emit()