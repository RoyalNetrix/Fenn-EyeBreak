# Eye break for Fenn

A 20-20-20 reminder on your Fenn notch.

## What it does

- Every 20 minutes (choose 20, 30, 45 or 60) the notch pops open, the pill pulses and a sound plays: look at something 20 ft (6 m) away for 20 seconds.
- When the 20 seconds end, the notch closes by itself and the timer restarts.
- Wide tile: a ring with the minutes left until the next break.
- Page: pause/resume, Break now, the interval chips, and **Pop up** and **Sound** switches.
- Don't want the notch to pop open? Turn **Pop up** off. The pill still pulses (and the sound still plays), and the countdown shows on the tile.

## Install

1. Copy this folder to `%APPDATA%\Fenn\plugins\eyebreak\` so that `plugin.toml` and `main.py` sit directly inside it.
2. In Fenn, open **Settings** and turn on **Plugin dev mode**. The tile appears within a few seconds, with no restart. (Without dev mode, restart Fenn.)
3. New tiles are added after the built-in ones, possibly on the second page. Use the pencil in the grid to move or resize it.

Requires Fenn with plugin support.

## Requirements

Python 3.8+ (Fenn can set it up for you, or use your own). No extra packages. The sound uses `winsound` (Windows); elsewhere it is silently skipped.

## Network and privacy

- None. Works fully offline.

## Settings and data

- Interval, Pop up and Sound are saved in `%APPDATA%\Fenn\plugin-data\eyebreak\config.json`.
- The break length is the `BREAK` constant (seconds) at the top of `main.py`.

## Limitations

- Timers are in memory: restarting Fenn restarts the countdown.
- With Pop up on, the notch is pinned open during a break, even over other windows. Fullscreen apps still hide Fenn.

## Troubleshooting

- **Tile says "Stopped":** hover it to see the error and the last lines of the plugin's output.
- **Nothing happens:** Fenn can set up Python for you. If that didn't work, make sure `python --version` works in a new PowerShell window, or install Python from python.org and tick "Add python.exe to PATH".
- **Full log:** the logs of the last ten Fenn runs are in `%APPDATA%\Fenn\logs`.
- **Plugins are programs.** They run with the same rights as Fenn. Read the code (it is one short file) before installing any plugin.

## Credits and license

MIT. See `LICENSE`.

## Files

- `plugin.toml`: the plugin manifest.
- `main.py`: the whole plugin.
- `LICENSE`, `.gitignore`.
