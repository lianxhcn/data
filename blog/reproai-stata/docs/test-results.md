# ReproAI 测试结果

## 测试环境

- 项目目录：`D:/github_lianxh/data/blog/reproai-stata`。
- Stata 19.5：`D:/stata19/StataMP-64.exe`，StataNow/MP 19.5，revision 24 Sep 2025。
- Stata 17：`D:/stata17/StataMP-64.exe`。
- Python：3.11.14（现有 `dml050` 环境）。
- ReproAI：`reproai-prep 0.4.10`，按官方 `INSTALL_FOR_AI.md` 的 Codex 分支安装；引擎可导入 `line1_core`。

## 基准包与冻结

`source/00_export_raw.do` 实际使用 `sysuse auto` 生成了两份 CSV：国产车 52 辆、进口车 22 辆；重新导入和追加后为 74 辆，`car_id` 唯一。参考包在 Stata 19.5 中完整运行，产生 `table1_regression.csv`、`price_mpg_scatter.png`、日志和 200 次 bootstrap 结果。关键估计为：`mpg = 21.853604`（robust SE 80.746740）、`weight = 3.464706`（0.777617）、`foreign = 3673.060378`（664.936111）。

`expected-results/` 保存 Stata 19.5 的冻结产物与参考包 SHA-256 清单。D01--D10 在运行 ReproAI 前已写入冻结的 `defect-register.md`。缺陷包运行前有 7 个普通文件和 1 个清单文件，共 6,749 字节（普通文件统计不含其清单）。

## ReproAI 命令与首轮结果

引擎实际命令为 `reproai.exe check`（不存在独立的 `comply` 子命令；官方 Codex Skill 将合规检查映射为带 `--venue aea` 的 `check`）。原始 stdout、stderr 和 JSON 均在 `reproai-runs/raw-reports/`：

- 2026-08-23 16:53:41--16:53:42：`reproai check broken-package --out check-generic`，退出码 0。
- 2026-08-23 16:53:41--16:53:43：`reproai check broken-package --venue aea --out check-aea`，退出码 0。
- 2026-08-23 16:53:41--16:53:44：同一 AEA 命令作为 `comply` 等价检查，退出码 0。

AEA 首轮 advisory 为 5 项：P0 2 项（D03 缺失脚本、D02 硬编码 `cd`），P1 1 项（D06 无随机种子），P2 2 项（D10 的映射/产物覆盖）。它没有识别 D04、D05、D07、D08；D01 与 D09 是预先指定的观察项。核心静态检出率为 4/8 = 50.0%。未将 AEA 的 README.pdf 缺失计作误报；这是 venue profile 的独立合规要求。静态 AEA 报告为 4 pass、1 fail、4 needs_author_action。

## 修复、复查与执行测试

2026-08-23 16:54:10--16:54:11 运行：`reproai fix broken-package --venue aea --apply --out reproai-runs/fixed-copy/broken-package_reproai_fixed`，退出码 0。原始 stdout 明确写道：`No auto-safe fixes available.` 引擎将 5 个 advisory 全部保留为需人工复核的建议，未创建修复副本。

因此，后续 `check` 和 `gate` 对预期修复路径均以退出码 2 结束，原因是该目录不存在；这不是静态失败计数，也不是运行测试。没有对原始缺陷包进行人工修复，`debug` 未运行，独立修复副本测试也未运行。复算 SHA-256（排除清单自身）与运行前清单一致，确认 `broken-package/` 未变化。

Stata 17 于 2026-08-23 16:55:10--16:55:26 对**参考包**完成兼容性运行；表、图、日志及 bootstrap 产物均生成。该结果不应误表述为“ReproAI 修复副本通过”。

## 研究者必须判断的问题与限制

- D01 的 `merge` 与 D09 的高价车删除涉及数据构造和样本选择，不能由静态工具替代研究判断。
- D06 设置种子会固定新的随机实现，ReproAI 正确将其列为非无损的 propose-only 建议。
- D07 的静默数据回退必须由作者确认预期数据集；工具未识别该风险。
- `map` 未运行：项目没有真实 LaTeX 论文稿，不能伪造输入。
- 静态检查和 smoke test 都不验证因果识别、模型设定或经济学结论。
