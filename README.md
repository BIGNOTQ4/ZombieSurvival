# Zombie Survival

A top-down 2D zombie survival game made with Python and Pygame. Survive waves of zombies, fight boss waves, collect power-ups, switch weapons, and choose upgrades between waves.

## Controls

- `WASD`: Move
- `Mouse`: Aim
- `Left Click`: Shoot
- `R`: Reload
- `1`: Pistol
- `2`: SMG
- `3`: Shotgun
- `ESC`: Pause

## Features

- Main menu, settings menu, controls screen, pause menu, and game over screen
- Easy, Normal, and Hard difficulty settings
- Pistol, SMG, and Shotgun weapon system
- Ammo, reloads, weapon switching, and weapon-specific fire behavior
- Multiple zombie types: Normal, Fast, Tank, and Boss
- Boss waves every 5th wave with boss health bar and charge attack
- Upgrade selection after each completed wave
- Power-up drops: Health Pack, Ammo Pack, Rapid Fire, Damage Boost, and Speed Boost
- High score saving
- Settings saving
- Shape-based visuals with no required external image or sound assets

## How To Run From Source

Install Python 3.10 or newer, then run:

```powershell
pip install -r requirements.txt
python main.py
```

The game creates `settings.json` and `high_score.json` automatically if they are missing.

## How To Build An EXE

Install PyInstaller:

```powershell
pip install pyinstaller
```

Build the game:

```powershell
pyinstaller --onefile --windowed --name ZombieSurvival main.py
```

The built executable will be created in the `dist` folder. When running as an EXE, `settings.json` and `high_score.json` are saved next to the executable.

Optional sound files can be placed in a `sounds` folder next to `main.py` or next to the built executable:

- `shoot.wav`
- `reload.wav`
- `zombie_hit.wav`
- `zombie_death.wav`
- `powerup.wav`
- `boss_wave.wav`
- `player_damage.wav`

Missing sound files are ignored safely, so the game runs without them.
