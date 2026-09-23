"""
Shared dependency bootstrap for the ScanSmith Python GUIs.

Call ensure_dependencies() before importing any third-party library.
It checks that everything in REQUIRED_PACKAGES is importable and attempts
an automatic `pip install` for anything missing. If that fails, and a
fallback_script was given (the sibling GUI), it launches that instead --
regardless of whether the install failure looks recoverable, since the
fallback runs its own independent bootstrap and may simply succeed where
this one didn't (flaky network, etc). Only if that also fails does it
show the user the exact command to run themselves, plus other options,
and exit.
"""

import importlib
import importlib.util
import os
import subprocess
import sys
import time

# import name -> pip package name
REQUIRED_PACKAGES = {"PIL": "Pillow"}

# Set on the environment of a subprocess we launch as a fallback, so that
# subprocess's own bootstrap won't try to launch a fallback of its own --
# otherwise two GUIs whose deps are both broken would ping-pong forever.
_FALLBACK_ACTIVE_ENV = "SCANSMITH_DEPS_FALLBACK_ACTIVE"


def _is_fallback_attempt() -> bool:
    return os.environ.get(_FALLBACK_ACTIVE_ENV) == "1"


def _try_launch_fallback(fallback_script) -> bool:
    """Launches the sibling GUI as a subprocess. Returns True if it appears
    to have started successfully (and blocks here until the user closes it,
    since it now owns the session), False if it exited quickly on its own
    (e.g. hit the same missing dependency)."""
    if not fallback_script or _is_fallback_attempt():
        return False
    if not os.path.exists(fallback_script):
        return False

    print(f"Trying the other QR code interface instead: {fallback_script}")
    env = dict(os.environ)
    env[_FALLBACK_ACTIVE_ENV] = "1"
    try:
        proc = subprocess.Popen([sys.executable, fallback_script], env=env)
    except Exception:
        return False

    time.sleep(1.5)
    if proc.poll() is not None and proc.returncode != 0:
        return False  # the fallback also failed almost immediately

    proc.wait()  # fallback launched fine -- let it run for the rest of the session
    return True


def _fail_with_instructions(missing_pip_names, tried_fallback=False):
    """Tells the user what to install (dialog if tkinter works, else console) and exits."""
    install_cmd = f"{sys.executable} -m pip install {' '.join(missing_pip_names)}"
    if sys.platform.startswith("win"):
        fallback = (
            "If installation keeps failing, you can use the C# desktop app in "
            "this repository instead — it needs no Python packages at all:\n\n"
            "    Open CustomQrApp/CustomQrSolution.slnx in Visual Studio and run it,\n"
            "    or run `dotnet run` from CustomQrApp/CustomQRCodeGenerator\n"
            "    (requires the .NET SDK)."
        )
    else:
        fallback = (
            "If installation keeps failing, try a different Python install "
            "(e.g. from python.org or `brew install python`) — its pip may "
            "work where this one doesn't. On a Windows machine, the C# app in "
            "CustomQrApp/ also works with no Python setup."
        )
    intro = (
        "Neither QR code interface in this app could start automatically."
        if tried_fallback else
        "This app needs the following Python package(s), and automatic installation failed."
    )
    message = (
        f"{intro}\n\nMissing package(s):\n\n    {', '.join(missing_pip_names)}\n\n"
        "Please install them yourself by running:\n\n"
        f"    {install_cmd}\n\n"
        f"then start the app again.\n\n{fallback}"
    )
    print(message, file=sys.stderr)
    try:
        import tkinter
        from tkinter import messagebox as _mb
        _root = tkinter.Tk()
        _root.withdraw()
        _mb.showerror("Missing dependencies", message)
        _root.destroy()
    except Exception:
        pass  # console message above is the fallback
    sys.exit(1)


def ensure_dependencies(fallback_script=None):
    """
    fallback_script: absolute path to the sibling GUI script to try launching
    if this one's dependencies can't be installed. Pass None if there isn't
    one (or this call is already running as someone else's fallback).
    """
    # tkinter first: it's part of the standard library but shipped as a
    # separate OS package on some systems, and pip can't install it.
    try:
        import tkinter  # noqa: F401
    except ImportError:
        if _try_launch_fallback(fallback_script):
            sys.exit(0)

        if sys.platform == "darwin":
            hint = "brew install python-tk (or reinstall Python from python.org)"
        elif sys.platform.startswith("linux"):
            hint = "sudo apt install python3-tk (Debian/Ubuntu) or your distro's equivalent"
        else:
            hint = "reinstall Python from python.org with the tcl/tk option enabled"
        intro = (
            "Neither QR code interface in this app could start: tkinter is missing.\n"
            if fallback_script else
            "This app needs tkinter, which is missing from your Python install.\n"
        )
        print(f"{intro}To fix it: {hint}", file=sys.stderr)
        sys.exit(1)

    missing = [
        pip_name
        for import_name, pip_name in REQUIRED_PACKAGES.items()
        if importlib.util.find_spec(import_name) is None
    ]
    if not missing:
        return

    print(f"Missing package(s): {', '.join(missing)} — attempting automatic install...")
    still_missing = []
    for pip_name in missing:
        installed = _pip_install(pip_name)
        importlib.invalidate_caches()
        import_name = next(k for k, v in REQUIRED_PACKAGES.items() if v == pip_name)
        if not installed or importlib.util.find_spec(import_name) is None:
            still_missing.append(pip_name)

    if still_missing:
        if _try_launch_fallback(fallback_script):
            sys.exit(0)
        _fail_with_instructions(still_missing, tried_fallback=bool(fallback_script))
    print("All dependencies installed.")
