# Eve Grabber

> **仅供学习使用，请严格遵守平台法律并保护创作者利益，禁止一切商业行为。**  
> 开源许可证见 [LICENSE](LICENSE)（MIT）；商业使用请先联系作者获得书面授权。

Python 运行时 + FFmpeg 已打包进 **onedir 文件夹**，双击 exe 即可使用，无需安装 Python / 配置环境变量。

## 功能

- 粘贴链接 → 解析标题 / 封面 / 作者 / 时长
- **合集 / 频道批量下载**：识别播放列表、B 站合集、YouTube 频道 / UP 主，一键「下载合集」「下载全部视频」，可限量（全部 / 最新 10/20/50/100）
- 画质预设：最佳 / 1080p / 720p / 480p / 仅音频（mp3）
- 实时进度：百分比、速度、ETA
- 任务队列：取消、打开文件、下载目录管理
- **下载历史**：持久化保存在本机（`%LOCALAPPDATA%\EveGrabber\`），支持一键重新下载 / 打开 / 删除 / 清空
- **字幕下载**：可选下载字幕（优先中文，含自动翻译字幕）
- **自动关机**：可选「全部下载完成后自动关机」，可随时取消
- 现代化玻璃拟态 UI + 动效
- 内置 FFmpeg（自动合并音视频）
- **下载历史**：持久化、按标题搜索、一键重新下载
- **客户端内热更新**：点击「检查更新」自动下载更新包并重启，无需打开浏览器
- **单实例限制**：重复双击只会提示，不会多开占用资源
- **YouTube 验证 / Cookie**：自动换客户端 + 限速 + 一键导入浏览器 Cookie，轻松过「请验证你不是机器人」
- 基于 [yt-dlp](https://github.com/yt-dlp/yt-dlp)，支持 [大量站点](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

## YouTube「请验证你不是机器人」

YouTube 的 bot 检查其实问了两件事：

| 问题               | 手段                                                |
| ------------------ | --------------------------------------------------- |
| 你是谁？           | Cookie（登录会话）                                  |
| 请求来自浏览器吗？ | 切换 yt-dlp 客户端（TV / Safari / MWeb…）+ 请求限速 |

本程序已内置组合策略，**多数情况无需任何操作**：

1. 自动依次尝试 `tv` → `web_safari` 等客户端（无需登录）
2. 仍失败则自动改用 Cookie（`web_safari`，**绝不会** Cookie + TV，避免会话失效）
3. 全部失败会弹出 **「Cookie · 绕过机器人验证」** 设置页，并给出中文步骤

### 一键获取 Cookie（推荐 · 无需装 Firefox / 无需退出浏览器）

Chrome / Edge **运行期间会锁定 Cookie 库**，直接读取会失败。本程序用系统自带的 Edge / Chrome 开**独立登录窗口**，通过调试接口直接取 Cookie：

1. 点界面 **「Cookie：…」** → **打开登录窗口**
2. 在弹出的独立窗口中登录 YouTube（**强烈建议小号**）
3. 点 **「我已登录，获取 Cookie」** → 自动写入 cookies.txt

> 主浏览器开着也能用；不装 Firefox；不受新版 Cookie 加密限制。

### 其他方式

- **从浏览器导入**：直接读本机浏览器 Cookie（Chrome/Edge 需先完全退出，Firefox 可边开边读）
- **选择 Cookie 文件**：在 `youtube.com` 页面用扩展 [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) 导出 Netscape 格式后导入

Cookie 文件：`%LOCALAPPDATA%\EveGrabber\cookies.txt`

### 模式说明

| 模式             | 行为                                    |
| ---------------- | --------------------------------------- |
| **自动**（默认） | 先换客户端；失败再用文件/浏览器 Cookie  |
| **浏览器**       | 每次直接读浏览器 Cookie（Firefox 最稳） |
| **文件**         | 固定使用 cookies.txt                    |
| **关闭**         | 不用 Cookie，仅客户端切换 + 限速        |

界面里还可手动指定 **客户端**（自动 / TV / Safari / MWeb）与 **限速保护**。

> 若使用代理 / VPN 的**机房 IP**，YouTube 会更严格。住宅网络通常更容易；Cookie 能显著提高成功率。

## ⚠️ 播放前请先安装 AV1 解码扩展（重要）

部分视频（尤其是 **B 站 / YouTube** 高画质或较新编码）使用 **AV1** 编码。

若下载完成后**能打开但无法播放 / 黑屏 / 只有声音**，几乎都是系统缺少 AV1 解码器，而不是下载坏了。

请提前安装微软官方 **AV1 Video Extension**（免费）：

- Microsoft Store：[AV1 Video Extension](https://apps.microsoft.com/detail/9mvzqvxjbq9v)
- 或在 PowerShell 中执行：

```powershell
winget install Microsoft.AV1VideoExtension
```

> **关于「集成到程序内」**：AV1 是 **Windows 系统级解码扩展**（受微软许可与商店分发约束），无法合法、稳定地打进本 exe 的单文件夹里。本程序选择**检测并提示**，请自行安装上述扩展（一次安装，系统所有播放器生效）。

## 直接使用（推荐）

1. 获取 `dist\EveGrabber\` **整个文件夹**
2. 双击其中的 `EveGrabber.exe`
3. 粘贴视频链接 → 点击「解析」或「直接下载」

> 注意：请整夹拷贝分发（exe + `_internal\` 等依赖），不要只拷贝 exe。  
> 同时只会允许运行 **一个实例**。

默认下载目录：exe 同级的 `downloads\`，可在界面中修改。

## 安卓端

同一产品线的 Android 客户端（Jetpack Compose + Miuix），功能与桌面端对齐：

- 粘贴链接解析 / 直接下载，支持 B 站、YouTube、X / Twitter、抖音、TikTok、微博等
- 合集 / 频道批量下载，可限量（5 / 10 / 20 / 50）
- 画质挡位、字幕、封面、下载队列、历史、断点续传
- 应用内 Cookie 捕获（YouTube / 抖音 / B 站 / X…）
- 设置 →「检查更新」：与桌面端**共用同一份 `update.json`**，下载 apk 后调起系统安装器

安装：下载 `EveGrabber-26.10.1.apk` 并允许安装未知来源；首次启动建议授予「所有文件访问」以便写入公共 `Download/EveGrabber`。

源码见 `android-app/compose-app/`，打包产物为 `EveGrabber-<版本>.apk`。

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

产物：`EveGrabber\`（内含 `EveGrabber.exe` 与依赖）。

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
EveGrabber.spec    # PyInstaller 配置
dist/EveGrabber/   # 打包产物（整夹分发）
```

