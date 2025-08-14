# Clover Shimeji - Sprite Assets Documentation

## Overview

This document provides a comprehensive guide for recreating the sprite assets required for the Clover Desktop Mascot application. Due to copyright restrictions, the original sprite files from Undertale Yellow cannot be distributed with this repository. Users must obtain and organize their own sprite assets following the structure outlined below.

## ⚠️ Important Legal Notice

**All sprite assets are the intellectual property of Team Undertale Yellow (@TeamUTY)**. This application is a fan-made project that requires users to:

1. **Legally obtain** sprite assets from Undertale Yellow
2. **Extract and organize** them according to this documentation
3. **Respect copyright** - do not redistribute the sprite files
4. **Credit the creators** - Team Undertale Yellow for all character designs and artwork

## 📁 Required Directory Structure

The `Sprites/` directory must contain the following structure with **exactly** these folder names:

```
Sprites/
├── Characters_interactions/     (288 files)
├── basket/                     (6 files)
├── cart/                       (4 files)
├── dancing!/                   (6 files)
├── dying/                      (50 files)
├── edward walking/             (51 files)
├── falls/                      (18 files)
├── gun/                        (51 files)
├── lying/                      (5 files)
├── meme/                       (4 files)
├── sitting/                    (13 files)
└── walking/                    (36 files)
```

**Total: 532 sprite files across 12 directories**

### ⚠️ Note on Missing Directories

The application code references additional sprite categories that may be part of a complete sprite set:
- `climb/` - Climbing animations
- `ending/` - Ending sequence sprites  
- `geno/` - Additional genocide route sprites
- `goggles/` - Goggles-related sprites
- `nod/` - Nodding animations
- `poses/` - Additional pose sprites
- `who gave trash to the kid/` - Special interaction sprites

These directories are **optional** and the application will function without them, but including them may provide additional animation variety if available in your sprite extraction.

## 🎭 Detailed Sprite Categories

*The following 12 categories are **required** for basic functionality:*

### 1. **walking/** (36 files)
Basic movement animations for Clover in all directions.

**Required subdirectories:**
- `spr_pl_down/` - Walking downward (4 frames: `spr_pl_down_0.png` to `spr_pl_down_3.png`)
- `spr_pl_left/` - Walking left (2 frames: `spr_pl_left_0.png`, `spr_pl_left_1.png`)
- `spr_pl_right/` - Walking right (2 frames: `spr_pl_right_0.png`, `spr_pl_right_1.png`)
- `spr_pl_up/` - Walking upward (4 frames: `spr_pl_up_0.png` to `spr_pl_up_3.png`)
- `spr_pl_run_down/` - Running downward (6 frames: `spr_pl_run_down_0.png` to `spr_pl_run_down_5.png`)
- `spr_pl_run_left/` - Running left (6 frames: `spr_pl_run_left_0.png` to `spr_pl_run_left_5.png`)
- `spr_pl_run_right/` - Running right (6 frames: `spr_pl_run_right_0.png` to `spr_pl_run_right_5.png`)
- `spr_pl_run_up/` - Running upward (6 frames: `spr_pl_run_up_0.png` to `spr_pl_run_up_5.png`)

### 2. **sitting/** (13 files)
Various sitting and relaxed poses for idle behavior.

**Required files/subdirectories:**
- `spr_clover_casual.png` - Single casual sitting sprite
- `spr_clover_sitting/` - Standard sitting animation (4 frames: `spr_clover_sitting_0.png` to `spr_clover_sitting_3.png`)
- `spr_clover_sit_dark/` - Dark sitting variation (4 frames: `spr_clover_sit_dark_0.png` to `spr_clover_sit_dark_3.png`)
- `spr_colver_wind/` - Wind-affected sitting (4 frames: `spr_colver_wind_0.png` to `spr_colver_wind_3.png`)

### 3. **dancing!/** (6 files)
Energetic dance animations for the "Dance Forever" mode.

