#!/usr/bin/env python3
"""
Mythoskull Payload Builder - Kraken HID
A desktop GUI for authoring DuckyScript payloads for the Kraken HID / pico-ducky
CircuitPython interpreter, with live preview, validation, export, and one-click
deploy to a connected CIRCUITPY drive.

Authorized use only. Build and run keystroke payloads solely on systems you own
or have written permission to test.

Created by Joshua Burton (p01yg107) / Mythoskull Hardware.
Pure standard library - no pip install required (needs Python 3.8+ with Tkinter).
"""

import os
import sys
import string
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_NAME = "Mythoskull Payload Builder"
VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Palette (single dark "terminal bench" theme)
# ---------------------------------------------------------------------------
BG      = "#0b1220"
PANEL   = "#0f1a2e"
PANEL2  = "#0a1322"
LINE    = "#22324e"
INK     = "#e6edf7"
DIM     = "#8aa0bd"
FAINT   = "#5b708f"
COPPER  = "#e08a3c"
TEAL    = "#2dd4bf"
RED     = "#ef5350"
OK      = "#52d273"
MONO    = ("Consolas" if sys.platform.startswith("win") else "Menlo"
           if sys.platform == "darwin" else "DejaVu Sans Mono")

# ---------------------------------------------------------------------------
# Interpreter contract - keep in sync with firmware/code.py
# ---------------------------------------------------------------------------
NAMED_KEYS = {
    "ENTER", "RETURN", "TAB", "SPACE", "ESC", "ESCAPE", "BACKSPACE", "DELETE",
    "DEL", "UP", "DOWN", "LEFT", "RIGHT", "UPARROW", "DOWNARROW", "LEFTARROW",
    "RIGHTARROW", "HOME", "END", "PAGEUP", "PAGEDOWN", "INSERT", "CAPSLOCK",
    "PRINTSCREEN", "GUI", "WINDOWS", "WIN", "COMMAND", "CTRL", "CONTROL",
    "SHIFT", "ALT", "OPTION", "MENU", "APP",
    "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
}
WORD_CMDS = {"STRING", "STRINGLN", "DELAY", "DEFAULT_DELAY", "DEFAULTDELAY",
             "STRING_DELAY", "STRINGDELAY", "REM"}


def is_key_token(tok):
    if tok.upper() in NAMED_KEYS:
        return True
    return len(tok) == 1 and tok.isalnum()


def parse_line(raw, index):
    """Return (lineno, act, kind, value, ok) for one script line, or None to skip."""
    line = raw.rstrip()
    stripped = line.strip()
    if stripped == "":
        return None
    if stripped.startswith("//"):
        return (index, "note", "rem", stripped[2:].strip(), True)

    sp = stripped.find(" ")
    cmd = (stripped if sp < 0 else stripped[:sp]).upper()
    args = "" if sp < 0 else stripped[sp + 1:]
    orig_args = "" if " " not in line else line.split(" ", 1)[1]

    if cmd == "REM":
        return (index, "note", "rem", args, True)
    if cmd == "STRING":
        return (index, "type", "type", orig_args, True)
    if cmd == "STRINGLN":
        return (index, "type + ENTER", "type", orig_args, True)
    if cmd == "DELAY":
        return (index, "wait", "wait", _ms(args) + " ms", True)
    if cmd in ("DEFAULT_DELAY", "DEFAULTDELAY"):
        return (index, "pace", "wait", "each step + " + _ms(args) + " ms", True)
    if cmd in ("STRING_DELAY", "STRINGDELAY"):
        return (index, "pace", "wait", "per char + " + _ms(args) + " ms", True)

    # Otherwise, treat as a key / combo line
    toks = stripped.split()
    if all(is_key_token(t) for t in toks):
        return (index, "press", "key", " + ".join(t.upper() for t in toks), True)
    return (index, "error", "bad", "Unknown command: " + cmd, False)


def _ms(s):
    try:
        return str(int(float(s)))
    except (ValueError, TypeError):
        return "0"


def parse_script(text):
    steps = []
    for i, raw in enumerate(text.split("\n"), start=1):
        res = parse_line(raw, i)
        if res:
            steps.append(res)
    bad = sum(1 for s in steps if not s[4])
    return steps, bad