## 许可证 / License

本项目采用 **MIT License**（见 [LICENSE](LICENSE)）。

同时请注意：

- 作者意向：**仅供学习与个人使用**，禁止将本软件用于侵权或未授权的商业分发
- 若需商业集成、上架或二次销售，请先联系作者获取书面许可
- 本软件依赖 **yt-dlp / FFmpeg / Qt(PySide6)** 等第三方组件，它们各自遵循原有许可证；使用 FFmpeg / 下载在线视频时，请自行遵守相关平台条款与版权法律

## 插画与许可

本应用图标使用 @living_deadroom 的原画。

- 角色「Eve」/ Eve.aic 原作美术与设定 © Living_deadroom（@Living_deadroom，twitter / X：Eve_scp exit），原作以 Creative Commons Attribution-ShareAlike 3.0 Unported（**CC BY-SA 3.0**）协议发布。
- 本应用内的首页表情插画为基于上述原作的再创作（已作适应性修改），依照 CC BY-SA 3.0 的「相同方式共享」条款，以同一协议（CC BY-SA 3.0）开源发布，源文件随应用仓库一并提供。
- Windows 版 exe 图标与 Android 版应用图标均直接使用上述原画，未作改动。

使用与再分发时请同时满足：

1. **署名**原作者 Living_deadroom，并注明本应用作过修改（图标除外，图标未修改）；
2. 衍生作品继续以 **CC BY-SA 3.0** 协议共享；
3. 不得附加额外限制条款。

协议全文：<https://creativecommons.org/licenses/by-sa/3.0/>

本应用与 Eve.aic 原作者无官方关联，角色著作权归原作者所有。

## 注意事项

- **强烈建议**先安装 AV1 Video Extension，否则部分视频无法播放（见上文）
- 下载完成后点「打开」若提示找不到文件，程序会自动打开下载目录并在历史中可重新下载
- 本软件仅供学习交流，请勿用于侵犯版权的用途

## 应用内更新（双端共用同一更新源）

更新源写在 `core/updater.py`（桌面端）与 `AppUpdater.kt`（安卓端），**两端读同一份清单**：

- 清单：`https://raw.githubusercontent.com/Thompson0075/Video_Downloader/main/update.json`
- 安装包：GitHub **Releases** 资产

### 双端统一的 update.json

一份清单同时服务 Windows 与 Android，按字段分流、互不干扰：

```json
{
  "version": "26.10.1",
  "notes": "更新说明",
  "package_url":         "https://github.com/Thompson0075/Video_Downloader/releases/download/v26.10.1/EveGrabber-win64-26.10.1.zip",
  "sha256":              "<zip 的 SHA-256>",
  "android_package_url": "https://github.com/Thompson0075/Video_Downloader/releases/download/v26.10.1/EveGrabber-26.10.1.apk",
  "android_sha256":      "<apk 的 SHA-256>",
  "min_android_versionCode": 49
}
```

| 字段                                     | 谁在读 | 说明                             |
| ---------------------------------------- | ------ | -------------------------------- |
| `version`                                | 双端   | 与本地版本比较，决定是否提示更新 |
| `package_url` / `sha256`                 | 桌面端 | zip 整包，下载后覆盖安装并重启   |
| `android_package_url` / `android_sha256` | 安卓端 | apk，下载后调起系统安装器        |
| `min_android_versionCode`                | 安卓端 | 可选，最低支持的 versionCode     |

缺失的字段只表示「这一端暂无更新」，**不会**影响另一端。你也可以只发桌面包或只发 apk。

### 各端行为

- **桌面端**：点「检查更新」→ 读清单 → 后台下载 zip → 校验 sha256 → 自动替换程序文件 → 重启。更新时保留 `downloads\`、`config.json`、`history.json`。
- **安卓端**：设置 →「检查更新」→ 读同一清单的 `android_package_url` → 下载 apk → 调起系统安装器。版本号采用与桌面一致的 `26.10.1` 形式。

**sha256 是什么？**  
对安装包算出的一段 64 位十六进制「指纹」。下载后指纹一致就说明文件没坏、没被篡改。  
`make_release_package.ps1` 会自动算好 zip 与 apk 的 sha256 并写入 `update.json`，**你不用手算**。
