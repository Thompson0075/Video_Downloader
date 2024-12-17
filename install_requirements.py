import subprocess
import sys

def install_requirements():
    try:
        # 打开并读取当前目录下的 requirements.txt 文件
        with open('requirements.txt', 'r') as file:
            packages = file.readlines()

        # 使用 pip 安装每个包
        for package in packages:
            package = package.strip()  # 去除行末的换行符和多余空格
            if package:  # 如果行不为空
                print(f"正在安装: {package}")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print("所有包安装完毕！")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == '__main__':
    install_requirements()