# ---------------------------------------------------------------------------
# Templates (benign only)
# ---------------------------------------------------------------------------
TEMPLATES = {
    "Start blank": "",
    "Mythoskull Notepad banner": "\n".join([
        "REM Mythoskull Notepad banner (benign demo)",
        "DELAY 1000", "GUI r", "DELAY 600", "STRING notepad", "ENTER", "DELAY 1500",
        "STRING ====================================================", "ENTER",
        "STRING [+] Mythoskull Hardware: ONLINE", "ENTER",
        "STRING [+] Created By: Joshua Burton Aka p01yg107", "ENTER",
        "STRING [+] Status: Ready for payload deployment.", "ENTER",
        "STRING ====================================================", "ENTER",
    ]),
    "Type a message in Notepad": "\n".join([
        "REM Open Notepad and type a message",
        "DELAY 800", "GUI r", "DELAY 500", "STRING notepad", "ENTER", "DELAY 1200",
        "STRING Hello from the Kraken HID.", "ENTER",
        "STRING Replace this line with your own text.", "ENTER",
    ]),
    "Open a website": "\n".join([
        "REM Open a website in the default browser",
        "DELAY 800", "GUI r", "DELAY 500", "STRING https://example.com", "ENTER",
    ]),
    "Open terminal & echo": "\n".join([
        "REM Open Windows terminal and echo a line",
        "DELAY 800", "GUI r", "DELAY 500", "STRING cmd", "ENTER", "DELAY 800",
        "STRING echo Kraken HID ready", "ENTER",
    ]),
}

# Command palette: (label, insert text, caret_at_end)
PALETTE = [
    ("Text", [("STRING", "STRING ", True), ("STRINGLN", "STRINGLN ", True)]),
    ("Timing", [("DELAY", "DELAY 500", False),
                ("DEFAULT_DELAY", "DEFAULT_DELAY 50", False),
                ("STRING_DELAY", "STRING_DELAY 15", False)]),
    ("Keys", [("ENTER", "ENTER", False), ("TAB", "TAB", False), ("ESC", "ESC", False),
              ("SPACE", "SPACE", False), ("BACKSPACE", "BACKSPACE", False),
              ("DELETE", "DELETE", False), ("UP", "UP", False), ("DOWN", "DOWN", False),
              ("LEFT", "LEFT", False), ("RIGHT", "RIGHT", False)]),
    ("Combos", [("GUI r", "GUI r", False), ("GUI d", "GUI d", False),
                ("CTRL c", "CTRL c", False), ("CTRL v", "CTRL v", False),
                ("CTRL a", "CTRL a", False), ("ALT F4", "ALT F4", False),
                ("ALT TAB", "ALT TAB", False), ("CTRL SHIFT ESC", "CTRL SHIFT ESC", False)]),
    ("Notes", [("REM comment", "REM ", True)]),
]


