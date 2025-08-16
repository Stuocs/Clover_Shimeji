#!/usr/bin/env python3
"""
Animation Loader - Handles loading and managing sprite animations
"""

import os
import glob
from PyQt5.QtGui import QPixmap
from utils.path_helper import get_sprites_path
import config

class AnimationLoader:
    """Loads and manages sprite animations from the assets directory."""
    
    def __init__(self):
        self.animations = {}
        self.categories = {}
        self.load_all_animations()
    
    def load_all_animations(self):
        """Load all animations from the sprites directory."""
        sprites_path = get_sprites_path()
        
        if not os.path.exists(sprites_path):
            print(f"Warning: Sprites directory not found at {sprites_path}")
            return
        
        # Scan all subdirectories in sprites folder
        for category_dir in os.listdir(sprites_path):
            category_path = os.path.join(sprites_path, category_dir)
            
            if not os.path.isdir(category_path):
                continue
            
            category_name = category_dir.lower().replace(' ', '_').replace('!', '').replace('-', '_')
            self.categories[category_name] = []
            
            # Check if this is a simple animation directory or has subdirectories
            subdirs = [d for d in os.listdir(category_path) if os.path.isdir(os.path.join(category_path, d))]
            
            if subdirs:
                # Has subdirectories (like walking/up, walking/down, etc.)
                for subdir in subdirs:
                    subdir_path = os.path.join(category_path, subdir)
                    animation_name = f"{category_name}_{subdir}"
                    self.load_animation_from_directory(animation_name, subdir_path)
                    self.categories[category_name].append(animation_name)
                
                # Also check for standalone PNG files in the same directory
                self.load_standalone_images(category_name, category_path)
            else:
                # Direct animation directory - check for special cases like gun sprites
                if category_name == 'gun':
                    self.load_gun_animations(category_name, category_path)
                else:
                    self.load_animation_from_directory(category_name, category_path)
                    self.categories[category_name].append(category_name)
    
    def load_standalone_images(self, category_name, directory_path):
        """Load standalone PNG files as single-frame animations."""
        import glob
        
        # Look for PNG files directly in the directory (not in subdirectories)
        png_files = glob.glob(os.path.join(directory_path, '*.png'))
        
        for png_file in png_files:
            filename = os.path.basename(png_file)
            # Remove .png extension to get animation name
            animation_name = os.path.splitext(filename)[0]
            
            # Load the single image as a one-frame animation
            from PyQt5.QtGui import QPixmap
            pixmap = QPixmap(png_file)
            if not pixmap.isNull():
                frame_rate = self.get_frame_rate_for_animation(animation_name)
                
                self.animations[animation_name] = {
                    'frames': [pixmap],
                    'frame_rate': frame_rate,
                    'loop': True
                }
                
                # Add to category
                self.categories[category_name].append(animation_name)
    
    def load_animation_from_directory(self, animation_name, directory_path):
        """Load an animation from a specific directory."""
        # Look for image files
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(directory_path, ext)))
        
        if not image_files:
            return
        
        # Sort files naturally (0.png, 1.png, 2.png, etc.)
        image_files.sort(key=lambda x: self.natural_sort_key(os.path.basename(x)))
        
        # Load frames
        frames = []
        for image_file in image_files:
            pixmap = QPixmap(image_file)
            if not pixmap.isNull():
                frames.append(pixmap)
        
        if frames:
            # Determine frame rate based on animation type
            frame_rate = self.get_frame_rate_for_animation(animation_name)
            
            self.animations[animation_name] = {
                'frames': frames,
                'frame_rate': frame_rate,
                'loop': True
            }
    
    def load_gun_animations(self, category_name, directory_path):
        """Load gun animations, separating different sprite types."""
        # Look for image files
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(directory_path, ext)))
        
        if not image_files:
            return
        
        # Group files by animation type based on filename patterns
        animation_groups = {}
        
        for image_file in image_files:
            filename = os.path.basename(image_file)
            
            # Determine animation type based on filename
            if 'clover_geno_unsummon' in filename:
                anim_type = 'spr_clover_geno_unsummon'
            elif 'clover_geno_summon' in filename:
                anim_type = 'spr_clover_geno_summon'
            elif 'heart_yellow_shot' in filename:
                anim_type = 'spr_heart_yellow_shot'
            elif 'shot_strong' in filename:
                anim_type = 'spr_shot_strong'
            else:
                # Default grouping for unknown patterns
                anim_type = 'unknown'
            
            if anim_type not in animation_groups:
                animation_groups[anim_type] = []
            animation_groups[anim_type].append(image_file)
        
        # Create separate animations for each group
        for anim_type, files in animation_groups.items():
            if anim_type == 'unknown':
                continue  # Skip unknown patterns
            
            # Sort files naturally
            files.sort(key=lambda x: self.natural_sort_key(os.path.basename(x)))
            
            # Load frames
            frames = []
            for image_file in files:
                pixmap = QPixmap(image_file)
                if not pixmap.isNull():
                    frames.append(pixmap)
            
            if frames:
                animation_name = f"{category_name}_{anim_type}"
                frame_rate = self.get_frame_rate_for_animation(animation_name)
                
                self.animations[animation_name] = {
                    'frames': frames,
                    'frame_rate': frame_rate,
                    'loop': True
                }
                
                # Add to category
                if category_name not in self.categories:
                    self.categories[category_name] = []
                self.categories[category_name].append(animation_name)
    
    def natural_sort_key(self, filename):
        """Generate a key for natural sorting of filenames."""
        import re
        # Extract numbers from filename for proper sorting
        parts = re.split(r'(\d+)', filename)
        return [int(part) if part.isdigit() else part for part in parts]
    
    def get_frame_rate_for_animation(self, animation_name):
        """Get appropriate frame rate based on animation type."""
        # Different animations have different optimal frame rates
        if 'walking' in animation_name or 'run' in animation_name:
            return config.get_setting('animation', 'walking_frame_rate', 120)
        elif 'dancing' in animation_name:
            return config.get_setting('animation', 'dancing_frame_rate', 100)
        elif 'sitting' in animation_name:
            return config.get_setting('animation', 'sitting_frame_rate', 200)
        elif 'meme' in animation_name:
            return config.get_setting('animation', 'meme_frame_rate', 150)
        elif 'lying' in animation_name:
            return config.get_setting('animation', 'lying_frame_rate', 200)
        elif 'nod' in animation_name:
            return config.get_setting('animation', 'nod_frame_rate', 150)
        else:
            return config.get_setting('animation', 'default_frame_rate', 150)
    
    def get_animation(self, animation_name):
        """Get a specific animation by name."""
        return self.animations.get(animation_name)
    
    def get_animations_by_category(self, category):
        """Get all animations in a specific category."""
        category = category.lower().replace(' ', '_')
        return self.categories.get(category, [])
    
    def get_all_animations(self):
        """Get list of all available animation names."""
        return list(self.animations.keys())
    
    def get_all_categories(self):
        """Get list of all available categories."""
        return list(self.categories.keys())
    
    def get_random_animation_from_category(self, category):
        """Get a random animation from a specific category."""
        import random
        animations = self.get_animations_by_category(category)
        if animations:
            return random.choice(animations)
        return None
    
    def animation_exists(self, animation_name):
        """Check if an animation exists."""
        return animation_name in self.animations
    
    def get_animation_info(self, animation_name):
        """Get information about an animation."""
        animation = self.get_animation(animation_name)
        if animation:
            return {
                'name': animation_name,
                'frame_count': len(animation['frames']),
                'frame_rate': animation['frame_rate'],
                'loops': animation['loop']
            }
        return None