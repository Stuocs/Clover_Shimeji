# 🦊🔫🤠 Clover Shimeji - Desktop Pet

  

**Clover Desktop Pet** (also known as Clover Shimeji) is an interactive desktop companion featuring Clover from Undertale Yellow. This adorable desktop mascot brings the beloved character to life on your screen with authentic animations, interactive behaviors, and charming personality traits that fans of Undertale Yellow will instantly recognize.

  

## What Does Clover Do?

  
Clover is your personal desktop companion that lives on your screen and interacts with you throughout your day. Here's everything this little cowboy can do:

  

### **Authentic Character Animations**

- **Walking Animations**: Clover walks around your desktop in all four directions (up, down, left, right) with smooth, game-accurate sprites

- **Running Animations**: When excited or following your mouse, Clover can run with increased speed

- **Sitting Animations**: Clover sits down peacefully, sometimes in different poses including a casual sitting position

- **Dancing Animations**: Clover performs the iconic dance moves from Undertale Yellow

- **Lying Down/Sleeping**: When in sleep mode, Clover gets eepy and sleep

- **Special Poses**: Various character poses and expressions from the game

- **Character Interactions**: Animations featuring interactions with other Undertale Yellow characters

- **Gun Animations**: Combat-related animations featuring Clover's weapon

- **Falling Animations**: Dynamic falling sequences when Clover drops from heights

- **Cart Animations**: Clover riding in a cart (And the whale)

- **Wind Effects**: Clover reacting to wind with flowing movements

  
### **Interactive Behaviors**

- **Drag and Drop**: Click and drag Clover anywhere on your screen - they'll follow your mouse smoothly

- **Right-Click Menu**: Access a comprehensive menu with all interaction options

- **Mouse Following**: Clover can follow your mouse cursor around the screen like a loyal companion

- **Intelligent Idle System**: When left alone, Clover has a sophisticated behavior system:

  - **Initial Idle**: Performs random actions every 3-8 seconds (sitting, walking, posing)

  - **Idle Sequence Trigger**: After 5 seconds of no interaction, enters special sequence

  - **Dance Phase**: Dances continuously for 60 seconds

  - **Exploration Phase**: Begins walking around your desktop randomly

  - **User Interaction Reset**: Any click, drag, or menu action returns to normal idle mode

  

### **Special Modes**

- **Eternal Dance Mode**: Toggle continuous dancing that overrides all other behaviors

- **Sleep Mode**: Clover gets eepy and go to sleep

- **Character Interaction Mode**: Access special animations featuring other Undertale Yellow characters

- **Size Scaling**: Adjust Clover's size from Normal to Giant (5 different size options)

* **Minigames**: You can play two differents minigames with our beloved cowboy
  

### **User Interaction System**

- **Left-Click + Drag**: Smoothly move Clover to any position on your screen

- **Right-Click Context Menu**: Access all features and modes

- **Automatic Positioning**: Clover stays within screen boundaries and handles multi-monitor setups

- **Non-Intrusive Design**: Clover appears above other windows but doesn't interfere with your work

- **Transparent Background**: Seamlessly integrates with your desktop wallpaper

  

### **Visual Features**

- **Pixel-Perfect Sprites**: All original sprites from Undertale Yellow, maintaining authentic pixel art style

- **Smooth Animations**: Fluid frame-by-frame animations with proper timing

- **Anti-Aliasing**: Optional smooth rendering for crisp visuals at any size

- **Transparency Support**: True transparency with no background artifacts

- **Multi-Monitor Support**: Works across multiple displays

  

## Step-by-Step Usage Guide

### Getting Started

