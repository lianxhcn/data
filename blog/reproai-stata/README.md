# ReproAI 的 Stata 复现包实测

本项目以 Stata 自带的 `auto.dta` 为数据来源，构造一个已验证的
`reference-package/` 和一个预先登记缺陷的 `broken-package/`。它用于记录
ReproAI 对计算复现材料、文件组织和静态风险的检查结果；不检验因果识别或
经济学结论。

## 运行参考包

1. 使用 Stata 17 或更高版本，在项目根目录运行：`do source/00_export_raw.do`。
   它从 `auto.dta` 生成两份 CSV：52 辆国产车和 22 辆进口车。
2. 将当前目录切换至 `reference-package/`，运行 `do master.do`。
3. 查看 `tables/table1_regression.csv`、`figures/price_mpg_scatter.png` 和
   `logs/reference_run.log`。

两份 CSV 是按观测行切分的，因此应以 `append using` 重新组合；按 `car_id`
使用 `merge` 并不符合这里的数据构造逻辑。

## 目录说明

- `reference-package/`：人工构造、Stata 独立验证的正确基准。
- `broken-package/`：预先登记 D01--D10 缺陷的唯一 ReproAI 输入。
- `reproai-runs/raw-reports/`：ReproAI 的未改写原始报告。
- `reproai-runs/fixed-copy/`：仅保存 ReproAI 实际生成的修复副本。
- `docs/`：缺陷登记、检测矩阵、测试报告与工作日志。

## 软件与依赖

测试优先使用 Stata 19.5，另行记录 Stata 17 测试。参考包仅依赖 Stata 内置
命令；ReproAI 的 Python 引擎版本和调用参数见 `docs/codex_work_log.md`。
预计一次参考包运行少于 1 分钟（bootstrap 为 200 次重复）。

## GitHub 链接说明

本项目已公开在 [lianxhcn/data 的 ReproAI Stata 目录](https://github.com/lianxhcn/data/tree/main/blog/reproai-stata)。
仓库中的 `reference-package/`、`broken-package/`、`reproai-runs/` 与 `docs/`
共同构成本文受控测试的可核对材料；推文正文位于 `article/reproai-stata.md`。
例如，原始数据文件可通过仓库页面中的对应文件访问。本文不以网页可访问性代替
Stata 运行验证，具体命令和结果仍以 `docs/test-results.md` 为准。
