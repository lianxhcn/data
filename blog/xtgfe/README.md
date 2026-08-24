# `xtgfe` 推文与独立复现材料

本目录对应连享会推文《分组固定效应模型 (GFE)：从双向固定效应到数据驱动的潜在分组》。正文、数据、Stata 程序、核验结果和图片集中存放于此，不依赖原始工作目录。

公开地址：<https://github.com/lianxhcn/data/tree/main/blog/xtgfe>

## 1. 目录

```text
xtgfe-blog/
├─ README.md
├─ xtgfe-article-final.md
├─ code/
│  ├─ run-all.do
│  └─ build-figures.do
├─ data/
│  ├─ xtgfe-bm2015.dta
│  ├─ static-bic-cached.csv
│  ├─ dynamic-bic-cached.csv
│  └─ g4-country-groups.csv
├─ output/
└─ logs/
```

`output/` 已附经过核验的 CSV 和 5 张发布图。重新运行程序时，稳定文件名的复现结果会写入同一目录。`logs/` 保存正式运行日志。

## 2. 软件环境

本项目已在以下环境完整测试：

- StataNow/MP 19.5；
- `xtgfe` 1.5.5；
- `reghdfe` 6.13.1。

首次运行前，在 Stata 中安装命令：

```stata
ssc install xtgfe, replace
ssc install ftools, replace
ssc install reghdfe, replace
```

`xtgfe` 使用随机搜索。两个程序都在相关估计前重置随机种子，避免前序命令改变后续分组。

## 3. 直接复现 5 张图

将 Stata 的工作目录切换到本项目根目录，再运行：

```stata
cd "D:/your-path/xtgfe-blog"
do "code/build-figures.do"
```

该程序通常需要约 2–3 分钟。它使用已经核验的动态 BIC 路径，不重新执行耗时的 $G=1,\ldots,15$ 搜索。程序会生成 5 张图、绘图 CSV、教学模拟分组诊断、$G=4$ 组别计数和 `logs/build-figures.log`。

## 4. 完整复现正文结果

若要重新估计静态和动态 BIC、三类标准误、桥梁回归、两组 999 次 bootstrap 以及全部图片，运行：

```stata
cd "D:/your-path/xtgfe-blog"
do "code/run-all.do"
```

完整程序耗时较长。基准机器上，两次 BIC 搜索和多组 bootstrap 合计可能需要 20–40 分钟。程序不会筛除 bootstrap 极端重复样本。

主要输出包括：

- `output/static-bic-full.csv`；
- `output/dynamic-bic-full.csv`；
- `output/model-results-full.csv`；
- 5 份绘图及对应 CSV；
- `logs/run-all.log` 和 `logs/build-figures.log`。

## 5. 核验基准

- 数据应为 90 个国家、7 个五年期、630 条观测。
- 静态和动态 BIC 都应选择 $G=10$，但两张 BIC 表来自不同模型，不能混用。
- 动态 $G=10$ 的 `lag_dem` 约为 0.2772，`lag_income` 约为 0.0753，模型隐含的长期乘数约为 0.1041。
- $G=4$ 的组规模应为 33、13、26、18。
- `xtgfe fx`、`e(alpha)` 和手工残差均值应在数值精度范围内一致。
- 999 次 bootstrap 中，`lag_dem` 的标准误通常约为 0.229–0.235，高于论文补充材料约 0.124 的参考值。当前差异原因尚未完全解释。

## 6. 文件来源与边界

`xtgfe-bm2015.dta`、动态 BIC 路径和参考国家分组来自本项目已经发布并核验的本地快照。缓存 CSV 用于快速制图；`run-all.do` 会从原始 `.dta` 文件重新估计两套 BIC。

这些结果用于说明模型设定、分组不确定性和软件操作。它们不能单独建立收入影响民主的因果关系。AI 或自动化工具可以帮助整理复现流程，但识别策略、估计设定和结果解释仍需研究者负责。
