#!/usr/bin/env python3
"""
Desktop Mascot - Main mascot window and display logic (Also some animations because I lost the track in animation_loader :D )
"""

import os
import random
import time
import config
import requests
import json
from urllib.parse import quote
try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
from PyQt5.QtWidgets import QWidget, QLabel, QMenu, QAction, QApplication, QSystemTrayIcon
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal, QThread, pyqtSignal as Signal
from PyQt5.QtGui import QPixmap, QPainter, QCursor, QIcon
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from .animation_loader import AnimationLoader
from .event_handler import EventHandler
from .logic import MascotLogic
from .settings_dialog import AFKBehaviorSettingsDialog

class DesktopMascot(QWidget):
    """Main mascot widget that displays on desktop."""
    
    def __init__(self):
        super().__init__()
        self.animation_loader = AnimationLoader()
        self.event_handler = EventHandler(self)
        self.logic = MascotLogic(self)
        
        # State variables
        self.current_animation = None
        self.current_animation_name = None
        self.current_frame = 0
        self.is_following_mouse = False
        self.is_sleeping = False
        self.is_falling = False
        self.is_dragging = False
        self.drag_start_position = QPoint()
        self.is_character_interaction = False
        
        # Running mode variables
        self.is_running_mode = False
        self.follow_start_time = None
        
        # Whale mail window tracking
        self.moved_windows = {}  # Store original positions of moved windows
        
        # Meme cart functionality
        self.meme_image_label = None
        self.current_meme_pixmap = None
        self.network_manager = QNetworkAccessManager()
        
        # Timers
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.next_frame)
        
        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self.logic.perform_random_action)
        
        self.mouse_follow_timer = QTimer()
        self.mouse_follow_timer.timeout.connect(self.follow_mouse)
        
        self.init_ui()
        self.init_system_tray()
        self.load_initial_animation()
        self.load_afk_behavior_settings()
        
    def init_ui(self):
        """Initialize the UI with transparent background and frameless window."""
        # Window properties for desktop overlay
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        
        # Make background transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        # Set initial size and position
        self.resize(64, 64)  # Default sprite size
        self.move(100, 100)  # Initial position
        
        # Create label for sprite display
        self.sprite_label = QLabel(self)
        self.sprite_label.setAlignment(Qt.AlignCenter)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
    
    def init_system_tray(self):
        """Initialize the system tray icon."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("System tray is not available on this system.")
            return
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Set icon (try premium icons first, fallback to default if needed)
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'clover_premium.ico')
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # Fallback to application icon if available
            self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        
        # Set tooltip
        self.tray_icon.setToolTip("Clover Desktop Mascot")
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Show/Hide mascot action
        show_hide_action = QAction("Show/Hide Mascot", self)
        show_hide_action.triggered.connect(self.toggle_mascot_visibility)
        tray_menu.addAction(show_hide_action)
        
        tray_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close_application)
        tray_menu.addAction(exit_action)
        
        # Set the menu
        self.tray_icon.setContextMenu(tray_menu)
        
        # Connect double-click to show/hide
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
        # Show the tray icon
        self.tray_icon.show()
        
        print("System tray icon initialized successfully.")
    
    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation (clicks)."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_mascot_visibility()
    
    def toggle_mascot_visibility(self):
        """Toggle the visibility of the mascot window."""
        if self.isVisible():
            self.hide()
            if hasattr(self, 'tray_icon'):
                self.tray_icon.showMessage(
                    "Clover Desktop Mascot",
                    "Mascot hidden. Double-click the tray icon or right-click and select 'Show/Hide Mascot' to show again.",
                    QSystemTrayIcon.Information,
                    3000
                )
        else:
            self.show()
            if hasattr(self, 'tray_icon'):
                self.tray_icon.showMessage(
                    "Clover Desktop Mascot",
                    "Mascot is now visible on your desktop.",
                    QSystemTrayIcon.Information,
                    2000
                )
        
    def load_initial_animation(self):
        """Load the initial idle animation."""
        sitting_animations = self.animation_loader.get_animations_by_category('sitting')
        if sitting_animations:
            self.start_animation(sitting_animations[0])
        else:
            # Fallback to any available animation
            all_animations = self.animation_loader.get_all_animations()
            if all_animations:
                self.start_animation(all_animations[0])
    
    def start_animation(self, animation_name, loop=True):
        """Start playing an animation."""
        animation = self.animation_loader.get_animation(animation_name)
        if not animation:
            return
            
        self.current_animation = animation
        self.current_animation_name = animation_name
        self.current_frame = 0
        self.animation_loop = loop
        
        # Update sprite size based on first frame
        if animation['frames']:
            first_frame = animation['frames'][0]
            self.resize(first_frame.width(), first_frame.height())
            self.sprite_label.resize(self.size())
        
        # Start animation timer
        self.animation_timer.start(animation.get('frame_rate', 150))
        self.update_sprite()
        
        # Idle timer functionality removed with idle mode
    
    def stop_animation(self):
        """Stop the current animation."""
        if self.animation_timer.isActive():
            self.animation_timer.stop()
        self.current_animation = None
        self.current_animation_name = None
        self.current_frame = 0
    
    def next_frame(self):
        """Advance to the next animation frame."""
        if not self.current_animation or not self.current_animation['frames']:
            return
            
        self.current_frame += 1
        
        if self.current_frame >= len(self.current_animation['frames']):
            if self.animation_loop:
                self.current_frame = 0
            else:
                self.animation_timer.stop()
                self.logic.on_animation_complete()
                return
        
        self.update_sprite()
    
    def update_sprite(self):
        """Update the displayed sprite."""
        if not self.current_animation or not self.current_animation['frames']:
            return
            
        if self.current_frame < len(self.current_animation['frames']):
            pixmap = self.current_animation['frames'][self.current_frame]
            
            # Apply size scaling
            current_scale = config.get_setting('size', 'current_scale', 1.0)
            if current_scale != 1.0:
                scaled_size = pixmap.size() * current_scale
                pixmap = pixmap.scaled(scaled_size, Qt.KeepAspectRatio, Qt.FastTransformation)
            
            # If sleeping and using precomposed ZZZ frames, use them instead
            if (self.is_sleeping and hasattr(self, 'zzz_composite_frames') and 
                self.zzz_composite_frames and hasattr(self, 'zzz_current_frame') and
                len(self.zzz_composite_frames) > 0):
                # Use precomposed frame to avoid recompositing
                pixmap = self.zzz_composite_frames[self.zzz_current_frame]
            
            self.sprite_label.setPixmap(pixmap)
            
            # Update widget and label size to match scaled sprite
            sprite_size = pixmap.size()
            self.resize(sprite_size)
            self.sprite_label.resize(sprite_size)
            self.sprite_label.move(0, 0)  # Ensure label is positioned at top-left
    
    def composite_zzz_overlay(self, base_pixmap, scale):
        """Composite ZZZ overlay on top of the base sprite."""
        from PyQt5.QtGui import QPainter
        
        # Get current ZZZ frame
        zzz_pixmap = self.zzz_frames[self.zzz_current_frame]
        
        # Scale ZZZ sprite if needed
        if scale != 1.0:
            zzz_scaled_size = zzz_pixmap.size() * scale
            zzz_pixmap = zzz_pixmap.scaled(zzz_scaled_size, Qt.KeepAspectRatio, Qt.FastTransformation)
        
        # Calculate progressive height offset for each ZZZ frame (0, 1, 2)
        # Frame 0: closest to head, Frame 2: highest
        height_offset = self.zzz_current_frame * int(10 * scale)  # Progressive height increase
        
        # Create a larger canvas to accommodate ZZZ sprites above the mascot
        zzz_space = int(60 * scale)  # Extra space above for ZZZ animation
        canvas_width = max(base_pixmap.width(), zzz_pixmap.width())
        canvas_height = base_pixmap.height() + zzz_space
        
        result_pixmap = QPixmap(canvas_width, canvas_height)
        result_pixmap.fill(Qt.transparent)
        
        # Draw the base sprite at the bottom of the canvas
        painter = QPainter(result_pixmap)
        base_x = (canvas_width - base_pixmap.width()) // 2
        base_y = zzz_space  # Position base sprite below ZZZ space
        painter.drawPixmap(base_x, base_y, base_pixmap)
        
        # Position ZZZ above Clover's head with progressive height
        zzz_x = (canvas_width - zzz_pixmap.width()) // 2
        zzz_y = zzz_space - zzz_pixmap.height() - int(5 * scale) - height_offset
        
        # Draw the ZZZ overlay
        painter.drawPixmap(zzz_x, zzz_y, zzz_pixmap)
        painter.end()
        
        return result_pixmap
    
    def follow_mouse(self):
        """Move mascot towards mouse cursor with proper walking/running animation."""
        if not self.is_following_mouse:
            return
            
        cursor_pos = QCursor.pos()
        mascot_pos = self.pos()
        
        # Calculate distance to cursor
        dx = cursor_pos.x() - mascot_pos.x()
        dy = cursor_pos.y() - mascot_pos.y()
        distance = (dx**2 + dy**2)**0.5
        
        # Stop if close enough and start dancing
        if distance < 50:
            # Start dancing for 10 seconds (10000 ms) regardless of current animation
            self.logic.start_timed_dance(10000)
            # Disable mouse following while dancing
            self.is_following_mouse = False
            self.mouse_follow_timer.stop()
            # Reset running mode
            self.is_running_mode = False
            self.follow_start_time = None
            return
        
        # Check if we should switch to running mode (after 10 seconds) or super running mode (after 20 seconds)
        import time
        current_time = time.time()
        is_super_running = False
        if self.follow_start_time:
            elapsed_time = current_time - self.follow_start_time
            if elapsed_time > 20:
                # Super running mode after 20 seconds (quadruple speed)
                self.is_running_mode = True
                is_super_running = True
            elif elapsed_time > 10:
                # Regular running mode after 10 seconds (double speed)
                self.is_running_mode = True
            
        # Determine primary direction and start appropriate animation
        if abs(dx) > abs(dy):
            # Horizontal movement is dominant
            if dx > 0:
                # Moving right
                target_animation = 'walking_spr_pl_run_right' if self.is_running_mode else 'walking_spr_pl_right'
                if self.current_animation_name != target_animation:
                    self.start_animation(target_animation, loop=True)
            else:
                # Moving left
                target_animation = 'walking_spr_pl_run_left' if self.is_running_mode else 'walking_spr_pl_left'
                if self.current_animation_name != target_animation:
                    self.start_animation(target_animation, loop=True)
        else:
            # Vertical movement is dominant
            if dy > 0:
                # Moving down
                target_animation = 'walking_spr_pl_run_down' if self.is_running_mode else 'walking_spr_pl_down'
                if self.current_animation_name != target_animation:
                    self.start_animation(target_animation, loop=True)
            else:
                # Moving up
                target_animation = 'walking_spr_pl_run_up' if self.is_running_mode else 'walking_spr_pl_up'
                if self.current_animation_name != target_animation:
                    self.start_animation(target_animation, loop=True)
        
        # Move towards cursor with appropriate speed
        if is_super_running:
            speed = 24  # Quadruple speed for super running mode
        elif self.is_running_mode:
            speed = 12  # Double speed for regular running mode
        else:
            speed = 6   # Normal walking speed
        if distance > 0:
            move_x = int(dx / distance * speed)
            move_y = int(dy / distance * speed)
            self.move(mascot_pos.x() + move_x, mascot_pos.y() + move_y)
    
    def set_follow_mouse(self, follow):
        """Enable or disable mouse following."""
        self.logic.on_user_interaction()  # User interaction
        self.is_following_mouse = follow
        if follow:
            # Stop random walking when following mouse
            self.logic.stop_random_walking_system()
            # Initialize timing for running mode
            import time
            self.follow_start_time = time.time()
            self.is_running_mode = False
            self.mouse_follow_timer.start(50)  # Update every 50ms
            self.idle_timer.stop()
            # Animation will be handled by follow_mouse() based on direction
        else:
            self.mouse_follow_timer.stop()
            # Reset running mode variables
            self.is_running_mode = False
            self.follow_start_time = None
            # Restart random walking if no other special modes are active
            if (self.logic.random_walking_enabled and 
                not self.logic.eternal_dance_mode and not self.logic.timed_dance_mode and 
                not self.is_sleeping and not getattr(self, 'is_falling', False)):
                self.logic.start_random_walking_system()
            # Stop walking/running animation when disabling mouse following
            if self.current_animation_name and self.current_animation_name.startswith('walking_'):
                self.logic.return_to_idle()
            else:
                self.logic.return_to_idle()
    
    def set_sleep_mode(self, sleep, auto_stop=False):
        """Enable or disable sleep mode."""
        if not auto_stop:
            self.logic.on_user_interaction()  # User interaction
        self.is_sleeping = sleep
        if sleep:
            # Stop random walking when sleeping
            self.logic.stop_random_walking_system()
            self.idle_timer.stop()
            self.mouse_follow_timer.stop()
            # Load and display only the specific sleep sprite
            self.start_sleep_animation()
        else:
            # Automatically trigger Return to AFK when sleep mode is deactivated
            self.return_to_afk_mode()
    
    def set_fall_mode(self, fall, auto_stop=False):
        """Enable or disable fall mode."""
        if not auto_stop:
            self.logic.on_user_interaction()  # User interaction
        self.is_falling = fall
        if fall:
            # Stop random walking when falling
            self.logic.stop_random_walking_system()
            self.idle_timer.stop()
            self.mouse_follow_timer.stop()
            # Start the fall animation
            self.start_fall_animation()
        else:
            # Automatically trigger Return to AFK when sleep mode is deactivated
            self.return_to_afk_mode()
    
    def return_to_afk_mode(self):
        """Return to AFK mode by disabling all special modes and enabling random walking."""
        self.logic.on_user_interaction()  # User interaction
        
        # Disable all special modes
        self.is_following_mouse = False
        self.is_sleeping = False
        if hasattr(self, 'is_falling'):
            self.is_falling = False
        if hasattr(self, 'is_character_interaction'):
            self.is_character_interaction = False
        
        # Stop all timers
        self.idle_timer.stop()
        self.mouse_follow_timer.stop()
        if hasattr(self.logic, 'walking_movement_timer'):
            self.logic.walking_movement_timer.stop()
        
        # Stop any dance modes
        if self.logic.eternal_dance_mode:
            self.logic.eternal_dance_mode = False
        if self.logic.timed_dance_mode:
            self.logic.timed_dance_mode = False
            if hasattr(self.logic, 'timed_dance_timer'):
                self.logic.timed_dance_timer.stop()
        
        # Stop ZZZ animation if running
        self.stop_zzz_animation()
        
        # Return to idle animation
        sitting_animations = self.animation_loader.get_animations_by_category('sitting')
        if sitting_animations:
            self.start_animation(sitting_animations[0])
        
        # Enable random walking system
        if not self.logic.random_walking_enabled:
            self.logic.random_walking_enabled = True
        
        # Start random walking system
        self.logic.start_random_walking_system()
        
        # Return to idle state
        self.logic.return_to_idle()
    
    def start_fall_animation(self):
        """Start the fall animation using the falls category."""
        # Get fall animations from the falls category
        fall_animations = self.animation_loader.get_animations_by_category('falls')
        if fall_animations:
            # Use the first fall animation available
            self.start_animation(fall_animations[0], loop=True)
        else:
            print("Warning: No fall animations found in falls category")
     
    def start_sleep_animation(self):
        """Start the sleep animation with Clover on bed and ZZZ overlay."""
        from utils.path_helper import get_sprites_path
        import os
        from PyQt5.QtGui import QPixmap, QPainter
        
        # Load the bed sprite and Clover lying sprite
        bed_sprite_path = os.path.join(get_sprites_path(), 'lying', 'spr_bed_dark_nosheet_0.png')
        clover_sprite_path = os.path.join(get_sprites_path(), 'lying', 'spr_pl_lying_0.png')
        
        if os.path.exists(bed_sprite_path) and os.path.exists(clover_sprite_path):
            bed_pixmap = QPixmap(bed_sprite_path)
            clover_pixmap = QPixmap(clover_sprite_path)
            
            if not bed_pixmap.isNull() and not clover_pixmap.isNull():
                # Create composite image with Clover on the bed
                composite_pixmap = self.create_bed_scene(bed_pixmap, clover_pixmap)
                
                # Create a custom animation with the composite frame
                self.current_animation = {
                    'frames': [composite_pixmap],
                    'frame_rate': 1000,  # Very slow since it's just one frame
                    'loop': True
                }
                self.current_animation_name = 'sleep_bed_scene'
                self.current_frame = 0
                self.animation_loop = True
                
                # Stop animation timer since it's a static image
                self.animation_timer.stop()
                
                # Load ZZZ sprites for overlay animation
                self.load_zzz_sprites()
                
                # Start ZZZ animation
                self.start_zzz_animation()
                
                # Update the sprite display
                self.update_sprite()
                return
        
        # Fallback to just Clover lying if bed sprite not found
        sleep_sprite_path = os.path.join(get_sprites_path(), 'lying', 'spr_pl_lying_0.png')
        if os.path.exists(sleep_sprite_path):
            pixmap = QPixmap(sleep_sprite_path)
            if not pixmap.isNull():
                self.current_animation = {
                    'frames': [pixmap],
                    'frame_rate': 1000,
                    'loop': True
                }
                self.current_animation_name = 'sleep_lying'
                self.current_frame = 0
                self.animation_loop = True
                self.animation_timer.stop()
                self.load_zzz_sprites()
                self.start_zzz_animation()
                
                # Update the sprite display
                self.update_sprite()
    
    def create_bed_scene(self, bed_pixmap, clover_pixmap):
        """Create a composite scene with Clover lying on the bed."""
        from PyQt5.QtGui import QPainter
        
        # Create a canvas large enough for both sprites
        canvas_width = max(bed_pixmap.width(), clover_pixmap.width())
        canvas_height = max(bed_pixmap.height(), clover_pixmap.height())
        
        # Create the composite pixmap
        composite = QPixmap(canvas_width, canvas_height)
        composite.fill(Qt.transparent)
        
        painter = QPainter(composite)
        
        # Draw the bed first (background)
        bed_x = (canvas_width - bed_pixmap.width()) // 2
        bed_y = (canvas_height - bed_pixmap.height()) // 2
        painter.drawPixmap(bed_x, bed_y, bed_pixmap)
        
        # Position Clover within the bed's theoretical center (sleeping area)
        # The bed sprite likely has padding, so we need to position Clover within the actual bed area
        # Adjust horizontally to center within the bed's sleeping surface
        clover_x = bed_x + (bed_pixmap.width() - clover_pixmap.width()) // 2 - 10
        
        # Position Clover's head on the pillow area (upper portion of the bed)
        # Move down from bed center to get head on pillow (opposite direction)
        clover_y = bed_y + (bed_pixmap.height() - clover_pixmap.height()) // 2 + 1
        
        painter.drawPixmap(clover_x, clover_y, clover_pixmap)
        
        painter.end()
        return composite
    
    def load_zzz_sprites(self):
        """Load ZZZ animation sprites and precomposite them with the sleep scene."""
        from utils.path_helper import get_sprites_path
        import os
        from PyQt5.QtGui import QPixmap
        
        self.zzz_frames = []
        self.zzz_composite_frames = []  # Precomposed frames to avoid visual loading
        sprites_path = get_sprites_path()
        lying_path = os.path.join(sprites_path, 'lying')
        
        # Load ZZZ sprites (0, 1, 2)
        for i in range(3):
            zzz_file = f'spr_zzz_{i}.png'
            zzz_path = os.path.join(lying_path, zzz_file)
            
            if os.path.exists(zzz_path):
                pixmap = QPixmap(zzz_path)
                if not pixmap.isNull():
                    self.zzz_frames.append(pixmap)
        
        # Initialize ZZZ animation state
        self.zzz_current_frame = 0
        
        if not self.zzz_frames:
            print("Warning: No ZZZ sprites found for sleep animation")
        else:
            # Precomposite all ZZZ frames with the current sleep scene to avoid visual loading
            self.precomposite_zzz_frames()
    
    def precomposite_zzz_frames(self):
        """Precomposite all ZZZ frames with the sleep scene to avoid visual loading during animation."""
        if not hasattr(self, 'current_animation') or not self.current_animation or not self.current_animation['frames']:
            return
            
        # Get the base sleep sprite
        base_pixmap = self.current_animation['frames'][0]
        current_scale = config.get_setting('size', 'current_scale', 1.0)
        
        # Apply scaling to base sprite
        if current_scale != 1.0:
            scaled_size = base_pixmap.size() * current_scale
            base_pixmap = base_pixmap.scaled(scaled_size, Qt.KeepAspectRatio, Qt.FastTransformation)
        
        # Clear previous composite frames
        self.zzz_composite_frames = []
        
        # Create composite frames for each ZZZ sprite
        for i, zzz_pixmap in enumerate(self.zzz_frames):
            composite_frame = self.create_zzz_composite(base_pixmap, zzz_pixmap, i, current_scale)
            self.zzz_composite_frames.append(composite_frame)
    
    def create_zzz_composite(self, base_pixmap, zzz_pixmap, frame_index, scale):
        """Create a single composite frame with ZZZ overlay."""
        from PyQt5.QtGui import QPainter
        
        # Scale ZZZ sprite if needed
        if scale != 1.0:
            zzz_scaled_size = zzz_pixmap.size() * scale
            zzz_pixmap = zzz_pixmap.scaled(zzz_scaled_size, Qt.KeepAspectRatio, Qt.FastTransformation)
        
        # Calculate progressive height offset for each ZZZ frame (0, 1, 2)
        height_offset = frame_index * int(10 * scale)  # Progressive height increase
        
        # Create a larger canvas to accommodate ZZZ sprites above the mascot
        zzz_space = int(60 * scale)  # Extra space above for ZZZ animation
        canvas_width = max(base_pixmap.width(), zzz_pixmap.width())
        canvas_height = base_pixmap.height() + zzz_space
        
        result_pixmap = QPixmap(canvas_width, canvas_height)
        result_pixmap.fill(Qt.transparent)
        
        # Draw the base sprite at the bottom of the canvas
        painter = QPainter(result_pixmap)
        base_x = (canvas_width - base_pixmap.width()) // 2
        base_y = zzz_space  # Position base sprite below ZZZ space
        painter.drawPixmap(base_x, base_y, base_pixmap)
        
        # Position ZZZ above Clover's head with progressive height
        zzz_x = (canvas_width - zzz_pixmap.width()) // 2
        zzz_y = zzz_space - zzz_pixmap.height() - int(5 * scale) - height_offset
        
        # Draw the ZZZ overlay
        painter.drawPixmap(zzz_x, zzz_y, zzz_pixmap)
        painter.end()
        
        return result_pixmap
    
    def start_zzz_animation(self):
        """Start the ZZZ overlay animation using precomposed frames."""
        if hasattr(self, 'zzz_composite_frames') and self.zzz_composite_frames:
            self.zzz_timer = QTimer()
            self.zzz_timer.timeout.connect(self.next_zzz_frame)
            self.zzz_timer.start(800)  # Slower animation to make it less jarring
    
    def next_zzz_frame(self):
        """Advance to the next ZZZ frame using precomposed frames."""
        if hasattr(self, 'zzz_composite_frames') and self.zzz_composite_frames:
            self.zzz_current_frame = (self.zzz_current_frame + 1) % len(self.zzz_composite_frames)
            # Directly set the precomposed frame to avoid recompositing
            self.sprite_label.setPixmap(self.zzz_composite_frames[self.zzz_current_frame])
            # Update widget size to match the composite frame
            frame_size = self.zzz_composite_frames[self.zzz_current_frame].size()
            self.resize(frame_size)
            self.sprite_label.resize(frame_size)
            self.sprite_label.move(0, 0)
    
    def stop_zzz_animation(self):
        """Stop the ZZZ overlay animation and clean up properly."""
        if hasattr(self, 'zzz_timer'):
            self.zzz_timer.stop()
            # Clear ZZZ-related attributes to prevent separate sprite loading
            if hasattr(self, 'zzz_composite_frames'):
                self.zzz_composite_frames = []
            if hasattr(self, 'zzz_frames'):
                self.zzz_frames = []
            self.zzz_current_frame = 0
            # Simply update the sprite without reloading animation to avoid separate loading
            self.update_sprite()
    
    def force_dance(self):
        """Toggle eternal dance mode."""
        if self.logic.eternal_dance_mode:
            # Stop eternal dance
            self.logic.stop_eternal_dance()
        else:
            # Start eternal dance
            self.logic.start_eternal_dance()
    
    def change_size(self, scale):
        """Change the mascot's size scale."""
        config.update_setting('size', 'current_scale', scale)
        # Force sprite update to apply new scale
        self.update_sprite()
    
    def get_current_size_name(self):
        """Get the display name for the current size."""
        current_scale = config.get_setting('size', 'current_scale', 1.0)
        available_scales = config.get_setting('size', 'available_scales', [1.0])
        scale_names = config.get_setting('size', 'scale_names', ['Normal'])
        
        try:
            index = available_scales.index(current_scale)
            return scale_names[index]
        except (ValueError, IndexError):
            return 'Custom'
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            # Check if we're in hide and seek waiting phase
            if hasattr(self, 'in_hide_seek_sequence') and self.in_hide_seek_sequence and hasattr(self, 'hide_seek_phase') and self.hide_seek_phase == 'waiting':
                print("Hide&Seek: Clover was clicked - Found!")
                self.on_clover_found()
                return
            
            # Don't call on_user_interaction for dragging to preserve eternal dance
            self.is_dragging = True
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
        elif event.button() == Qt.RightButton:
            # Don't call on_user_interaction for right-click to preserve eternal dance
            self.show_context_menu(event.globalPos())
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for dragging."""
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_position)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
    
    def show_context_menu(self, position):
        """Show the right-click context menu."""
        menu = QMenu(self)
        
        # Dance action (toggle eternal dance)
        dance_text = "Stop Dancing" if self.logic.eternal_dance_mode else "Dance Forever"
        dance_action = QAction(dance_text, self)
        dance_action.triggered.connect(self.force_dance)
        menu.addAction(dance_action)
        
        # Follow mouse action
        follow_action = QAction("Follow Mouse", self)
        follow_action.setCheckable(True)
        follow_action.setChecked(self.is_following_mouse)
        follow_action.triggered.connect(lambda: self.set_follow_mouse(not self.is_following_mouse))
        menu.addAction(follow_action)
        
        # Sit submenu
        sit_menu = QMenu("Sit", self)
        
        # Sit Wind option
        sit_wind_action = QAction("Sit Wind", self)
        sit_wind_action.triggered.connect(lambda: self.start_sitting_animation('sitting_spr_colver_wind'))
        sit_menu.addAction(sit_wind_action)
        
        # Sitting option
        sitting_action = QAction("Sitting", self)
        sitting_action.triggered.connect(lambda: self.start_sitting_animation('sitting_spr_clover_sitting'))
        sit_menu.addAction(sitting_action)
        
        # Sit Dark option
        sit_dark_action = QAction("Sit Dark", self)
        sit_dark_action.triggered.connect(lambda: self.start_sitting_animation('sitting_spr_clover_sit_dark'))
        sit_menu.addAction(sit_dark_action)
        
        # Casual option
        casual_action = QAction("Casual", self)
        casual_action.triggered.connect(lambda: self.start_sitting_animation('spr_clover_casual'))
        sit_menu.addAction(casual_action)
        
        menu.addMenu(sit_menu)
        
        # Sleep action
        sleep_action = QAction("Sleep", self)
        sleep_action.setCheckable(True)
        sleep_action.setChecked(self.is_sleeping)
        sleep_action.triggered.connect(lambda: self.set_sleep_mode(not self.is_sleeping))
        menu.addAction(sleep_action)
        
        # Fall action
        fall_action = QAction("Fall", self)
        fall_action.setCheckable(True)
        fall_action.setChecked(getattr(self, 'is_falling', False))
        fall_action.triggered.connect(lambda: self.set_fall_mode(not getattr(self, 'is_falling', False)))
        menu.addAction(fall_action)
        
        # AFK mode toggle action
        afk_enabled = config.get_setting('afk_behavior', 'afk_mode_enabled', True)
        afk_status = "ON" if afk_enabled else "OFF"
        afk_action = QAction(f"AFK Mode ({afk_status})", self)
        afk_action.triggered.connect(self.toggle_afk_mode)
        menu.addAction(afk_action)
        
        # Return to AFK action (only show when AFK is enabled)
        if afk_enabled:
            return_afk_action = QAction("Return to AFK", self)
            return_afk_action.triggered.connect(self.return_to_afk_mode)
            menu.addAction(return_afk_action)
        
        menu.addSeparator()
        
        # Size submenu
        size_menu = menu.addMenu(f"Size ({self.get_current_size_name()})")
        available_scales = config.get_setting('size', 'available_scales', [1.0])
        scale_names = config.get_setting('size', 'scale_names', ['Normal'])
        current_scale = config.get_setting('size', 'current_scale', 1.0)
        
        for scale, name in zip(available_scales, scale_names):
            size_action = QAction(name, self)
            size_action.setCheckable(True)
            size_action.setChecked(scale == current_scale)
            size_action.triggered.connect(lambda checked, s=scale: self.change_size(s))
            size_menu.addAction(size_action)
        
        menu.addSeparator()
        
        # Character interactions submenu
        char_menu = menu.addMenu("Character")
        char_interactions = self.animation_loader.get_animations_by_category('characters_interactions')
        for interaction in char_interactions:
            action = QAction(interaction.replace('_', ' ').title(), self)
            action.triggered.connect(lambda checked, anim=interaction: self.start_character_interaction(anim))
            char_menu.addAction(action)
        
        menu.addSeparator()
        
        # Cart movement action
        cart_action = QAction("Cart Ride", self)
        cart_action.triggered.connect(self.start_cart_movement)
        menu.addAction(cart_action)
        
        # Meme cart movement action
        meme_cart_action = QAction("Meme Cart", self)
        meme_cart_action.triggered.connect(self.start_meme_cart_movement)
        menu.addAction(meme_cart_action)
        
        # Whale mail movement action
        whale_action = QAction("Whale Mail", self)
        whale_action.triggered.connect(self.start_whale_mail_movement)
        menu.addAction(whale_action)
        
        menu.addSeparator()
        
        # Minigames submenu
        minigames_menu = menu.addMenu("Minigames")
        
        # Hide and Seek minigame
        hide_seek_action = QAction("Hide and Seek", self)
        hide_seek_action.triggered.connect(self.start_hide_and_seek_sequence)
        minigames_menu.addAction(hide_seek_action)
        
        # Showdown minigame
        showdown_action = QAction("Showdown", self)
        showdown_action.triggered.connect(self.start_showdown_sequence)
        minigames_menu.addAction(showdown_action)
        
        menu.addSeparator()
        
        # AFK Behavior Settings action
        settings_action = QAction("AFK Behavior Settings", self)
        settings_action.triggered.connect(self.show_afk_settings)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close_application)
        menu.addAction(exit_action)
        
        menu.exec_(position)
    
    def show_afk_settings(self):
        """Show the AFK behavior settings dialog."""
        dialog = AFKBehaviorSettingsDialog(self)
        dialog.exec_()
    
    def toggle_afk_mode(self):
        """Toggle AFK mode on/off."""
        current_state = config.get_setting('afk_behavior', 'afk_mode_enabled', True)
        new_state = not current_state
        config.update_setting('afk_behavior', 'afk_mode_enabled', new_state)
        
        if new_state:
            print("AFK mode enabled")
            # Restart AFK behaviors if enabled
            self.return_to_afk_mode()
        else:
            print("AFK mode disabled")
            # Stop current AFK behaviors
            self.logic.random_walking_timer.stop()
    
    def disable_afk_mode_temporarily(self):
        """Temporarily disable AFK mode when an action starts."""
        config.update_setting('afk_behavior', 'afk_mode_enabled', False)
        config.update_setting('flags', 'had_afk_mode_enabled', True)
        self.logic.random_walking_timer.stop()
        print("AFK mode temporarily disabled")
    
    def re_enable_afk_mode(self):
        """Re-enable AFK mode when an action ends."""
        config.update_setting('afk_behavior', 'afk_mode_enabled', True)
        config.update_setting('flags', 'had_afk_mode_enabled', False)
        print("AFK mode re-enabled")
        # Restart AFK behaviors
        self.return_to_afk_mode()
    
    def start_sitting_animation(self, animation_name):
        """Start a specific sitting animation."""
        self.logic.on_user_interaction()  # User interaction
        
        # Stop any current timers and movements
        self.idle_timer.stop()
        self.mouse_follow_timer.stop()
        if hasattr(self.logic, 'walking_movement_timer'):
            self.logic.walking_movement_timer.stop()
        
        # Stop random walking
        self.logic.stop_random_walking_system()
        
        # Reset states
        self.is_following_mouse = False
        self.is_sleeping = False
        if hasattr(self, 'is_falling'):
            self.is_falling = False
        
        # Stop any special modes
        if self.logic.eternal_dance_mode:
            self.logic.eternal_dance_mode = False
        if self.logic.timed_dance_mode:
            self.logic.timed_dance_mode = False
            self.logic.timed_dance_timer.stop()
        
        # Start the requested sitting animation
        sitting_animations = self.animation_loader.get_animations_by_category('sitting')
        target_animation = None
        
        for anim in sitting_animations:
            if anim == animation_name:
                target_animation = anim
                break
        
        if target_animation:
            self.start_animation(target_animation)
        else:
            # Fallback to first sitting animation if specific one not found
            if sitting_animations:
                self.start_animation(sitting_animations[0])
    
    def start_character_interaction(self, animation_name):
        """Start a character interaction animation."""
        self.logic.on_user_interaction()  # User interaction
        self.is_character_interaction = True
        # Stop random walking during character interactions
        self.logic.stop_random_walking_system()
        self.idle_timer.stop()  # Stop any running idle timer
        self.start_animation(animation_name, loop=False)
    
    def start_cart_movement(self):
        """Start cart animation with left-to-right movement across screen."""
        # Register as user interaction to prevent interruptions
        self.logic.on_user_interaction()
        
        # Stop all timers and set interaction state
        self.idle_timer.stop()
        self.animation_timer.stop()
        if hasattr(self, 'zzz_timer'):
            self.zzz_timer.stop()
        
        self.is_character_interaction = True
        
        # Clear any previously moved windows
        self.moved_windows = {}
        
        # Get screen dimensions
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry()
        
        # Set starting position (left side of screen)
        self.move(-self.width(), self.y())
        
        # Start cart animation
        cart_animations = self.animation_loader.get_animations_by_category('cart')
        if cart_animations:
            self.start_animation(cart_animations[0], loop=True)
        
        # Set up movement timer
        self.cart_movement_timer = QTimer()
        self.cart_movement_timer.timeout.connect(self.update_cart_position)
        
        # Movement parameters
        self.cart_target_x = screen_rect.width() + self.width()  # End position (right side)
        self.cart_start_x = -self.width()  # Start position (left side)
        self.cart_current_x = self.cart_start_x
        self.cart_speed = 3  # pixels per update
        
        # Start movement
        self.cart_movement_timer.start(16)  # ~60 FPS
    
    def update_cart_position(self):
        """Update cart position during movement animation."""
        self.cart_current_x += self.cart_speed
        self.move(int(self.cart_current_x), self.y())
        
        # Check for windows in path and push them
        self.push_windows_in_cart_path()
        
        # Check if cart has moved off screen
        if self.cart_current_x >= self.cart_target_x:
            # Stop movement and restore moved windows
            self.cart_movement_timer.stop()
            self.restore_moved_windows()
            self.is_character_interaction = False
            
            # Return to center of screen and resume normal behavior
            from PyQt5.QtWidgets import QDesktopWidget
            desktop = QDesktopWidget()
            screen_rect = desktop.screenGeometry()
            center_x = (screen_rect.width() - self.width()) // 2
            center_y = (screen_rect.height() - self.height()) // 2
            self.move(center_x, center_y)
            
            # Return to idle animation
            sitting_animations = self.animation_loader.get_animations_by_category('sitting')
            if sitting_animations:
                self.start_animation(sitting_animations[0])
            
            # Resume AFK behaviors after cart ride completes
            import random
            self.logic.random_walking_timer.start(random.randint(3000, 8000))
    
    def start_meme_cart_movement(self):
        """Start meme cart animation with left-to-right movement and random meme display."""
        # Register as user interaction to prevent interruptions
        self.logic.on_user_interaction()
        
        # Stop all timers and set interaction state
        self.idle_timer.stop()
        self.animation_timer.stop()
        if hasattr(self, 'zzz_timer'):
            self.zzz_timer.stop()
        
        self.is_character_interaction = True
        
        # Clear any previously moved windows
        self.moved_windows = {}
        
        # Get screen dimensions
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry()
        
        # Set starting position (left side of screen)
        self.move(-self.width(), self.y())
        
        # Start meme cart animation
        meme_animations = self.animation_loader.get_animations_by_category('meme')
        if meme_animations:
            self.start_animation(meme_animations[0], loop=True)
        
        # Fetch and display random meme
        self.fetch_and_display_meme()
        
        # Set up movement timer
        self.meme_cart_movement_timer = QTimer()
        self.meme_cart_movement_timer.timeout.connect(self.update_meme_cart_position)
        
        # Movement parameters
        self.meme_cart_target_x = screen_rect.width() + self.width()  # End position (right side)
        self.meme_cart_start_x = -self.width()  # Start position (left side)
        self.meme_cart_current_x = self.meme_cart_start_x
        self.meme_cart_speed = 3  # pixels per update
        
        # Start movement
        self.meme_cart_movement_timer.start(16)  # ~60 FPS
    
    def update_meme_cart_position(self):
        """Update meme cart position during movement animation."""
        self.meme_cart_current_x += self.meme_cart_speed
        self.move(int(self.meme_cart_current_x), self.y())
        
        # Check if we've reached halfway point to release meme
        halfway_point = (self.meme_cart_start_x + self.meme_cart_target_x) / 2
        if not hasattr(self, 'meme_released') and self.meme_cart_current_x >= halfway_point:
            # Release meme in center of screen at halfway point
            self.release_meme_in_center()
            self.meme_released = True
        
        # Update meme position to follow cart only if not yet released
        if self.meme_image_label and not hasattr(self, 'meme_released'):
            meme_x = int(self.meme_cart_current_x) - 50  # Position meme to the left of cart
            meme_y = self.y() + self.height()  # Position meme below the mascot (hooked from below)
            self.meme_image_label.move(meme_x, meme_y)
        
        # Check for windows in path and push them
        #self.push_windows_in_cart_path()
        
        # Check if cart has moved off screen
        if self.meme_cart_current_x >= self.meme_cart_target_x:
            # Stop movement and restore moved windows
            self.meme_cart_movement_timer.stop()
            #self.restore_moved_windows()
            self.is_character_interaction = False
            
            # Reset meme release flag for next time
            if hasattr(self, 'meme_released'):
                delattr(self, 'meme_released')
            
            # Return to center of screen and resume normal behavior
            from PyQt5.QtWidgets import QDesktopWidget
            desktop = QDesktopWidget()
            screen_rect = desktop.screenGeometry()
            center_x = (screen_rect.width() - self.width()) // 2
            center_y = (screen_rect.height() - self.height()) // 2
            self.move(center_x, center_y)
            
            # Return to idle animation
            sitting_animations = self.animation_loader.get_animations_by_category('sitting')
            if sitting_animations:
                self.start_animation(sitting_animations[0])
            
            # Resume AFK behaviors after meme cart ride completes
            import random
            self.logic.random_walking_timer.start(random.randint(3000, 8000))
    
    def start_whale_mail_movement(self):
        """Start whale mail animation with bottom-to-top movement across screen."""
        # Register as user interaction to prevent interruptions
        self.logic.on_user_interaction()
        
        # Stop all timers and set interaction state
        self.idle_timer.stop()
        self.animation_timer.stop()
        if hasattr(self, 'zzz_timer'):
            self.zzz_timer.stop()
        
        self.is_character_interaction = True
        
        # Clear any previously moved windows
        self.moved_windows = {}
        
        # Get screen dimensions
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry()
        
        # Set starting position (bottom of screen)
        self.move(self.x(), screen_rect.height())
        
        # Start basket animation
        basket_animations = self.animation_loader.get_animations_by_category('basket')
        if basket_animations:
            self.start_animation(basket_animations[0], loop=True)
        
        # Set up movement timer
        self.whale_movement_timer = QTimer()
        self.whale_movement_timer.timeout.connect(self.update_whale_position)
        
        # Movement parameters
        self.whale_target_y = -self.height()  # End position (top of screen)
        self.whale_start_y = screen_rect.height()  # Start position (bottom of screen)
        self.whale_current_y = self.whale_start_y
        self.whale_speed = 2  # pixels per update (slower than cart for more graceful movement)
        
        # Start movement
        self.whale_movement_timer.start(16)  # ~60 FPS
    
    def update_whale_position(self):
        """Update whale position during movement animation."""
        self.whale_current_y -= self.whale_speed
        self.move(self.x(), int(self.whale_current_y))
        
        # Check for windows in path and push them
        self.push_windows_in_path()
        
        # Check if whale has moved off screen
        if self.whale_current_y <= self.whale_target_y:
            # Stop movement and restore moved windows
            self.whale_movement_timer.stop()
            self.restore_moved_windows()
            self.is_character_interaction = False
            
            # Return to center of screen and resume normal behavior
            from PyQt5.QtWidgets import QDesktopWidget
            desktop = QDesktopWidget()
            screen_rect = desktop.screenGeometry()
            center_x = (screen_rect.width() - self.width()) // 2
            center_y = (screen_rect.height() - self.height()) // 2
            self.move(center_x, center_y)
            
            # Return to idle animation
            sitting_animations = self.animation_loader.get_animations_by_category('sitting')
            if sitting_animations:
                self.start_animation(sitting_animations[0])
            
            # Resume AFK behaviors after whale mail completes
            import random
            self.logic.random_walking_timer.start(random.randint(3000, 8000))
    
    def start_hide_and_seek_sequence(self):
        # Check if is not already in a game
        if config.get_setting('flags', 'mascot_in_game', True) is False:
            
            """Start the Hide and Seek minigame sequence."""
            # Register as user interaction to prevent interruptions
            self.logic.on_user_interaction()
        
            # Temporarily disable AFK mode during minigame
            if config.get_setting('afk_behavior', 'afk_mode_enabled', True) is True:
                self.disable_afk_mode_temporarily()
        
            # Automatically reset character size to normal to prevent movement bugs
            self.change_size(1.0)
            print("Hide&Seek: Character size reset to normal to prevent movement bugs")

            # Stop all timers and set interaction state
            self.idle_timer.stop()
            self.animation_timer.stop()
            if hasattr(self, 'zzz_timer'):
                self.zzz_timer.stop()
        
            self.is_character_interaction = True
            self.in_hide_seek_sequence = False  # Initialize flag
            self.hide_seek_phase = 'grab'  # Track current phase: grab, move_to_taskbar, hide, waiting, found
        
            # Start with Edward grabbing Clover
            self.start_hide_seek_grab_phase()
    
    def start_hide_seek_grab_phase(self):
        """Phase 1: Edward grabs Clover."""
        self.in_hide_seek_sequence = True
        self.hide_seek_phase = 'grab'
        
        # Start grab animation
        grab_animation = 'edward_walking_spr_ed_grab_clover'
        if self.animation_loader.animation_exists(grab_animation):
            self.start_animation(grab_animation, loop=False)
            
            # Calculate duration and move to next phase
            animation_info = self.animation_loader.get_animation_info(grab_animation)
            if animation_info:
                duration = animation_info['frame_count'] * animation_info['frame_rate'] + 500
            else:
                duration = 2000
            
            QTimer.singleShot(int(duration), self.start_hide_seek_move_phase)
        else:
            print(f"Animation not found: {grab_animation}")
            self.start_hide_seek_move_phase()
    
    def start_hide_seek_move_phase(self):
        """Phase 2: Edward moves to Windows taskbar with Clover."""
        self.hide_seek_phase = 'move_to_taskbar'
        
        # Get screen dimensions and taskbar position (bottom of screen)
        screen = QApplication.primaryScreen().geometry()
        taskbar_x = screen.width() // 2  # Center of taskbar
        taskbar_y = screen.height() - 50  # Near bottom of screen
        
        # Set up movement to taskbar
        self.hide_seek_target_x = taskbar_x
        self.hide_seek_target_y = taskbar_y
        
        # Determine initial direction and start appropriate walking animation
        self.update_hide_seek_walking_animation()
        self.start_hide_seek_movement()
    
    def update_hide_seek_walking_animation(self):
        """Update Edward's walking animation based on movement direction."""
        current_x = self.x()
        current_y = self.y()
        
        # Calculate direction to target
        dx = self.hide_seek_target_x - current_x
        dy = self.hide_seek_target_y - current_y
        
        # Determine primary direction and select appropriate animation
        if abs(dx) > abs(dy):
            # Horizontal movement is dominant
            if dx > 0:
                # Moving right
                walk_animation = 'edward_walking_spr_ed_right_walk_clover'
            else:
                # Moving left
                walk_animation = 'edward_walking_spr_ed_left_walk_clover'
        else:
            # Vertical movement is dominant
            if dy > 0:
                # Moving down
                walk_animation = 'edward_walking_spr_ed_down_walk_clover'
            else:
                # Moving up
                walk_animation = 'edward_walking_spr_ed_up_walk_clover'
        
        # Start the appropriate walking animation if it exists and is different from current
        if (self.animation_loader.animation_exists(walk_animation) and 
            self.current_animation_name != walk_animation):
            self.start_animation(walk_animation, loop=True)
            print(f"Hide&Seek: Switching to {walk_animation} animation")
        elif not self.animation_loader.animation_exists(walk_animation):
            print(f"Hide&Seek: Animation not found: {walk_animation}, using fallback")
            # Fallback to down animation
            fallback_animation = 'edward_walking_spr_ed_down_walk_clover'
            if self.animation_loader.animation_exists(fallback_animation):
                self.start_animation(fallback_animation, loop=True)
    
    def start_hide_seek_movement(self):
        """Move Edward towards the taskbar."""
        if not hasattr(self, 'hide_seek_movement_timer'):
            self.hide_seek_movement_timer = QTimer()
            self.hide_seek_movement_timer.timeout.connect(self.update_hide_seek_position)
        
        self.hide_seek_movement_timer.start(50)  # Update every 50ms
    
    def update_hide_seek_position(self):
        """Update Edward's position during movement to taskbar."""
        current_x = self.x()
        current_y = self.y()
        
        # Calculate direction and distance
        dx = self.hide_seek_target_x - current_x
        dy = self.hide_seek_target_y - current_y
        distance = (dx**2 + dy**2)**0.5
        
        print(f"Hide&Seek Movement: Current({current_x}, {current_y}), Target({self.hide_seek_target_x}, {self.hide_seek_target_y}), Distance: {distance:.1f}")
        
        if distance < 30:  # Increased threshold to make it easier to trigger
            print("Hide&Seek: Reached target, starting drop phase")
            self.hide_seek_movement_timer.stop()
            self.start_hide_seek_drop_phase()
        else:
            # Update walking animation based on current movement direction
            self.update_hide_seek_walking_animation()
            
            # Move towards target
            speed = 10
            move_x = int(speed * dx / distance) if distance > 0 else 0
            move_y = int(speed * dy / distance) if distance > 0 else 0
            
            new_x = current_x + move_x
            new_y = current_y + move_y
            
            # Keep within screen bounds
            screen = QApplication.primaryScreen().geometry()
            new_x = max(0, min(new_x, screen.width() - self.width()))
            new_y = max(0, min(new_y, screen.height() - self.height()))
            
            self.move(new_x, new_y)
    
    def start_hide_seek_drop_phase(self):
        """Phase 3: Edward drops Clover and Clover hides."""
        print("Hide&Seek: Starting drop phase")
        self.hide_seek_phase = 'drop'
        
        # Start place animation
        place_animation = 'edward_walking_spr_ed_place_clover'
        if self.animation_loader.animation_exists(place_animation):
            self.start_animation(place_animation, loop=False)
            
            # Calculate duration and move to hide phase
            animation_info = self.animation_loader.get_animation_info(place_animation)
            if animation_info:
                duration = animation_info['frame_count'] * animation_info['frame_rate'] + 800
            else:
                duration = 2000
            
            QTimer.singleShot(int(duration), self.start_hide_seek_hide_phase)
        else:
            self.start_hide_seek_hide_phase()
    
    def start_hide_seek_hide_phase(self):
        """Phase 4: Clover hides visually using various creative methods."""
        print("Hide&Seek: Starting hide phase")
        self.hide_seek_phase = 'hide'
        
        # Save original scale before hiding
        if not hasattr(self, 'original_scale_before_hiding'):
            self.original_scale_before_hiding = config.get_setting('size', 'current_scale', 1.0)
        
        # Choose a random hiding method
        hiding_methods = [
            self.hide_on_desktop,
            self.hide_behind_windows,
            self.hide_in_taskbar_area,
            self.hide_partially_offscreen,
            self.hide_very_small,
            self.hide_in_user_directories
        ]
        
        # Choose random hiding method
        hiding_method = random.choice(hiding_methods)
        hiding_method()
        
        # Start waiting phase
        self.hide_seek_phase = 'waiting'
        print(f"Clover is hiding somewhere! Find and click on him to win!")
        
        # Set up detection for clicks on Clover
        self.start_visual_detection()
    
    def hide_on_desktop(self):
        """Hide Clover in corners and edges of the desktop."""
        screen = QApplication.primaryScreen().geometry()
        
        # Define possible hiding spots (corners and edges)
        hiding_spots = [
            (50, 50),  # Top-left corner
            (screen.width() - 100, 50),  # Top-right corner
            (50, screen.height() - 100),  # Bottom-left corner
            (screen.width() - 100, screen.height() - 100),  # Bottom-right corner
            (screen.width() // 2, 50),  # Top center
            (screen.width() // 2, screen.height() - 100),  # Bottom center
            (50, screen.height() // 2),  # Left center
            (screen.width() - 100, screen.height() // 2),  # Right center
        ]
        
        # Choose random hiding spot
        self.hide_seek_position = random.choice(hiding_spots)
        
        # Make Clover smaller and move to hiding spot
        self.change_size(0.8)
        self.move(self.hide_seek_position[0], self.hide_seek_position[1])
        self.start_animation('sitting_spr_clover_sit_dark', loop=True)
        print("Clover is hiding on the desktop!")
    
    def hide_behind_windows(self):
        """Hide Clover behind or near open windows."""
        if WIN32_AVAILABLE:
            try:
                # Get all visible windows
                windows = []
                def enum_windows_proc(hwnd, lParam):
                    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                        rect = win32gui.GetWindowRect(hwnd)
                        if rect[2] - rect[0] > 100 and rect[3] - rect[1] > 100:  # Only consider reasonably sized windows
                            windows.append(rect)
                    return True
                
                win32gui.EnumWindows(enum_windows_proc, 0)
                
                if windows:
                    # Choose a random window and hide near its edge
                    window_rect = random.choice(windows)
                    
                    # Hide near window edges
                    positions = [
                        (window_rect[0] - 50, window_rect[1] + 50),  # Left edge
                        (window_rect[2] + 10, window_rect[1] + 50),  # Right edge
                        (window_rect[0] + 50, window_rect[1] - 50),  # Top edge
                        (window_rect[0] + 50, window_rect[3] + 10),  # Bottom edge
                    ]
                    
                    self.hide_seek_position = random.choice(positions)
                    self.change_size(0.4)
                    self.move(max(0, self.hide_seek_position[0]), max(0, self.hide_seek_position[1]))
                    self.start_animation('sitting_spr_clover_sit_dark', loop=True)
                    print("Clover is hiding near a window!")
                    return
            except Exception as e:
                print(f"Error hiding behind windows: {e}")
        
        # Fallback to desktop hiding
        self.hide_on_desktop()
    
    def hide_in_taskbar_area(self):
        """Hide Clover near the taskbar area."""
        screen = QApplication.primaryScreen().geometry()
        
        # Hide near taskbar (bottom of screen)
        taskbar_positions = [
            (100, screen.height() - 80),
            (screen.width() // 2, screen.height() - 80),
            (screen.width() - 150, screen.height() - 80),
            (50, screen.height() - 120),  # Slightly above taskbar
        ]
        
        self.hide_seek_position = random.choice(taskbar_positions)
        self.change_size(0.6)  # Moderately small near taskbar
        self.move(self.hide_seek_position[0], self.hide_seek_position[1])
        self.start_animation('sitting_spr_clover_sit_dark', loop=True)
        print("Clover is hiding near the taskbar!")
    
    def hide_partially_offscreen(self):
        """Hide Clover partially off the screen edges."""
        screen = QApplication.primaryScreen().geometry()
        
        # Positions where Clover is partially off-screen
        offscreen_positions = [
            (-30, screen.height() // 2),  # Left edge, partially hidden
            (screen.width() - 20, screen.height() // 2),  # Right edge, partially hidden
            (screen.width() // 2, -30),  # Top edge, partially hidden
            (screen.width() // 2, screen.height() - 20),  # Bottom edge, partially hidden
        ]
        
        self.hide_seek_position = random.choice(offscreen_positions)
        self.change_size(0.9)
        self.move(self.hide_seek_position[0], self.hide_seek_position[1])
        self.start_animation('sitting_spr_clover_sit_dark', loop=True)
        print("Clover is hiding at the screen edge!")
    
    def hide_very_small(self):
        """Hide Clover by making him very small in a random location."""
        screen = QApplication.primaryScreen().geometry()
        
        # Random position anywhere on screen
        x = random.randint(100, screen.width() - 200)
        y = random.randint(100, screen.height() - 200)
        
        self.hide_seek_position = (x, y)
        self.change_size(0.5)  # Small but visible
        self.move(self.hide_seek_position[0], self.hide_seek_position[1])
        self.start_animation('sitting_spr_clover_sit_dark', loop=True)
        print("Clover is hiding very small somewhere!")
    
    def hide_in_user_directories(self):
        """Hide Clover in random locations within user directories (Documents, Pictures, Videos, Music, Downloads)."""
        import os
        
        print("Hide&Seek: Starting directory-based hiding!")
        
        # Get user home directory
        user_home = os.path.expanduser("~")
        print(f"Hide&Seek: User home directory: {user_home}")
        
        # Define target directories
        target_dirs = [
            os.path.join(user_home, "Documents"),
            os.path.join(user_home, "Pictures"),
            os.path.join(user_home, "Videos"),
            os.path.join(user_home, "Music"),
            os.path.join(user_home, "Downloads")
        ]
        
        # Filter existing directories
        existing_dirs = [d for d in target_dirs if os.path.exists(d) and os.path.isdir(d)]
        print(f"Hide&Seek: Found {len(existing_dirs)} existing directories: {[os.path.basename(d) for d in existing_dirs]}")
        
        if not existing_dirs:
            # Fallback to desktop hiding if no directories found
            print("Hide&Seek: No user directories found, falling back to desktop hiding")
            self.hide_on_desktop()
            return
        
        # Choose a random directory
        chosen_dir = random.choice(existing_dirs)
        
        # Get all subdirectories (including the chosen directory itself)
        all_dirs = [chosen_dir]
        try:
            for root, dirs, files in os.walk(chosen_dir):
                for d in dirs:
                    full_path = os.path.join(root, d)
                    if os.path.exists(full_path):
                        all_dirs.append(full_path)
                # Limit to prevent excessive searching
                if len(all_dirs) > 50:
                    break
        except (PermissionError, OSError):
            # If we can't access subdirectories, just use the main directory
            pass
        
        # Choose a random directory from all available
        final_dir = random.choice(all_dirs)
        print(f"Hide&Seek: Selected directory: {final_dir}")
        print(f"Hide&Seek: Total directories found: {len(all_dirs)}")
        
        # Calculate position based on directory path hash for consistency
        # This ensures Clover appears in a predictable location relative to the directory
        dir_hash = hash(final_dir) % 1000
        screen = QApplication.primaryScreen().geometry()
        
        # Use hash to determine position within screen bounds
        x = (dir_hash % (screen.width() - 200)) + 100
        y = ((dir_hash // 10) % (screen.height() - 200)) + 100
        
        self.hide_seek_position = (x, y)
        print(f"Hide&Seek: Calculated position: ({x}, {y})")
        
        # Make Clover smaller and move to calculated position
        self.change_size(0.7)  # Medium size
        self.move(self.hide_seek_position[0], self.hide_seek_position[1])
        self.start_animation('sitting_spr_clover_sit_dark', loop=True)
        
        # Store the directory for reference
        self.hide_seek_directory = final_dir
        dir_name = os.path.basename(final_dir) if final_dir != chosen_dir else os.path.basename(chosen_dir)
        print(f"Hide&Seek: Clover is hiding somewhere related to: {dir_name}")
    
    def start_visual_detection(self):
        """Set up visual detection for when player clicks on Clover."""
        print("Hide&Seek: Visual detection started - click on Clover to find him!")
        
        # Enable mouse events for Clover
        self.setMouseTracking(True)
        
        # Set up a timer for auto-discovery as last resort (5 minutes)
        if not hasattr(self, 'hide_seek_detection_timer'):
            self.hide_seek_detection_timer = QTimer()
            self.hide_seek_detection_timer.timeout.connect(self.check_visual_timeout)
        
        self.hide_seek_start_time = time.time()
        self.hide_seek_detection_timer.start(5000)  # Check every 5 seconds
    
    def check_visual_timeout(self):
        """Check if enough time has passed for auto-discovery (last resort)."""
        elapsed = time.time() - self.hide_seek_start_time
        if elapsed > 300:  # Auto-find after 5 minutes (last resort)
            print("Hide&Seek: Auto-discovery timeout (5 min) - Clover found!")
            self.on_clover_found()
    
    # Old file-based detection methods removed - now using visual click detection
    
    def on_clover_found(self):
        """Called when Clover is found - start celebration."""
        self.hide_seek_phase = 'found'
        
        # Stop detection timer
        if hasattr(self, 'hide_seek_detection_timer'):
            self.hide_seek_detection_timer.stop()
        
        # Make Clover visible again
        self.setVisible(True)
        
        # Move to center of screen for celebration
        screen = QApplication.primaryScreen().geometry()
        center_x = screen.width() // 2 - self.width() // 2
        center_y = screen.height() // 2 - self.height() // 2
        self.move(center_x, center_y)
        
        # Start dancing celebration
        self.start_hide_seek_celebration()
    
    def start_hide_seek_celebration(self):
        """Start the victory dance celebration."""
        # Start dance animation
        dance_animations = self.animation_loader.get_animations_by_category('dancing!')
        if dance_animations:
            self.start_animation(dance_animations[0], loop=True)
            
            # Dance for 5 seconds then return to normal
            QTimer.singleShot(5000, self.end_hide_seek_sequence)
        else:
            # Fallback to normal ending
            self.end_hide_seek_sequence()
    
    def end_hide_seek_sequence(self):
        """End the Hide and Seek sequence and return to normal behavior."""
        print("Hide&Seek: Ending sequence and cleaning up")
        
        # Stop any movement timers
        if hasattr(self, 'hide_seek_movement_timer'):
            self.hide_seek_movement_timer.stop()
        if hasattr(self, 'hide_seek_detection_timer'):
            self.hide_seek_detection_timer.stop()
        
        self.is_character_interaction = False
        self.in_hide_seek_sequence = False
        self.hide_seek_phase = None
        
        # Restore original size if it was changed during hiding
        if hasattr(self, 'original_scale_before_hiding'):
            self.change_size(self.original_scale_before_hiding)
            delattr(self, 'original_scale_before_hiding')
        
        # Make sure Clover is visible
        self.setVisible(True)
        
        # Re-enable AFK mode and restart behaviors
        if config.get_setting('flags', 'had_afk_mode_enabled', True) is True:
            self.re_enable_afk_mode()
        
        # Return to idle animation
        sitting_animations = self.animation_loader.get_animations_by_category('sitting')
        if sitting_animations:
            self.start_animation(sitting_animations[0])
        
        # Make the mascot can make a game again    
        config.update_setting('flags', 'mascot_in_game', False)

    # cleanup_hidden_file method removed - no longer needed with visual detection
    
    def start_showdown_sequence(self):
        # Check if is not already in a game
        if config.get_setting('flags', 'mascot_in_game', True) is False:
            
            """Start the Showdown minigame sequence."""
            config.update_setting('flags', 'mascot_in_game', True)
            
            # Register as user interaction to prevent interruptions
            self.logic.on_user_interaction()
        
            # Temporarily disable AFK mode during minigame
            if config.get_setting('afk_behavior', 'afk_mode_enabled', True) is True:
                self.disable_afk_mode_temporarily()
        
            # Size is preserved during showdown minigame
            self.showdown_original_size = self.size()
            # Stop all timers and set interaction state
            self.idle_timer.stop()
            self.animation_timer.stop()
            if hasattr(self, 'zzz_timer'):
                self.zzz_timer.stop()
        
            self.is_character_interaction = True
            self.in_showdown_sequence = True
            self.showdown_phase = 'summon'  # Track current phase: summon, shooting
        
            # Initialize bullet tracking lists
            self.showdown_heart_bullets = []
            self.showdown_strong_bullets = []
        
            # Move to bottom center of screen for dramatic effect
            screen = QApplication.primaryScreen().geometry()
            center_x = screen.width() // 2 - self.width() // 2
            bottom_y = screen.height() - self.height() - 50  # 50px margin from bottom
            self.move(center_x, bottom_y)
        
            # Start with gun summoning animation
            self.start_showdown_summon_phase()
    
    def start_showdown_summon_phase(self):
        """Phase 1: Clover summons the gun."""
        self.showdown_phase = 'summon'
        
        # Start gun summoning animation
        summon_animation = 'gun_spr_clover_geno_summon'
        if self.animation_loader.animation_exists(summon_animation):
            self.start_animation(summon_animation, loop=False)
            
            # Calculate duration to reach last frame and stay there
            animation_info = self.animation_loader.get_animation_info(summon_animation)
            if animation_info:
                duration = animation_info['frame_count'] * animation_info['frame_rate']
            else:
                duration = 3000  # Fallback duration
            
            # After animation completes, stay on last frame and start shooting
            QTimer.singleShot(int(duration), self.hold_summon_last_frame)
        else:
            print(f"Animation not found: {summon_animation}")
            # Fallback to shooting phase
            self.start_showdown_shooting_phase()
    
    def hold_summon_last_frame(self):
        """Hold Clover on the last frame of summoning animation and start shooting."""
        # Get the summoning animation and set to last frame
        summon_animation = 'gun_spr_clover_geno_summon'
        animation = self.animation_loader.get_animation(summon_animation)
        if animation and animation['frames']:
            # Set to last frame (frame 23, index 23)
            self.current_frame = len(animation['frames']) - 1
            self.animation_timer.stop()  # Stop animation timer to hold frame
            self.update_sprite()  # Update to show last frame
            print(f"Showdown: Holding on last frame ({self.current_frame})")
        
        # Start shooting phase
        self.start_showdown_shooting_phase()
    
    def start_showdown_shooting_phase(self):
        """Phase 2: Clover starts shooting with heart bullets towards mouse."""
        self.showdown_phase = 'shooting'
        
        # Initialize shooting variables
        self.showdown_heart_bullets = []  # List to track active bullets
        self.showdown_shooting_timer = QTimer()
        
        # Initialize difficulty progression variables
        self.showdown_base_shooting_interval = 600  # Base shooting interval in ms
        self.showdown_base_sliding_interval = 50   # Base sliding update interval in ms
        self.showdown_base_slide_speed = 3          # Base sliding speed in pixels
        self.showdown_speed_multiplier = 1          # Current speed multiplier
        
        # Initialize difficulty progression timer (every 10 seconds)
        self.showdown_difficulty_timer = QTimer()
        self.showdown_difficulty_timer.timeout.connect(self.increase_showdown_difficulty)
        self.showdown_difficulty_timer.start(10000)  # 10 seconds
        
        # Initialize sliding variables
        self.showdown_sliding_timer = QTimer()
        self.showdown_sliding_timer.timeout.connect(self.update_clover_sliding)
        self.showdown_sliding_timer.start(self.showdown_base_sliding_interval)
        
        # Start continuous shooting sequence
        self.showdown_shooting_timer.timeout.connect(self.fire_showdown_shot)
        self.showdown_shooting_timer.start(self.showdown_base_shooting_interval)
        
        print("Showdown: Started continuous shooting and sliding towards mouse cursor")
    
    def increase_showdown_difficulty(self):
        """Double the laser firing rate and sliding speed every 10 seconds."""
        if self.showdown_phase != 'shooting':
            return
            
        # Double the speed multiplier
        self.showdown_speed_multiplier *= 2
        
        # Calculate new intervals (faster = smaller interval)
        new_shooting_interval = max(50, self.showdown_base_shooting_interval // self.showdown_speed_multiplier)
        new_sliding_interval = max(10, self.showdown_base_sliding_interval // self.showdown_speed_multiplier)
        
        # Restart timers with new intervals
        self.showdown_shooting_timer.stop()
        self.showdown_shooting_timer.start(new_shooting_interval)
        
        self.showdown_sliding_timer.stop()
        self.showdown_sliding_timer.start(new_sliding_interval)
        
        print(f"Showdown: Difficulty increased! Speed multiplier: {self.showdown_speed_multiplier}x")
        print(f"Showdown: New shooting interval: {new_shooting_interval}ms, sliding interval: {new_sliding_interval}ms")
        
        # Start strong shots when reaching 4x speed
        if self.showdown_speed_multiplier >= 4 and not hasattr(self, 'showdown_strong_shot_timer'):
            self.start_strong_shots()
        elif hasattr(self, 'showdown_strong_shot_timer') and self.showdown_strong_shot_timer:
            # Double strong shot speed every 10 seconds after 4x
            self.showdown_strong_shot_speed_multiplier *= 2
            new_strong_interval = max(100, self.showdown_base_strong_interval // self.showdown_strong_shot_speed_multiplier)
            self.showdown_strong_shot_timer.stop()
            self.showdown_strong_shot_timer.start(new_strong_interval)
            print(f"Showdown: Strong shot speed increased! Multiplier: {self.showdown_strong_shot_speed_multiplier}x")
    
    def update_clover_sliding(self):
        """Update Clover's position to slide towards mouse cursor horizontally."""
        if self.showdown_phase != 'shooting':
            return
            
        # Get current mouse position
        mouse_pos = QCursor.pos()
        
        # Calculate target X position (center Clover under mouse)
        target_x = mouse_pos.x() - self.width() // 2
        current_x = self.x()
        
        # Calculate sliding speed (slower than mouse movement, affected by difficulty multiplier)
        distance = target_x - current_x
        slide_speed = self.showdown_base_slide_speed * self.showdown_speed_multiplier
        
        # Move towards target with sliding effect
        if abs(distance) > slide_speed:
            if distance > 0:
                new_x = current_x + slide_speed
            else:
                new_x = current_x - slide_speed
        else:
            new_x = target_x  # Snap to target if very close
        
        # Keep Clover within screen bounds
        screen = QApplication.primaryScreen().geometry()
        new_x = max(0, min(new_x, screen.width() - self.width()))
        
        # Update position (keep Y at bottom)
        self.move(new_x, self.y())
    
    def fire_showdown_shot(self):
        """Fire a single shot towards the mouse cursor."""
        # Get current mouse position
        mouse_pos = QCursor.pos()
        
        # Create heart bullet sprite above Clover
        heart_bullet = self.create_heart_bullet(mouse_pos)
        if heart_bullet:
            self.showdown_heart_bullets.append(heart_bullet)
        
        print(f"Showdown: Fired shot towards mouse at ({mouse_pos.x()}, {mouse_pos.y()})")
        
        # Clean up old bullets that are no longer active
        self.showdown_heart_bullets = [bullet for bullet in self.showdown_heart_bullets if bullet and not bullet.isHidden()]
    
    def create_heart_bullet(self, target_pos):
        """Create a heart bullet sprite that appears above Clover and moves towards target."""
        # Get heart bullet animation
        heart_animation = 'gun_spr_heart_yellow_shot'
        if not self.animation_loader.animation_exists(heart_animation):
            print(f"Heart bullet animation not found: {heart_animation}")
            return None
        
        # Get current scale for bullet scaling
        current_scale = config.get_setting('size', 'current_scale', 1.0)
        
        # Create a new QLabel for the heart bullet
        heart_bullet = QLabel()
        heart_bullet.setParent(None)  # Make it a top-level widget
        heart_bullet.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        heart_bullet.setAttribute(Qt.WA_TranslucentBackground)
        
        # Get first frame of heart animation and apply scaling
        animation_data = self.animation_loader.get_animation(heart_animation)
        if animation_data and animation_data['frames']:
            first_frame = animation_data['frames'][0]
            # Scale the bullet sprite to match Clover's size
            if current_scale != 1.0:
                scaled_size = first_frame.size() * current_scale
                first_frame = first_frame.scaled(scaled_size, Qt.KeepAspectRatio, Qt.FastTransformation)
            heart_bullet.setPixmap(first_frame)
            heart_bullet.resize(first_frame.size())
        
        # Position heart bullet above Clover (scaled offset)
        scaled_offset = int(30 * current_scale)  # Scale the vertical offset
        clover_x = self.x() + self.width() // 2
        clover_y = self.y() - scaled_offset  # Above Clover
        heart_bullet.move(clover_x - heart_bullet.width() // 2, clover_y)
        
        # Store target position and scale for movement
        heart_bullet.target_x = target_pos.x()
        heart_bullet.target_y = target_pos.y()
        heart_bullet.bullet_scale = current_scale  # Store scale for animation
        
        # Initialize animation frame and tracking
        heart_bullet.animation_frame = 0
        heart_bullet.animation_complete = False
        
        # Show the heart bullet
        heart_bullet.show()
        
        # Animate the heart bullet towards target
        self.animate_heart_bullet(heart_bullet)
        
        return heart_bullet
    
    def animate_heart_bullet(self, heart_bullet):
        """Animate a heart bullet moving towards target and detect mouse hits."""
        # Set up animation variables
        heart_bullet.animation_frame = 0
        heart_bullet.move_distance = 0
        
        # Get animation data
        heart_animation = 'gun_spr_heart_yellow_shot'
        animation_data = self.animation_loader.get_animation(heart_animation)
        
        # Calculate movement direction
        start_x = heart_bullet.x()
        start_y = heart_bullet.y()
        target_x = heart_bullet.target_x
        target_y = heart_bullet.target_y
        
        dx = target_x - start_x
        dy = target_y - start_y
        distance = (dx**2 + dy**2)**0.5
        
        if distance == 0:
            return  # No movement needed
        
        # Normalize direction and set speed (scaled with bullet size and showdown speed)
        base_speed = 8  # base pixels per update
        bullet_scale = getattr(heart_bullet, 'bullet_scale', 1.0)
        showdown_speed_multiplier = getattr(self, 'showdown_speed_multiplier', 1.0)
        speed = base_speed * bullet_scale * showdown_speed_multiplier  # Scale speed with bullet size and showdown speed
        move_x = (dx / distance) * speed
        move_y = (dy / distance) * speed
        
        # Create timer for bullet animation and store it on the bullet object
        bullet_timer = QTimer()
        heart_bullet.bullet_timer = bullet_timer  # Store timer for cleanup
        
        def update_bullet():
            try:
                if not heart_bullet or heart_bullet.isHidden():
                    bullet_timer.stop()
                    return
                
                # Update animation frame (play once, then stay on last frame)
                if animation_data and animation_data['frames'] and not heart_bullet.animation_complete:
                    frames = animation_data['frames']
                    heart_bullet.animation_frame += 1
                    if heart_bullet.animation_frame >= len(frames):
                        heart_bullet.animation_frame = len(frames) - 1  # Stay on last frame
                        heart_bullet.animation_complete = True
                    
                    # Apply scaling to animation frames
                    frame = frames[heart_bullet.animation_frame]
                    if bullet_scale != 1.0:
                        scaled_size = frame.size() * bullet_scale
                        frame = frame.scaled(scaled_size, Qt.KeepAspectRatio, Qt.FastTransformation)
                    heart_bullet.setPixmap(frame)
                
                # Move bullet towards target
                current_pos = heart_bullet.pos()
                new_x = current_pos.x() + move_x
                new_y = current_pos.y() + move_y
                heart_bullet.move(int(new_x), int(new_y))
                heart_bullet.move_distance += speed
                
                # Check if bullet hit the mouse cursor (within 30 pixel radius)
                current_mouse_pos = QCursor.pos()
                bullet_center_x = heart_bullet.x() + heart_bullet.width() // 2
                bullet_center_y = heart_bullet.y() + heart_bullet.height() // 2
                
                hit_distance = ((bullet_center_x - current_mouse_pos.x())**2 + 
                               (bullet_center_y - current_mouse_pos.y())**2)**0.5
                
                # Use a fixed base hit radius that doesn't scale with bullet size
                # This ensures consistent hit detection regardless of Clover's size
                hit_radius = 30  # Fixed radius for consistent gameplay
                if hit_distance <= hit_radius:  # Hit detected!
                    print("Showdown: Heart bullet hit the mouse! You win!")
                    bullet_timer.stop()
                    # Remove from tracking list first
                    if heart_bullet in self.showdown_heart_bullets:
                        self.showdown_heart_bullets.remove(heart_bullet)
                    heart_bullet.hide()
                    heart_bullet.deleteLater()
                    # Start victory sequence with unsummon animation
                    self.start_showdown_victory_sequence()
                    return
                
                # Remove bullet if it's moved too far or off screen (scaled distance)
                max_distance = 1000 * bullet_scale
                screen = QApplication.primaryScreen().geometry()
                if (heart_bullet.move_distance > max_distance or 
                    new_x < -100 or new_x > screen.width() + 100 or
                    new_y < -100 or new_y > screen.height() + 100):
                    bullet_timer.stop()
                    # Remove from tracking list first
                    if heart_bullet in self.showdown_heart_bullets:
                        self.showdown_heart_bullets.remove(heart_bullet)
                    heart_bullet.hide()
                    heart_bullet.deleteLater()
            except RuntimeError:
                # Object has been deleted, stop timer
                bullet_timer.stop()
                return
        
        bullet_timer.timeout.connect(update_bullet)
        bullet_timer.start(30)  # Update every 30ms for smooth movement
    
    def start_strong_shots(self):
        """Initialize strong shot system when reaching 8x speed."""
        print("Showdown: Starting strong shots at 8x speed!")
        
        # Initialize strong shot variables
        self.showdown_strong_bullets = []  # List to track active strong bullets
        self.showdown_base_strong_interval = 800  # Base strong shot interval in ms
        self.showdown_strong_shot_speed_multiplier = 1  # Strong shot speed multiplier
        
        # Start strong shot timer
        self.showdown_strong_shot_timer = QTimer()
        self.showdown_strong_shot_timer.timeout.connect(self.fire_strong_shot)
        self.showdown_strong_shot_timer.start(self.showdown_base_strong_interval)
    
    def fire_strong_shot(self):
        """Fire a strong shot towards the current mouse position."""
        if self.showdown_phase != 'shooting':
            return
            
        # Get current mouse position
        mouse_pos = QCursor.pos()
        print(f"Showdown: Fired strong shot towards mouse at ({mouse_pos.x()}, {mouse_pos.y()})")
        
        # Create and track the strong bullet
        strong_bullet = self.create_strong_bullet(mouse_pos)
        if strong_bullet:
            self.showdown_strong_bullets.append(strong_bullet)
    
    def create_strong_bullet(self, target_pos):
        """Create a strong bullet widget that appears directly over the mouse position."""
        # Create QLabel for strong bullet
        strong_bullet = QLabel()
        strong_bullet.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        strong_bullet.setAttribute(Qt.WA_TranslucentBackground)
        
        # Get current scale for bullet scaling
        current_scale = config.get_setting('size', 'current_scale', 1.0)
        
        # Get first frame of strong shot animation and apply scaling
        strong_animation = 'gun_spr_shot_strong'
        animation_data = self.animation_loader.get_animation(strong_animation)
        if animation_data and animation_data['frames']:
            first_frame = animation_data['frames'][0]
            # Scale the bullet sprite to match Clover's size
            if current_scale != 1.0:
                scaled_size = first_frame.size() * current_scale
                first_frame = first_frame.scaled(scaled_size, Qt.KeepAspectRatio, Qt.FastTransformation)
            strong_bullet.setPixmap(first_frame)
            strong_bullet.resize(first_frame.size())
        
        # Position strong bullet directly over the mouse position
        mouse_x = target_pos.x()
        mouse_y = target_pos.y()
        strong_bullet.move(mouse_x - strong_bullet.width() // 2, mouse_y - strong_bullet.height() // 2)
        
        # Store scale for animation
        strong_bullet.bullet_scale = current_scale
        
        # Initialize animation frame and tracking
        strong_bullet.animation_frame = 0
        strong_bullet.animation_complete = False
        
        # Show the strong bullet
        strong_bullet.show()
        
        # Animate the strong bullet in place
        self.animate_strong_bullet(strong_bullet)
        
        return strong_bullet
    
    def animate_strong_bullet(self, strong_bullet):
        """Animate a strong bullet in place and detect mouse hits when animation completes."""
        # Set up animation variables
        strong_bullet.animation_frame = 0
        
        # Get animation data
        strong_animation = 'gun_spr_shot_strong'
        animation_data = self.animation_loader.get_animation(strong_animation)
        
        # Create timer for bullet animation and store it on the bullet object
        bullet_timer = QTimer()
        strong_bullet.bullet_timer = bullet_timer  # Store timer for cleanup
        
        def update_strong_bullet():
            try:
                if not strong_bullet or strong_bullet.isHidden():
                    bullet_timer.stop()
                    return
                
                # Update animation frame (play once, then check for mouse hit when complete)
                if animation_data and animation_data['frames']:
                    frames = animation_data['frames']
                    
                    if not strong_bullet.animation_complete:
                        strong_bullet.animation_frame += 1
                        if strong_bullet.animation_frame >= len(frames):
                            # Animation complete
                            strong_bullet.animation_frame = len(frames) - 1  # Stay on last frame
                            strong_bullet.animation_complete = True
                            
                            # Check if mouse is over the animation when it completes
                            current_mouse_pos = QCursor.pos()
                            bullet_center_x = strong_bullet.x() + strong_bullet.width() // 2
                            bullet_center_y = strong_bullet.y() + strong_bullet.height() // 2
                            
                            hit_distance = ((bullet_center_x - current_mouse_pos.x())**2 + 
                                          (bullet_center_y - current_mouse_pos.y())**2)**0.5
                            
                            # Use a fixed hit radius for consistent gameplay
                            hit_radius = 30  # Fixed radius for consistent gameplay
                            if hit_distance <= hit_radius:  # Hit detected!
                                print("Showdown: Mouse was over strong shot when animation completed! You lose!")
                                bullet_timer.stop()
                                # Remove from tracking list first
                                if strong_bullet in self.showdown_strong_bullets:
                                    self.showdown_strong_bullets.remove(strong_bullet)
                                strong_bullet.hide()
                                strong_bullet.deleteLater()
                                # Start defeat sequence
                                self.start_showdown_defeat_sequence()
                                return
                            else:
                                # Animation completed but mouse wasn't over it, remove after a short delay
                                QTimer.singleShot(500, lambda: self.remove_strong_bullet(strong_bullet, bullet_timer))
                                return
                    
                    # Apply scaling to animation frames
                    bullet_scale = getattr(strong_bullet, 'bullet_scale', 1.0)
                    frame = frames[strong_bullet.animation_frame]
                    if bullet_scale != 1.0:
                        scaled_size = frame.size() * bullet_scale
                        frame = frame.scaled(scaled_size, Qt.KeepAspectRatio, Qt.FastTransformation)
                    strong_bullet.setPixmap(frame)
                    
            except RuntimeError:
                # Object has been deleted, stop timer
                bullet_timer.stop()
                return
        
        bullet_timer.timeout.connect(update_strong_bullet)
        # Animation speed based on strong shot multiplier
        speed_multiplier = getattr(self, 'showdown_strong_shot_speed_multiplier', 1)
        animation_interval = max(25, 50 // speed_multiplier)  # Faster animation with higher multiplier
        bullet_timer.start(animation_interval)
    
    def remove_strong_bullet(self, strong_bullet, bullet_timer=None):
        """Remove a strong bullet after animation completes."""
        if strong_bullet:
            try:
                # Stop the bullet timer if it exists on the bullet object
                if hasattr(strong_bullet, 'bullet_timer'):
                    strong_bullet.bullet_timer.stop()
                # Also stop the passed timer for backward compatibility
                if bullet_timer and bullet_timer.isActive():
                    bullet_timer.stop()
                
                # Remove from tracking list first
                if hasattr(self, 'showdown_strong_bullets') and strong_bullet in self.showdown_strong_bullets:
                    self.showdown_strong_bullets.remove(strong_bullet)
                strong_bullet.hide()
                strong_bullet.deleteLater()
            except RuntimeError as e:
                # Handle case where QLabel has already been deleted
                print(f"Warning: Strong bullet QLabel already deleted: {e}")
                # Still try to remove from tracking list if possible
                if hasattr(self, 'showdown_strong_bullets') and strong_bullet in self.showdown_strong_bullets:
                    try:
                        self.showdown_strong_bullets.remove(strong_bullet)
                    except (ValueError, RuntimeError):
                        pass
    
    def start_showdown_defeat_sequence(self):
        """Handle defeat when hit by a strong shot."""
        print("Showdown: Player defeated by strong shot!")
        
        # Stop all showdown timers
        if hasattr(self, 'showdown_shooting_timer'):
            self.showdown_shooting_timer.stop()
        if hasattr(self, 'showdown_sliding_timer'):
            self.showdown_sliding_timer.stop()
        if hasattr(self, 'showdown_difficulty_timer'):
            self.showdown_difficulty_timer.stop()
        if hasattr(self, 'showdown_strong_shot_timer'):
            self.showdown_strong_shot_timer.stop()
        
        # Clean up all bullets
        for heart_bullet in self.showdown_heart_bullets:
            if heart_bullet:
                try:
                    # Stop the bullet timer if it exists
                    if hasattr(heart_bullet, 'bullet_timer'):
                        heart_bullet.bullet_timer.stop()
                    heart_bullet.hide()
                    heart_bullet.deleteLater()
                except RuntimeError as e:
                    # Handle case where QLabel has already been deleted
                    print(f"Warning: Heart bullet QLabel already deleted: {e}")
        self.showdown_heart_bullets.clear()
        
        for strong_bullet in getattr(self, 'showdown_strong_bullets', []):
            if strong_bullet:
                try:
                    strong_bullet.hide()
                    strong_bullet.deleteLater()
                except RuntimeError as e:
                    # Handle case where QLabel has already been deleted
                    print(f"Warning: Strong bullet QLabel already deleted: {e}")
        if hasattr(self, 'showdown_strong_bullets'):
            self.showdown_strong_bullets.clear()
        
        # Start unsummon animation before ending
        self.showdown_phase = 'defeat_unsummon'
        print("Showdown: Attempting to start defeat unsummon animation...")
        
        # Try to find and start unsummon animation
        all_animations = self.animation_loader.get_all_animations()
        unsummon_animations = [name for name in all_animations if 'unsummon' in name.lower()]
        print(f"Showdown: Available unsummon animations: {unsummon_animations}")
        
        # Try different possible names for the unsummon animation
        possible_names = ['spr_clover_geno_unsummon', 'gun_spr_clover_geno_unsummon', 'geno_spr_clover_geno_unsummon']
        unsummon_started = False
        
        for anim_name in possible_names:
            if self.animation_loader.animation_exists(anim_name):
                print(f"Showdown: Found unsummon animation: {anim_name}")
                self.start_animation(anim_name, loop=False)
                unsummon_started = True
                break
        
        if unsummon_started:
            # Set timer to end showdown after unsummon animation completes
            # Use the animation name that was actually found
            found_anim_name = None
            for anim_name in possible_names:
                if self.animation_loader.animation_exists(anim_name):
                    found_anim_name = anim_name
                    break
            
            if found_anim_name:
                unsummon_info = self.animation_loader.get_animation_info(found_anim_name)
                if unsummon_info:
                    unsummon_duration = unsummon_info['frame_count'] * unsummon_info['frame_rate']
                    print(f"Showdown: Defeat unsummon duration calculated: {unsummon_duration}ms")
                else:
                    unsummon_duration = 2000  # Fallback duration if animation not found
            else:
                unsummon_duration = 2000  # Fallback duration if animation not found
        else:
            print("Showdown: Defeat unsummon animation not found, ending immediately")
            unsummon_duration = 100  # Very short delay before ending
        
        # Create timer to end showdown after unsummon completes
        if not hasattr(self, 'defeat_transition_timer'):
            self.defeat_transition_timer = QTimer()
            self.defeat_transition_timer.setSingleShot(True)
            self.defeat_transition_timer.timeout.connect(self.end_showdown_sequence)
        
        self.defeat_transition_timer.start(unsummon_duration)
    
    def start_showdown_victory_sequence(self):
        """Start the victory sequence with unsummon animation followed by dancing."""
        print("Showdown: Starting victory sequence with unsummon animation")
        
        # Stop all showdown timers first
        if hasattr(self, 'showdown_shooting_timer'):
            self.showdown_shooting_timer.stop()
        if hasattr(self, 'showdown_sliding_timer'):
            self.showdown_sliding_timer.stop()
        if hasattr(self, 'showdown_difficulty_timer'):
            self.showdown_difficulty_timer.stop()
        
        # Clean up any remaining heart bullets
        for heart_bullet in self.showdown_heart_bullets:
            if heart_bullet:
                try:
                    heart_bullet.hide()
                    heart_bullet.deleteLater()
                except RuntimeError as e:
                    # Handle case where QLabel has already been deleted
                    print(f"Warning: Heart bullet QLabel already deleted: {e}")
        self.showdown_heart_bullets.clear()
        
        # Start unsummon animation
        self.showdown_phase = 'victory_unsummon'
        print("Showdown: Attempting to start unsummon animation...")
        
        # Debug: Print all available animations to find the correct name
        all_animations = self.animation_loader.get_all_animations()
        unsummon_animations = [name for name in all_animations if 'unsummon' in name.lower()]
        print(f"Showdown: Available unsummon animations: {unsummon_animations}")
        
        # Try different possible animation names
        possible_names = ['spr_clover_geno_unsummon', 'gun_spr_clover_geno_unsummon', 'geno_spr_clover_geno_unsummon']
        animation_found = False
        
        for anim_name in possible_names:
            if self.animation_loader.animation_exists(anim_name):
                print(f"Showdown: Found unsummon animation: {anim_name}")
                self.start_animation(anim_name, loop=False)
                animation_found = True
                break
        
        if animation_found:
            # Set timer to transition to dancing after unsummon animation completes
            # Use the animation name that was actually found
            found_anim_name = None
            for anim_name in possible_names:
                if self.animation_loader.animation_exists(anim_name):
                    found_anim_name = anim_name
                    break
            
            if found_anim_name:
                unsummon_info = self.animation_loader.get_animation_info(found_anim_name)
                if unsummon_info:
                    unsummon_duration = unsummon_info['frame_count'] * unsummon_info['frame_rate']
                    print(f"Showdown: Unsummon duration calculated: {unsummon_duration}ms")
                else:
                    unsummon_duration = 2000  # Fallback duration if animation not found
            else:
                unsummon_duration = 2000  # Fallback duration if animation not found
                print("Showdown: Using fallback duration: 2000ms")
        else:
            print("Showdown: Unsummon animation not found, skipping to dance")
            unsummon_duration = 100  # Very short delay before dancing
            
        self.victory_transition_timer = QTimer()
        self.victory_transition_timer.timeout.connect(self.start_victory_dance)
        self.victory_transition_timer.setSingleShot(True)
        self.victory_transition_timer.start(unsummon_duration)
    
    def start_victory_dance(self):
        """Start the victory dance animation after unsummon completes."""
        print("Showdown: Starting victory dance!")
        
        # Start dancing animation
        dance_animations = self.animation_loader.get_animations_by_category('dancing!')
        if dance_animations:
            self.start_animation(dance_animations[0], loop=True)
        
        # Set timer to end the victory sequence after dancing for a while
        self.victory_dance_timer = QTimer()
        self.victory_dance_timer.timeout.connect(self.end_showdown_sequence)
        self.victory_dance_timer.setSingleShot(True)
        self.victory_dance_timer.start(3000)  # Dance for 3 seconds
    
    def end_showdown_sequence(self):
        """End the Showdown sequence and return to normal behavior."""
        print("Showdown: Ending sequence and cleaning up")
        
        # Stop shooting timer
        if hasattr(self, 'showdown_shooting_timer'):
            self.showdown_shooting_timer.stop()
        
        # Stop sliding timer
        if hasattr(self, 'showdown_sliding_timer'):
            self.showdown_sliding_timer.stop()
        
        # Stop difficulty progression timer
        if hasattr(self, 'showdown_difficulty_timer'):
            self.showdown_difficulty_timer.stop()
        
        # Stop strong shot timer
        if hasattr(self, 'showdown_strong_shot_timer'):
            self.showdown_strong_shot_timer.stop()
        
        # Stop victory sequence timers
        if hasattr(self, 'victory_transition_timer'):
            self.victory_transition_timer.stop()
        if hasattr(self, 'victory_dance_timer'):
            self.victory_dance_timer.stop()
        
        # Clean up any remaining heart bullets
        for heart_bullet in self.showdown_heart_bullets:
            if heart_bullet:
                try:
                    # Stop the bullet timer if it exists
                    if hasattr(heart_bullet, 'bullet_timer'):
                        heart_bullet.bullet_timer.stop()
                    heart_bullet.hide()
                    heart_bullet.deleteLater()
                except RuntimeError as e:
                    # Handle case where QLabel has already been deleted
                    print(f"Warning: Heart bullet QLabel already deleted: {e}")
        self.showdown_heart_bullets.clear()
        
        # Clean up any remaining strong bullets
        for strong_bullet in getattr(self, 'showdown_strong_bullets', []):
            if strong_bullet:
                try:
                    # Stop the bullet timer if it exists
                    if hasattr(strong_bullet, 'bullet_timer'):
                        strong_bullet.bullet_timer.stop()
                    strong_bullet.hide()
                    strong_bullet.deleteLater()
                except RuntimeError as e:
                    # Handle case where QLabel has already been deleted
                    print(f"Warning: Strong bullet QLabel already deleted: {e}")
        if hasattr(self, 'showdown_strong_bullets'):
            self.showdown_strong_bullets.clear()
        
        # Reset state
        self.is_character_interaction = False
        self.in_showdown_sequence = False
        self.showdown_phase = None
        
        # Reset speed multipliers and base intervals to prevent stacking between showdowns
        if hasattr(self, 'showdown_speed_multiplier'):
            self.showdown_speed_multiplier = 1
        if hasattr(self, 'showdown_strong_shot_speed_multiplier'):
            self.showdown_strong_shot_speed_multiplier = 1
        if hasattr(self, 'showdown_base_shooting_interval'):
            self.showdown_base_shooting_interval = 600
        if hasattr(self, 'showdown_base_sliding_interval'):
            self.showdown_base_sliding_interval = 50
        if hasattr(self, 'showdown_base_slide_speed'):
            self.showdown_base_slide_speed = 3
        if hasattr(self, 'showdown_base_strong_interval'):
            self.showdown_base_strong_interval = 800
        
        # Re-enable AFK mode and restart behaviors
        if config.get_setting('flags', 'had_afk_mode_enabled', True) is True:
            self.re_enable_afk_mode()
        
        # Return to idle animation
        sitting_animations = self.animation_loader.get_animations_by_category('sitting')
        if sitting_animations:
            self.start_animation(sitting_animations[0])
            
        # Make the mascot can make a game again
        config.update_setting('flags', 'mascot_in_game', False)
    
    def start_next_edward_animation(self):
        """Start the next animation in the Edward Walking sequence."""
        if self.edward_sequence_index < len(self.edward_sequence):
            animation_name = self.edward_sequence[self.edward_sequence_index]
            
            # Check if animation exists
            if self.animation_loader.animation_exists(animation_name):
                # Mark that we're in Edward sequence to prevent logic interference
                self.in_edward_sequence = True
                
                # Start the animation (don't loop for sequence)
                self.start_animation(animation_name, loop=False)
                
                # Set up movement for walking animations
                self.setup_edward_movement(animation_name)
                
                # Set up timer to move to next animation when current one finishes
                animation_info = self.animation_loader.get_animation_info(animation_name)
                if animation_info:
                    # Calculate duration based on frame count and frame rate
                    duration = animation_info['frame_count'] * animation_info['frame_rate']
                    
                    # Add some delay between animations
                    if self.edward_sequence_index == 0:  # After grab
                        duration += 500  # Extra pause after grabbing
                    elif self.edward_sequence_index == len(self.edward_sequence) - 1:  # Before place
                        duration += 800  # Longer pause for place animation to complete
                    else:
                        duration += 200  # Short pause between walking animations
                    
                    # Set timer for next animation
                    QTimer.singleShot(int(duration), self.continue_edward_sequence)
                else:
                    # Fallback timing if animation info not available
                    QTimer.singleShot(2000, self.continue_edward_sequence)
            else:
                print(f"Animation not found: {animation_name}")
                self.continue_edward_sequence()
        else:
            # Sequence complete, return to normal behavior
            self.end_edward_sequence()
    
    def setup_edward_movement(self, animation_name):
        """Set up movement for Edward walking animations."""
        # Stop any existing movement timer
        if hasattr(self, 'edward_movement_timer'):
            self.edward_movement_timer.stop()
        
        # Determine movement direction and set up timer
        if 'up_walk' in animation_name:
            self.edward_movement_direction = 'up'
            self.start_edward_movement()
        elif 'right_walk' in animation_name:
            self.edward_movement_direction = 'right'
            self.start_edward_movement()
        elif 'down_walk' in animation_name:
            self.edward_movement_direction = 'down'
            self.start_edward_movement()
        elif 'left_walk' in animation_name:
            self.edward_movement_direction = 'left'
            self.start_edward_movement()
        else:
            # Not a walking animation, no movement needed
            self.edward_movement_direction = None
    
    def start_edward_movement(self):
        """Start the movement timer for Edward walking."""
        if not hasattr(self, 'edward_movement_timer'):
            self.edward_movement_timer = QTimer()
            self.edward_movement_timer.timeout.connect(self.update_edward_position)
        
        self.edward_movement_timer.start(50)  # Update every 50ms for smooth movement
    
    def update_edward_position(self):
        """Update Edward's position during walking animations."""
        if not hasattr(self, 'edward_movement_direction') or self.edward_movement_direction is None:
            return
        
        # Movement speed (pixels per update)
        speed = 4
        current_pos = self.pos()
        
        # Calculate new position based on direction
        if self.edward_movement_direction == 'up':
            new_pos = QPoint(current_pos.x(), current_pos.y() - speed)
        elif self.edward_movement_direction == 'right':
            new_pos = QPoint(current_pos.x() + speed, current_pos.y())
        elif self.edward_movement_direction == 'down':
            new_pos = QPoint(current_pos.x(), current_pos.y() + speed)
        elif self.edward_movement_direction == 'left':
            new_pos = QPoint(current_pos.x() - speed, current_pos.y())
        else:
            return
        
        # Keep within screen bounds
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry()
        
        # Ensure the mascot stays within screen bounds
        if (new_pos.x() >= 0 and new_pos.x() + self.width() <= screen_rect.width() and
            new_pos.y() >= 0 and new_pos.y() + self.height() <= screen_rect.height()):
            self.move(new_pos)
    
    def continue_edward_sequence(self):
        """Continue to the next animation in the Edward sequence."""
        # Stop movement timer when transitioning to next animation
        if hasattr(self, 'edward_movement_timer'):
            self.edward_movement_timer.stop()
        
        self.edward_sequence_index += 1
        self.start_next_edward_animation()
    
    def end_edward_sequence(self):
        """End the Edward Walking sequence and return to normal behavior."""
        # Stop movement timer
        if hasattr(self, 'edward_movement_timer'):
            self.edward_movement_timer.stop()
        
        self.is_character_interaction = False
        self.in_edward_sequence = False  # Clear the flag
        
        # Restart random walking if no other special modes are active
        if (self.logic.random_walking_enabled and not self.logic.eternal_dance_mode and 
            not self.logic.timed_dance_mode and not self.is_sleeping and 
            not self.is_following_mouse and not getattr(self, 'is_falling', False)):
            self.logic.start_random_walking_system()
        
        # Return to idle animation
        sitting_animations = self.animation_loader.get_animations_by_category('sitting')
        if sitting_animations:
            self.start_animation(sitting_animations[0])
        
        # Resume AFK behaviors after Edward sequence completes
        import random
        self.logic.random_walking_timer.start(random.randint(3000, 8000))
    
    def push_windows_in_path(self):
        """Detect and push windows that are in Clover's path during whale mail animation."""
        if not WIN32_AVAILABLE:
            return
        
        try:
            # Get Clover's current position and size
            clover_rect = self.geometry()
            clover_x = clover_rect.x()
            clover_y = clover_rect.y()
            clover_width = clover_rect.width()
            clover_height = clover_rect.height()
            
            # Define the area to check for windows (close to Clover)
            check_margin = -5
            check_left = clover_x - check_margin
            check_right = clover_x + clover_width + check_margin
            check_top = clover_y - check_margin
            check_bottom = clover_y + clover_height + check_margin
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                    # Skip our own window
                    window_title = win32gui.GetWindowText(hwnd)
                    if "Desktop Mascot" in window_title or "Clover" in window_title:
                        return True
                    
                    # Get window position and size
                    try:
                        window_rect = win32gui.GetWindowRect(hwnd)
                        win_left, win_top, win_right, win_bottom = window_rect
                        
                        # Check if window intersects with Clover's path
                        if (win_left < check_right and win_right > check_left and
                            win_top < check_bottom and win_bottom > check_top):
                            
                            # Store original position if not already stored
                            if hwnd not in self.moved_windows:
                                self.moved_windows[hwnd] = (win_left, win_top)
                            
                            # Calculate push distance (move window up by Clover's speed)
                            push_distance = self.whale_speed + 2
                            new_top = win_top - push_distance
                            new_left = win_left
                            
                            # Move the window
                            win32gui.SetWindowPos(
                                hwnd, 0, new_left, new_top, 0, 0,
                                win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
                            )
                    except:
                        # Skip windows that can't be moved
                        pass
                return True
            
            # Enumerate all windows
            win32gui.EnumWindows(enum_windows_callback, [])
            
        except Exception as e:
            # Silently handle any errors to avoid disrupting the animation
            pass
    
    def push_windows_in_cart_path(self):
        """Detect and push windows that are in Clover's path during cart ride animation."""
        if not WIN32_AVAILABLE:
            return
        
        try:
            # Get Clover's current position and size
            clover_rect = self.geometry()
            clover_x = clover_rect.x()
            clover_y = clover_rect.y()
            clover_width = clover_rect.width()
            clover_height = clover_rect.height()
            
            # Define the area to check for windows (close to Clover)
            check_margin = -5
            check_left = clover_x - check_margin
            check_right = clover_x + clover_width + check_margin
            check_top = clover_y - check_margin
            check_bottom = clover_y + clover_height + check_margin
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                    # Skip our own window
                    window_title = win32gui.GetWindowText(hwnd)
                    if "Desktop Mascot" in window_title or "Clover" in window_title:
                        return True
                    
                    # Get window position and size
                    try:
                        window_rect = win32gui.GetWindowRect(hwnd)
                        win_left, win_top, win_right, win_bottom = window_rect
                        
                        # Check if window intersects with Clover's path
                        if (win_left < check_right and win_right > check_left and
                            win_top < check_bottom and win_bottom > check_top):
                            
                            # Store original position if not already stored
                            if hwnd not in self.moved_windows:
                                self.moved_windows[hwnd] = (win_left, win_top)
                            
                            # Calculate push distance (move window right by Clover's speed)
                            push_distance = self.cart_speed + 2
                            new_left = win_left + push_distance
                            new_top = win_top
                            
                            # Move the window
                            win32gui.SetWindowPos(
                                hwnd, 0, new_left, new_top, 0, 0,
                                win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
                            )
                    except:
                        # Skip windows that can't be moved
                        pass
                return True
            
            # Enumerate all windows
            win32gui.EnumWindows(enum_windows_callback, [])
            
        except Exception as e:
            # Silently handle any errors to avoid disrupting the animation
            pass
    
    def restore_moved_windows(self):
        """Restore all moved windows to their original positions."""
        if not WIN32_AVAILABLE or not self.moved_windows:
            return
        
        try:
            for hwnd, (original_x, original_y) in self.moved_windows.items():
                try:
                    # Check if window still exists and is visible
                    if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
                        win32gui.SetWindowPos(
                            hwnd, 0, original_x, original_y, 0, 0,
                            win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
                        )
                except:
                    # Skip windows that can't be moved or no longer exist
                    pass
            
            # Clear the moved windows dictionary
            self.moved_windows = {}
            
        except Exception as e:
            # Silently handle any errors
            pass
    
    def fetch_and_display_meme(self):
        """Fetch a random Undertale Yellow meme from Google Images and display it."""
        try:
            # Start fetching meme in a separate thread to avoid blocking UI
            from PyQt5.QtCore import QThread, QObject, pyqtSignal
            
            class MemeWorker(QObject):
                meme_fetched = pyqtSignal(object)  # Signal to emit the fetched image
                
                def fetch_meme(self):
                    try:
                        # Search for Undertale Yellow memes
                        search_query = "Undertale yellow memes"
                        
                        # Use requests to get Google Images search results
                        import requests
                        from urllib.parse import quote
                        import re
                        
                        # Google Images search URL
                        search_url = f"https://www.google.com/search?q={quote(search_query)}&tbm=isch"
                        
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                        }
                        
                        response = requests.get(search_url, headers=headers, timeout=10)
                        
                        if response.status_code == 200:
                            # Extract image URLs from the HTML
                            img_urls = re.findall(r'"(https://[^"]*\.(?:jpg|jpeg|png|gif))"', response.text)
                            
                            if img_urls:
                                # Filter for reasonable sized images and pick a random one
                                import random
                                selected_url = random.choice(img_urls[:10])  # Use first 10 results
                                
                                # Download the image
                                img_response = requests.get(selected_url, headers=headers, timeout=10)
                                if img_response.status_code == 200:
                                    from PyQt5.QtGui import QPixmap
                                    pixmap = QPixmap()
                                    if pixmap.loadFromData(img_response.content):
                                        # Scale image to reasonable size
                                        if pixmap.width() > 600 or pixmap.height() > 600:
                                            pixmap = pixmap.scaled(600, 600, Qt.KeepAspectRatio, Qt.FastTransformation)
                                        self.meme_fetched.emit(pixmap)
                                        return
                        
                        # If we get here, something failed - emit None to trigger placeholder
                        self.meme_fetched.emit(None)
                        
                    except Exception as e:
                        print(f"Error in meme worker: {e}")
                        self.meme_fetched.emit(None)
            
            # Create worker and thread
            self.meme_worker = MemeWorker()
            self.meme_thread = QThread()
            
            # Move worker to thread
            self.meme_worker.moveToThread(self.meme_thread)
            
            # Connect signals
            self.meme_worker.meme_fetched.connect(self.on_meme_fetched)
            self.meme_thread.started.connect(self.meme_worker.fetch_meme)
            
            # Start the thread
            self.meme_thread.start()
            
        except Exception as e:
            print(f"Error setting up meme fetching: {e}")
            self.display_meme_placeholder()
    
    def display_meme_placeholder(self):
        """Display a placeholder meme image."""
        try:
            # Create meme display label if it doesn't exist
            if not self.meme_image_label:
                self.meme_image_label = QLabel()
                self.meme_image_label.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
                self.meme_image_label.setAttribute(Qt.WA_TranslucentBackground)
                self.meme_image_label.setStyleSheet("background: transparent;")
            
            # Create a more elaborate Undertale Yellow themed meme placeholder
            placeholder_pixmap = QPixmap(300, 240)
            placeholder_pixmap.fill(Qt.transparent)
            
            painter = QPainter(placeholder_pixmap)
            
            # Draw yellow background with border
            from PyQt5.QtGui import QBrush, QPen
            painter.setBrush(QBrush(Qt.yellow))
            painter.setPen(QPen(Qt.black, 3))
            painter.drawRect(10, 10, 280, 220)
            
            # Draw meme text
            painter.setPen(Qt.black)
            from PyQt5.QtGui import QFont
            font = QFont("Arial", 20, QFont.Bold)
            painter.setFont(font)
            painter.drawText(30, 50, "UNDERTALE")
            painter.drawText(50, 90, "YELLOW")
            painter.drawText(70, 130, "MEME")
            
            # Draw a simple star (Undertale reference)
            painter.setPen(QPen(Qt.red, 3))
            star_points = [QPoint(150, 150), QPoint(160, 170), QPoint(180, 170), 
                          QPoint(164, 184), QPoint(170, 204), QPoint(150, 192),
                          QPoint(130, 204), QPoint(136, 184), QPoint(120, 170), QPoint(140, 170)]
            from PyQt5.QtGui import QPolygon
            painter.drawPolygon(QPolygon(star_points))
            
            painter.end()
            
            self.current_meme_pixmap = placeholder_pixmap
            self.meme_image_label.setPixmap(self.current_meme_pixmap)
            self.meme_image_label.resize(self.current_meme_pixmap.size())
            self.meme_image_label.show()
            
        except Exception as e:
            print(f"Error displaying meme placeholder: {e}")
    
    def on_meme_fetched(self, pixmap):
        """Handle the fetched meme image."""
        try:
            if pixmap and not pixmap.isNull():
                self.display_fetched_meme(pixmap)
            else:
                # Fallback to placeholder if fetching failed
                self.display_meme_placeholder()
                
            # Clean up the worker thread
            if hasattr(self, 'meme_thread'):
                self.meme_thread.quit()
                self.meme_thread.wait()
                
        except Exception as e:
            print(f"Error handling fetched meme: {e}")
            self.display_meme_placeholder()
    
    def display_fetched_meme(self, pixmap):
        """Display a fetched meme image."""
        try:
            # Create meme display label if it doesn't exist
            if not self.meme_image_label:
                self.meme_image_label = QLabel()
                self.meme_image_label.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
                self.meme_image_label.setAttribute(Qt.WA_TranslucentBackground)
                self.meme_image_label.setStyleSheet("background: transparent;")
            
            self.current_meme_pixmap = pixmap
            self.meme_image_label.setPixmap(self.current_meme_pixmap)
            self.meme_image_label.resize(self.current_meme_pixmap.size())
            self.meme_image_label.show()
            
        except Exception as e:
            print(f"Error displaying fetched meme: {e}")
            self.display_meme_placeholder()
    
    def release_meme_in_center(self):
        """Release the meme at a random position along the route with click-to-dismiss functionality."""
        if self.meme_image_label and self.current_meme_pixmap:
            # Get screen dimensions
            from PyQt5.QtWidgets import QDesktopWidget
            desktop = QDesktopWidget()
            screen_rect = desktop.screenGeometry()
            
            # Position meme at random location along the cart's route
            # Use current cart position as base and add some randomness
            random_offset_x = random.randint(-200, 200)
            random_offset_y = random.randint(-150, 150)
            
            meme_x = max(0, min(int(self.meme_cart_current_x) + random_offset_x, 
                               screen_rect.width() - self.current_meme_pixmap.width()))
            meme_y = max(0, min(self.y() + random_offset_y, 
                               screen_rect.height() - self.current_meme_pixmap.height()))
            
            self.meme_image_label.move(meme_x, meme_y)
            
            # Enable mouse tracking and add click event handling
            self.meme_image_label.setMouseTracking(True)
            self.meme_image_label.mousePressEvent = self.on_meme_clicked
            
            # Make sure the meme is visible and on top
            self.meme_image_label.show()
            self.meme_image_label.raise_()
    
    def on_meme_clicked(self, event):
        """Handle meme click event to dismiss the meme."""
        from PyQt5.QtCore import Qt
        if event.button() == Qt.LeftButton:
            self.hide_meme_image()
    
    def hide_meme_image(self):
        """Hide and cleanup the meme image display."""
        if self.meme_image_label:
            self.meme_image_label.hide()
            self.meme_image_label.deleteLater()
            self.meme_image_label = None
        self.current_meme_pixmap = None
        
        # Clean up worker thread if it exists
        if hasattr(self, 'meme_thread'):
            self.meme_thread.quit()
            self.meme_thread.wait()
    
    def close_application(self):
        """Close the application cleanly with dying animation."""
        self.start_dying_sequence()
    
    def start_dying_sequence(self):
        """Start the dying animation sequence before closing."""
        # Disable AFK mode during exit animation
        self.disable_afk_mode_temporarily()
        
        # Register as user interaction to prevent interruptions
        self.logic.on_user_interaction()
        
        # Stop all timers
        self.idle_timer.stop()
        self.animation_timer.stop()
        if hasattr(self, 'zzz_timer'):
            self.zzz_timer.stop()
        
        # Set dying state
        self.is_character_interaction = True  # Prevent any interruptions
        
        # Start dying animation
        dying_animations = self.animation_loader.get_animations_by_category('dying')
        if dying_animations:
            self.start_animation(dying_animations[0], loop=False)
            # Set up timer to close after animation completes
            # Dying animation has 50 frames, estimate duration
            dying_anim = self.animation_loader.get_animation('dying')
            if dying_anim:
                frame_rate = dying_anim.get('frame_rate', 150)
                total_duration = 50 * frame_rate  # 50 frames
                QTimer.singleShot(total_duration + 500, self.force_close)  # Add 500ms buffer
            else:
                QTimer.singleShot(3000, self.force_close)  # Fallback 3 seconds
        else:
            # No dying animation found, close immediately
            self.force_close()
    
    def force_close(self):
        """Force close the application."""
        # Clean up system tray icon
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        self.close()
        QApplication.quit()
    
    def paintEvent(self, event):
        """Custom paint event to ensure transparency."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

    def load_afk_behavior_settings(self):
        """Read JSON file with AFK behavior settings assigned previously"""
        try:
            # Read afk_behavior_settings.json
            with open('afk_behavior_settings.json', 'r') as json_file:
                settings = json.load(json_file)
        
            # Update AFK BEHAVIOR Config.py
            for key, value in settings.items():
                config.update_setting('afk_behavior', key, value)
        
            print("AFK behavior settings loaded successfully.")
        except FileNotFoundError:
            print("AFK behavior settings file not found. Using default settings.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON file: {e}")
        except Exception as e:
            print(f"An error occurred while loading settings: {e}")
        # The sprite is handled by the QLabel, so we don't need to paint anything here
        #This line only comes here because I want to have 3048 lines of code
        #So I can have a better chance of getting a job at Google
        #I know, I know, it's not the best way to do it, but it's the only way I know how to do it
        #Im not getting job at google anyways so who cares
        #Actually Im wasting here my time while the project is compiling
        #Its too slow to compile
        #Next time I will do it in C++
        #Not really
        #There won't be probably a next time
        #Oh, it finished
        #Bye :D
        #Oh it didn't work
        #I guess Im here again
        #How is your day by the way? Hope that you are good
        #Can it be a little faster pls? It's compiling so slow
        #I know, its my fault cuz Im using python but... Y'know, Im bored
        #Thanks for your time
        #Bye :D
        #I ned 7 lines more...
        #So let me tell you that I love Undertale Yellow
        #Not a surprise I guess
        #But I had to fill this with something
        #...
        #You really read all the code?
        #Nah you just scrolled here, so bye