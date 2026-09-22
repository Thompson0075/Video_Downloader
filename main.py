from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is importable when running from source.
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from core.app_bridge import AppBridge
from core.config import load_config, save_window_size
from core.paths import bundle_root, qml_dir
from core.single_instance import SingleInstance


def _notify_already_running() -> None:
    """Best-effort native notice so silent double-click is not mysterious."""
    try:
        if sys.platform == "win32":
            import ctypes

            ctypes.windll.user32.MessageBoxW(
                None,
                "视频下载器已在运行中。\n请勿重复打开多个实例，以免占用过多资源。",
                "视频下载器",
                0x00000040,  # MB_ICONINFORMATION
            )
    except Exception:
        pass


def main() -> int:
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    guard = SingleInstance()
    if not guard.try_acquire():
        _notify_already_running()
        return 0

    app = QGuiApplication(sys.argv)
    app.setApplicationName("Video Downloader")
    app.setOrganizationName("VideoDownloader")
    app.setApplicationVersion("2.0.5")
    # Help Windows group taskbar / notifications correctly
    try:
        if sys.platform == "win32":
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "VideoDownloader.Desktop.2.0.2"
            )
    except Exception:
        pass

    icon_path = bundle_root() / "assets" / "icon.png"
    ico_path = bundle_root() / "assets" / "icon.ico"
    icon = QIcon()
    if ico_path.exists():
        icon = QIcon(str(ico_path))
    elif icon_path.exists():
        icon = QIcon(str(icon_path))
    if not icon.isNull():
        app.setWindowIcon(icon)

    bridge = AppBridge()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("Backend", bridge)

    qml_file = qml_dir() / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    if not engine.rootObjects():
        print("Failed to load QML UI:", qml_file, file=sys.stderr)
        guard.release()
        return 1

    window = engine.rootObjects()[0]
    cfg = load_config()
    # restore size
    try:
        window.setProperty("width", int(cfg.window_width or 1080))
        window.setProperty("height", int(cfg.window_height or 720))
    except Exception:
        pass
    if not icon.isNull():
        try:
            window.setProperty("icon", icon)
        except Exception:
            pass

    def persist_size() -> None:
        try:
            save_window_size(
                int(window.property("width")),
                int(window.property("height")),
            )
        except Exception:
            pass

    def cleanup() -> None:
        persist_size()
        guard.release()

    app.aboutToQuit.connect(cleanup)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
