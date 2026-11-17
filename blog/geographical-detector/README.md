# 地理探测器 (Geographical Detector) 配套代码与数据

本目录为连享会「地理探测器」系列推文的配套材料，包含示例数据、离散化核心模块、OPGD 网格搜索、概念图与实操脚本，以及导出的结果表。所有代码均已实际运行，可直接复现推文中的结果。

## 目录结构

```text
geographical-detector/
  ndvi_40.csv               # 示例数据，713 个空间单元 × 7 个变量
  mydisc.py                 # 五种离散化方法，几何间隔与标准差对齐 R 版 GD
  opgd_search.py            # OPGD 网格搜索
  scripts/
    01-principle/           # 篇一 4 张概念示意图的绘图脚本
    02-detectors/           # 篇二 6 张概念示意图的绘图脚本
    03-opgd/                # 篇三本地验证脚本
    04-practice/            # 篇四批量 OPGD、主模型与绘图脚本
  results/                  # 篇四导出的因子、交互、生态结果表 (utf-8-sig)
```

## 环境依赖

- Python 3.10 及以上
- 第三方程序包：`geodetector`、`mapclassify`、`pandas`、`numpy`、`scipy`、`matplotlib`、`scikit-learn`

```bash
pip install geodetector mapclassify pandas numpy scipy matplotlib scikit-learn
```

## 快速开始

在本目录下运行，即可直接读取数据并导入核心模块，无需调整路径。

```python
import pandas as pd
from mydisc import disc_breaks, disc_labels
from opgd_search import opgd

dat = pd.read_csv("ndvi_40.csv")

# 对连续变量 Tempchange 执行 OPGD 网格搜索
best, res = opgd(dat["Tempchange"].values, dat["NDVIchange"].values)
print(best)
```

## 数据说明

`ndvi_40.csv` 为地理探测器的经典公开示例数据，包含 713 个空间单元，变量如下：

- `NDVIchange`：归一化植被指数变化量，被解释变量 (连续)
- `Tempchange`、`Precipitation`、`GDP`、`Popdensity`：连续解释变量
- `Climatezone`、`Mining`：分类解释变量

该数据与经管类研究同构：把 `NDVIchange` 替换为自己的被解释变量，把其余变量替换为实际因子，代码即可套用。

## 与推文的对应关系

| 推文 | 对应脚本 |
|---|---|
| 篇一：原理与 q 值 | `scripts/01-principle/` |
| 篇二：四大探测器原理 | `scripts/02-detectors/` |
| 篇三：OPGD 与离散化 | `mydisc.py`、`opgd_search.py`、`scripts/03-opgd/` |
| 篇四：Python 完整实操 | `scripts/04-practice/`、`results/` |
| 篇五：论文写作与误区 | 参考 `results/` 的结果表组织 |

## 说明

- 地理探测器测度的是空间解释力，而非因果效应，因果识别需结合相应的识别策略。
- 配图已托管于连享会阿里云 OSS，本仓库只保留可生成图片的脚本，不重复存放二进制图片。