**Required subdirectory:**
- `spr_pl_dance/` - Dance animation sequence (6 frames: `spr_pl_dance_0.png` to `spr_pl_dance_5.png`)

### 4. **lying/** (5 files)
Sleep mode and lying down animations.

**Required files:**
- `spr_pl_lying_0.png` - Clover lying down
- `spr_bed_dark_nosheet_0.png` - Bed/surface sprite
- `spr_zzz_0.png`, `spr_zzz_1.png`, `spr_zzz_2.png` - Sleep effect sprites

### 5. **falls/** (18 files)
Falling and tumbling animations.

**Required files:**
- `spr_falldown_0.png` through `spr_falldown_17.png` - Complete falling sequence (18 frames)

### 6. **gun/** (51 files)
Genocide route and weapon-related animations.

**Required files:**
- `spr_clover_geno_summon_0.png` through `spr_clover_geno_summon_23.png` - Gun summoning (24 frames)
- `spr_clover_geno_unsummon_0.png` through `spr_clover_geno_unsummon_11.png` - Gun unsummoning (12 frames)
- `spr_heart_yellow_shot_0.png` through `spr_heart_yellow_shot_4.png` - Heart shot effects (5 frames)
- `spr_shot_strong_0.png` through `spr_shot_strong_9.png` - Strong shot effects (10 frames)

### 7. **dying/** (50 files)
Death and dramatic sequence animations.

**Required files:**
- Numbered sequences: `0 (1).png` through `0 (19).png` (19 frames)
- Numbered sequences: `1 (1).png` through `1 (14).png` (14 frames)
- Numbered sequences: `2 (1).png` through `2 (17).png` (17 frames)

### 8. **Characters_interactions/** (288 files)
Complex character interaction sequences.

**Required subdirectories:**
- `hug/` - Hugging animations with numbered sequences and sprite folders
- `spr_clover_holds_ceroba/` - Clover holding Ceroba (44 frames: `spr_clover_holds_ceroba_0.png` to `spr_clover_holds_ceroba_43.png`)
- `spr_pacifist_ending_martlet_take_hat/` - Hat-taking sequence (37 frames: `spr_pacifist_ending_martlet_take_hat_0.png` to `spr_pacifist_ending_martlet_take_hat_36.png`)
- `spr_pacifist_ending_starlo_take_gun/` - Gun-taking sequence (49 frames: `spr_pacifist_ending_starlo_take_gun_0.png` to `spr_pacifist_ending_starlo_take_gun_48.png`)
- `spr_rooftop_fistbump_martlet/` - Fistbump interaction
- Various pacifist ending group hug/unhug sprite folders

### 9. **edward walking/** (51 files)
Special character interaction with Edward.

**Required subdirectories:**
- `spr_ed_grab_clover/` - Edward grabbing Clover (18 frames: `spr_ed_grab_clover_0.png` to `spr_ed_grab_clover_17.png`)
- `spr_ed_place_clover/` - Edward placing Clover (13 frames: `spr_ed_place_clover_0.png` to `spr_ed_place_clover_12.png`)
- `spr_ed_up_walk_clover/` - Edward walking up with Clover (4 frames: `spr_ed_up_walk_clover_0.png` to `spr_ed_up_walk_clover_3.png`)
- `spr_ed_down_walk_clover/` - Edward walking down with Clover (4 frames: `spr_ed_down_walk_clover_0.png` to `spr_ed_down_walk_clover_3.png`)
- `spr_ed_left_walk_clover/` - Edward walking left with Clover (4 frames: `spr_ed_left_walk_clover_0.png` to `spr_ed_left_walk_clover_3.png`)
- `spr_ed_right_walk_clover/` - Edward walking right with Clover (4 frames: `spr_ed_right_walk_clover_0.png` to `spr_ed_right_walk_clover_3.png`)
- `spr_clover_sit_dark/` - Related sitting sprites (4 frames: `spr_clover_sit_dark_0.png` to `spr_clover_sit_dark_3.png`)

