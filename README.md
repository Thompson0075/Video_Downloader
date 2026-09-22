# 视频下载器 · Video Downloader

> **仅供学习使用，请严格遵守平台法律并保护创作者利益，禁止一切商业行为。**

Python 运行时 + FFmpeg 已打包进 **onedir 文件夹**，双击 exe 即可使用，无需安装 Python / 配置环境变量。

## 功能

- 粘贴链接 → 解析标题 / 封面 / 作者 / 时长
- 画质预设：最佳 / 1080p / 720p / 480p / 仅音频（mp3）
- 实时进度：百分比、速度、ETA
- 任务队列：取消、打开文件、下载目录管理
- **下载历史**：持久化保存在本机（`%LOCALAPPDATA%\VideoDownloader\`），支持一键重新下载 / 打开 / 删除 / 清空
- **字幕下载**：可选下载字幕（优先中文，含自动翻译字幕）
- **自动关机**：可选「全部下载完成后自动关机」，可随时取消
- 现代化玻璃拟态 UI + 动效
- 内置 FFmpeg（自动合并音视频）
- **单实例限制**：重复双击只会提示，不会多开占用资源
- 基于 [yt-dlp](https://github.com/yt-dlp/yt-dlp)，支持 [大量站点](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

## ⚠️ 播放前请先安装 AV1 解码扩展（重要）

部分视频（尤其是 **B 站 / YouTube** 高画质或较新编码）使用 **AV1** 编码。

若下载完成后**能打开但无法播放 / 黑屏 / 只有声音**，几乎都是系统缺少 AV1 解码器，而不是下载坏了。

请提前安装微软官方 **AV1 Video Extension**（免费）：

- Microsoft Store：[AV1 Video Extension](https://apps.microsoft.com/detail/9mvzqvxjbq9v)
- 或在 PowerShell 中执行：

```powershell
winget install Microsoft.AV1VideoExtension
```

## 直接使用（推荐）

1. 获取 `VideoDownloader\` **整个文件夹**
2. 双击其中的 `VideoDownloader.exe`
3. 粘贴视频链接 → 点击「解析」或「直接下载」

> 注意：请整夹拷贝分发（exe + `_internal\` 等依赖），不要只拷贝 exe。  
> 同时只会允许运行 **一个实例**。

默认下载目录：exe 同级的 `downloads\`，可在界面中修改。

## 从源码运行

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
.\.venv\Scripts\python main.py
```

## 打包（onedir 文件夹版）

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

产物：`VideoDownloader\`（内含 `VideoDownloader.exe` 与依赖）。

> 选用 onedir 是为了**启动更快**：无需像 onefile 那样每次解压到 `%TEMP%`。分发时请打包整个文件夹。

## 目录结构

```
main.py                 # 入口（含单实例保护）
core/                   # 下载引擎、配置、路径、Qt 桥接
ui/                     # QML 现代化界面
vendor/ffmpeg/bin/      # 内置 ffmpeg.exe / ffprobe.exe
assets/                 # 图标
scripts/                # 辅助脚本
build.ps1               # 一键打包脚本（onedir）
VideoDownloader.spec    # PyInstaller 配置
dist/VideoDownloader/   # 打包产物（整夹分发）
```

## 注意事项

- **强烈建议**先安装 AV1 Video Extension，否则部分视频无法播放（见上文）
- 下载完成后点「打开」若提示找不到文件，程序会自动打开下载目录并在历史中可重新下载
- 本软件仅供学习交流，请勿用于侵犯版权的用途
