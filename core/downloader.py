"""yt-dlp download engine with progress callbacks and bundled ffmpeg."""
from __future__ import annotations

import os
import re
import threading
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

import yt_dlp

from core.paths import ffmpeg_dir


class CancelledError(Exception):
    """Raised inside yt-dlp hooks to abort a download."""


@dataclass
class FormatOption:
    format_id: str
    ext: str
    resolution: str
    fps: float | None
    vcodec: str | None
    acodec: str | None
    filesize: int | None
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "format_id": self.format_id,
            "ext": self.ext,
            "resolution": self.resolution,
            "fps": self.fps,
            "vcodec": self.vcodec,
            "acodec": self.acodec,
            "filesize": self.filesize,
            "note": self.note,
        }


@dataclass
class VideoInfo:
    url: str
    title: str = ""
    uploader: str = ""
    duration: float | None = None
    thumbnail: str = ""
    webpage_url: str = ""
    formats: list[FormatOption] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "uploader": self.uploader,
            "duration": self.duration,
            "thumbnail": self.thumbnail,
            "webpage_url": self.webpage_url,
            "formats": [f.to_dict() for f in self.formats],
        }


def _format_size(num: int | None) -> str:
    if not num:
        return "—"
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024  # type: ignore[assignment]
    return f"{num:.1f} TB"


def format_bytes(num: float | None) -> str:
    return _format_size(int(num) if num else None)


def human_speed(bps: float | None) -> str:
    if not bps:
        return "—"
    return f"{_format_size(int(bps))}/s"


def human_eta(seconds: float | None) -> str:
    if seconds is None or seconds < 0 or seconds != seconds:
        return "—"
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    return f"{seconds // 3600}h {(seconds % 3600) // 60}m"


def quality_format_selector(quality: str, audio_format: str = "mp3") -> str:
    """Map UI quality preset to a yt-dlp format selector."""
    if quality == "audio":
        if audio_format == "m4a":
            return "bestaudio[ext=m4a]/bestaudio"
        if audio_format == "opus":
            return "bestaudio[ext=opus]/bestaudio"
        return "bestaudio/best"
    height = {
        "best": None,
        "1080": 1080,
        "720": 720,
        "480": 480,
    }.get(quality)
    if height is None:
        return "bestvideo+bestaudio/best"
    return (
        f"bestvideo[height<={height}]+bestaudio/"
        f"best[height<={height}]/best"
    )


def extract_info(url: str, progress: Optional[Callable[[str], None]] = None) -> VideoInfo:
    def log(msg: str) -> None:
        if progress:
            progress(msg)

    opts: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "ffmpeg_location": str(ffmpeg_dir()),
        "socket_timeout": 30,
    }
    log("正在解析链接…")
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if info is None:
            raise RuntimeError("无法解析该链接")
        if info.get("_type") == "playlist" and info.get("entries"):
            info = info["entries"][0] or info

        formats: list[FormatOption] = []
        for f in info.get("formats") or []:
            if f.get("vcodec") in (None, "none") and f.get("acodec") in (None, "none"):
                continue
            height = f.get("height")
            width = f.get("width")
            if height:
                resolution = f"{width or '?'}x{height}"
            elif f.get("acodec") not in (None, "none"):
                resolution = "audio"
            else:
                resolution = f.get("format_note") or f.get("resolution") or "—"
            note_parts = []
            if f.get("fps"):
                note_parts.append(f"{f['fps']:.0f}fps")
            if f.get("vcodec") and f["vcodec"] != "none":
                note_parts.append(str(f["vcodec"]).split(".")[0])
            if f.get("acodec") and f["acodec"] != "none":
                note_parts.append(str(f["acodec"]).split(".")[0])
            if f.get("tbr"):
                note_parts.append(f"{f['tbr']:.0f}k")
            formats.append(
                FormatOption(
                    format_id=f.get("format_id") or "",
                    ext=f.get("ext") or "",
                    resolution=resolution,
                    fps=f.get("fps"),
                    vcodec=f.get("vcodec"),
                    acodec=f.get("acodec"),
                    filesize=f.get("filesize") or f.get("filesize_approx"),
                    note=" · ".join(note_parts),
                )
            )

        return VideoInfo(
            url=url,
            title=info.get("title") or "未知标题",
            uploader=info.get("uploader") or info.get("channel") or "未知作者",
            duration=info.get("duration"),
            thumbnail=info.get("thumbnail") or "",
            webpage_url=info.get("webpage_url") or url,
            formats=formats,
        )


