# panelcheck_demo

Sphinx 教学用面板检查包，Python 3.11，提供主键检查、缺失汇总和面板概览。
只做描述性检查，不自动清洗数据，也不提供计量估计。

本项目位于 lianxhcn/data 仓库的 `blog/sphinx-panelcheck-demo/`。

## 安装与验证

在本目录执行 (Windows PowerShell)：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe -m pip install --no-build-isolation -e .
.venv\Scripts\python.exe tools/verify.py --stage local
.venv\Scripts\python.exe -m http.server 8000 --bind 127.0.0.1 --directory docs/_build/local/html
```

浏览器打开 http://127.0.0.1:8000/。重复验证时使用新的 stage 名，避免覆盖已有日志。
Linux 中将 `.venv\Scripts\python.exe` 替换为 `.venv/bin/python`。

requirements-lock.txt 固定实测依赖。首次安装需要网络或包缓存；模拟数据不依赖网络下载。
验证脚本执行 pytest、两个案例脚本、Markdown 中的所有 Python 块、Sphinx doctest、
严格 HTML 构建和 linkcheck，并检查网页内部链接、锚点与静态资源。
日志默认位于 `output/verification/{stage}/`。

## 文档和发布

`src/panelcheck/` 是真实包，`examples/` 生成模拟数据，`docs/` 保存文档源。
Markdown 叙述页使用 MyST；NumPy 风格 docstring 使用 napoleon；
`docs/api_functions.rst` 通过 autosummary 和 autodoc 自动生成 API 页面。
`docs/generated/` 和 `docs/_build/` 是构建产物，不提交到 Git。

部署由仓库根目录的 `.github/workflows/sphinx-panelcheck-demo-pages.yml` 管理。
PR 仅验证，main 上相关文件变化在验证通过后发布到 Pages 子路径。
文档地址为 https://lianxhcn.github.io/data/blog/sphinx-panelcheck-demo/，部署状态以 Actions 结果为准。
新增其他站点时应合并到同一 Pages artifact，避免多个工作流互相覆盖。

当前使用英文搜索索引，支持 API 名检索；中文分词搜索未验收。
仓库级 MIT 许可证保持不变。
