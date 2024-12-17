from flask import Flask, render_template, request, jsonify
import os
import yt_dlp
import traceback
import threading
import tkinter as tk
from tkinter import scrolledtext

def log_error(e):
    with open("error_log.txt", "a") as f:
        f.write(str(e) + "\n")
        f.write(traceback.format_exc() + "\n")

# Flask app setup
app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"  # 默认下载文件夹

# 确保下载文件夹存在
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def download_video(url, output_folder):
    """
    使用 yt-dlp 下载视频
    :param url: 视频网址
    :param output_folder: 保存视频的文件夹
    :return: 下载结果消息
    """
    ydl_opts = {
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),  # 保存路径和文件名模板
        'format': 'bestvideo+bestaudio/best',  # 下载最佳视频和音频
        'merge_output_format': 'mp4',  # 合并输出为 mp4 格式
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            return "下载完成！"
    except Exception as e:
        return f"下载出错: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': '请输入有效的网址'}), 400

    message = download_video(url, DOWNLOAD_FOLDER)
    return jsonify({'status': 'success', 'message': message})

def run_flask_app():
    """
    运行 Flask 应用程序
    """
    app.run(debug=True, use_reloader=False)

def create_gui():
    """
    创建 Tkinter GUI，用于显示运行状态并控制应用退出
    """
    root = tk.Tk()
    root.title("App Monitor")
    root.geometry("500x400")

    # 显示状态的文本框
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20)
    text_area.pack(pady=10)

    # 退出按钮
    def quit_app():
        root.destroy()
        os._exit(0)  # 强制退出所有线程

    quit_button = tk.Button(root, text="退出应用", command=quit_app, bg="red", fg="white")
    quit_button.pack(pady=10)

    return root, text_area

def update_gui(text_area, message):
    """
    更新 GUI 文本框中的内容
    """
    text_area.insert(tk.END, message + "\n")
    text_area.see(tk.END)

if __name__ == '__main__':
    # 创建 GUI
    gui, text_area = create_gui()

    # 在另一个线程中运行 Flask
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    # 更新 GUI 状态
    update_gui(text_area, "Flask 应用程序已启动！")
    update_gui(text_area, "访问 http://127.0.0.1:5000 查看 Web 界面。")

    # 启动 Tkinter 主循环
    gui.mainloop()
