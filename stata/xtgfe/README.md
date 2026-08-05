# `xtgfe`：Bonhomme and Manresa (2015) 复现实例

本目录用于存放连享会 `xtgfe` 推文的在线数据、Stata 程序和结果核对说明。案例复现 Bonhomme and Manresa (2015) 关于收入与民主的经验应用。

## 文件

- `xtgfe_bm2015.dta`：90 个国家、7 个五年期的平衡面板数据。
- `xtgfe_bm2015.do`：从数据检查、TWFE、BIC 选组，到 GFE 估计和组别路径绘图的完整程序。
- `xtgfe_expected_results.md`：关键结果、版本信息和本地测试清单。
- `xtgfe_model_results.md`：TWFE 与 GFE 的实测结果汇总。
- `xtgfe_bic_results.csv`：$G=1,\ldots,15$ 的完整 BIC 与 SSR 表。
- `xtgfe_g4_country_groups.csv`：$G=4$ 的国家分组清单。

## 在线调用

```stata
use "https://raw.githubusercontent.com/lianxhcn/data/main/stata/xtgfe/xtgfe_bm2015.dta", clear
do  "https://raw.githubusercontent.com/lianxhcn/data/main/stata/xtgfe/xtgfe_bm2015.do"
```

直接执行 `.do` 文件时，程序会自行载入在线数据。由于 GFE 的目标函数非凸，程序固定随机种子；不同的 `xtgfe` 版本、算法参数或随机种子仍可能得到略有差异的局部最优解。

完整程序含 BIC 搜索和 100 次单位 bootstrap 等耗时步骤。StataNow/MP 19.5 的 BIC 搜索约需 673 秒；运行前应预留时间。

## 组数设定

本案例不把 `groups(4)` 当作面向初学者的任意简化。Bonhomme and Manresa (2015) 的处理包含两个不同层次：

- 论文用 $G=4$ 展示四类具有清楚经济含义的民主化路径：高民主、低民主、较早转型和较晚转型。
- 论文附录的信息准则在候选集合 $G=1,\ldots,15$ 中选择 $G=10$。作者强调，该准则在相应渐近条件下给出真实组数的上界。

因此，程序先使用 `groups(15) bic refit` 执行数据驱动的组数选择，并以 $G=10$ 复现核心系数；随后另外估计 $G=4$，只用于展示论文讨论的四类典型路径。

## 数据来源

当前文件取自 `xtgfe` 作者提供的公开镜像：

- <https://eruygurakademi.com/datasets/xtgfe/Acemoglu_etal.dta>

该文件是 Acemoglu et al. (2008) 五年期面板样本的 Stata 整理版，亦用于 Bonhomme and Manresa (2015) 的收入与民主应用。原始来源、变量说明及复现关系详见 `xtgfe` 帮助文件和本文参考文献。

## 参考文献

- Bonhomme, S., & Manresa, E. (2015). Grouped patterns of heterogeneity in panel data. *Econometrica*, 83(3), 1147-1184. <https://doi.org/10.3982/ECTA11319>
- Acemoglu, D., Johnson, S., Robinson, J. A., & Yared, P. (2008). Income and democracy. *American Economic Review*, 98(3), 808-842. <https://doi.org/10.1257/aer.98.3.808>
