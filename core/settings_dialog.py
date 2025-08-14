#!/usr/bin/env python3
"""
Settings dialog for configuring AFK behaviors
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, 
    QLabel, QGroupBox, QScrollArea, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt
import config

class AFKBehaviorSettingsDialog(QDialog):
    """Dialog for configuring which AFK behaviors are enabled."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AFK Behavior Settings")
        self.setModal(True)
        self.resize(400, 500)
        
        # Store original settings for cancel functionality
        self.original_settings = {}
        for key in config.AFK_BEHAVIOR_SETTINGS:
            self.original_settings[key] = config.get_setting('afk_behavior', key, True)
        
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Configure AFK Behaviors")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "Select which animations and behaviors you want Clover to perform automatically when idle (AFK mode)."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("margin: 5px 10px; color: #666;")
        layout.addWidget(desc_label)
        
        # Scroll area for checkboxes
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Create behavior groups
        self.create_movement_group(scroll_layout)
        self.create_animation_group(scroll_layout)
        self.create_interaction_group(scroll_layout)
        self.create_special_group(scroll_layout)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Select All / Deselect All buttons
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all)
        button_layout.addWidget(deselect_all_btn)
        
        button_layout.addStretch()
        
        # OK and Cancel buttons
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept_settings)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_movement_group(self, layout):
        """Create movement behaviors group."""
        group = QGroupBox("Movement Behaviors")
        group_layout = QVBoxLayout(group)
        
        self.walking_cb = QCheckBox("Walking & Running")
        self.walking_cb.setToolTip("Clover will randomly walk and run around the screen")
        group_layout.addWidget(self.walking_cb)
        
        self.mouse_following_cb = QCheckBox("Mouse Following")
        self.mouse_following_cb.setToolTip("Clover will briefly follow the mouse cursor")
        group_layout.addWidget(self.mouse_following_cb)
        
        self.cart_rides_cb = QCheckBox("Cart Rides")
        self.cart_rides_cb.setToolTip("Clover will ride in carts across the screen")
        group_layout.addWidget(self.cart_rides_cb)
        
        self.whale_mail_cb = QCheckBox("Whale Mail Delivery")
        self.whale_mail_cb.setToolTip("Clover will deliver mail via whale")
        group_layout.addWidget(self.whale_mail_cb)
        
        layout.addWidget(group)
    
    def create_animation_group(self, layout):
        """Create animation behaviors group."""
        group = QGroupBox("Animation Behaviors")
        group_layout = QVBoxLayout(group)
        
        self.sitting_cb = QCheckBox("Sitting Animations")
        self.sitting_cb.setToolTip("Clover will sit in various poses")
        group_layout.addWidget(self.sitting_cb)
        
        self.dancing_cb = QCheckBox("Dancing")
        self.dancing_cb.setToolTip("Clover will perform dance animations")
        group_layout.addWidget(self.dancing_cb)
        
        self.sleeping_cb = QCheckBox("Sleeping")
        self.sleeping_cb.setToolTip("Clover will lie down and sleep with ZZZ animations")
        group_layout.addWidget(self.sleeping_cb)
        
        self.falling_cb = QCheckBox("Falling")
        self.falling_cb.setToolTip("Clover will fall down and get back up")
        group_layout.addWidget(self.falling_cb)
        
        layout.addWidget(group)
    
    def create_interaction_group(self, layout):
        """Create interaction behaviors group."""
        group = QGroupBox("Interactive Behaviors")
        group_layout = QVBoxLayout(group)
        
        self.character_interactions_cb = QCheckBox("Character Interactions")
        self.character_interactions_cb.setToolTip("Clover will interact with other characters")
        group_layout.addWidget(self.character_interactions_cb)
        
        self.minigames_cb = QCheckBox("Minigames")
        self.minigames_cb.setToolTip("Clover will play various minigames")
        group_layout.addWidget(self.minigames_cb)
        
        layout.addWidget(group)
    
    def create_special_group(self, layout):
        """Create special behaviors group."""
        group = QGroupBox("Special Behaviors")
        group_layout = QVBoxLayout(group)
        
        # Add note about special behaviors
        note_label = QLabel("Note: These are advanced behaviors that may interact with your desktop")
        note_label.setStyleSheet("color: #888; font-style: italic; margin: 5px;")
        note_label.setWordWrap(True)
        group_layout.addWidget(note_label)
        
        layout.addWidget(group)
    
    def load_current_settings(self):
        """Load current settings into the checkboxes."""
        self.walking_cb.setChecked(config.get_setting('afk_behavior', 'enable_walking', True))
        self.sitting_cb.setChecked(config.get_setting('afk_behavior', 'enable_sitting', True))
        self.dancing_cb.setChecked(config.get_setting('afk_behavior', 'enable_dancing', True))
        self.character_interactions_cb.setChecked(config.get_setting('afk_behavior', 'enable_character_interactions', True))
        self.sleeping_cb.setChecked(config.get_setting('afk_behavior', 'enable_sleeping', True))
        self.falling_cb.setChecked(config.get_setting('afk_behavior', 'enable_falling', True))
        self.cart_rides_cb.setChecked(config.get_setting('afk_behavior', 'enable_cart_rides', True))
        self.mouse_following_cb.setChecked(config.get_setting('afk_behavior', 'enable_mouse_following', True))
        self.minigames_cb.setChecked(config.get_setting('afk_behavior', 'enable_minigames', True))
        self.whale_mail_cb.setChecked(config.get_setting('afk_behavior', 'enable_whale_mail', True))
    
    def select_all(self):
        """Select all checkboxes."""
        self.walking_cb.setChecked(True)
        self.sitting_cb.setChecked(True)
        self.dancing_cb.setChecked(True)
        self.character_interactions_cb.setChecked(True)
        self.sleeping_cb.setChecked(True)
        self.falling_cb.setChecked(True)
        self.cart_rides_cb.setChecked(True)
        self.mouse_following_cb.setChecked(True)
        self.minigames_cb.setChecked(True)
        self.whale_mail_cb.setChecked(True)
    
    def deselect_all(self):
        """Deselect all checkboxes."""
        self.walking_cb.setChecked(False)
        self.sitting_cb.setChecked(False)
        self.dancing_cb.setChecked(False)
        self.character_interactions_cb.setChecked(False)
        self.sleeping_cb.setChecked(False)
        self.falling_cb.setChecked(False)
        self.cart_rides_cb.setChecked(False)
        self.mouse_following_cb.setChecked(False)
        self.minigames_cb.setChecked(False)
        self.whale_mail_cb.setChecked(False)
    
    def accept_settings(self):
        """Apply the settings and close the dialog."""
        # Check if at least one behavior is enabled
        any_enabled = (
            self.walking_cb.isChecked() or
            self.sitting_cb.isChecked() or
            self.dancing_cb.isChecked() or
            self.character_interactions_cb.isChecked() or
            self.sleeping_cb.isChecked() or
            self.falling_cb.isChecked() or
            self.cart_rides_cb.isChecked() or
            self.mouse_following_cb.isChecked() or
            self.minigames_cb.isChecked() or
            self.whale_mail_cb.isChecked()
        )
        
        if not any_enabled:
            QMessageBox.warning(
                self, 
                "No Behaviors Selected", 
                "You must enable at least one AFK behavior. Clover needs something to do when idle!"
            )
            return
        
        # Save settings
        config.update_setting('afk_behavior', 'enable_walking', self.walking_cb.isChecked())
        config.update_setting('afk_behavior', 'enable_sitting', self.sitting_cb.isChecked())
        config.update_setting('afk_behavior', 'enable_dancing', self.dancing_cb.isChecked())
        config.update_setting('afk_behavior', 'enable_character_interactions', self.character_interactions_cb.isChecked())
        config.update_setting('afk_behavior', 'enable_sleeping', self.sleeping_cb.isChecked())
        config.update_setting('afk_behavior', 'enable_falling', self.falling_cb.isChecked())
        config.update_setting('afk_behavior', 'enable_cart_rides', self.cart_rides_cb.isChecked())
        config.update_setting('afk_behavior', 'enable_mouse_following', self.mouse_following_cb.isChecked())
        config.update_setting('afk_behavior', 'enable_minigames', self.minigames_cb.isChecked())
        config.update_setting('afk_behavior', 'enable_whale_mail', self.whale_mail_cb.isChecked())
        
        self.accept()
    
    def reject(self):
        """Cancel the dialog and restore original settings."""
        # Restore original settings
        for key, value in self.original_settings.items():
            config.update_setting('afk_behavior', key, value)
        
        super().reject()