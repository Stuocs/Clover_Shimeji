#!/usr/bin/env python3
"""
Configuration settings for Clover Desktop Mascot
"""

# Animation settings
ANIMATION_SETTINGS = {
    'default_frame_rate': 150,  # milliseconds per frame
    'walking_frame_rate': 120,
    'dancing_frame_rate': 90,   # slightly slower dancing animation
    'sitting_frame_rate': 200,
    'lying_frame_rate': 200,
    'nod_frame_rate': 150
}

# Behavior settings
BEHAVIOR_SETTINGS = {
    'idle_action_min_interval': 3000,  # minimum time between random actions (ms)
    'idle_action_max_interval': 8000,  # maximum time between random actions (ms)
    'mouse_follow_speed': 3,           # pixels per update when following mouse
    'mouse_follow_update_rate': 50,    # milliseconds between position updates
    'mouse_proximity_threshold': 100,  # pixels - distance to consider mouse "near"
    'mouse_idle_threshold': 5000,      # milliseconds of no movement to consider mouse idle
    'reaction_probability': 0.3,       # probability of reacting when mouse is near
    'idle_sequence_trigger_time': 5000,  # time before starting dance sequence (ms)
    'dance_sequence_duration': 60000,   # duration of dance sequence (ms)
    'walking_action_min_interval': 2000,  # minimum time between walking actions (ms)
    'walking_action_max_interval': 5000   # maximum time between walking actions (ms)
}

# Action weights for random selection
ACTION_WEIGHTS = {
    'sitting': 30,
    'walking': 20,
    'lying': 15,
    'dancing': 10,
    'nod': 15,
    'poses': 10
}

# Window settings
WINDOW_SETTINGS = {
    'initial_x': 100,      # initial X position
    'initial_y': 100,      # initial Y position
    'default_width': 64,   # default sprite width
    'default_height': 64,  # default sprite height
    'always_on_top': True, # keep mascot on top of other windows
    'transparent_background': True
}

# Size scaling settings
SIZE_SETTINGS = {
    'current_scale': 2.5,    # current size scale (1.0 = original size)
    'available_scales': [1.0, 1.5, 2.0, 2.5, 3.0, 5.0, 50.0],  # available size options
    'scale_names': ['Normal', 'Large', 'Extra Large', 'Huge', 'Giant', 'Extra Giant', 'Screen']  # display names for scales
}

# Performance settings
PERFORMANCE_SETTINGS = {
    'max_action_history': 5,           # number of recent actions to remember
    'animation_cache_size': 50,        # maximum number of animations to cache
    'low_resource_mode': False,        # enable for better performance on low-end systems
    'reduce_animation_quality': False  # reduce animation quality for performance
}

# Debug settings
DEBUG_SETTINGS = {
    'enable_debug_output': False,      # print debug information
    'show_animation_info': False,      # show current animation info
    'log_mouse_events': False,         # log mouse interaction events
    'log_behavior_changes': False      # log behavior state changes
}

# Character interaction settings
CHARACTER_SETTINGS = {
    'enable_character_interactions': True,  # enable character interaction animations
    'interaction_duration': 5000,          # how long character interactions play (ms)
    'auto_return_to_idle': True             # automatically return to idle after interactions
}

# AFK behavior settings
AFK_BEHAVIOR_SETTINGS = {
    'afk_mode_enabled': True,      # master toggle for AFK mode
    'enable_walking': True,        # enable random walking/running
    'enable_sitting': True,        # enable sitting animations
    'enable_dancing': True,        # enable dance animations
    'enable_character_interactions': True,  # enable character interactions
    'enable_sleeping': True,       # enable sleep mode
    'enable_falling': True,        # enable fall mode
    'enable_cart_rides': True,     # enable cart rides
    'enable_mouse_following': True, # enable brief mouse following
    'enable_minigames': True,      # enable minigames
    'enable_whale_mail': True      # enable whale mail delivery
}

# AFK Flag Settings
FLAGS_SETTINGS = {
    'had_afk_mode_enabled': False,      # Flag for minigames in AFK mode
    'mascot_in_game': False,            # Flag to indicate if the mascot is in a game
}

def get_setting(category, key, default=None):
    """Get a configuration setting by category and key."""
    categories = {
        'animation': ANIMATION_SETTINGS,
        'behavior': BEHAVIOR_SETTINGS,
        'action_weights': ACTION_WEIGHTS,
        'window': WINDOW_SETTINGS,
        'size': SIZE_SETTINGS,
        'performance': PERFORMANCE_SETTINGS,
        'debug': DEBUG_SETTINGS,
        'character': CHARACTER_SETTINGS,
        'afk_behavior': AFK_BEHAVIOR_SETTINGS,
        'flags': FLAGS_SETTINGS
    }
    
    settings = categories.get(category, {})
    return settings.get(key, default)

def update_setting(category, key, value):
    """Update a configuration setting."""
    categories = {
        'animation': ANIMATION_SETTINGS,
        'behavior': BEHAVIOR_SETTINGS,
        'action_weights': ACTION_WEIGHTS,
        'window': WINDOW_SETTINGS,
        'size': SIZE_SETTINGS,
        'performance': PERFORMANCE_SETTINGS,
        'debug': DEBUG_SETTINGS,
        'character': CHARACTER_SETTINGS,
        'afk_behavior': AFK_BEHAVIOR_SETTINGS,
        'flags': FLAGS_SETTINGS
    }
    
    if category in categories:
        categories[category][key] = value
        return True
    return False

def get_all_settings():
    """Get all configuration settings."""
    return {
        'animation': ANIMATION_SETTINGS,
        'behavior': BEHAVIOR_SETTINGS,
        'action_weights': ACTION_WEIGHTS,
        'window': WINDOW_SETTINGS,
        'size': SIZE_SETTINGS,
        'performance': PERFORMANCE_SETTINGS,
        'debug': DEBUG_SETTINGS,
        'character': CHARACTER_SETTINGS
    }

def reset_to_defaults():
    """Reset all settings to their default values."""
    # This would reload the default values
    # Implementation depends on whether you want to persist settings
    pass