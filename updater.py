import requests
import zipfile
import io
import os
import shutil
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def get_remote_version():
    try:
        version_file_url = "http://tool.yiranalso.site/tool/video_downloader/version.txt"
        response = requests.get(version_file_url)

        if response.status_code == 200:
            return response.text.encode('gbk').decode('utf-8').strip()
        else:
            print(f"获取远程版本号失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"请求远程版本号时发生错误: {e}")
        return None

def get_local_version(file_path="current_version.txt"):
    try:
        with open(file_path, "r", encoding="GBK") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("本地版本文件未找到，使用默认版本号。")
        return None



def download_and_extract_repo(repo_url, local_dir):
    try:
        print("正在下载远程仓库文件...")
        response = requests.get(repo_url)

        if response.status_code == 200:
            print("下载成功，开始解压...")
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                temp_dir = "temp_repo"
                zip_file.extractall(temp_dir)

            extracted_dir = os.path.join(temp_dir, "Video_Downloader-main")
            if os.path.isdir(extracted_dir):
                print("解压完成，开始替换本地文件...")
                replace_files(extracted_dir, local_dir)
            else:
                print("未找到解压后的目录，更新失败。")

            shutil.rmtree(temp_dir)
            print("文件替换完成。")
        else:
            print(f"下载失败，HTTP 状态码: {response.status_code}")

    except Exception as e:
        print(f"下载或解压文件时发生错误: {e}")


# 替换本地文件
def replace_files(src_dir, dest_dir):
    try:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                relative_path = os.path.relpath(root, src_dir)
                dest_file = os.path.join(dest_dir, relative_path, file)

                os.makedirs(os.path.dirname(dest_file), exist_ok=True)

                shutil.copy2(os.path.join(root, file), dest_file)
                print(f"替换文件: {dest_file}")
    except Exception as e:
        print(f"替换文件时发生错误: {e}")


# 检查更新
def check_update():
    print("正在检查更新...")

    remote_version = get_remote_version()
    if remote_version:
        print(f"远程版本: {remote_version}")
    else:
        print("无法获取远程版本号，跳过更新检查。")
        return

    local_version = get_local_version()
    if local_version:
        print(f"本地版本: {local_version}")
    else:
        print("无法读取本地版本号，跳过更新检查。")
        return

    if remote_version != local_version:
        print("发现新版本，开始更新...")
        repo_url = "https://github.com/Thompson0075/Video_Downloader/archive/refs/heads/main.zip"

        local_dir = os.path.dirname(os.path.abspath(__file__))

        download_and_extract_repo(repo_url, local_dir)

        with open(os.path.join(local_dir, "current_version.txt"), "w", encoding="GBK") as file:
            file.write(remote_version)
    else:
        print("已是最新版本，无需更新。")


if __name__ == "__main__":
    check_update()