1. **Launch the Application**: Run the executable or Python script (If you want to run the python script, you may want to read "SPRITES.md"

2. **First Appearance**: Clover appears on your screen in a default position (Top left)

3. **Initial Behavior**: Clover starts in idle mode, performing random actions

  

### Basic Interactions

1. **Moving Clover**:

   - Left-click on Clover and hold

   - Drag to your desired position

   - Release to place Clover there

   - Clover will remember this position as their new "home"

  

2. **Accessing the Menu**:

   - Right-click on Clover

   - A context menu appears with all available options

   - Click any option to activate it

   - Click elsewhere to close the menu

  

### Detailed Feature Walkthrough

#### **Dance Forever Mode**

1. Right-click on Clover

2. Select "Dance Forever" from the menu

3. Clover immediately starts dancing and continues indefinitely

4. The menu option changes to "Stop Dancing"

5. Select "Stop Dancing" to return to normal behavior

6. **Note**: This mode overrides all other behaviors including idle sequences

  
#### **Follow Mouse Mode**

1. Right-click on Clover

2. Select "Follow Mouse" from the menu

3. Clover will smoothly follow your mouse cursor around the screen

4. **Behavior**: Clover maintains a small distance from the cursor and moves smoothly


#### **Sleep Mode**

1. Right-click on Clover

2. Select "Sleep" from the menu

3. Clover lies down and displays "zzz" sleep indicators

4. Minimal CPU usage and animation activity

5. Select "Wake Up" from the menu to return to normal behavior

6. **Perfect for**: When you want Clover present but inactive

  

#### **Size Adjustment**

1. Right-click on Clover

2. Hover over "Size" to see the submenu

3. Current size is displayed in the menu title (e.g., "Size (Current: Normal)")

4. Available options:

   - **Normal**: 1x scale (original size)

   - **Large**: 1.5x scale

   - **Extra Large**: 2x scale

   - **Huge**: 2.5x scale

   - **Giant**: 3x scale
   
   - **Extra Giant**: 5x scale
   
   - **Screen**: Yes

5. Click any size to apply immediately

6. **Note**: All animations work perfectly at any size (**Except for screen size**)


#### **Character Interactions**

1. Right-click on Clover

2. Select "Character" from the menu

3. Access special animations featuring:

   - Interactions with other Undertale Yellow characters

   - Story moments and scenes

   - Character-specific poses and expressions

4. These animations play once and return to normal behavior

  

#### **Understanding Idle Behavior**

1. **Normal Idle** (default state):

   - Clover performs random actions every 3-8 seconds

   - Actions include: sitting, walking short distances, posing, nodding

   - Completely random selection keeps Clover unpredictable and charming

  

2. **Idle Sequence** (triggered after 5 seconds of no interaction):

   - **Phase 1**: Clover starts dancing continuously

   - **Duration**: Dances for exactly 60 seconds

   - **Phase 2**: Begins random walking around the desktop

   - **Walking Behavior**: Moves in random directions, changes direction periodically

   - **Reset Condition**: Any user interaction (click, drag, menu) returns to normal idle

  

3. **Interaction Detection**:

   - Left-clicking and dragging Clover

   - Right-clicking to open the menu

   - Selecting any menu option

   - **Result**: Immediately cancels idle sequence and returns to normal behavior

  

## Installation


### Option 1: Download Executable (Recommended)

1. Download the latest release from the releases page

2. Extract the ZIP file to your desired location

3. Run `CloverMascot.exe`

4. Clover will appear on your desktop immediately!

  

### Option 2: Run from Source

#### Prerequisites

- Python 3.8 or higher

- Windows 10/11 (primary support, it works on linux too)

- At least 50MB free RAM (Or a potato, you choose)

#### Installation Steps

1. **Clone the Repository**:

   ```bash

   git clone https://github.com/Stuocs/Clover_Shimeji.git

   cd Clover_Shimeji

   ```

  

2. **Install Dependencies**:

   ```bash

   pip install -r requirements.txt

   ```


3. **Run the Application**:

   ```bash

   python main.py

   ```

#### Building Your Own Executable

To create a standalone executable:

```bash

python build.py

```

The executable will be created in the `dist/` directory.

  

### System Requirements

- **OS**: Windows 10/11 (primary), Linux

- **RAM**: Minimum 50MB, Recommended 100MB (potato)

- **CPU**: Any modern processor (very low CPU usage) (Yep, a potato)

- **Graphics**: Basic 2D graphics support (You guessed it a potato)

- **Disk Space**: 50MB (Another potato)

  

## Usage

### Basic Controls


- **Left-click and drag**: Move the mascot around the screen

- **Right-click**: Open the context menu with options:

  - **Dance Forever**: Toggle eternal dance mode - Clover will dance continuously until deactivated

  - **Follow Mouse**: Toggle mouse following mode

  - **AFK Mode**: Return to automatic random actions

  - **Sleep**: Put the mascot to sleep (minimal activity)

  - **Size**: Change Clover's display size

  - **Character**: Access character interaction animations

  - **Exit**: Close the application

  

### Behavior Modes

  

1. **Idle Mode** (default): The mascot performs random actions every 3-8 seconds

2. **Idle Sequence**: When no user interaction occurs:

   - After 5 seconds: Starts dancing continuously for 1 minute

   - After dance ends: Begins random walking around the screen

   - Continues until user interacts (click, drag, or menu action)

3. **Follow Mouse Mode**: The mascot smoothly follows your mouse cursor

4. **Sleep Mode**: The mascot lies down and stops most activities

  

### Eternal Dance Mode

  

Clover can be set to dance continuously:

- Right-click and select "Dance Forever" to enable eternal dance mode

- Clover will dance continuously, overriding all other behaviors

- The menu option changes to "Stop Dancing" when active

- Click "Stop Dancing" to return to normal behavior

- Eternal dance mode takes priority over idle sequences and random actions

  

### Size Scaling

  

Clover's display size can be adjusted:

- Right-click and select "Size" to access size options

- The current size is displayed in the menu title

- Size changes apply immediately and persist until changed again

- All animations and behaviors work at any size
  

### Advanced Features

- **Multi-Monitor Support**: Works seamlessly across multiple displays

- **DPI Awareness**: Scales properly on high-DPI displays

- **Window Management**: Stays above other windows without interfering

- **Crash Recovery**: Automatically restarts if unexpected errors occur

- **Hot Reload**: Development feature for real-time sprite updates

- **Configurable Settings**: Customizable through config.py (Have fun dear developer)


### Animation System

- **Frame-Perfect Timing**: Maintains consistent 60 FPS animation (Im lying lol)

- **Smooth Interpolation**: Fluid movement between positions

- **State Management**: Intelligent switching between animation states

- **Sprite Caching**: Pre-loads all animations for smooth playback

- **Anti-Aliasing**: Optional smooth rendering for crisp visuals

  

## Project Structure

  

```

Clover_Project/

├── main.py              # Main application entry point

├── config.py            # Configuration settings and constants

├── build.py             # Build script for creating executable

├── requirements.txt     # Python dependencies

├── .gitignore          # Git ignore file

├── README.md           # This documentation

├── core/               # Core application modules

│   ├── mascot.py       # Main mascot class and behavior logic

│   ├── animation.py    # Animation system and state management

│   └── sprite_loader.py # Sprite loading and caching system

├── utils/              # Utility modules

│   ├── screen.py       # Screen positioning and multi-monitor support

│   └── menu.py         # Right-click context menu implementation

├── watcher/            # Development utilities

│   └── file_watcher.py # Hot reload functionality for development

├── Sprites/            # All sprite assets (organized by animation type)

│   ├── walking/        # Walking animations (all directions)

│   ├── sitting/        # Sitting and resting animations

│   ├── dancing/        # Dancing and celebration animations

│   ├── sleeping/       # Sleep mode animations

│   ├── character/      # Character interaction sprites

│   └── [other dirs]    # Additional animation categories

└── assets/             # Application resources

    ├── clover_premium.ico # High-quality application icon

    └── sprites/        # Additional sprite resources

```

  

## Configuration


You can customize Clover's behavior by editing `config.py`:
  

```python

# Animation timing

DEFAULT_FRAME_RATE = 150          # ms per frame (≈ 6.66 FPS)
IDLE_ACTION_MIN_INTERVAL = 3000  # ms between idle actions
IDLE_ACTION_MAX_INTERVAL = 8000  # ms between idle actions
DANCE_SEQUENCE_DURATION = 60000  # ms of dancing in idle sequence

# Visual settings

DEFAULT_SCALE = 2.5               # Initial sprite scale
ANTI_ALIASING = True              # Smooth rendering
TRANSPARENT_BACKGROUND = True     # Transparent background

# Behavior settings

MOUSE_PROXIMITY_THRESHOLD = 100   # Distance in px to consider the mouse "near"
MOUSE_FOLLOW_SPEED = 3            # Speed in px per update
MOUSE_FOLLOW_UPDATE_RATE = 50     # ms between position updates
IDLE_SEQUENCE_TRIGGER_TIME = 5000 # ms before starting idle sequence

```

  

## Adding New Animations

  

To add new animations:

  

1. Create a new folder in the `Sprites` directory

2. Add numbered image files (0.png, 1.png, 2.png, etc.)

3. The animation will be automatically loaded on next startup

  

### Animation Categories

  

- **sitting**: Idle sitting animations

- **walking**: Movement animations (can have subdirectories for directions)

- **dancing**: Dance animations

- **lying**: Sleeping/lying down animations

- **poses**: Special pose animations

- **characters_interactions**: Character interaction scenes



## Troubleshooting

### Common Issues

1. **Clover doesn't appear**: Check if running as administrator is required

2. **Clover disappears**: Check if moved off-screen, restart application

3. **Menu doesn't work**: Try right-clicking directly on Clover's sprite

4. **Animation stuttering**: Close other resource-intensive applications


### System Requirements

  

- **Windows**: Windows 7 or later

- **Linux**: X11 window system with compositing support

- **RAM**: Minimum 50MB available

- **CPU**: Any modern processor

  

## License


This project is for educational and personal use. Sprite assets are from Undertale Yellow.

  

## Contributing

  

We welcome contributions! Here's how you can help:

  

1. **Report Bugs**: Open an issue with detailed reproduction steps

2. **Suggest Features**: Share your ideas for new animations or behaviors

3. **Submit Code**: Fork the repository and submit pull requests

4. **Create Sprites**: Design new animations following the existing style (I will gladly add more animations if you share with me the sprites, DM me in [reddit](https://www.reddit.com/user/Kair-Os/) please ^^ )

5. **Improve Documentation**: Help make the README even better

  

### Development Setup

1. Fork the repository

2. Create a feature branch: `git checkout -b feature-name`

3. Make your changes

4. Test thoroughly

5. Submit a pull request

  

## License


This project is created for educational and entertainment purposes. The code is open source, but please respect the original creators' rights to the character designs and sprites.

  

## Credits and Acknowledgments

  

### **Primary Credits**

**All sprites, character designs, and Clover-related content used in this project are the intellectual property of Team Undertale Yellow (@TeamUTY)**

  

- **Game**: Undertale Yellow

- **Character**: Clover (R.I.P. Little Deputy)

- **Original Creators**: Team Undertale Yellow (@TeamUTY)

- **Sprite Artists**: The talented pixel artists of Team Undertale Yellow

- **Character Design**: Team Undertale Yellow development team

  

### **Specific Acknowledgments**

- **Clover Character Sprites**: All walking, sitting, dancing, sleeping, and character interaction sprites are original assets from Undertale Yellow

- **Animation Frames**: Every animation frame used in this desktop pet is sourced from the official Undertale Yellow game files

- **Character Personality**: Clover's behaviors and animations reflect the authentic character from Undertale Yellow

- **Artistic Style**: The pixel art style and color palette maintain the original Undertale Yellow aesthetic

  

### **Team Undertale Yellow**

Undertale Yellow is a fan-made prequel to Undertale, created by a dedicated team of developers, artists, musicians, and writers. This desktop pet project serves as a tribute to their incredible work and the beloved character of Clover.

  

**Official Team Undertale Yellow Links**:

- [Twitter/X: @TeamUTY](https://x.com/UndertaleYellow)

- [Official Website](https://gamejolt.com/games/UndertaleYellow/136925)

  

### **Desktop Pet Development**

- **Programming**: Desktop pet implementation and behavior system

- **Integration**: Adaptation of game sprites for desktop pet functionality

- **UI/UX**: Context menu and interaction system design

- **Optimization**: Performance optimization for desktop use

  

### **Special Thanks**

- Team Undertale Yellow for creating such an amazing character and game

- The Undertale community for their continued support and creativity

- Shimeji desktop pet creators for inspiring the desktop companion concept

- All beta testers and contributors who helped improve this project (That we are 2 friends and me lol)

  

### **Disclaimer**

This desktop pet is a fan-made tribute project and is not officially affiliated with Team Undertale Yellow. All character rights, sprites, and related intellectual property belong to Team Undertale Yellow. This project is created with respect and admiration for their work.



**Please support the official Undertale Yellow game and Team Undertale Yellow's work!**


[![Buy Me A Coffee](https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png)](https://www.buymeacoffee.com/alfredoespp)

# IMPORTANT

> This project requires the original **Undertale Yellow** sprites.
> You can extract them from your legitimate copy of the game using the [Undertale Mod Tool](https://github.com/UnderminersTeam/UndertaleModTool).
> Place the extracted files in the `Sprites/` folder before running the program.
> If you want to avoid this, download the binary from releases.

# All the donations will be used to support this project and future ones (If someone wanna help).





