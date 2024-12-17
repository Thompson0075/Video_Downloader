import subprocess
import sys
import os
import threading


def run_install_requirements():

    print("正在安装依赖...")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    install_script_path = os.path.join(current_dir, 'install_requirements.py')

    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--progress-bar', 'on'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        if result.stdout:
            print("Install Requirements 输出:")
            print(result.stdout)
        if result.stderr:
            print("Install Requirements 错误:")
            print(result.stderr)

        if result.returncode == 0:
            print("依赖安装完成！")
        else:
            print(f"依赖安装失败，返回码: {result.returncode}")
            sys.exit(1)

    except FileNotFoundError:
        print(f"找不到 {install_script_path}，请检查路径。")
        sys.exit(1)
    except Exception as e:
        print(f"运行 install_requirements.py 时发生错误: {e}")
        sys.exit(1)



def check_flask_installed():
    try:
        subprocess.run([sys.executable, "-m", "pip", "show", "flask"], check=True)
        print("Flask 已安装。")
    except subprocess.CalledProcessError:
        print("Flask 未安装，请先安装 Flask。")
        sys.exit(1)

def run_updater():

    print("正在检查更新...")
    try:
        result = subprocess.run(
            [sys.executable, "updater.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        if result.stdout:
            print("Updater 输出:")
            print(result.stdout)
        if result.stderr:
            print("Updater 错误:")
            print(result.stderr)

        if result.returncode == 0:
            print("更新检查完成！")
        else:
            print(f"更新失败，返回码: {result.returncode}")
            sys.exit(1)

    except FileNotFoundError:
        print("找不到 updater.py，请检查路径。")
        sys.exit(1)
    except Exception as e:
        print(f"运行 updater.py 时发生错误: {e}")
        sys.exit(1)


def run_app():

    print("正在启动应用程序...")

    check_flask_installed()

    try:
        process = subprocess.Popen(
            [sys.executable, "app.py"],  # 使用当前 Python 解释器
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        threading.Thread(target=log_output, args=(process, "App"), daemon=True).start()

        process.wait()
        if process.returncode == 0:
            print("应用程序正常退出。")
        else:
            print(f"应用程序退出时返回码: {process.returncode}")
            sys.exit(1)

    except FileNotFoundError:
        print("找不到 app.py，请检查路径。")
        sys.exit(1)
    except Exception as e:
        print(f"运行 app.py 时发生错误: {e}")
        sys.exit(1)


def log_output(process, stream_name):
    while True:
        line = process.stdout.readline()
        if line == "" and process.poll() is not None:
            break
        if line:
            print(f"[{stream_name}] {line.strip()}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    #run_install_requirements()

    # 运行 updater.py 检查更新
    run_updater()

    # 再运行 app.py
    run_app()
