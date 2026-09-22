# GitHub Release 发布说明模板

> 使用方法：复制下面模板正文，去掉首尾分隔线，替换 `{{...}}` 占位符后粘贴到 GitHub Release 描述框。  
> 标题（Release title）建议：`v{{版本号}} · {{一句话亮点}}`  
> Tag：`v{{版本号}}`（与 `update.json` 的 `version` 一致，例如 `2.0.5`）

---

## 📦 视频下载器 v{{版本号}}

**发布日期**：{{YYYY-MM-DD}}  
**适用平台**：Windows 10 / 11（x64）

### ✨ 更新内容

#### 新增
- {{新功能 1，例如：历史记录支持按标题搜索}}
- {{新功能 2，例如：客户端内热更新，点击「检查更新」自动下载安装}}

#### 优化
- {{体验/性能改进，例如：标题过长时单行省略，不再挤掉右侧按钮}}

#### 修复
- {{问题修复，例如：下载完成后点「打开」提示文件不存在}}

### 📥 下载

| 文件 | 说明 |
|------|------|
| `VideoDownloader-win64-{{版本号}}.zip` | **推荐**。解压后双击 `VideoDownloader\VideoDownloader.exe` |

**安装说明**

1. 下载 zip 并**整夹解压**到任意目录（不要只解压 exe）
2. 双击 `VideoDownloader.exe`
3. 下载文件默认在 exe 同级的 `downloads\`（可自定义）

> 旧版用户：客户端内点 **「检查更新」** 即可自动升级到本版本，无需手动下载。

### ⚠️ 使用前提示

- **强烈建议安装 AV1 解码扩展**，否则部分视频（B 站 / YouTube 高画质）无法播放：  
  [Microsoft Store · AV1 Video Extension](https://apps.microsoft.com/detail/9mvzqvxjbq9v)  
  或执行：`winget install Microsoft.AV1VideoExtension`
- 本软件**仅供学习使用**，请尊重创作者版权，禁止商业用途
- 支持站点以 [yt-dlp 兼容列表](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) 为准

### 🔧 开发者备注（可选删除）

**校验（如已填写 sha256）**

```text
sha256: {{更新包 sha256，可留空}}
```

**热更新清单**（发布后请同步提交到仓库 `main`）

```json
{
  "version": "{{版本号}}",
  "notes": "{{与上方「更新内容」一致的一两句话摘要}}",
  "package_url": "https://github.com/Thompson0075/Video_Downloader/releases/download/v{{版本号}}/VideoDownloader-win64-{{版本号}}.zip",
  "sha256": "{{可选}}"
}
```

**打包命令**

```powershell
powershell -ExecutionPolicy Bypass -File scripts\make_release_package.ps1 -Version {{版本号}}
```

**本地验证更新流程**

```powershell
.\.venv\Scripts\python.exe scripts\test_updater.py
```

---

## 当前版本可直接粘贴的示例（v2.0.5 占位已按现有功能填好）

```markdown
## 📦 视频下载器 v2.0.5

**发布日期**：2026-09-23  
**适用平台**：Windows 10 / 11（x64）

### ✨ 更新内容

#### 新增
- 下载历史：持久化保存、按标题搜索、一键重新下载
- 客户端内热更新：点「检查更新」自动下载 zip 并安装重启（不跳浏览器）
- 可选下载字幕（优先中文，含自动/翻译字幕）
- 可选「全部下载完成后自动关机」

#### 优化
- 历史区布局重叠修复；标题过长单行省略，按钮不再被挤出
- onedir 打包，启动更快

#### 修复
- 下载完成后点「打开」提示「文件不存在」（合并/转码后路径已正确识别）

### 📥 下载

| 文件 | 说明 |
|------|------|
| `VideoDownloader-win64-2.0.5.zip` | **推荐**。解压后双击 `VideoDownloader\VideoDownloader.exe` |

**安装说明**

1. 下载 zip 并**整夹解压**到任意目录
2. 双击 `VideoDownloader.exe`
3. 默认下载目录为 exe 同级 `downloads\`

> 旧版用户：客户端内点 **「检查更新」** 即可自动升级。

### ⚠️ 使用前提示

- **请先安装 [AV1 Video Extension](https://apps.microsoft.com/detail/9mvzqvxjbq9v)**，否则部分视频无法播放  
  （PowerShell：`winget install Microsoft.AV1VideoExtension`）
- 仅供学习使用，请尊重创作者版权，禁止商业用途

### 🔧 开发者备注

```json
{
  "version": "2.0.5",
  "notes": "历史搜索、客户端内热更新、字幕与自动关机。",
  "package_url": "https://github.com/Thompson0075/Video_Downloader/releases/download/v2.0.5/VideoDownloader-win64-2.0.5.zip",
  "sha256": ""
}
```
```