### 10. **cart/** (4 files)
Cart-riding animations.

**Required subdirectory:**
- `spr_player_cart/` - Cart riding sequence (4 frames)

### 11. **meme/** (4 files)
Special meme-related animations.

**Required files:**
- `spr_player_cart__meme_0.png` through `spr_player_cart__meme_3.png` - Meme cart sequence (4 frames)

### 12. **basket/** (6 files)
Basket-related animations and interactions.

**Required files:**
- `spr_mail_whale_basket_with_clover_yellow_0.png` through `spr_mail_whale_basket_with_clover_yellow_5.png` - Mail whale basket sequence (6 frames)

## 🔧 Technical Requirements

### File Format
- **Format:** PNG with transparency
- **Color depth:** 32-bit RGBA recommended
- **Background:** Transparent
- **Compression:** Standard PNG compression

### Naming Conventions
- **Frame numbering:** Zero-indexed (starts from `_0.png`)
- **Exact naming:** File names must match exactly as specified
- **Case sensitivity:** Maintain exact case as shown
- **No spaces:** Use underscores instead of spaces

### Image Specifications
- **Typical size:** Varies by sprite (usually 16x16 to 64x64 pixels)
- **Pixel art style:** Maintain original pixel art aesthetic
- **Transparency:** Preserve alpha channel for proper desktop integration
- **Consistency:** Maintain consistent sprite dimensions within animation sequences

## 📋 Extraction Guide

### From Undertale Yellow Game Files

1. **Locate game installation** directory
2. **Find sprite assets** (typically in `data` or `sprites` folders)
3. **Extract using appropriate tools** (GameMaker Studio extractors, etc.)
4. **Organize according to this structure**
5. **Verify file counts** match the numbers specified above

### Verification Checklist

- [ ] All 12 main directories created
- [ ] File counts match specified numbers
- [ ] All files are PNG format with transparency
- [ ] Naming conventions followed exactly
- [ ] No missing frames in animation sequences
- [ ] Sprites maintain original quality and dimensions

## 🚀 Integration

Once sprites are properly organized:

1. Place the complete `Sprites/` directory in the project root
2. Run the application: `python main.py`
3. The animation loader will automatically detect and load all sprites
4. Verify animations work correctly through the right-click menu

## 🔍 Troubleshooting

### Common Issues

**Animation not playing:**
- Check file naming matches exactly
- Verify all frames in sequence are present
- Ensure PNG transparency is preserved

**Missing sprites:**
- Verify directory structure matches exactly
- Check file counts against this documentation
- Ensure case-sensitive naming is correct

**Performance issues:**
- Optimize PNG file sizes if needed
- Ensure sprites aren't excessively large
- Check for corrupted image files

## 🛠️ Quick Setup Verification

After organizing your sprites, run this quick verification:

```bash
# Navigate to project directory
cd /path/to/Clover_Project

# Run the application
python main.py
```

**Expected behavior:**
- Clover appears on desktop
- Right-click menu shows all options
- Walking animations work smoothly
- Dance mode activates properly
- Sleep mode functions correctly

## 📞 Support

For technical issues with sprite integration:
1. Verify your sprite organization matches this documentation
2. Check the application logs for specific error messages
3. Ensure you have legal access to Undertale Yellow assets
4. Verify all 532 files are present and properly named
5. Test with a minimal sprite set first (walking, sitting, dancing)

## 🙏 Credits

**All sprite assets and character designs:** Team Undertale Yellow (@TeamUTY)

**This documentation:** Created for the Clover Desktop Mascot fan project

**Legal compliance:** Users are responsible for obtaining sprites legally and respecting copyright

---

*This documentation is provided to help fans create their own desktop mascot experience while respecting the intellectual property rights of the original creators.*