"""App configuration + download history persistence.

History and settings are stored in a user-writable data directory so they
survive restarts even if the install folder is rebuilt / moved.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

from core.paths import app_root, is_frozen


def data_dir() -> Path:
    """Stable writable dir for config / history (not inside Program Files)."""
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    if base:
        p = Path(base) / "VideoDownloader"
    else:
        p = app_root() / "userdata"
    try:
        p.mkdir(parents=True, exist_ok=True)
    except OSError:
        p = app_root() / "userdata"
        p.mkdir(parents=True, exist_ok=True)
    return p


@dataclass
class AppConfig:
    download_dir: str = ""
    quality: str = "best"  # best | 1080 | 720 | 480 | audio
    audio_format: str = "mp3"  # mp3 | m4a | opus
    max_concurrent: int = 2
    window_width: int = 1080
    window_height: int = 720
    download_subtitles: bool = False
    subtitle_langs: str = "zh-Hans,zh,en"
    auto_shutdown: bool = False
    history: list = field(default_factory=list)

    @property
    def download_path(self) -> Path:
        if self.download_dir:
            p = Path(self.download_dir)
        else:
            from core.paths import default_download_dir

            p = default_download_dir()
        try:
            p.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        return p


def config_file() -> Path:
    return data_dir() / "config.json"


def history_file() -> Path:
    return data_dir() / "history.json"


def _read_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_history() -> list:
    data = _read_json(history_file())
    if isinstance(data, list):
        return [h for h in data if isinstance(h, dict)]
    # migrate from old config.json
    cfg_data = _read_json(config_file())
    if isinstance(cfg_data, dict) and isinstance(cfg_data.get("history"), list):
        return [h for h in cfg_data["history"] if isinstance(h, dict)]
    return []


def save_history(items: list) -> None:
    path = history_file()
    tmp = path.with_suffix(".json.tmp")
    payload = [h for h in items if isinstance(h, dict)]
    try:
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)
    except OSError:
        try:
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass


def load_config() -> AppConfig:
    data = _read_json(config_file())
    cfg = AppConfig()
    if isinstance(data, dict):
        known = set(AppConfig.__dataclass_fields__)
        try:
            for key, value in data.items():
                if key in known and key != "history":
                    setattr(cfg, key, value)
        except Exception:
            pass
    # history lives in its own file (never clobbered by window-size saves)
    cfg.history = load_history()
    return cfg


def save_config(cfg: AppConfig) -> None:
    """Persist settings only — history is written separately via save_history."""
    payload = asdict(cfg)
    payload.pop("history", None)
    path = config_file()
    tmp = path.with_suffix(".json.tmp")
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    try:
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
    except OSError:
        try:
            path.write_text(text, encoding="utf-8")
        except OSError:
            pass


def save_window_size(width: int, height: int) -> None:
    """Update only window size without touching history."""
    cfg = load_config()
    cfg.window_width = int(width)
    cfg.window_height = int(height)
    save_config(cfg)
