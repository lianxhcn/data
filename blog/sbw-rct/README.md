# SBW：随机实验中的稳定平衡权重

连享会推文《SBW：稳定平衡权重法如何提高随机实验的估计精度？》配套材料。两个 Python 脚本可以独立运行，无需 clone 整个 data 仓库。此目录遵循用户指定的 `lianxhcn/data/blog/sbw-rct` 资源位置。

全部数据为教学模拟，代码为独立实现，不是原论文复现包，也不包含 AMP 试验数据。

## 1. 文件

| 文件 | 用途 |
| --- | --- |
| [sbw_apply.py](sbw_apply.py) | 多协变量权重、CSV 读写、ATE/RD/RR/MW 与完整 bootstrap |
| [sbw-demo.py](sbw-demo.py) | 手算案例、两个预测强度情形的重复模拟及二元协变量示例 |
| [sbw-trial.csv](sbw-trial.csv) | 600 人的固定模拟数据，可独立读取 |
| [python-effects.csv](python-effects.csv) | 2,000 次 bootstrap 的已运行参考结果 |
| [python-balance.csv](python-balance.csv) | 调整前后均值的已运行参考结果 |
| [sbw_optweight.R](sbw_optweight.R) | 已实测的 R 权重、四项指标与完整 bootstrap |
| [r-effects.csv](r-effects.csv) | 与 Python 使用共同抽样索引的 R 参考结果 |
| [LICENSE](LICENSE) | 沿用 data 仓库已有 MIT 许可 |

## 2. 从生成 CSV 到完整估计

先下载 `sbw_apply.py`，在该文件所在目录的终端安装依赖并运行：

```bash
python -m pip install numpy scipy pandas
python sbw_apply.py --make-demo sbw-trial.csv
python sbw_apply.py --csv sbw-trial.csv --bootstrap 2000 --out results
```

如果已经下载了本目录的 `sbw-trial.csv`，跳过生成命令。生成命令不会覆盖同名文件。也可以用自己按下表整理的 CSV 替换输入，输出路径由 `--out` 指定。

| 列名 | 含义 | 编码/单位 |
| --- | --- | --- |
| A | 随机分配的培训资格 | 0=对照组，1=处理组 |
| age | 培训前年龄 | 岁 |
| education | 培训前受教育年限 | 年 |
| pre_income | 培训前一年收入 | 万元 |
| income | 培训后一年收入 | 万元 |
| employed | 随访时是否就业 | 0/1 |

本数据有 600 行、6 列，处理组 292 人、对照组 308 人，无缺失。输入数据与 pandas 输出 CSV 使用带 BOM 的 UTF-8 编码，便于 Windows Excel 查看。分类变量需先转成虚拟变量并避免完全共线。可以修改脚本的 `COVARIATES` 设置加入其他已编码的处理前协变量。

数据种子为 20260911，bootstrap 种子为 20260910。收入效应设为 0.6 万元；就业采用 logistic 概率模型，其中处理变量系数 0.4 属于 log-odds 尺度，不是 40 个百分点。

## 3. 结果如何查看

`results/effects.csv` 的实际参考结果如下，均为 SBW 的点估计与逐项 95% Wald 区间。区间没有进行多重检验调整。

| 指标 | 点估计 | 95% 区间 |
| --- | --- | --- |
| 收入 ATE (万元) | 0.583011853 | [0.421014732, 0.745008974] |
| 就业 RD (概率尺度) | 0.079379897 | [0.003726106, 0.155033688] |
| 就业 RR | 1.191532725 | [1.005714527, 1.411683133] |
| 收入 MW | 0.582117189 | [0.558798204, 0.605436174] |

RD 乘以 100 才得到百分点。RR 的 `se_working_scale` 对应 log(RR) 标准误，区间已转回 RR 原尺度。MW 是两组独立抽取两个人时的排序比较，不是个体受益比例。

