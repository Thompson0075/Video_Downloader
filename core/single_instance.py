"""Single-instance guard using a Windows named mutex (fallback: lock file)."""
from __future__ import annotations

import sys
from pathlib import Path

from core.paths import app_root

MUTEX_NAME = "Local\\VideoDownloader_SingleInstance_Mutex_v2"


class SingleInstance:
    def __init__(self) -> None:
        self.acquired = False
        self._mutex_handle = None  # per-instance; do not share via global
        self._lock_path = app_root() / ".videodownloader.lock"

    def try_acquire(self) -> bool:
        """Return True if this process owns the instance; False if another is running."""
        if sys.platform == "win32":
            return self._try_acquire_mutex()
        return self._try_acquire_lockfile()

    def _try_acquire_mutex(self) -> bool:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        ERROR_ALREADY_EXISTS = 183

        handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
        if not handle:
            return self._try_acquire_lockfile()

        last_error = kernel32.GetLastError()
        if last_error == ERROR_ALREADY_EXISTS:
            # Another instance owns the name — drop our handle, do not run.
            kernel32.CloseHandle(handle)
            self._mutex_handle = None
            self.acquired = False
            return False

        self._mutex_handle = handle
        self.acquired = True
        return True

    def _try_acquire_lockfile(self) -> bool:
        try:
            # Atomic create; FileExistsError => already running
            fd = open(self._lock_path, "x", encoding="utf-8")
            try:
                fd.write(str(Path(sys.argv[0]).resolve()))
            finally:
                fd.close()
            self.acquired = True
            return True
        except FileExistsError:
            self.acquired = False
            return False
        except OSError:
            # If lock cannot be created, do not block the user
            self.acquired = True
            return True

    def release(self) -> None:
        if self._mutex_handle is not None:
            try:
                import ctypes

                ctypes.windll.kernel32.CloseHandle(self._mutex_handle)
            except Exception:
                pass
            self._mutex_handle = None
        try:
            if self._lock_path.exists():
                self._lock_path.unlink(missing_ok=True)
        except OSError:
            pass
        self.acquired = False
