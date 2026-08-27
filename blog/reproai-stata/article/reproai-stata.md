

> **作者：** 连小白 (连享会)<br>
> **邮箱：** <lianxhcn@163.com>

&emsp;

- **Title**: ReproAI 实测：它能帮 Stata 复现包发现什么，又会漏掉什么？
- **Keywords**: ReproAI, Stata, 复现包, 静态检查, 可重复性, 论文复现


一套 Stata 代码在作者电脑上能够运行，不等于它已经是一个合格的复现包。换一台电脑，绝对路径失效；少复制一个辅助脚本，主程序中断；`bootstrap` 没有固定随机种子，结果每次略有不同；原始数据缺了一份，代码却悄悄缩小样本继续运行。这些问题未必涉及复杂的计量方法，却会直接增加复现成本。

[上一篇](https://www.lianxh.cn/search.html?s=reproai) 介绍了 [ReproAI](https://reproai.org/) 的公开功能：它面向 Stata、R 和 Python 复现包，主要完成结构扫描、风险排序、副本修订和可选冒烟测试。本文不再重复产品说明，而是追问一个更具体的问题：把一套事先埋入缺陷的 Stata 复现包交给 ReproAI，它究竟能发现什么，又会漏掉什么？

本文不做产品介绍式演示，而是做一次受控实测。完整的参考包、冻结缺陷包、检测矩阵和结果记录已公开在 [lianxhcn/data 的 ReproAI Stata 项目](https://github.com/lianxhcn/data/tree/main/blog/reproai-stata)，读者可据此核对本文的测试设计和结论。我们先用 Stata 自带的 `auto.dta` 建立一个已经跑通的参考包，再构造一个含有 10 项预设问题的缺陷包，并在第一次运行 ReproAI 之前冻结缺陷清单。结果很直接：在纳入核心静态检出率的 8 项缺陷中，ReproAI 0.4.10 找到 4 项，检出率为 50.0%；`fix --apply` 没有执行自动修复，也没有生成修复副本。

这不是一个可外推的“准确率”，更不是复现成功率。它只回答一个较窄但实用的问题：在这套小型 Stata 复现包中，ReproAI 能帮作者发现什么，又会漏掉什么？

![图 1：受控测试流程。正确参考包只用于建立基准；ReproAI 的输入仅为缺陷包。](https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/reproai-stata-fig01-test-flow-20260824-214221.png)

> **图 1：受控测试流程。** 正确参考包只用于建立可核对的基准；ReproAI 的输入仅为冻结后的缺陷包。D01–D10 在第一次运行 ReproAI 之前登记，工具没有看到缺陷编号、参考包或预期答案。

## 1. 实测设计：先建立一个能跑通的基准包

测试使用 Stata 自带的 1978 年汽车数据。为模拟研究者从本地原始文件开始工作的场景，我们没有让分析程序直接调用 `sysuse auto`，而是先生成稳定的观测编号 `car_id`，再按汽车产地把数据导出为两份 CSV，放入 `raw/` 文件夹：

- `raw/auto_domestic.csv`：52 辆国产车，`foreign = 0`；
- `raw/auto_foreign.csv`：22 辆进口车，`foreign = 1`。

导出程序的关键部分如下。`nolabel` 用来输出 `foreign` 的底层数值，而不是值标签。

```stata
version 17.0
clear all
sysuse auto, clear

gen long car_id = _n

preserve
    keep if foreign == 0
    export delimited using "raw/auto_domestic.csv", ///
        replace nolabel
restore

keep if foreign == 1
export delimited using "raw/auto_foreign.csv", ///
    replace nolabel
```

这两份文件是把同一张表按“观测行”拆开，所以重组时应当纵向追加，而不是按键横向合并。Stata 的 `append using` 接受 `.dta` 文件，因此先把第一份 CSV 临时保存，再读入第二份并追加：

```stata
clear
tempfile domestic

import delimited using "raw/auto_domestic.csv", ///
    clear varnames(1)
save `domestic'

import delimited using "raw/auto_foreign.csv", ///
    clear varnames(1)
append using `domestic'

sort car_id
isid car_id
assert _N == 74

save "data/auto_combined.dta", replace
```

这里最值得保留的不是 `append` 本身，而是后面的两个断言。`isid car_id` 检查编号是否唯一，`assert _N == 74` 检查样本量是否符合预期。文件能被读入，只说明语法没有报错；只有这些针对数据结构的检查通过，才能确认两份数据按预定方式拼了回来。

## 2. 基准结果：回归只用来核对执行

参考包估计下面这个简单模型：

$$
price_i = \alpha + \beta_1 mpg_i + \beta_2 weight_i + \beta_3 foreign_i + \varepsilon_i.
$$

普通回归采用 robust 标准误；另对 `mpg` 的系数做 200 次 bootstrap，并把随机种子固定为 `20260822`：

```stata
use "data/auto_combined.dta", clear

regress price mpg weight i.foreign, vce(robust)

bootstrap _b[mpg], reps(200) seed(20260822): ///
    regress price mpg weight i.foreign
```

StataNow/MP 19.5 运行参考包后，主回归结果如下：

| 变量 | 系数 | Robust 标准误 |
|---|---:|---:|
| `mpg` | 21.853604 | 80.746740 |
| `weight` | 3.464706 | 0.777617 |
| `foreign` | 3673.060378 | 664.936111 |

同一个参考包也在 Stata 17 中完成了兼容性运行。这组结果只用于确认数据、代码和输出链条确实可以执行，不用于解释汽车价格，也不承担因果含义。后文更不能把它写成“ReproAI 验证了回归结果”，因为 ReproAI 没有运行这个参考包。

本次测试环境为 Windows 10 专业版 22H2、Python 3.11.14、`reproai-prep 0.4.10`，规则版本为 2026.07.07。写清这些版本很重要：工具规则会更新，今天的扫描结果不必然等同于未来版本的结果。

## 3. 缺陷设置：先冻结问题，再让工具检查

如果先看工具报告，再总结“它发现了哪些问题”，很容易把工具说过的内容当成全部标准答案。为减少这种事后挑选，我们在第一次运行 ReproAI 之前，把 D01–D10 写入缺陷登记表并冻结。ReproAI 只接触 `broken-package/`，没有看到参考包、缺陷编号或预期答案。

| ID | 预设问题 | 核心检出率 | 实际结果 |
|---|---|:---:|---|
| D01 | 对按行切分的两份数据错误使用 `merge 1:1 car_id` | 否 | 未报告 |
| D02 | `master.do` 中硬编码本机绝对路径 | 是 | 检出，P0 |
| D03 | 主程序调用包内不存在的辅助脚本 | 是 | 检出，P0 |
| D04 | README 未记录软件和命令版本 | 是 | 未报告 |
| D05 | 对已存在的输出目录直接执行 `mkdir` | 是 | 未报告 |
| D06 | bootstrap 未设置随机种子 | 是 | 检出，P1 |
| D07 | 进口车 CSV 缺失时，静默改用国产车样本 | 是 | 未报告 |
| D08 | README 缺少入口、耗时、依赖和输出说明 | 是 | 未报告 |
| D09 | 未解释地执行 `drop if price > 10000` | 否 | 未报告 |
| D10 | 代码没有标注表、图与生成命令的对应关系 | 是 | 检出，P2 |

D01 和 D09 事先被列为边界观察项，不进入核心检出率。判断 D01 需要知道两份 CSV 是按行切分的；判断 D09 则需要追问删去高价汽车是否有研究设计依据。把它们排除在分母之外，不是因为问题不重要，而是因为它们不能仅凭通用静态规则稳定裁定。

## 4. 检查结果：发现了哪些结构性问题

实际调用了通用检查和 AEA venue 检查。当前安装的引擎没有单独的 `comply` 子命令，合规检查通过 `check --venue aea` 完成。关键命令为：

```text
reproai check broken-package --out check-generic
reproai check broken-package --venue aea --out check-aea
reproai fix broken-package --venue aea --apply --out <fixed-copy>
```

检查共给出 5 项 advisory，其中 P0 两项、P1 一项、P2 两项。在本次 5 条 advisory 中，P0 的两项分别对应缺失脚本和绝对路径，P1 对应未设随机种子，P2 对应表图映射与输出产物提示；其余含义以工具当期规则为准。

| ReproAI 规则 | 优先级 | 对应问题 | 为什么有用 |
|---|:---:|---|---|
| `A5-stable-includes` | P0 | D03 | 主程序引用了不存在的 `04_format_tables.do`，运行一定会中断。 |
| `A9-nested-cd` | P0 | D02 | 绝对路径把项目绑定在作者电脑上，并可能破坏相对路径。 |
| `C8-unseeded-stochastic` | P1 | D06 | bootstrap 未设种子，随机抽样结果无法稳定重现。 |
| `A12-table-comment-mapping` | P2 | D10 | 估计命令没有 `Table N` 或 `Figure N` 锚点，不利于逐项核对。 |
| `D1-output-artifact-coverage` | P2 | D10 的相关方面 | 估计结果没有清楚保存为可定位的表格产物。 |

核心静态检出率的计算为：

$$
\text{Detection Rate} = \frac{4}{8} = 50.0\%.
$$

![图 2：核心缺陷检出情况与边界观察项。](https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/reproai-stata-fig02-detection-matrix-20260824-214221.png)

> **图 2：核心缺陷检出情况。** 8 项核心缺陷中检出 4 项、漏检 4 项；D01 和 D09 属于边界观察项，不进入分母。图中的 50.0% 只描述这一套受控测试包，不是 ReproAI 的一般准确率或复现成功率。

这个数值只描述本次人为构造的小样本缺陷集，不能外推为 ReproAI 对一般复现包的准确率。更有价值的发现是：文件依赖、绝对路径和随机种子都属于“扫描代码即可形成较明确判断”的问题，工具在这些位置能较快减轻人工排查负担；表图映射建议则有助于数据编辑和合作者追踪结果来源。

AEA profile 还给出 4 项 `pass`、1 项 `fail` 和 4 项 `needs_author_action`。例如，包顶层缺少 `README.pdf` 被判为失败；数据可得性、数据来源、计算要求、受限数据处理等内容需要作者确认。这里有一个细节：AEA 模块中的 `AEA-NO-ABS-PATHS` 显示为通过，通用 advisory 却检出了硬编码 `cd`。本次只能说明不同模块的规则覆盖不完全一致，不能据此简单断言其中一项一定是误报。

## 5. 漏检边界：代码能跑，不等于样本正确

工具没有报告 D04、D05、D07 和 D08。其中最需要警惕的是 D07：如果 `auto_foreign.csv` 不存在，缺陷代码会继续使用 52 辆国产车做分析，而不是明确中止。对运行环境而言，这段代码“成功执行”了；对研究设计而言，样本已经从 74 条悄悄缩成 52 条。

这类 silent fallback 很难只靠“是否报错”判断。作者至少应在读入阶段显式确认文件和样本：

```stata
confirm file "raw/auto_domestic.csv"
confirm file "raw/auto_foreign.csv"

* 数据重组后再检查样本结构
assert _N == 74
assert inlist(foreign, 0, 1)
count if foreign == 0
assert r(N) == 52
count if foreign == 1
assert r(N) == 22
```

D01 和 D09 未被工具报告，进一步说明了同一个边界。`merge` 还是 `append` 取决于数据究竟按变量拆分还是按观测拆分；`drop if price > 10000` 是否合理，取决于事先声明的样本规则。静态检查可以发现常见代码形态，却不知道研究者为何构造这两份数据，也不能替作者决定哪些观测应该进入估计样本。

README 的漏检同样值得保留。工具的 AEA 模块提示了若干模板要求，但没有完整覆盖我们预设的版本、入口、运行时间、依赖和输出说明。对真实项目而言，这些内容仍应当由作者按一份明确的交付清单逐项核对。

## 6. 修复结果：没有生成自动修复副本

这次测试最容易被误写的地方，是 `fix --apply`。命令退出码为 0，但原始输出明确写道：

```text
No auto-safe fixes available.
5 advisory item(s) are propose-only — review and apply manually.
```

也就是说，ReproAI 没有修改原缺陷包，也没有创建预期的修复副本。随后对该目标路径执行 `check` 和 `gate` 得到退出码 2，原因只是目标目录不存在，不能解释为“修复后的 Stata 代码运行失败”。由于没有修复副本，本次也没有运行面向修复副本的 `debug` 冒烟测试。

这个结果并不意外。补齐缺失脚本需要知道文件来源；选择随机种子会改变 bootstrap 的具体随机实现；取消静默回退和解释样本删除都涉及作者意图。与其让工具擅自改动研究含义，把这些建议保留为 `propose-only` 更符合无损修复的边界。

为核对包的完整性，我们还比较了 `fix` 前后的 SHA-256，原始 `broken-package/` 保持不变。Stata 19.5 和 Stata 17 跑通的是正确的 `reference-package/`，不是一个并不存在的 ReproAI 修复包。由此能得出的结论只有两条：正确基准包可以运行，原缺陷包没有被工具偷偷改写。

> 本文测试的是一个由 Stata 自带 `auto.dta` 构造的小型复现包。ReproAI 在这里执行的是静态预检与材料合规检查；它不会替代对数据构造、样本筛选、识别策略和经济学解释的人工判断。本次 `fix --apply` 未生成自动修复副本，因此本文不把参考包的 Stata 运行结果归功于 ReproAI，也不声称 ReproAI 已验证回归结论。

## 7. 使用建议：把它放在提交前预检环节

基于这次测试，ReproAI 更适合放在“作者自查”与“正式复现”之间。一个稳妥的流程是：先冻结待提交版本并保留原包，再运行静态检查；优先处理 P0、P1，并逐项核对工具没有覆盖的数据读取、样本筛选和 README；如果工具实际生成了修复副本，再审查差异；随后在干净目录中用目标版本的 Stata 从入口程序完整运行，并把表、图、日志和论文逐项对应。

提交前至少还要人工确认以下事项：

- 每个输入文件都显式检查，缺失时停止运行，而不是换样本继续；
- 数据拆分方式与 `append`、`merge` 的选择一致，合并后检查唯一键、样本量和分组数；
- 随机过程设置种子，并记录 Stata、Python/R 及用户命令版本；
- 顶层入口能够在新目录运行，输出目录的创建可以重复执行；
- README 写明入口、依赖、预计耗时、数据来源、输出位置和受限数据安排；
- 每张表、每幅图都能追溯到具体脚本、命令和实际输出文件。

因此，本文对 ReproAI 的评价是有限而正面的：它能较快发现一部分结构性、可移植性和随机性问题，也能提醒作者整理表图映射；但静态扫描的盲区会直接落在数据逻辑、样本规则和研究判断上。更合适的用法不是“让 AI 替我复现”，而是“在交包之前，让它先帮我做一轮有边界的材料体检”。

### 复现材料

本文项目已公开在 [lianxhcn/data 的 ReproAI Stata 项目](https://github.com/lianxhcn/data/tree/main/blog/reproai-stata)。公开目录保留支撑文章结论所需的材料：

- `reference-package/`：能够运行的正确参考包；
- `broken-package/`：冻结后的缺陷包；
- `docs/defect-register.md`：预设缺陷登记；
- `docs/detection-matrix.csv`：逐项检出矩阵；
- `expected-results/`：冻结的基准结果；
- `reproai-runs/raw-reports/`：ReproAI 的必要 JSON、stdout 和修复结果记录。

### 参考文献

1. Horiuchi, Y. (n.d.). *AI-Assisted Research Project Management and Replication Guide*. [Link](https://yhoriuchi.github.io/replication-package-guide/), [PDF](), [Google](<https://scholar.google.com/scholar?q=Yusaku+Horiuchi+AI-Assisted+Research+Project+Management+and+Replication+Guide>), [GitHub](https://github.com/yhoriuchi/replication-package-guide/).
2. ReproAI. (**2026**). *ReproAI Prep: Author-facing replication-package pre-diagnose tool* (version and rule set checked on 2026-08-23). [Link](https://github.com/reproai/reproai), [PDF](), [Google](<https://scholar.google.com/scholar?q=ReproAI+Prep+author-facing+replication-package+pre-diagnose+tool>). [Website](https://reproai.org/), [Install](https://github.com/reproai/reproai/blob/main/INSTALL_FOR_AI.md).
3. Xu, Y., & Yang, L. Y. (**2026**). *Scaling Reproducibility: An AI-Assisted Workflow for Large-Scale Replication and Reanalysis* (arXiv:2602.16733, v3). arXiv. [Link](https://doi.org/10.48550/arXiv.2602.16733), [PDF](https://arxiv.org/pdf/2602.16733), [Google](<https://scholar.google.com/scholar?q=Scaling+Reproducibility%3A+An+AI-Assisted+Workflow+for+Large-Scale+Replication+and+Reanalysis>).

### 相关推文

- [Claude Code Skills 写作指南：如何写好一个可复用的 SKILL.md](https://www.lianxh.cn/details/1791.html)
- [没有 Claude Code，如何实现 Skills？ChatGPT、DeepSeek、豆包](https://www.lianxh.cn/details/1794.html)
