"""Resolve bundled resource paths for both source runs and frozen exe."""
from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def app_root() -> Path:
    """Project root in source mode, or the exe folder when frozen."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def bundle_root() -> Path:
    """Where bundled data files live (PyInstaller _MEIPASS / _internal, or project root)."""
    if is_frozen():
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        # onedir fallback: files may sit next to the exe or under _internal
        exe_dir = Path(sys.executable).resolve().parent
        internal = exe_dir / "_internal"
        if internal.is_dir():
            return internal
        return exe_dir
    return Path(__file__).resolve().parents[1]


def ffmpeg_dir() -> Path:
    return bundle_root() / "vendor" / "ffmpeg" / "bin"


def ffmpeg_exe() -> Path:
    return ffmpeg_dir() / "ffmpeg.exe"


def ffprobe_exe() -> Path:
    return ffmpeg_dir() / "ffprobe.exe"


def qml_dir() -> Path:
    return bundle_root() / "ui"


def default_download_dir() -> Path:
    return app_root() / "downloads"
