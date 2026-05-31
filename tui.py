"""Terminal checkbox: arrows + space + enter. Stdlib only; macOS / Linux / Windows 10+."""

import os
import sys


def _read_key():
    """Block for one keypress; return a normalized name or empty string."""
    if os.name == "nt":
        import msvcrt
        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):
            return {b"H": "up", b"P": "down"}.get(msvcrt.getch(), "")
        return {b"\r": "enter", b" ": "space", b"\x03": "cancel",
                b"\x1b": "cancel", b"q": "cancel", b"Q": "cancel"}.get(ch, "")

    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            if sys.stdin.read(1) == "[":
                return {"A": "up", "B": "down"}.get(sys.stdin.read(1), "")
            return "cancel"
        return {"\r": "enter", "\n": "enter", " ": "space",
                "\x03": "cancel", "q": "cancel", "Q": "cancel"}.get(ch, "")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def checkbox(prompt, choices):
    """Show a checkbox list; return chosen items in input order.

    Arrows navigate, Space toggles, Enter confirms, Q or Esc cancels (returns []).
    """
    if os.name == "nt":
        os.system("")  # enable ANSI escapes on Windows 10+

    cursor = 0
    marked = [False] * len(choices)
    prev_lines = 0
    sys.stdout.write("\x1b[?25l")  # hide cursor
    try:
        while True:
            lines = [prompt, ""]
            for i, name in enumerate(choices):
                pointer = ">" if i == cursor else " "
                box = "[x]" if marked[i] else "[ ]"
                lines.append(f" {pointer} {box} {name}")
            lines.append("")
            lines.append(" Up/Down: move   Space: toggle   Enter: confirm   Q: cancel")

            # Move to the start of the previous frame and clear to end of screen.
            # Counted-up redraw avoids the broken \x1b[s/\x1b[u save/restore behavior
            # in macOS Terminal and Windows Console when the first render scrolls.
            if prev_lines:
                sys.stdout.write(f"\x1b[{prev_lines}F\x1b[0J")
            sys.stdout.write("\n".join(lines) + "\n")
            sys.stdout.flush()
            prev_lines = len(lines)

            key = _read_key()
            if key == "up":
                cursor = (cursor - 1) % len(choices)
            elif key == "down":
                cursor = (cursor + 1) % len(choices)
            elif key == "space":
                marked[cursor] = not marked[cursor]
            elif key == "enter":
                return [c for c, m in zip(choices, marked) if m]
            elif key == "cancel":
                return []
    finally:
        sys.stdout.write("\x1b[?25h")  # show cursor
        sys.stdout.flush()