class DownloadJob:
    """One download running on a worker thread with cancel support."""

    def __init__(
        self,
        job_id: str,
        url: str,
        output_dir: Path,
        quality: str = "best",
        audio_format: str = "mp3",
        format_id: str | None = None,
        download_subs: bool = False,
        subtitle_langs: str = "zh-Hans,zh,en",
        on_progress: Optional[Callable[[dict], None]] = None,
        on_finished: Optional[Callable[[dict], None]] = None,
    ) -> None:
        self.job_id = job_id
        self.url = url
        self.output_dir = Path(output_dir)
        self.quality = quality
        self.audio_format = audio_format
        self.format_id = format_id
        self.download_subs = download_subs
        self.subtitle_langs = subtitle_langs or "zh-Hans,zh,en"
        self.on_progress = on_progress
        self.on_finished = on_finished
        self._cancel = threading.Event()
        self._thread: threading.Thread | None = None
        self.title = ""
        self.status = "queued"
        self.percent = 0.0
        self.speed = 0.0
        self.eta: float | None = None
        self.downloaded = 0
        self.total = 0
        self.error = ""
        self.filepath = ""
        self.video_id = ""
        self.started_at = 0.0

    def cancel(self) -> None:
        self._cancel.set()
        self.status = "cancelling"
        self._emit_progress()

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def join(self, timeout: float | None = None) -> None:
        if self._thread:
            self._thread.join(timeout)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.job_id,
            "url": self.url,
            "title": self.title,
            "status": self.status,
            "percent": self.percent,
            "speed": self.speed,
            "eta": self.eta,
            "downloaded": self.downloaded,
            "total": self.total,
            "error": self.error,
            "filepath": self.filepath,
            "quality": self.quality,
            "download_subs": self.download_subs,
            "speed_text": human_speed(self.speed if self.status == "downloading" else 0),
            "eta_text": human_eta(self.eta if self.status == "downloading" else None),
            "size_text": format_bytes(self.total or self.downloaded),
        }

    def _emit_progress(self) -> None:
        if self.on_progress:
            try:
                self.on_progress(self.to_dict())
            except Exception:
                pass

    def _emit_finished(self) -> None:
        if self.on_finished:
            try:
                self.on_finished(self.to_dict())
            except Exception:
                pass

    def _hook(self, d: dict) -> None:
        if self._cancel.is_set():
            raise CancelledError("用户取消")

        status = d.get("status")
        if status == "downloading":
            self.status = "downloading"
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes") or 0
            self.total = int(total or 0)
            self.downloaded = int(downloaded or 0)
            if total:
                self.percent = min(100.0, downloaded / total * 100.0)
            self.speed = float(d.get("speed") or 0)
            eta = d.get("eta")
            self.eta = float(eta) if eta is not None else None
            info = d.get("info_dict") or {}
            if info.get("title"):
                self.title = info["title"]
            self._emit_progress()
        elif status == "finished":
            self.percent = 100.0
            self.speed = 0.0
            self.eta = None
            # Intermediate path only — final merged/extracted path is resolved in _run.
            filename = d.get("filename")
            if filename and not self.filepath:
                self.filepath = filename
            self.status = "processing"
            self._emit_progress()

    def _build_opts(self) -> dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        outtmpl = str(self.output_dir / "%(title).200B [%(id)s].%(ext)s")

        if self.quality == "audio":
            postprocessors = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.audio_format,
                    "preferredquality": "0",
                }
            ]
            fmt = quality_format_selector("audio", self.audio_format)
            merge_format = None
        else:
            postprocessors = []
            fmt = (
                self.format_id
                if self.format_id and self.format_id != "auto"
                else quality_format_selector(self.quality, self.audio_format)
            )
            merge_format = "mp4"

        opts: dict[str, Any] = {
            "outtmpl": outtmpl,
            "format": fmt,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "ffmpeg_location": str(ffmpeg_dir()),
            "progress_hooks": [self._hook],
            "retries": 5,
            "fragment_retries": 5,
            "socket_timeout": 30,
            "concurrent_fragment_downloads": 4,
            "windowsfilenames": True,
        }
        if merge_format:
            opts["merge_output_format"] = merge_format
            opts["postprocessor_args"] = {
                "ffmpeg": ["-c:v", "copy", "-c:a", "copy", "-movflags", "+faststart"]
            }
        if postprocessors:
            opts["postprocessors"] = postprocessors
            opts["keepvideo"] = False

        # Subtitles: manual first, then auto-generated as fallback
        if self.download_subs:
            langs = [x.strip() for x in self.subtitle_langs.split(",") if x.strip()]
            if not langs:
                langs = ["zh-Hans", "zh", "en"]
            opts["writesubtitles"] = True
            opts["writeautomaticsub"] = True
            opts["subtitleslangs"] = langs
            opts["subtitlesformat"] = "srt/ass/vtt/best"
            # Keep sidecar .srt/.vtt next to the video (embed optional)
            embed = False
            if embed and merge_format:
                opts.setdefault("postprocessors", []).append(
                    {"key": "FFmpegEmbedSubtitle", "already_have_subtitle": False}
                )
        return opts

    def _resolve_final_filepath(self, info: dict | None, ydl: yt_dlp.YoutubeDL | None) -> str:
        """Pick the real on-disk file after merge / audio extract (not the intermediate)."""
        candidates: list[str] = []

        def add(value: Any) -> None:
            if value and isinstance(value, str):
                candidates.append(value)

        if info:
            self.video_id = str(info.get("id") or self.video_id or "")
            self.title = info.get("title") or self.title
            # yt-dlp updates filepath after postprocessors (merge / extract-audio)
            req = info.get("requested_downloads") or []
            for item in req:
                add(item.get("filepath"))
                add(item.get("filename"))
            add(info.get("filepath"))
            add(info.get("filename"))
            add(info.get("_filename"))

        add(self.filepath)

        # prepare_filename before postprocess; still useful as a stem match hint
        prepared = ""
        if ydl is not None and info:
            try:
                prepared = ydl.prepare_filename(info)
            except Exception:
                prepared = ""
        add(prepared)

        def exists_file(path_str: str) -> Path | None:
            try:
                p = Path(path_str)
                if p.is_file():
                    return p.resolve()
            except OSError:
                return None
            return None

        for cand in candidates:
            hit = exists_file(cand)
            if hit:
                return str(hit)

        # If intermediate remains but merge renamed (e.g. .f137.mp4 -> .mp4), search by stem/id
        search_dirs = {self.output_dir}
        for cand in candidates:
            try:
                search_dirs.add(Path(cand).parent)
            except Exception:
                pass

        stems = set()
        for cand in candidates + ([prepared] if prepared else []):
            name = Path(cand).name
            stems.add(name)
            # strip yt-dlp format suffix like ".f137" / ".f251"
            stems.add(re.sub(r"\.f\d+", "", name))
            stems.add(re.sub(r"\.f\d+", "", Path(cand).stem))

        if self.video_id:
            stems.add(self.video_id)

        skip_ext = {".part", ".ytdl", ".temp", ".download"}
        best: Path | None = None
        best_mtime = -1.0
        for folder in search_dirs:
            try:
                if not folder.is_dir():
                    continue
                for file in folder.iterdir():
                    if not file.is_file() or file.suffix.lower() in skip_ext:
                        continue
                    if ".part" in file.name or file.name.endswith(".ytdl"):
                        continue
                    name = file.name
                    stem = file.stem
                    matched = False
                    if self.video_id and self.video_id in name:
                        matched = True
                    else:
                        for s in stems:
                            if not s:
                                continue
                            if name == s or stem == Path(s).stem or name.startswith(Path(s).stem[:40]):
                                matched = True
                                break
                    if matched:
                        try:
                            mtime = file.stat().st_mtime
                        except OSError:
                            mtime = -1
                        if mtime > best_mtime:
                            best = file
                            best_mtime = mtime
            except OSError:
                continue

        if best is not None:
            return str(best.resolve())
        return str(Path(candidates[0]).resolve()) if candidates else ""

    def _run(self) -> None:
        self.started_at = time.time()
        self.status = "starting"
        self._emit_progress()
        try:
            opts = self._build_opts()
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                if info:
                    if info.get("_type") == "playlist" and info.get("entries"):
                        entries = [e for e in info.get("entries") if e]
                        info = entries[0] if entries else info
                    self.filepath = self._resolve_final_filepath(info, ydl)
                if self._cancel.is_set():
                    raise CancelledError("用户取消")
            if not self.filepath or not Path(self.filepath).is_file():
                # last chance: search output folder by video id
                self.filepath = self._resolve_final_filepath({"id": self.video_id, "title": self.title}, None)
            if not self.filepath or not Path(self.filepath).is_file():
                raise RuntimeError(
                    f"下载已结束但未找到输出文件（标题：{self.title or self.url}）"
                )
            self.status = "completed"
            self.percent = 100.0
            self.speed = 0.0
            self.eta = None
        except CancelledError:
            self.status = "cancelled"
            self.speed = 0.0
            self.eta = None
            self._cleanup_partial()
        except Exception as e:
            self.status = "error"
            self.error = str(e) or traceback.format_exc(limit=3)
            self.speed = 0.0
            self.eta = None
        self._emit_progress()
        self._emit_finished()

    def _cleanup_partial(self) -> None:
        """Best-effort remove of partial files for cancelled jobs."""
        if not self.filepath:
            return
        p = Path(self.filepath)
        for candidate in (p, p.with_suffix(p.suffix + ".part"), Path(str(p) + ".part")):
            try:
                if candidate.exists() and candidate.is_file():
                    candidate.unlink(missing_ok=True)
            except OSError:
                pass
        # Also clean temp fragments nearby
        try:
            for frag in self.output_dir.glob(f"{p.stem}*"):
                if frag.suffix in {".part", ".ytdl", ".temp"} or ".part" in frag.name:
                    frag.unlink(missing_ok=True)
        except OSError:
            pass
