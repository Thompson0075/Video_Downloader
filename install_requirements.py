import subprocess
import sys

def install_requirements():
    try:
        with open('requirements.txt', 'r') as file:
            packages = file.readlines()

        for package in packages:
            package = package.strip() 
            if package:
                print(f"正在安装: {package}")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print("所有包安装完毕！")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == '__main__':
    install_requirements()
