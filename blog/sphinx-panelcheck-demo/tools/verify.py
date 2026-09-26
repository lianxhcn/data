"""执行代码、文档和本地链接验证；任一步失败立即停止并保留日志。"""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def run(args, name, logdir, cwd=ROOT):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    result = subprocess.run([sys.executable, *args], cwd=cwd, env=env,
                            capture_output=True, text=True, encoding="utf-8")
    content = f"COMMAND: python {' '.join(args)}\nCWD: {cwd}\nEXIT: {result.returncode}\n"
    content += result.stdout + result.stderr
    (logdir / f"{name}.log").write_text(content, encoding="utf-8")
    print(f"{name}: exit {result.returncode}", flush=True)
    if result.returncode:
        print(content)
        raise SystemExit(result.returncode)


def check_links(html):
    # 检查每个 HTML 的内部 href、片段 id 和静态资源文件，外链另由 linkcheck 检查。
    pages = {p.resolve(): BeautifulSoup(p.read_text(encoding="utf-8"), "html.parser")
             for p in html.rglob("*.html") if "_static" not in p.relative_to(html).parts}
    failures, count = [], 0
    for path, soup in pages.items():
        for element in soup.select("[href], [src]"):
            value = element.get("href", element.get("src", ""))
            url = urlsplit(value)
            if url.scheme or url.netloc or not value:
                continue
            count += 1
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not target.exists():
                failures.append(f"{path.name}: missing {value}")
            elif url.fragment and target in pages:
                anchor = unquote(url.fragment)
                if not pages[target].find(id=anchor):
                    failures.append(f"{path.name}: missing anchor {value}")
    return {"pages": len(pages), "links_checked": count, "failures": failures}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True)
    parser.add_argument("--report-dir", default="output/verification")
    options = parser.parse_args()
    logdir = Path(options.report_dir).resolve() / options.stage
    logdir.mkdir(parents=True, exist_ok=False)
    run(["-m", "pip", "check"], "pip-check", logdir)
    run(["-m", "pytest", "-q"], "pytest", logdir)
    run(["examples/make_data.py"], "make-data", logdir)
    run(["examples/analyze.py"], "example", logdir)
    # 每一段文档代码都在空临时目录的新进程执行，不能依赖之前页面定义的 df。
    blocks = []
    for page in sorted((ROOT / "docs").glob("*.md")):
        for i, match in enumerate(re.finditer(r"^```python\s*\n(.*?)^```", page.read_text(encoding="utf-8"), re.M | re.S), 1):
            name = f"doc-{page.stem}-{i}"
            with tempfile.TemporaryDirectory() as temporary:
                script = Path(temporary) / "example.py"
                script.write_text(match[1], encoding="utf-8")
                run([str(script)], name, logdir, cwd=temporary)
            blocks.append(name)
    (logdir / "executed-blocks.json").write_text(json.dumps(blocks, indent=2), encoding="utf-8")
    build = ROOT / "docs" / "_build" / options.stage
    for builder in ["doctest", "html", "linkcheck"]:
        run(["-m", "sphinx", "-E", "-a", "-W", "--keep-going", "-b", builder,
             "docs", str(build / builder)], f"sphinx-{builder}", logdir)
    result = check_links(build / "html")
    (logdir / "local-links.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result), flush=True)
    if result["failures"]:
        raise SystemExit(1)
    print("ALL CHECKS PASSED", flush=True)


if __name__ == "__main__":
    main()
