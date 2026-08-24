# Codex 工作日志

## 预检

- 本地仓库：`D:/github_lianxh/data`；工作开始分支为 `content/agent-sna-auto-net`。
- 开始时仓库已有多项与本任务无关的未提交文件；本任务未修改、还原或暂存它们。
- 项目开始前 `blog/reproai-stata/` 不存在；本轮创建的目录是唯一新增项目目录。
- 实际 Stata 19.5 路径：`D:/stata19/StataMP-64.exe`；Stata 17 路径：`D:/stata17/StataMP-64.exe`；Python 为 3.11.14。

## 安装与命令记录

- 2026-08-23 读取官方 `https://raw.githubusercontent.com/reproai/reproai/master/INSTALL_FOR_AI.md`，克隆官方仓库并审阅 `codex-plugin/install.sh` 后执行 Codex 安装分支。
- 已链接 `reproai-check`、`reproai-comply`、`reproai-fix`、`reproai-debug`、`reproai-map` 等 Skills；Python 引擎版本为 `reproai-prep 0.4.10`。
- 直接调用 Stata GUI 的两次 `/e do` 尝试会脱离终端且没有执行目标文件，已判为无效；后续均使用等待子进程退出、并由临时 wrapper 显式 `cd` 到包根目录的方式。wrapper 与 Stata 日志保存在 `reproai-runs/execution-logs/` 或项目根目录的批处理日志中。
- ReproAI 的 `check`、AEA `check`、AEA 合规等价检查和 `fix --apply` 的参数、时间和退出状态见 `docs/test-results.md`，原始文件见 `reproai-runs/raw-reports/`。

## 生成与验证

- `source/00_export_raw.do` 从 Stata 自带 `auto.dta` 实际生成两份 CSV；两份副本的 SHA-256 相同。
- 参考包已用 Stata 19.5 和 Stata 17 运行。Stata 19.5 的结果冻结在 `expected-results/`。
- 原始缺陷包的运行前 SHA-256 清单为 `broken-package/MANIFEST-SHA256-before.txt`；复查证明其普通文件未变化。
- `fix --apply` 未产生副本，故没有运行 `debug`，也没有虚构独立复现结果。

## Git 与发布

- 未执行 `git add`、commit、push、PR 或远程覆盖操作。
- 预期网页地址：`https://github.com/lianxhcn/data/tree/main/blog/reproai-stata`。
- 该项目尚未推送；README 中 raw URL 仅是待替换格式，未声称可访问。