`results/balance.csv` 保存各组的调整前均值、全样本目标和加权后均值。示例中最大绝对偏差约为 2.1e-14；两组最大权重约为 1.0962 和 1.1043，均无零权重。另有 `weighted-data.csv`、`bootstrap.csv`、`diagnostics.json`，用于检查个人权重、抽样结果和环境版本。

## 4. 重现手算和重复实验

只需下载另一个独立脚本 `sbw-demo.py`：

```bash
python -m pip install numpy
python sbw-demo.py
```

默认只计算，将手算数据、5,000 次重复模拟、二元协变量 bootstrap 和 JSON 汇总写入脚本所在目录。需要重新绘图时安装 Matplotlib，并通过 `--font` 指定自己的中文字体文件路径；制图不是估计的必要步骤。

原有预测较强设定下，未调整和 SBW 的经验标准差为 0.049924907240079204 与 0.043139750904629896，标准差下降约 13.6%。无预测作用情形下几乎没有收益。该 400 人重复模拟与本目录 600 人 CSV 示范承担不同任务，不应混为同一实验。

## 5. 运行验证与范围

原始参考环境：Python 3.12.13、NumPy 2.3.5、SciPy 1.17.0、pandas 2.2.3；绘图版本 Matplotlib 3.10.8。2026-09-07 本机复核环境：Python 3.11.14、NumPy 2.4.2、SciPy 1.15.3、pandas 2.3.3。两份脚本均已完整运行，原 5,000 次重复模拟的标准差与参考值一致。普通 CPU 即可，无需 GPU 或 API。

已运行：CSV 生成、重新读取、2,000 次完整 bootstrap；核对手算权重、MW、非负约束生效的情形，以及精确平衡无解时明确报错。权重没有按观察结果挑选，失败的重抽样不会静默删除。浮点输出可能因软件版本出现末位差异。

脚本适用于独立个体随机分配、相同完整分析样本、低维数值协变量。未实现复杂随机化、缺失数据、抽样权重或删失生存分析。对于很大的样本或很多协变量，应另行评估求解器性能。

R 已在 R 4.4.3、optweight 2.0.1、osqp 1.0.0 下实测。下载 `sbw_optweight.R` 和同一份 `sbw-trial.csv`，在 R 中安装一次 `install.packages("optweight")`，然后在终端运行：

```bash
Rscript --vanilla sbw_optweight.R sbw-trial.csv r-results
```

脚本保持 `tols=0`、`target.tols=0`、`min.w=0`、`norm="l2"`，并明确采用 `solver="osqp"`、`eps_abs=1e-9`、`eps_rel=1e-9`。`r-results/effects.csv` 保存四项指标与区间，`session-info.txt` 保存实际环境。

核验时采用与 Python 完全相同的 2,000 行重抽样索引，每次重新求目标均值和权重，失败次数为零。权重最大绝对差异小于 `3e-14`，点估计、标准误和区间端点最大差异小于 `6e-15`，最大标准化均值偏差小于 `9e-15`。`r-effects.csv` 是这次共同抽样核验的输出。

上述公开运行命令不需要共同索引文件，会使用 R 自身随机数生成器完成 2,000 次 bootstrap。R 与 Python 即使设定同一整数种子也不会产生相同抽样，因此读者重跑所得点估计应一致，标准误和区间允许有 Monte Carlo 波动。共同索引和全部重抽样日志不在公开资源范围内。

## 6. 来源

Irish, K., Zubizarreta, J., & Luedtke, A. (2026). Simple Covariate Adjustment for Many Estimands Using Stable Balancing Weights. [Link](https://doi.org/10.48550/arXiv.2609.01638), [PDF](https://arxiv.org/pdf/2609.01638).

实现对照：[optweight 官方文档](https://ngreifer.github.io/optweight/reference/optweight.html)。第三方论文仅提供链接，其权利不因本目录许可而改变。
