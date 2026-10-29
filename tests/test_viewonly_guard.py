"""Static coverage checks for the client-side View Only input boundary.

This is a source audit, NOT a replacement for integration testing with Sunshine.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
INPUT = APP / "streaming" / "input"
EXPECTED_FILES = [
    "keyboard.cpp", "mouse.cpp", "gamepad.cpp",
    "reltouch.cpp", "abstouch.cpp",
]

guarded = 0
unguarded = []

for file in APP.rglob("*.cpp"):
    content = file.read_text(encoding="utf-8")
    for match in re.finditer(r"\b(LiSend\w+)\s*\(", content):
        line = content.count("\n", 0, match.start()) + 1
        unguarded.append(f"{file.relative_to(ROOT)}:{line}: {match.group(1)}")

for file_name in EXPECTED_FILES:
    file = INPUT / file_name
    content = file.read_text(encoding="utf-8")
    assert '#include "viewonlyguard.h"' in content, file
    guarded += len(re.findall(r"ViewOnlyGuard::send\(LiSend\w+,", content))

assert not unguarded, "Unguarded Limelight input calls:\n" + "\n".join(unguarded)
assert guarded >= 49, f"Expected at least 49 guarded calls, found {guarded}"

main = (APP / "main.cpp").read_text(encoding="utf-8")
session = (APP / "streaming" / "session.cpp").read_text(encoding="utf-8")
handler = (INPUT / "input.cpp").read_text(encoding="utf-8")

assert 'commandLineArgs.removeAll("--view-only")' in main
assert "streamParser.parse(commandLineArgs, preferences);" in main
assert "quitParser.parse(commandLineArgs);" in main
assert "pairParser.parse(commandLineArgs);" in main
assert "listParser.parse(commandLineArgs);" in main
assert "parse(commandLineArgs))" not in main

assert 'ViewOnlyGuard::enabled() ? 0 : m_InputHandler->getAttachedGamepadMask()' in session
assert 'm_GamepadMask = ViewOnlyGuard::enabled() ? 0 :' in handler
assert 'if (ViewOnlyGuard::enabled())' in handler

print(f"PASS: {guarded} outgoing input call sites guarded in {len(EXPECTED_FILES)} SDL sources")
print("PASS: client-side flag, controller mask and local capture guards present")
