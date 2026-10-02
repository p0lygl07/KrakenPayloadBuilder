import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

# Give the host time to enumerate the HID device
time.sleep(2.0)

# Named keys usable alone or in a combo (e.g. "CTRL ALT DELETE", "ALT F4")
NAMED = {
    "ENTER": Keycode.ENTER, "RETURN": Keycode.ENTER,
    "TAB": Keycode.TAB, "SPACE": Keycode.SPACE,
    "ESC": Keycode.ESCAPE, "ESCAPE": Keycode.ESCAPE,
    "BACKSPACE": Keycode.BACKSPACE, "DELETE": Keycode.DELETE, "DEL": Keycode.DELETE,
    "UP": Keycode.UP_ARROW, "DOWN": Keycode.DOWN_ARROW,
    "LEFT": Keycode.LEFT_ARROW, "RIGHT": Keycode.RIGHT_ARROW,
    "UPARROW": Keycode.UP_ARROW, "DOWNARROW": Keycode.DOWN_ARROW,
    "LEFTARROW": Keycode.LEFT_ARROW, "RIGHTARROW": Keycode.RIGHT_ARROW,
    "HOME": Keycode.HOME, "END": Keycode.END,
    "PAGEUP": Keycode.PAGE_UP, "PAGEDOWN": Keycode.PAGE_DOWN,
    "INSERT": Keycode.INSERT, "CAPSLOCK": Keycode.CAPS_LOCK,
    "PRINTSCREEN": Keycode.PRINT_SCREEN,
    "GUI": Keycode.GUI, "WINDOWS": Keycode.GUI, "WIN": Keycode.GUI, "COMMAND": Keycode.GUI,
    "CTRL": Keycode.CONTROL, "CONTROL": Keycode.CONTROL,
    "SHIFT": Keycode.SHIFT, "ALT": Keycode.ALT, "OPTION": Keycode.ALT,
    "MENU": Keycode.APPLICATION, "APP": Keycode.APPLICATION,
    "F1": Keycode.F1, "F2": Keycode.F2, "F3": Keycode.F3, "F4": Keycode.F4,
    "F5": Keycode.F5, "F6": Keycode.F6, "F7": Keycode.F7, "F8": Keycode.F8,
    "F9": Keycode.F9, "F10": Keycode.F10, "F11": Keycode.F11, "F12": Keycode.F12,
}
DIGITS = {
    "0": Keycode.ZERO, "1": Keycode.ONE, "2": Keycode.TWO, "3": Keycode.THREE,
    "4": Keycode.FOUR, "5": Keycode.FIVE, "6": Keycode.SIX, "7": Keycode.SEVEN,
    "8": Keycode.EIGHT, "9": Keycode.NINE,
}

def token_to_code(tok):
    up = tok.upper()
    if up in NAMED:
        return NAMED[up]
    if len(tok) == 1 and tok.isalpha():
        return getattr(Keycode, up)   # A-Z
    if tok in DIGITS:
        return DIGITS[tok]
    return None

def send_combo(tokens):
    codes = []
    for t in tokens:
        c = token_to_code(t)
        if c is not None:
            codes.append(c)
    if codes:
        kbd.send(*codes)

def run_payload(filename):
    default_delay = 0.0
    string_delay = 0.0
    try:
        with open(filename, "r") as f:
            for raw in f:
                line = raw.rstrip("\r\n")
                stripped = line.strip()
                if not stripped or stripped.startswith("REM") or stripped.startswith("//"):
                    continue

                parts = stripped.split(" ", 1)
                cmd = parts[0].upper()
                args = parts[1] if len(parts) > 1 else ""
                # keep original (non-upper) args for STRING typing
                orig_args = line.split(" ", 1)[1] if " " in line else ""

                if cmd == "STRING":
                    if string_delay > 0:
                        for ch in orig_args:
                            layout.write(ch)
                            time.sleep(string_delay)
                    else:
                        layout.write(orig_args)
                elif cmd == "STRINGLN":
                    layout.write(orig_args)
                    kbd.send(Keycode.ENTER)
                elif cmd == "DELAY":
                    try:
                        time.sleep(float(args) / 1000.0)
                    except ValueError:
                        pass
                elif cmd in ("DEFAULT_DELAY", "DEFAULTDELAY"):
                    try:
                        default_delay = float(args) / 1000.0
                    except ValueError:
                        pass
                elif cmd in ("STRING_DELAY", "STRINGDELAY"):
                    try:
                        string_delay = float(args) / 1000.0
                    except ValueError:
                        pass
                elif cmd == "REPEAT":
                    pass  # handled inline by builders; no-op here
                else:
                    # Treat the whole line as a key or key-combo
                    # (ENTER, TAB, ALT F4, CTRL ALT DELETE, GUI r, etc.)
                    send_combo(stripped.split(" "))

                if default_delay > 0:
                    time.sleep(default_delay)
                time.sleep(0.01)
    except OSError:
        time.sleep(1)
        kbd.send(Keycode.GUI, Keycode.R)
        time.sleep(0.4)
        layout.write("notepad\n")
        time.sleep(0.6)
        layout.write("Error: payload.dd not found on CIRCUITPY drive.\n")

run_payload("/payload.dd")

# Stop after one run so the payload does not loop
while True:
    time.sleep(1)
