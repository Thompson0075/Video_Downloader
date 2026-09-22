"""Qt bridge exposing download engine to QML."""
from __future__ import annotations

import os
import re
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QUrl, QTimer, Signal, Slot, Property

from core.config import (
    AppConfig,
    load_config,
    load_history,
    save_config,
    save_history,
)
from core.downloader import (
    DownloadJob,
    extract_info,
    format_bytes,
    human_eta,
    human_speed,
    quality_format_selector,
)
from core.paths import ffmpeg_exe, is_frozen


def _safe_filename_chars(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip() or "video"


class AppBridge(QObject):
    videoInfoReady = Signal(dict)
    videoInfoFailed = Signal(str)
    analyzeStarted = Signal()
    jobAdded = Signal(dict)
    jobUpdated = Signal(dict)
    jobFinished = Signal(dict)
    toast = Signal(str, str)  # type: str, message
    configChanged = Signal()
    historyChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._config = load_config()
        self._config.history = load_history()
        self._jobs: dict[str, DownloadJob] = {}
        self._analyzing = False
        self._shutdown_armed = False

    # ----- config properties -----
    def _get_download_dir(self) -> str:
        return str(self._config.download_path)

    def _set_download_dir(self, value: str) -> None:
        value = (value or "").strip()
        self._config.download_dir = value
        try:
            self._config.download_path.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        save_config(self._config)
        self.configChanged.emit()

    downloadDir = Property(str, _get_download_dir, _set_download_dir, notify=configChanged)

    def _get_quality(self) -> str:
        return self._config.quality

    def _set_quality(self, value: str) -> None:
        if value in {"best", "1080", "720", "480", "audio"}:
            self._config.quality = value
            save_config(self._config)
            self.configChanged.emit()

    quality = Property(str, _get_quality, _set_quality, notify=configChanged)

    def _get_audio_format(self) -> str:
        return self._config.audio_format

    def _set_audio_format(self, value: str) -> None:
        if value in {"mp3", "m4a", "opus"}:
            self._config.audio_format = value
            save_config(self._config)
            self.configChanged.emit()

    audioFormat = Property(str, _get_audio_format, _set_audio_format, notify=configChanged)

    def _get_download_subtitles(self) -> bool:
        return bool(self._config.download_subtitles)

    def _set_download_subtitles(self, value: bool) -> None:
        self._config.download_subtitles = bool(value)
        save_config(self._config)
        self.configChanged.emit()

    downloadSubtitles = Property(
        bool, _get_download_subtitles, _set_download_subtitles, notify=configChanged
    )

    def _get_auto_shutdown(self) -> bool:
        return bool(self._config.auto_shutdown)

    def _set_auto_shutdown(self, value: bool) -> None:
        self._config.auto_shutdown = bool(value)
        save_config(self._config)
        self.configChanged.emit()

    autoShutdown = Property(bool, _get_auto_shutdown, _set_auto_shutdown, notify=configChanged)

    def _get_subtitle_langs(self) -> str:
        return self._config.subtitle_langs or "zh-Hans,zh,en"

    def _set_subtitle_langs(self, value: str) -> None:
        self._config.subtitle_langs = (value or "zh-Hans,zh,en").strip()
        save_config(self._config)
        self.configChanged.emit()

    subtitleLangs = Property(str, _get_subtitle_langs, _set_subtitle_langs, notify=configChanged)

    def _get_history(self) -> list:
        return list(self._config.history)

    history = Property(list, _get_history, notify=historyChanged)

    @Slot(result=str)
    def ffmpegStatus(self) -> str:
        exe = ffmpeg_exe()
        return "ok" if exe.exists() else "missing"

    @Slot(result=str)
    def appVersion(self) -> str:
        return "2.0.3"

    @Slot(result=str)
    def defaultQuality(self) -> str:
        return quality_format_selector(self._config.quality, self._config.audio_format)

    # ----- analyze -----
    @Slot(str)
    def analyze(self, url: str) -> None:
        url = (url or "").strip()
        if not url:
            self.videoInfoFailed.emit("请输入视频链接")
            return
        if self._analyzing:
            self.toast.emit("warn", "正在解析中，请稍候")
            return
        self._analyzing = True
        self.analyzeStarted.emit()

        import threading

        def worker() -> None:
            try:
                info = extract_info(url)
                self.videoInfoReady.emit(info.to_dict())
            except Exception as e:  # noqa: BLE001
                self.videoInfoFailed.emit(str(e))
            finally:
                self._analyzing = False

        threading.Thread(target=worker, daemon=True).start()

    # ----- download -----
    @Slot(str, str)
    def startDownload(self, url: str, format_id: str = "auto") -> None:
        url = (url or "").strip()
        if not url:
            self.toast.emit("error", "请输入视频链接")
            return
        job_id = uuid.uuid4().hex[:12]
        job = DownloadJob(
            job_id=job_id,
            url=url,
            output_dir=self._config.download_path,
            quality=self._config.quality,
            audio_format=self._config.audio_format,
            format_id=format_id if format_id and format_id != "auto" else None,
            download_subs=self._config.download_subtitles,
            subtitle_langs=self._config.subtitle_langs,
            on_progress=self._on_job_progress,
            on_finished=self._on_job_finished,
        )
        self._jobs[job_id] = job
        payload = job.to_dict()
        payload["quality"] = self._config.quality
        self.jobAdded.emit(payload)
        job.start()
        self.toast.emit("info", "已加入下载队列")

    @Slot(str)
    def cancelJob(self, job_id: str) -> None:
        job = self._jobs.get(job_id)
        if job:
            job.cancel()
            self.toast.emit("warn", "正在取消下载…")

    @Slot(result=list)
    def listJobs(self) -> list:
        return [j.to_dict() for j in self._jobs.values()]

    def _on_job_progress(self, payload: dict) -> None:
        self.jobUpdated.emit(payload)

    def _on_job_finished(self, payload: dict) -> None:
        self.jobFinished.emit(payload)
        status = payload.get("status")
        title = payload.get("title") or payload.get("url")
        if status == "completed":
            self.toast.emit("success", f"下载完成：{title}")
            self._append_history(
                title=payload.get("title") or "未命名",
                url=payload.get("url") or "",
                filepath=payload.get("filepath") or "",
                quality=payload.get("quality") or self._config.quality,
            )
        elif status == "cancelled":
            self.toast.emit("warn", "已取消下载")
        elif status == "error":
            self.toast.emit("error", f"下载失败：{payload.get('error') or '未知错误'}")
        self._maybe_auto_shutdown()

    def _active_job_count(self) -> int:
        busy = {"queued", "starting", "downloading", "processing", "cancelling"}
        return sum(1 for j in self._jobs.values() if j.status in busy)

    def _maybe_auto_shutdown(self) -> None:
        """Shutdown after all downloads finish, if user enabled auto_shutdown."""
        if not self._config.auto_shutdown:
            return
        if self._active_job_count() > 0:
            return
        if not self._jobs:
            return
        # Only shutdown if at least one job completed in this session
        completed = any(j.status == "completed" for j in self._jobs.values())
        if not completed:
            return
        self.toast.emit("warn", "全部任务已完成，60 秒后自动关机…")
        self._shutdown_armed = True

        def do_shutdown() -> None:
            import time

            for _ in range(60):
                if not self._shutdown_armed or self._active_job_count() > 0:
                    self.toast.emit("info", "已取消自动关机")
                    return
                time.sleep(1)
            self._perform_shutdown()

        import threading

        threading.Thread(target=do_shutdown, daemon=True).start()

    @Slot()
    def cancelAutoShutdown(self) -> None:
        self._shutdown_armed = False
        self.toast.emit("info", "已取消自动关机")

    def _perform_shutdown(self) -> None:
        self.toast.emit("warn", "正在关机…")
        try:
            if sys.platform == "win32":
                subprocess.Popen(["shutdown", "/s", "/t", "0"])
            else:
                subprocess.Popen(["shutdown", "-h", "now"])
        except OSError as e:
            self.toast.emit("error", f"关机失败：{e}")

    def _append_history(self, title: str, url: str, filepath: str, quality: str = "") -> None:
        from datetime import datetime

        entry = {
            "id": uuid.uuid4().hex[:10],
            "title": title or "未命名",
            "url": url or "",
            "filepath": filepath or "",
            "quality": quality or "",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "exists": bool(filepath and Path(filepath).exists()),
        }
        rest = [h for h in self._config.history if h.get("url") != entry["url"]]
        self._config.history = [entry] + rest[:79]
        save_history(self._config.history)
        self.historyChanged.emit()

    @Slot(result=list)
    def getHistory(self) -> list:
        items = []
        for h in self._config.history:
            fp = h.get("filepath") or ""
            items.append({**h, "exists": bool(fp and Path(fp).exists())})
        return items

    @Slot(str)
    def redownloadFromHistory(self, entry_id: str) -> None:
        entry = next((h for h in self._config.history if h.get("id") == entry_id), None)
        if not entry or not entry.get("url"):
            self.toast.emit("error", "历史记录缺少链接，无法重新下载")
            return
        self.startDownload(entry["url"], "auto")

    @Slot()
    def clearHistory(self) -> None:
        self._config.history = []
        save_history([])
        self.historyChanged.emit()
        self.toast.emit("info", "下载历史已清空")

    @Slot(str)
    def removeHistory(self, entry_id: str) -> None:
        self._config.history = [h for h in self._config.history if h.get("id") != entry_id]
        save_history(self._config.history)
        self.historyChanged.emit()

    # ----- shell helpers -----
    @Slot(result=str)
    def pickFolder(self) -> str:
        from PySide6.QtWidgets import QFileDialog

        path = QFileDialog.getExistingDirectory(
            None,
            "选择下载目录",
            str(self._config.download_path),
        )
        if path:
            self.downloadDir = path
        return path or ""

    @Slot(str)
    def openFile(self, path: str) -> None:
        candidate = self._locate_file(path)
        if not candidate:
            hint = path or "(空路径)"
            self.toast.emit("error", f"文件不存在：{Path(hint).name if path else hint}")
            self.openDownloadDir()
            return
        try:
            if sys.platform == "win32":
                os.startfile(str(candidate))  # noqa: S606
            else:
                subprocess.Popen(["xdg-open", str(candidate)])
        except OSError as e:
            self.toast.emit("error", f"无法打开文件：{e}")

    def _locate_file(self, path: str) -> Path | None:
        if not path:
            return None
        p = Path(path)
        if p.is_file():
            return p
        folder = self._config.download_path
        name = p.name
        stem = re.sub(r"\.f\d+", "", p.stem)
        patterns = [name, f"{stem}.*"]
        try:
            for pattern in patterns:
                for hit in folder.glob(pattern):
                    if hit.is_file() and hit.suffix.lower() not in {".part", ".ytdl", ".temp"}:
                        return hit
        except OSError:
            pass
        try:
            for hit in folder.rglob(name):
                if hit.is_file():
                    return hit
        except OSError:
            pass
        return None

    @Slot()
    def openDownloadDir(self) -> None:
        folder = self._config.download_path
        folder.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(str(folder))  # noqa: S606
        else:
            subprocess.Popen(["xdg-open", str(folder)])

    @Slot(str, result=str)
    def formatSize(self, value: str) -> str:
        try:
            return format_bytes(float(value))
        except (TypeError, ValueError):
            return "—"

    @Slot(result=str)
    def pasteClipboard(self) -> str:
        from PySide6.QtGui import QGuiApplication

        clip = QGuiApplication.clipboard()
        text = clip.text().strip() if clip else ""
        return text

    @Slot(result=str)
    def supportedHint(self) -> str:
        return "支持 yt-dlp 兼容站点：YouTube / Bilibili / Twitter 等"
