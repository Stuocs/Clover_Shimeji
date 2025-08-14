#!/usr/bin/env python3
"""
Mascot Logic - Handles behavior, random actions, and state management
"""

import random
import time
import config
from PyQt5.QtCore import QObject, QTimer

class MascotLogic(QObject):
    """Manages the mascot's behavior logic and decision making."""
    
    def __init__(self, mascot):
        super().__init__()
        self.mascot = mascot
        
        # Behavior weights for random action selection
        self.action_weights = {
            'sitting': 30,
            'walking': 20,
            'lying': 15,
            'dancing': 10,
            'nod': 15,
            'poses': 10
        }
        
        # State tracking
        self.current_behavior_mode = 'idle'
        self.last_action = None
        self.action_history = []
        self.max_history = 5
        
        # New idle sequence tracking
        self.last_user_interaction = time.time()
        self.idle_sequence_state = 'waiting'  # 'waiting', 'dancing', 'walking'
        self.dance_start_time = None
        self.dance_duration = config.get_setting('behavior', 'dance_sequence_duration', 60000)
        self.idle_trigger_time = config.get_setting('behavior', 'idle_sequence_trigger_time', 5000)
        
        # Persistent dance mode
        self.eternal_dance_mode = False
        
        # Timed dance mode
        self.timed_dance_mode = False
        
        # Idle mode control - removed
        # self.idle_mode_enabled = False
        self.timed_dance_timer = QTimer()
        self.timed_dance_timer.timeout.connect(self.stop_timed_dance)
        self.timed_dance_timer.setSingleShot(True)
        
        # Enhanced AFK system (default behavior when no modes are active)
        self.random_walking_enabled = True
        self.random_walking_timer = QTimer()
        self.random_walking_timer.timeout.connect(self.perform_enhanced_afk_behavior)
        self.random_walking_timer.setSingleShot(True)
        self.current_walk_direction = None
        self.walk_duration = 0
        self.walk_start_time = None
        self.is_running_mode = False
        
        # Timers for behavior management
        self.behavior_timer = QTimer()
        self.behavior_timer.timeout.connect(self.update_behavior)
        
        # Timer for idle sequence management
        self.idle_sequence_timer = QTimer()
        self.idle_sequence_timer.timeout.connect(self.check_idle_sequence)
        self.idle_sequence_timer.start(1000)  # Check every second
        
        # Start random walking after a short delay
        QTimer.singleShot(3000, self.start_random_walking_system)
        
    def perform_random_action(self):
        """Perform a random idle action based on weights and history."""
        if self.mascot.is_sleeping or self.mascot.is_following_mouse or self.mascot.is_character_interaction:
            return
        
        # Don't perform random actions during eternal dance mode
        if self.eternal_dance_mode:
            return
            
        # Random actions functionality removed with idle mode
        return
            
        # Check if we're in idle sequence mode
        if self.idle_sequence_state != 'waiting':
            return  # Let idle sequence handle behavior
        
        # Get available actions
        available_actions = self.get_available_actions()
        
        if not available_actions:
            return
        
        # Select action based on weights and avoid repetition
        selected_action = self.select_weighted_action(available_actions)
        
        if selected_action:
            self.execute_action(selected_action)
            self.update_action_history(selected_action)
    
    def perform_random_walk(self):
        """Perform random walking movement with directional animations."""
        print(f"Random walk triggered! (idle mode removed)")
        
        # Don't walk if any special mode is active
        if (self.mascot.is_sleeping or self.mascot.is_following_mouse or 
            self.mascot.is_character_interaction or self.eternal_dance_mode or 
            self.timed_dance_mode or getattr(self.mascot, 'is_falling', False)):
            print("Random walk blocked by special mode")
            return
        
        # Idle mode removed - random walking is now always available when no special modes are active
        
        # Get screen dimensions
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry()
        
        # Get current position
        current_x = self.mascot.x()
        current_y = self.mascot.y()
        
        # Check if we should switch to running mode (after 10 seconds of cumulative walking)
        import time
        current_time = time.time()
        
        # Initialize walking session timer if not set
        if not hasattr(self, 'walking_session_start_time') or self.walking_session_start_time is None:
            self.walking_session_start_time = current_time
            self.is_running_mode = False
        
        # Check if we've been walking long enough to switch to running mode
        walking_session_duration = current_time - self.walking_session_start_time
        if walking_session_duration > 10:
            self.is_running_mode = True
            print(f"Switching to running mode after {walking_session_duration:.1f} seconds of walking!")
        else:
            print(f"Walking session duration: {walking_session_duration:.1f} seconds (need 10s for running mode)")
        
        # Define possible directions and their animations
        directions = {
            'left': {'animation': 'walking_spr_pl_run_left' if self.is_running_mode else 'walking_spr_pl_left', 'dx': -4 if self.is_running_mode else -2, 'dy': 0},
            'right': {'animation': 'walking_spr_pl_run_right' if self.is_running_mode else 'walking_spr_pl_right', 'dx': 4 if self.is_running_mode else 2, 'dy': 0},
            'up': {'animation': 'walking_spr_pl_run_up' if self.is_running_mode else 'walking_spr_pl_up', 'dx': 0, 'dy': -4 if self.is_running_mode else -2},
            'down': {'animation': 'walking_spr_pl_run_down' if self.is_running_mode else 'walking_spr_pl_down', 'dx': 0, 'dy': 4 if self.is_running_mode else 2}
        }
        
        # Filter directions to avoid going off screen
        valid_directions = []
        margin = 50  # Keep some margin from screen edges
        
        for direction, data in directions.items():
            new_x = current_x + (data['dx'] * 50)  # Predict position after 50 steps
            new_y = current_y + (data['dy'] * 50)
            
            if (margin <= new_x <= screen_rect.width() - self.mascot.width() - margin and
                margin <= new_y <= screen_rect.height() - self.mascot.height() - margin):
                valid_directions.append(direction)
        
        # If no valid directions, move to center and try again
        if not valid_directions:
            center_x = (screen_rect.width() - self.mascot.width()) // 2
            center_y = (screen_rect.height() - self.mascot.height()) // 2
            self.mascot.move(center_x, center_y)
            # Reset walking session timer when repositioning
            self.walking_session_start_time = None
            self.is_running_mode = False
            self.random_walking_timer.start(2000)  # Wait 2 seconds before next walk
            return
        
        # Choose random direction
        import random
        chosen_direction = random.choice(valid_directions)
        direction_data = directions[chosen_direction]
        
        # Start walking/running animation
        walking_animations = self.mascot.animation_loader.get_animations_by_category('walking')
        if walking_animations:
            # Find the specific directional animation
            target_animation = direction_data['animation']
            
            # Debug: Print what we're looking for
            print(f"Looking for animation: {target_animation}")
            print(f"Available animations: {walking_animations}")
            print(f"Is running mode: {self.is_running_mode}")
            
            # Check if the target animation exists in the loaded animations
            animation_found = False
            for anim in walking_animations:
                if target_animation == anim:  # Use exact match instead of 'in'
                    print(f"Found exact match: {anim}")
                    self.mascot.start_animation(anim, loop=True)
                    animation_found = True
                    break
            
            # If exact match not found, try partial match
            if not animation_found:
                for anim in walking_animations:
                    if target_animation in anim:
                        print(f"Found partial match: {anim}")
                        self.mascot.start_animation(anim, loop=True)
                        animation_found = True
                        break
            
            if animation_found:
                self.current_walk_direction = chosen_direction
                self.walk_duration = random.randint(3000, 7000)  # Walk/run for 3-7 seconds
                
                # Start movement
                self.start_walking_movement(direction_data['dx'], direction_data['dy'])
                
                # Schedule next walk
                self.random_walking_timer.start(self.walk_duration + random.randint(1000, 3000))
            else:
                # Fallback to any walking animation
                self.mascot.start_animation(random.choice(walking_animations), loop=True)
                self.random_walking_timer.start(random.randint(3000, 6000))
    
    def perform_enhanced_afk_behavior(self):
        """Enhanced AFK behavior that randomly chooses between various activities."""
        print("Enhanced AFK behavior triggered!")
        
        # Check if AFK mode is enabled
        import config
        if not config.get_setting('afk_behavior', 'afk_mode_enabled', True):
            print("AFK behavior blocked - AFK mode is disabled")
            return
        
        # Don't perform AFK behaviors if any special mode is active
        if (self.mascot.is_sleeping or self.mascot.is_following_mouse or 
            self.mascot.is_character_interaction or self.eternal_dance_mode or 
            self.timed_dance_mode or getattr(self.mascot, 'is_falling', False) or
            getattr(self.mascot, 'is_dragging', False) or
            getattr(self.mascot, 'in_hide_seek_sequence', False) or
            getattr(self.mascot, 'in_showdown_sequence', False) or
            getattr(self.mascot, 'in_edward_sequence', False)):
            print("AFK behavior blocked by special mode")
            return
        
        import random
        
        # Define AFK behavior probabilities (weights) - only include enabled behaviors
        import config
        afk_behaviors = {}
        
        if config.get_setting('afk_behavior', 'enable_walking', True):
            afk_behaviors['walk'] = 35  # Walking/running (most common)
        if config.get_setting('afk_behavior', 'enable_sitting', True):
            afk_behaviors['sit'] = 20   # Sitting animations
        if config.get_setting('afk_behavior', 'enable_dancing', True):
            afk_behaviors['dance'] = 10 # Dance animations
        if config.get_setting('afk_behavior', 'enable_character_interactions', True):
            afk_behaviors['character'] = 8 # Character interactions
        if config.get_setting('afk_behavior', 'enable_sleeping', True):
            afk_behaviors['sleep'] = 5  # Sleep mode
        if config.get_setting('afk_behavior', 'enable_falling', True):
            afk_behaviors['fall'] = 3   # Fall mode
        if config.get_setting('afk_behavior', 'enable_cart_rides', True):
            afk_behaviors['cart'] = 6   # Cart rides
        if config.get_setting('afk_behavior', 'enable_mouse_following', True):
            afk_behaviors['follow_mouse'] = 5 # Follow mouse briefly
        if config.get_setting('afk_behavior', 'enable_minigames', True):
            afk_behaviors['minigame'] = 5  # Minigames if available
        if config.get_setting('afk_behavior', 'enable_whale_mail', True):
            afk_behaviors['whale_mail'] = 3  # Whale mail delivery
        
        # If no behaviors are enabled, fallback to walking
        if not afk_behaviors:
            afk_behaviors['walk'] = 35
        
        # Create weighted list for random selection
        weighted_choices = []
        for behavior, weight in afk_behaviors.items():
            weighted_choices.extend([behavior] * weight)
        
        # Select random behavior
        chosen_behavior = random.choice(weighted_choices)
        print(f"Chosen AFK behavior: {chosen_behavior}")
        
        # Execute the chosen behavior
        if chosen_behavior == 'walk':
            self.perform_random_walk()
        elif chosen_behavior == 'sit':
            self.perform_random_sitting()
        elif chosen_behavior == 'dance':
            self.perform_random_dance()
        elif chosen_behavior == 'character':
            self.perform_random_character_interaction()
        elif chosen_behavior == 'sleep':
            self.perform_random_sleep()
        elif chosen_behavior == 'fall':
            self.perform_random_fall()
        elif chosen_behavior == 'cart':
            self.perform_random_cart_ride()
        elif chosen_behavior == 'follow_mouse':
            self.perform_random_mouse_follow()
        elif chosen_behavior == 'minigame':
             self.perform_random_minigame()
        elif chosen_behavior == 'whale_mail':
            self.perform_random_whale_mail()
    
    def perform_random_sitting(self):
        """Randomly choose and start a sitting animation."""
        sitting_animations = ['sitting_spr_colver_wind', 'sitting_spr_clover_sitting', 
                             'sitting_spr_clover_sit_dark', 'spr_clover_casual']
        import random
        chosen_sit = random.choice(sitting_animations)
        print(f"AFK: Starting sitting animation: {chosen_sit}")
        self.mascot.start_sitting_animation(chosen_sit)
        # Stop sitting after a random duration and resume AFK behaviors
        QTimer.singleShot(random.randint(8000, 15000), self.stop_afk_sitting)
    
    def perform_random_dance(self):
        """Start a random dance animation."""
        print("AFK: Starting dance")
        self.start_eternal_dance()
        # Stop dance after some time and return to AFK
        import random
        QTimer.singleShot(random.randint(10000, 20000), self.stop_afk_dance)
    
    def stop_afk_dance(self):
        """Stop AFK dance and resume AFK behaviors."""
        self.stop_eternal_dance()
        import random
        self.random_walking_timer.start(random.randint(3000, 8000))
    
    def perform_random_character_interaction(self):
        """Start a random character interaction."""
        char_interactions = self.mascot.animation_loader.get_animations_by_category('characters_interactions')
        if char_interactions:
            import random
            chosen_interaction = random.choice(char_interactions)
            print(f"AFK: Starting character interaction: {chosen_interaction}")
            self.mascot.start_character_interaction(chosen_interaction)
            # Schedule next AFK behavior after character interaction completes
            QTimer.singleShot(random.randint(5000, 10000), self.resume_afk_after_character_interaction)
        else:
            # Fallback to walking if no character interactions available
            self.perform_random_walk()
    
    def resume_afk_after_character_interaction(self):
        """Resume AFK behaviors after character interaction completion."""
        print("AFK: Character interaction completed, resuming AFK behaviors")
        import random
        self.random_walking_timer.start(random.randint(2000, 5000))
    
    def perform_random_sleep(self):
        """Start sleep mode for a random duration."""
        print("AFK: Going to sleep")
        self.mascot.set_sleep_mode(True, auto_stop=True)
        # Wake up after random time
        import random
        QTimer.singleShot(random.randint(8000, 20000), self.wake_from_afk_sleep)
    
    def wake_from_afk_sleep(self):
        """Wake up from AFK sleep and resume AFK behaviors."""
        self.mascot.set_sleep_mode(False, auto_stop=True)
        import random
        self.random_walking_timer.start(random.randint(2000, 5000))
    
    def perform_random_fall(self):
        """Start fall mode for a random duration."""
        print("AFK: Starting to fall")
        self.mascot.set_fall_mode(True, auto_stop=True)
        # Stop falling after random time
        import random
        QTimer.singleShot(random.randint(5000, 12000), self.stop_afk_fall)
    
    def stop_afk_fall(self):
        """Stop AFK fall and resume AFK behaviors."""
        self.mascot.set_fall_mode(False, auto_stop=True)
        import random
        self.random_walking_timer.start(random.randint(2000, 5000))
    
    def perform_random_cart_ride(self):
        """Start a random cart ride."""
        import random
        cart_types = ['normal', 'meme']
        chosen_cart = random.choice(cart_types)
        print(f"AFK: Starting {chosen_cart} cart ride")
        
        if chosen_cart == 'normal':
            self.mascot.start_cart_movement()
        else:
            self.mascot.start_meme_cart_movement()
        
        # Cart rides handle their own completion and AFK resumption
    
    def perform_random_mouse_follow(self):
        """Briefly follow the mouse cursor."""
        print("AFK: Following mouse briefly")
        self.mascot.set_follow_mouse(True)
        # Stop following after a longer time to allow reaching the mouse
        import random
        QTimer.singleShot(random.randint(15000, 25000), self.stop_afk_mouse_follow)
    
    def stop_afk_mouse_follow(self):
        """Stop AFK mouse following and resume AFK behaviors."""
        self.mascot.set_follow_mouse(False)
        # Only restart random walking if not in special modes (dance, sleep, etc.)
        if (self.random_walking_enabled and not self.eternal_dance_mode and 
            not self.timed_dance_mode and not self.mascot.is_sleeping and 
            not getattr(self.mascot, 'is_falling', False)):
            import random
            self.random_walking_timer.start(random.randint(2000, 5000))
    
    def stop_afk_sitting(self):
        """Stop AFK sitting and resume AFK behaviors."""
        print("AFK: Stopping sitting animation and resuming AFK behaviors")
        # Return to idle state and resume AFK behaviors
        self.return_to_idle()
        import random
        self.random_walking_timer.start(random.randint(2000, 5000))
    
    def perform_random_minigame(self):
        """Start a random minigame if available."""
        # Check if minigames are available in the mascot
        if hasattr(self.mascot, 'start_hide_and_seek_sequence'):
            import random
            minigames = ['hide_and_seek']
            # Add showdown if available
            if hasattr(self.mascot, 'start_showdown_sequence'):
                minigames.append('showdown')
            
            chosen_game = random.choice(minigames)
            print(f"AFK: Starting minigame: {chosen_game}")
            
            if chosen_game == 'hide_and_seek':
                self.mascot.start_hide_and_seek_sequence()
            elif chosen_game == 'showdown':
                self.mascot.start_showdown_sequence()
            
            # Minigames typically handle their own completion, but add fallback
            QTimer.singleShot(random.randint(15000, 30000), self.resume_afk_after_minigame)
        else:
            # Fallback to walking if no minigames available
            self.perform_random_walk()
    
    def resume_afk_after_minigame(self):
        """Resume AFK behaviors after minigame completion."""
        import random
        self.random_walking_timer.start(random.randint(3000, 8000))
    
    def perform_random_whale_mail(self):
        """Start whale mail delivery animation."""
        print("AFK: Starting whale mail delivery")
        self.mascot.start_whale_mail_movement()
        # Whale mail handles its own completion and AFK resumption
    
    def start_walking_movement(self, dx, dy):
        """Start the actual movement during walking."""
        if not hasattr(self, 'walking_movement_timer'):
            self.walking_movement_timer = QTimer()
            self.walking_movement_timer.timeout.connect(self.update_walking_position)
        
        self.walking_dx = dx
        self.walking_dy = dy
        self.walking_movement_timer.start(50)  # Update position every 50ms
        
        # Stop movement after walk duration
        QTimer.singleShot(self.walk_duration, self.stop_walking_movement)
    
    def update_walking_position(self):
        """Update mascot position during walking."""
        if (self.mascot.is_sleeping or self.mascot.is_following_mouse or 
            self.mascot.is_character_interaction or self.eternal_dance_mode or 
            self.timed_dance_mode or getattr(self.mascot, 'is_falling', False)):
            self.stop_walking_movement()
            return
        
        # Get screen dimensions
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry()
        
        # Calculate new position
        new_x = self.mascot.x() + self.walking_dx
        new_y = self.mascot.y() + self.walking_dy
        
        # Check boundaries
        margin = 20
        if (margin <= new_x <= screen_rect.width() - self.mascot.width() - margin and
            margin <= new_y <= screen_rect.height() - self.mascot.height() - margin):
            self.mascot.move(new_x, new_y)
        else:
            # Hit boundary, stop walking
            self.stop_walking_movement()
    
    def stop_walking_movement(self):
        """Stop the walking movement and return to sitting."""
        if hasattr(self, 'walking_movement_timer'):
            self.walking_movement_timer.stop()
        
        # Don't reset walking session timer when movement stops - let it persist for running mode
        
        # Return to sitting animation if no special modes are active
        if (not self.mascot.is_sleeping and not self.mascot.is_following_mouse and 
            not self.mascot.is_character_interaction and not self.eternal_dance_mode and 
            not self.timed_dance_mode and not getattr(self.mascot, 'is_falling', False)):
            sitting_animations = self.mascot.animation_loader.get_animations_by_category('sitting')
            if sitting_animations:
                import random
                self.mascot.start_animation(random.choice(sitting_animations), loop=True)
    
    def start_random_walking_system(self):
        """Start the random walking system."""
        print(f"Starting random walking system. Enabled: {self.random_walking_enabled}")
        if self.random_walking_enabled:
            # Reset walking session timer when starting
            self.walking_session_start_time = None
            self.is_running_mode = False
            delay = random.randint(2000, 5000)
            print(f"Random walking timer started with delay: {delay}ms")
            self.random_walking_timer.start(delay)
    
    def stop_random_walking_system(self):
        """Stop the random walking system."""
        self.random_walking_timer.stop()
        if hasattr(self, 'walking_movement_timer'):
            self.walking_movement_timer.stop()
        # Reset walking session timer when stopping
        self.walking_session_start_time = None
        self.is_running_mode = False
      
    def get_available_actions(self):
        """Get list of available actions based on loaded animations."""
        available = []
        
        for category, weight in self.action_weights.items():
            animations = self.mascot.animation_loader.get_animations_by_category(category)
            if animations:
                available.append((category, weight, animations))
        
        return available
    
    def select_weighted_action(self, available_actions):
        """Select an action using weighted random selection, avoiding recent repeats."""
        # Adjust weights based on recent history
        adjusted_actions = []
        
        for category, weight, animations in available_actions:
            # Reduce weight if action was used recently
            recent_count = self.action_history.count(category)
            adjusted_weight = max(1, weight - (recent_count * 5))
            adjusted_actions.append((category, adjusted_weight, animations))
        
        # Create weighted list
        weighted_list = []
        for category, weight, animations in adjusted_actions:
            weighted_list.extend([category] * weight)
        
        if not weighted_list:
            return None
        
        # Select random category
        selected_category = random.choice(weighted_list)
        
        # Get animations for selected category
        for category, _, animations in adjusted_actions:
            if category == selected_category:
                return (category, random.choice(animations))
        
        return None
    
    def execute_action(self, action_info):
        """Execute a specific action."""
        category, animation_name = action_info
        
        # Determine if action should loop
        loop = self.should_action_loop(category)
        
        # Special handling for walking - choose direction
        if category == 'walking':
            animation_name = self.select_walking_direction()
        
        # Start the animation
        self.mascot.start_animation(animation_name, loop=loop)
        self.last_action = category
        
        # Set timer for action duration if not looping
        if not loop:
            duration = self.get_action_duration(category)
            QTimer.singleShot(duration, self.return_to_idle)
    
    def should_action_loop(self, category):
        """Determine if an action should loop continuously."""
        non_looping_actions = ['dancing', 'nod', 'poses']
        return category not in non_looping_actions
    
    def get_action_duration(self, category):
        """Get the duration for non-looping actions."""
        durations = {
            'dancing': 3000,  # 3 seconds
            'nod': 1500,      # 1.5 seconds
            'poses': 2000     # 2 seconds
        }
        return durations.get(category, 2000)
    
    def select_walking_direction(self):
        """Select a walking direction, potentially towards mouse if nearby."""
        walking_animations = self.mascot.animation_loader.get_animations_by_category('walking')
        
        if not walking_animations:
            return None
        
        # Check if mouse is nearby and not idle
        if (self.mascot.event_handler.is_mouse_near_mascot(200) and 
            not self.mascot.event_handler.is_mouse_idle):
            # Walk towards mouse
            direction = self.mascot.event_handler.get_mouse_direction_from_mascot()
            direction_animation = f"walking_{direction}"
            
            if direction_animation in walking_animations:
                return direction_animation
        
        # Random direction
        return random.choice(walking_animations)
    
    def update_action_history(self, action):
        """Update the action history to avoid repetition."""
        self.action_history.append(action)
        
        # Keep only recent history
        if len(self.action_history) > self.max_history:
            self.action_history.pop(0)
    
    def return_to_idle(self):
        """Return mascot to idle state."""
        if self.mascot.is_sleeping or self.mascot.is_following_mouse:
            return
        
        # Stop current timers
        self.mascot.idle_timer.stop()
        self.mascot.mouse_follow_timer.stop()
        
        # Reset states
        self.mascot.is_following_mouse = False
        self.mascot.is_sleeping = False
        
        # Start idle sitting animation
        sitting_animations = self.mascot.animation_loader.get_animations_by_category('sitting')
        if sitting_animations:
            self.mascot.start_animation(random.choice(sitting_animations))
        
        # Idle timer functionality removed with idle mode
    
    def on_animation_complete(self):
        """Called when a non-looping animation completes."""
        # Don't interfere if we're in the middle of Edward sequence
        if hasattr(self.mascot, 'in_edward_sequence') and self.mascot.in_edward_sequence:
            return
        
        # Check if we're in a hide and seek sequence and should not interfere
        if hasattr(self.mascot, 'in_hide_seek_sequence') and self.mascot.in_hide_seek_sequence:
            return
        
        # Reset character interaction flag if it was set
        if self.mascot.is_character_interaction:
            self.mascot.is_character_interaction = False
            # Resume AFK behaviors after character interaction completes
            import random
            self.random_walking_timer.start(random.randint(3000, 8000))
            return
        
        # Return to idle after animation completes
        QTimer.singleShot(500, self.return_to_idle)  # Small delay before returning to idle
    
    def set_behavior_mode(self, mode):
        """Set the current behavior mode."""
        self.current_behavior_mode = mode
        
        if mode == 'idle':
            self.return_to_idle()
        elif mode == 'follow_mouse':
            self.mascot.set_follow_mouse(True)
        elif mode == 'sleep':
            self.mascot.set_sleep_mode(True)
    
    def update_behavior(self):
        """Update behavior based on current mode and conditions."""
        # Skip behavior updates if in eternal dance or timed dance mode
        if self.eternal_dance_mode or self.timed_dance_mode:
            return
            
        if self.current_behavior_mode == 'idle':
            # Check for environmental triggers
            if self.mascot.event_handler.is_mouse_near_mascot(100):
                # Mouse is nearby, maybe react
                if random.random() < 0.3:  # 30% chance to react
                    self.react_to_mouse_proximity()
    
    def react_to_mouse_proximity(self):
        """React when mouse is near the mascot."""
        # Choose a reaction
        reactions = ['nod', 'poses']
        available_reactions = []
        
        for reaction in reactions:
            animations = self.mascot.animation_loader.get_animations_by_category(reaction)
            if animations:
                available_reactions.extend([(reaction, anim) for anim in animations])
        
        if available_reactions:
            category, animation = random.choice(available_reactions)
            self.execute_action((category, animation))
    
    def check_idle_sequence(self):
        """Check and manage the idle sequence behavior."""
        if self.mascot.is_sleeping or self.mascot.is_following_mouse or self.eternal_dance_mode or self.mascot.is_character_interaction:
            return
        
        # Idle sequence functionality removed with idle mode
        return
        
        current_time = time.time()
        time_since_interaction = (current_time - self.last_user_interaction) * 1000  # Convert to milliseconds
        
        if self.idle_sequence_state == 'waiting':
            # If no interaction for configured time, start dancing
            if time_since_interaction > self.idle_trigger_time:
                self.start_idle_dance_sequence()
        
        elif self.idle_sequence_state == 'dancing':
            # Check if dance duration is complete
            if self.dance_start_time and (current_time - self.dance_start_time) * 1000 >= self.dance_duration:
                self.start_idle_walking_sequence()
        
        elif self.idle_sequence_state == 'walking':
            # Continue random walking until user interaction
            if time_since_interaction < 1000:  # User interacted recently
                self.reset_idle_sequence()
    
    def start_idle_dance_sequence(self):
        """Start the 1-minute dance sequence."""
        dancing_animations = self.mascot.animation_loader.get_animations_by_category('dancing')
        if dancing_animations:
            self.idle_sequence_state = 'dancing'
            self.dance_start_time = time.time()
            self.mascot.idle_timer.stop()  # Stop normal idle timer
            self.mascot.start_animation(random.choice(dancing_animations), loop=True)
    
    def start_idle_walking_sequence(self):
        """Start the random walking sequence after dancing."""
        self.idle_sequence_state = 'walking'
        self.dance_start_time = None
        self.perform_walking_action()
        
        # Set up timer for random walking actions
        min_interval = config.get_setting('behavior', 'walking_action_min_interval', 2000)
        max_interval = config.get_setting('behavior', 'walking_action_max_interval', 5000)
        QTimer.singleShot(random.randint(min_interval, max_interval), self.perform_walking_action)
    
    def perform_walking_action(self):
        """Perform a walking action during idle sequence."""
        if self.idle_sequence_state != 'walking':
            return
        
        walking_animations = self.mascot.animation_loader.get_animations_by_category('walking')
        if walking_animations:
            selected_animation = random.choice(walking_animations)
            self.mascot.start_animation(selected_animation, loop=False)
            
            # Schedule next walking action
            min_interval = config.get_setting('behavior', 'walking_action_min_interval', 2000)
            max_interval = config.get_setting('behavior', 'walking_action_max_interval', 5000)
            QTimer.singleShot(random.randint(min_interval, max_interval), self.perform_walking_action)
    
    def reset_idle_sequence(self):
        """Reset the idle sequence to waiting state."""
        self.idle_sequence_state = 'waiting'
        self.dance_start_time = None
        self.return_to_idle()
    
    def on_user_interaction(self):
        """Called when user interacts with the mascot."""
        # Auto-stop eternal dance mode when any action is triggered
        if self.eternal_dance_mode:
            self.stop_eternal_dance()
            return  # Let stop_eternal_dance handle the state reset
        
        # Auto-stop sleep mode when any action is triggered
        if self.mascot.is_sleeping:
            self.mascot.set_sleep_mode(False, auto_stop=True)
            return  # Let set_sleep_mode handle the state reset
        
        # Auto-stop fall mode when any action is triggered
        if getattr(self.mascot, 'is_falling', False):
            self.mascot.set_fall_mode(False, auto_stop=True)
            return  # Let set_fall_mode handle the state reset
        
        # Stop random walking when user interactions occur
        self.stop_random_walking_system()
        
        self.last_user_interaction = time.time()
        if self.idle_sequence_state != 'waiting':
            self.reset_idle_sequence()
    
    def start_eternal_dance(self):
        """Start eternal dance mode - mascot will dance continuously."""
        # Auto-stop sleep mode if active
        if self.mascot.is_sleeping:
            self.mascot.set_sleep_mode(False, auto_stop=True)
        
        # Auto-stop fall mode if active
        if getattr(self.mascot, 'is_falling', False):
            self.mascot.set_fall_mode(False, auto_stop=True)
        
        self.eternal_dance_mode = True
        self.stop_random_walking_system()
        self.reset_idle_sequence()  # Stop any idle sequence
        # Get dancing animations and start one
        dancing_animations = self.mascot.animation_loader.get_animations_by_category('dancing')
        if dancing_animations:
            self.mascot.start_animation(dancing_animations[0], loop=True)
    
    def stop_eternal_dance(self):
        """Stop eternal dance mode and return to normal behavior."""
        self.eternal_dance_mode = False
        # Restart random walking if no other special modes are active
        if (self.random_walking_enabled and not self.timed_dance_mode and 
            not getattr(self.mascot, 'is_falling', False)):
            self.start_random_walking_system()
        self.on_user_interaction()  # Reset interaction timer
        self.return_to_idle()
    
    def start_timed_dance(self, duration_ms=60000):
        """Start timed dance mode - mascot will dance for specified duration."""
        self.timed_dance_mode = True
        self.stop_random_walking_system()
        self.reset_idle_sequence()  # Stop any idle sequence
        # Get dancing animations and start one
        dancing_animations = self.mascot.animation_loader.get_animations_by_category('dancing')
        if dancing_animations:
            self.mascot.start_animation(dancing_animations[0], loop=True)
        # Start timer to stop dancing after duration
        self.timed_dance_timer.start(duration_ms)
    
    def stop_timed_dance(self):
        """Stop timed dance mode and return to normal behavior."""
        self.timed_dance_mode = False
        self.timed_dance_timer.stop()
        # Restart random walking if no other special modes are active
        if (self.random_walking_enabled and not self.eternal_dance_mode and 
            not getattr(self.mascot, 'is_falling', False)):
            self.start_random_walking_system()
        self.on_user_interaction()  # Reset interaction timer
        self.return_to_idle()

    # Idle mode functionality removed
    
    def get_current_state(self):
        """Get current state information."""
        return {
            'behavior_mode': self.current_behavior_mode,
            'last_action': self.last_action,
            'is_sleeping': self.mascot.is_sleeping,
            'is_following_mouse': self.mascot.is_following_mouse,
            'idle_sequence_state': self.idle_sequence_state,
            'eternal_dance_mode': self.eternal_dance_mode,
            # idle_mode_enabled removed
            'current_animation': self.mascot.current_animation['frames'][0] if self.mascot.current_animation else None
        }