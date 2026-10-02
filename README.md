# Mythoskull Payload Builder

A desktop GUI for authoring **DuckyScript** payloads for the **Kraken HID** (and any
pico-ducky style CircuitPython HID device). Build a payload with the command palette,
watch a live preview of exactly what the board will do, validate it against the
interpreter, then export `payload.dd` or deploy it straight to a connected board.

> ⚠️ **Authorized use only.** This tool builds keystroke scripts for a USB HID device.
> Run payloads only on systems you own or have written permission to test. You are
> responsible for how you use what you build.

---

## Features

- **Command palette** — Text, Timing, Keys, and Combos, inserted with one click
- **Live preview** — every line translated to a plain-English action before you deploy
- **Validation** — unsupported commands are flagged so the board never silently skips a line
- **Templates** — benign starters (Notepad banner, type-a-message, open-website, terminal echo)
- **Export** — save `payload.dd`, or **Deploy to Kraken** writes it straight to the `CIRCUITPY` drive
- **Zero dependencies** — pure Python standard library (Tkinter)

## Requirements

- **Python 3.8+** with Tkinter
  - **Windows / macOS:** included with the official [python.org](https://www.python.org/downloads/) installer
  - **Linux:** install Tkinter if missing — `sudo apt install python3-tk`

## Run it

**Windows:** double-click `run.bat`, or:
```powershell
python payload_builder.py
```

**macOS / Linux:**
```bash
./run.sh
# or
python3 payload_builder.py
```

## Flash a board (firmware)

The `firmware/` folder has the matching CircuitPython interpreter.

1. Flash CircuitPython onto the Pico (hold **BOOTSEL**, plug in, drop the `.uf2` on the
   `RPI-RP2` drive). Get the `.uf2` from [circuitpython.org](https://circuitpython.org/board/raspberry_pi_pico/).
2. Copy `firmware/code.py` and `firmware/payload.dd` onto the `CIRCUITPY` drive.
3. Copy the `adafruit_hid` library into `CIRCUITPY/lib/` (from the matching
   [CircuitPython library bundle](https://circuitpython.org/libraries) for your CP version).
4. Replug the board to run.

## Supported DuckyScript

| Command | Meaning |
|---|---|
| `STRING <text>` | Type text |
| `STRINGLN <text>` | Type text, then press Enter |
| `DELAY <ms>` | Wait |
| `DEFAULT_DELAY <ms>` | Pause added after every command |
| `STRING_DELAY <ms>` | Pause between each typed character |
| `REM <text>` / `// <text>` | Comment (ignored) |
| `ENTER`, `TAB`, `ESC`, `UP`, `F4`, … | Single key |
| `GUI r`, `CTRL ALT DELETE`, `ALT F4`, … | Key combo (space-separated) |

## Build a standalone .exe (optional)

For customers who don't have Python, build a single-file executable with PyInstaller:

```powershell
pip install pyinstaller
.\build_exe.ps1
```
The `.exe` lands in `dist/`.

## License

MIT — see [LICENSE](LICENSE).

---

Mythoskull Hardware · Kraken HID · built by Joshua Burton ([p01yg107](https://github.com/p0lygl07))
