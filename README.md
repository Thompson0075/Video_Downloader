**##本软件仅供学习使用，请严格遵守平台法律和保护创作者的利益，禁止一切商业行为！##**

**安装流程：**

本软件需要安装在python下运行，请提前安装好python环境。

![image](http://tool.yiranalso.site/tool/video_downloader/pictures/image-20241217014319633.png)

首先打开“启动前先运行本文件.bat”，等待必要模块的安装。

![image](http://tool.yiranalso.site/tool/video_downloader/pictures/image-20241217013802495.png)

必要模块装好后双击“启动器.exe”，会自动启动updater.py与app.py （Windows环境下双击start.bat亦可启动)。

![image](http://tool.yiranalso.site/tool/video_downloader/pictures/image-20241217013936176.png)

![image](http://tool.yiranalso.site/tool/video_downloader/pictures/image-20241217013908911.png)

![image](http://tool.yiranalso.site/tool/video_downloader/pictures/image-20241217014212052.png)

*如果启动器失效，或者想要绕过updater.py，请在当前目录下打开cmd，使用命令python app.py打开即可*

运行成功后会有检测程序检测模块缺失。
FFmpeg特殊，需要自己下载，然后在系统环境中配置。也可以选择使用本人提供的install_ffmpeg.exe脚本一键安装配置，但是请给予它管理员权限运行！

![image](http://tool.yiranalso.site/tool/video_downloader/pictures/image-20241217014127343.png)

![image](http://tool.yiranalso.site/tool/video_downloader/pictures/image-20241217014146570.png)


*本软件使用的是yt-dlp下载视频，支持[网站的列表](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)。*

**注意：**

如果下载阿B的视频无法播放，那是因为它是使用AV1方式解码，请自行查询自己的硬件是否支持AV1解码，然后去微软官方下载[Av1 Video Extension](https://apps.microsoft.com/detail/9mvzqvxjbq9v?hl=zh-cn&gl=US)或者其他的解码软件

![image](http://tool.yiranalso.site/tool/video_downloader/pictures/image-20241217012805235.png)

**其他事项**

本软件使用的是WebUI，请保证http://127.0.0.1:5000/的端口畅通无阻。
install_ffmpeg.exe会从[网站](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip)下载ffmpeg-7.1-essentials_build.zip文件，在C:/ffmpeg中解压，最终会将C:\ffmpeg\ffmpeg-7.1-essentials_build\bin加入到用户变量中。
如果在使用中有问题，请将error_log.txt发送至[邮箱](mailto:huyiran0075@gmail.com)。

**##再次重申：本软件仅供学习使用，请严格遵守平台法律和保护创作者的利益，禁止一切商业行为！##**
