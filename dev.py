"""热重载启动脚本 - 监听 .py 文件变化自动重启应用"""
import os
import sys
import time
import subprocess
from pathlib import Path

WATCH_DIR = Path(__file__).parent
EXTENSIONS = ('.py',)
IGNORE = {'__pycache__', '.git', 'resource', '.workbuddy'}
DEBOUNCE = 1.0  # 秒，防止频繁重启

def get_mtimes():
    """获取所有 .py 文件的修改时间"""
    mtimes = {}
    for f in WATCH_DIR.rglob('*'):
        if f.is_file() and f.suffix in EXTENSIONS:
            rel = f.relative_to(WATCH_DIR)
            if not any(part in IGNORE for part in rel.parts):
                mtimes[str(f)] = f.stat().st_mtime
    return mtimes

def run_app():
    """启动应用，返回进程对象"""
    return subprocess.Popen(
        [sys.executable, str(WATCH_DIR / 'git_gui.py')],
        cwd=str(WATCH_DIR)
    )

def main():
    print("=" * 50)
    print("  Git Manager - 热重载模式")
    print("  监听文件变化，保存即重启")
    print("  按 Ctrl+C 停止")
    print("=" * 50)

    mtimes = get_mtimes()
    proc = run_app()
    print(f"  [启动] PID={proc.pid}")

    try:
        while True:
            time.sleep(0.5)

            # 检查进程是否还活着
            if proc.poll() is not None:
                print(f"  [退出] 进程已结束，重新启动...")
                time.sleep(1)
                mtimes = get_mtimes()
                proc = run_app()
                print(f"  [启动] PID={proc.pid}")
                continue

            # 检查文件变化
            new_mtimes = get_mtimes()
            changed = []
            for f, t in new_mtimes.items():
                if f not in mtimes or mtimes[f] != t:
                    changed.append(os.path.relpath(f, WATCH_DIR))

            # 检查删除的文件
            for f in mtimes:
                if f not in new_mtimes:
                    changed.append(os.path.relpath(f, WATCH_DIR))

            if changed:
                print(f"\n  [检测到变化]")
                for c in changed:
                    print(f"    → {c}")
                print(f"  [重启中...]")
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                time.sleep(DEBOUNCE)
                mtimes = get_mtimes()
                proc = run_app()
                print(f"  [启动] PID={proc.pid}")

    except KeyboardInterrupt:
        print("\n  [停止]")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("  已退出")

if __name__ == "__main__":
    main()
