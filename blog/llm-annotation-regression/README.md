# LLM 文本标注：准确率很高，回归结论就可靠吗？

丁星星 (连享会) 推文的配套资源。这里用 100 个虚构项目说明：即使两套标签具有相同的准确率、精确率、召回率和混淆矩阵，误判对象不同，也可能使简单 OLS 系数一正一负。

所有数据均为确定性教学构造，无需 API 密钥或外部数据。本文借鉴 Carlson and Burbano (2026) 提出的标注验证问题；本目录不包含该论文的真实众筹数据，也不复现其 Logit 实验。

## 文件用途

| 文件 | 用途 |
| --- | --- |
| [llm_annotation_demo.py](llm_annotation_demo.py) | 构造数据、估计 OLS、计算分类指标、核对数值并绘图 |
| [llm-annotation-toy-data.csv](llm-annotation-toy-data.csv) | 100 条教学观测 |
| [llm-annotation-toy-results.csv](llm-annotation-toy-results.csv) | 设定标签及 A、B 两套误分类标签的核验结果 |
| [llm-annotation-regression-comparison-20260907-185451.png](llm-annotation-regression-comparison-20260907-185451.png) | 推文使用的中文配图，1200 × 850 px |

## 运行方法

打开[脚本原文](https://raw.githubusercontent.com/lianxhcn/data/main/blog/llm-annotation-regression/llm_annotation_demo.py)，保存为 `llm_annotation_demo.py`，然后在该文件所在目录打开终端。脚本自行生成数据，无需事先下载两个 CSV。

```bash
python -m pip install numpy==2.3.5 matplotlib==3.10.8
python llm_annotation_demo.py
```

2026 年 10 月 19 日已在独立的 Python 3.12.14 环境中，使用上述 NumPy 和 Matplotlib 版本实际运行，并单独核对了推文的精简代码。

正常运行时会显示三个系数和 `All checks passed`，随后列出两个 CSV 和一张 PNG 的保存路径：

| 标签 | 准确率 | OLS 系数 |
| --- | ---: | ---: |
| 设定标签 (`true`) | 1.00 | 0.3000 |
| 标注 A | 0.90 | -0.1625 |
| 标注 B | 0.90 | 0.4625 |

A、B 两套标签均有 TP=10、FP=10、FN=0、TN=80，精确率为 0.50，召回率为 1.00，F1 为 2/3。代码还用两组成功率之差独立核对了 OLS 系数。

默认输出写入脚本所在目录；重复运行会更新两个同名 CSV。配图以运行时的北京时间命名，因此文件名与本目录保留的推文配图不同。图中的单位为百分点，即 OLS 系数乘以 100。未绘制置信区间，因为本例只展示固定数据中的算术关系。

如需改变输出目录，可运行 `python llm_annotation_demo.py --output-dir results`。脚本会尝试使用已安装的中文字体；没有合适字体时自动使用英文标签，也可用 `--font` 指定本地中文字体文件。完整脚本中的固定结果断言用于核验原例子；尝试改变误判数量和位置时，请使用推文中的精简代码。

## 数据字段

两个 CSV 均采用 UTF-8 BOM 编码。

| 数据字段 | 含义 |
| --- | --- |
| `project_id` | 教学项目编号，1–100 |
| `true_social_benefit` | 人为设定的社会效益标签，1 表示有，0 表示无 |
| `success` | 人为设定的众筹结果，1 表示成功，0 表示失败 |
| `label_A` | 将 10 个无社会效益且失败的项目误标为 1 |
| `label_B` | 将 10 个无社会效益且成功的项目误标为 1 |

结果表中，`label` 为标签方案，`n` 为观测数；`accuracy`、`precision`、`recall`、`f1` 为分类指标；`tp`、`fp`、`fn`、`tn` 为混淆矩阵计数；`success_rate_label1` 和 `success_rate_label0` 为按相应标签分组后的成功率；`ols_coefficient` 为含截距、无其他解释变量的 OLS 系数。

## 论文与方法来源

Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. *Strategic Management Journal, 47*(3), 699–725. [期刊论文](https://doi.org/10.1002/smj.70023)；[作者 PDF](https://faculty.wharton.upenn.edu/wp-content/uploads/2025/09/The-use-of-LLMs-to-Annotate-Data.pdf)；[作者代码仓库](https://github.com/LLMAnnotationResearch/llm-annotation-framework)。

推文另介绍 Egami et al. 的设计型监督学习 (DSL)：[2024 年 11 月 17 日工作论文](https://naokiegami.com/paper/dsl_ss.pdf)、[官方文档](https://naokiegami.com/dsl/)。本目录没有执行 DSL 校正。
