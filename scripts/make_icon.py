"""Generate a simple app icon (PNG + ICO) with Qt — no Pillow required."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

from PySide6.QtCore import QRectF, Qt, QPointF
from PySide6.QtGui import (
    QGuiApplication,
    QIcon,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QColor,
    QPen,
    QFont,
    QRadialGradient,
)


def paint_icon(size: int = 256) -> QImage:
    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setRenderHint(QPainter.SmoothPixmapTransform, True)

    # Rounded background
    radius = size * 0.22
    path = QPainterPath()
    path.addRoundedRect(0, 0, size, size, radius, radius)
    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0.0, QColor("#5B7CFF"))
    grad.setColorAt(0.55, QColor("#6C8CFF"))
    grad.setColorAt(1.0, QColor("#A78BFA"))
    p.fillPath(path, grad)

    # Soft highlight
    glow = QRadialGradient(QPointF(size * 0.3, size * 0.25), size * 0.55)
    glow.setColorAt(0.0, QColor(255, 255, 255, 70))
    glow.setColorAt(1.0, QColor(255, 255, 255, 0))
    p.fillPath(path, glow)

    # Download arrow (shaft + head)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor("#FFFFFF"))

    cx = size / 2
    # stem
    stem_w = size * 0.12
    stem_h = size * 0.28
    p.drawRoundedRect(
        QRectF(cx - stem_w / 2, size * 0.22, stem_w, stem_h),
        stem_w * 0.35,
        stem_w * 0.35,
    )
    # arrow head
    head = QPainterPath()
    head.moveTo(cx, size * 0.62)
    head.lineTo(cx - size * 0.18, size * 0.40)
    head.lineTo(cx + size * 0.18, size * 0.40)
    head.closeSubpath()
    p.drawPath(head)

    # tray / base bar
    p.drawRoundedRect(
        QRectF(size * 0.22, size * 0.68, size * 0.56, size * 0.10),
        size * 0.04,
        size * 0.04,
    )

    p.end()
    return img


def save_ico(img: QImage, path: Path) -> None:
    """Write a multi-size PNG-in-ICO (Vista+), reliably picked up by Explorer / PyInstaller."""
    from PySide6.QtCore import QBuffer, QIODevice

    sizes = [16, 24, 32, 48, 64, 128, 256]
    png_blobs: list[tuple[int, int, bytes]] = []
    for size in sizes:
        scaled = img.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        buf = QBuffer()
        buf.open(QIODevice.WriteOnly)
        scaled.save(buf, "PNG")
        png_blobs.append((size, size, bytes(buf.data())))
        buf.close()

    import io

    count = len(png_blobs)
    out = io.BytesIO()
    out.write(struct.pack("<HHH", 0, 1, count))
    offset = 6 + 16 * count
    entries = b""
    data = b""
    for w, h, blob in png_blobs:
        ww = 0 if w >= 256 else w
        hh = 0 if h >= 256 else h
        entries += struct.pack("<BBBBHHII", ww, hh, 0, 0, 1, 32, len(blob), offset)
        data += blob
        offset += len(blob)
    out.write(entries)
    out.write(data)
    path.write_bytes(out.getvalue())


def main() -> int:
    QGuiApplication(sys.argv)
    assets = Path(__file__).resolve().parents[1] / "assets"
    assets.mkdir(exist_ok=True)
    img = paint_icon(256)
    png_path = assets / "icon.png"
    ico_path = assets / "icon.ico"
    img.save(str(png_path))
    save_ico(img, ico_path)
    print(f"Wrote {png_path}")
    print(f"Wrote {ico_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