# ---------------------------------------------------------------------------
# CIRCUITPY detection (cross-platform, stdlib only)
# ---------------------------------------------------------------------------
def find_circuitpy():
    found = []
    if sys.platform.startswith("win"):
        import ctypes
        for letter in string.ascii_uppercase:
            root = "{}:\\".format(letter)
            if not os.path.exists(root):
                continue
            name = ctypes.create_unicode_buffer(1024)
            fsname = ctypes.create_unicode_buffer(1024)
            try:
                ok = ctypes.windll.kernel32.GetVolumeInformationW(
                    ctypes.c_wchar_p(root), name, 1024, None, None, None, fsname, 1024)
                if ok and name.value.upper() == "CIRCUITPY":
                    found.append(root)
            except Exception:
                pass
    else:
        bases = ["/Volumes"]
        user = os.environ.get("USER", "")
        bases += ["/media/" + user, "/run/media/" + user, "/media", "/run/media"]
        for base in bases:
            if not os.path.isdir(base):
                continue
            direct = os.path.join(base, "CIRCUITPY")
            if os.path.isdir(direct):
                found.append(direct)
            try:
                for sub in os.listdir(base):
                    p = os.path.join(base, sub, "CIRCUITPY")
                    if os.path.isdir(p):
                        found.append(p)
            except OSError:
                pass
    # de-dupe preserving order
    seen, out = set(), []
    for f in found:
        if f not in seen:
            seen.add(f); out.append(f)
    return out


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------
class PayloadBuilder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("{} - Kraken HID".format(APP_NAME))
        self.geometry("1040x720")
        self.minsize(820, 560)
        self.configure(bg=BG)
        self._build()
        self.editor.insert("1.0", TEMPLATES["Mythoskull Notepad banner"])
        self.refresh()

    # ---- layout ----
    def _build(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=16, pady=(14, 6))
        tk.Label(header, text="\U0001F989", font=(MONO, 20), bg=BG, fg=COPPER).pack(side="left")
        tb = tk.Frame(header, bg=BG)
        tb.pack(side="left", padx=10)
        tk.Label(tb, text=APP_NAME, font=(MONO, 15, "bold"), bg=BG, fg=INK).pack(anchor="w")
        tk.Label(tb, text="Kraken HID  -  build DuckyScript, preview, export payload.dd",
                 font=(MONO, 9), bg=BG, fg=DIM).pack(anchor="w")

        notice = tk.Label(
            self,
            text=("⚠  Authorized use only. Run payloads only on systems you own or "
                  "have written permission to test."),
            font=(MONO, 9), bg="#1c1608", fg="#f0d8bf", anchor="w", padx=10, pady=7)
        notice.pack(fill="x", padx=16, pady=(0, 10))

        # toolbar
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=16, pady=(0, 10))
        tk.Label(bar, text="Template", font=(MONO, 9), bg=BG, fg=DIM).pack(side="left", padx=(0, 6))
        self.tpl_var = tk.StringVar(value="Mythoskull Notepad banner")
        tpl = ttk.Combobox(bar, textvariable=self.tpl_var, state="readonly",
                           values=list(TEMPLATES.keys()), width=28)
        tpl.pack(side="left")
        tpl.bind("<<ComboboxSelected>>", self.on_template)
        self._btn(bar, "Clear", self.on_clear).pack(side="left", padx=6)
        self._btn(bar, "Save payload.dd", self.on_save).pack(side="right")
        self._btn(bar, "Deploy to Kraken", self.on_deploy, primary=True).pack(side="right", padx=6)

        # main split
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        rail = tk.Frame(main, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        rail.pack(side="left", fill="y", padx=(0, 12))
        rail_inner = tk.Frame(rail, bg=PANEL)
        rail_inner.pack(fill="both", expand=True, padx=10, pady=10)
        for group, items in PALETTE:
            tk.Label(rail_inner, text=group.upper(), font=(MONO, 8, "bold"),
                     bg=PANEL, fg=TEAL).pack(anchor="w", pady=(8, 3))
            row = tk.Frame(rail_inner, bg=PANEL)
            row.pack(anchor="w", fill="x")
            col = 0
            for label, ins, caret in items:
                b = tk.Button(row, text=label, font=(MONO, 8), bg=PANEL2, fg=INK,
                              activebackground=LINE, activeforeground=INK, relief="flat",
                              bd=0, padx=7, pady=4, cursor="hand2",
                              command=lambda s=ins, c=caret: self.insert_cmd(s, c))
                b.grid(row=col // 2, column=col % 2, sticky="w", padx=2, pady=2)
                col += 1

        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        ed_hd = tk.Frame(right, bg=PANEL2)
        ed_hd.pack(fill="x")
        tk.Label(ed_hd, text="payload.dd", font=(MONO, 9), bg=PANEL2, fg=DIM).pack(side="left", padx=10, pady=5)
        self.lc = tk.Label(ed_hd, text="", font=(MONO, 9), bg=PANEL2, fg=FAINT)
        self.lc.pack(side="right", padx=10)

        self.editor = tk.Text(right, bg="#0a1322", fg=INK, insertbackground=TEAL,
                              font=(MONO, 11), relief="flat", bd=0, undo=True,
                              wrap="none", padx=12, pady=10, height=14)
        self.editor.pack(fill="both", expand=True)
        self.editor.bind("<KeyRelease>", lambda e: self.refresh())

        self.status = tk.Label(right, text="", font=(MONO, 9), bg=PANEL2, fg=OK, anchor="w",
                               padx=10, pady=5)
        self.status.pack(fill="x")

        pv_hd = tk.Frame(right, bg=PANEL2)
        pv_hd.pack(fill="x", pady=(10, 0))
        tk.Label(pv_hd, text="Live preview - what the board will do", font=(MONO, 9),
                 bg=PANEL2, fg=DIM).pack(side="left", padx=10, pady=5)
        self.sc = tk.Label(pv_hd, text="", font=(MONO, 9), bg=PANEL2, fg=FAINT)
        self.sc.pack(side="right", padx=10)

        self.preview = tk.Text(right, bg=PANEL, fg=INK, font=(MONO, 10), relief="flat",
                               bd=0, height=9, padx=10, pady=8, state="disabled", wrap="none")
        self.preview.pack(fill="both", expand=True)
        self.preview.tag_config("type", foreground=TEAL)
        self.preview.tag_config("key", foreground=COPPER)
        self.preview.tag_config("wait", foreground=DIM)
        self.preview.tag_config("rem", foreground=FAINT)
        self.preview.tag_config("bad", foreground=RED)
        self.preview.tag_config("ln", foreground=FAINT)

    def _btn(self, parent, text, cmd, primary=False):
        return tk.Button(parent, text=text, command=cmd, font=(MONO, 9, "bold" if primary else "normal"),
                         bg=(COPPER if primary else PANEL), fg=("#1a1206" if primary else INK),
                         activebackground=("#ffab5e" if primary else LINE),
                         activeforeground=("#1a1206" if primary else INK),
                         relief="flat", bd=0, padx=12, pady=6, cursor="hand2")

    # ---- behavior ----
    def insert_cmd(self, snippet, caret_end):
        # place each command on its own line
        cur = self.editor.index("insert")
        line_start = self.editor.get(cur + " linestart", cur)
        prefix = "" if line_start == "" else "\n"
        self.editor.insert("insert", prefix + snippet)
        self.editor.focus_set()
        self.refresh()

    def on_template(self, _=None):
        name = self.tpl_var.get()
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", TEMPLATES.get(name, ""))
        self.refresh()

    def on_clear(self):
        self.editor.delete("1.0", "end")
        self.tpl_var.set("Start blank")
        self.refresh()

    def on_save(self):
        path = filedialog.asksaveasfilename(
            title="Save payload", defaultextension=".dd",
            initialfile="payload.dd",
            filetypes=[("DuckyScript", "*.dd"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(self.editor.get("1.0", "end-1c"))
            messagebox.showinfo(APP_NAME, "Saved:\n" + path)
        except OSError as e:
            messagebox.showerror(APP_NAME, "Could not save:\n" + str(e))

    def on_deploy(self):
        _, bad = parse_script(self.editor.get("1.0", "end-1c"))
        if bad and not messagebox.askyesno(
                APP_NAME, "{} unsupported line(s) will be skipped by the board.\n"
                          "Deploy anyway?".format(bad)):
            return
        drives = find_circuitpy()
        if not drives:
            messagebox.showwarning(
                APP_NAME, "No CIRCUITPY drive found.\n\n"
                "Plug in a flashed Kraken HID and try again.")
            return
        target = drives[0]
        dest = os.path.join(target, "payload.dd")
        try:
            with open(dest, "w", encoding="utf-8", newline="\n") as f:
                f.write(self.editor.get("1.0", "end-1c"))
            messagebox.showinfo(
                APP_NAME, "Deployed payload.dd to:\n" + target +
                "\n\nSafely eject, then replug the board to run.")
        except OSError as e:
            messagebox.showerror(APP_NAME, "Could not write to the board:\n" + str(e))

    def refresh(self):
        text = self.editor.get("1.0", "end-1c")
        lines = text.split("\n")
        self.lc.config(text="{} line{}".format(len(lines), "" if len(lines) == 1 else "s"))
        steps, bad = parse_script(text)

        self.preview.config(state="normal")
        self.preview.delete("1.0", "end")
        if not steps:
            self.preview.insert("end", "Nothing yet. Load a template or click commands on the left.", "rem")
        else:
            for lineno, act, kind, val, ok in steps:
                self.preview.insert("end", "{:>3}  ".format(lineno), "ln")
                self.preview.insert("end", "{:<13}".format(act), kind)
                self.preview.insert("end", val + "\n")
        self.preview.config(state="disabled")

        self.sc.config(text="{} step{}".format(len(steps), "" if len(steps) == 1 else "s") if steps else "")
        if bad:
            self.status.config(text="⚠  {} unsupported line{}".format(bad, "" if bad == 1 else "s"), fg=RED)
        else:
            self.status.config(text="✓  valid", fg=OK)


def main():
    app = PayloadBuilder()
    app.mainloop()


if __name__ == "__main__":
    main()
