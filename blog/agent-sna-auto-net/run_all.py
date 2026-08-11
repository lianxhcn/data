"""一键生成数据、验证数据、分析网络并核验输出。"""

from pathlib import Path
import os
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def run(script: str) -> None:
    """使用当前解释器执行子脚本，失败时立即停止。"""
    command = [sys.executable, str(ROOT / "scripts" / script)]
    print(f"[run_all] running {script}")
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    subprocess.run(command, cwd=ROOT, check=True, env=env)


if __name__ == "__main__":
    for filename in (
        "generate_data.py",
        "validate_data.py",
        "analyze_network.py",
        "validate_outputs.py",
    ):
        run(filename)
    print("[run_all] all checks passed")
