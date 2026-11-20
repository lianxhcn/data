# xtpvarcoint 面板 VAR、协整与截面相关：复现材料

本文件夹存放连享会推文《面板 VAR、协整与截面相关：xtpvarcoint 命令详解》的完整复现脚本。推文以 Stata 第三方命令 `xtpvarcoint` 为主线，演示面板单位根、协整秩检验、面板 VAR 估计与稳定性诊断，并对脉冲响应与方差分解的官方缺陷给出修复代码。

## 一、软件环境

- Stata 14 或更高版本（材料在 Stata 19 MP 下验证）。
- 第三方命令 `xtpvarcoint`，验证时为 1.0.1 版本（2026-04-05）。
- 配图脚本需要 Python 3，以及 `numpy`、`matplotlib`。

## 二、数据

使用 Stata 自带的 Grunfeld 投资数据，通过 `webuse grunfeld` 在线载入，无需额外下载。数据为 10 家公司、1935—1954 年共 20 年的强平衡面板，含企业投资 `invest`、企业市值 `mvalue` 与资本存量 `kstock` 三个变量。

## 三、文件清单与复现顺序

| 顺序 | 文件 | 内容 |
|---|---|---|
| 1 | `01-install.do` | 安装并核验 `xtpvarcoint` 版本 |
| 2 | `02-unitroot.do` | 面板单位根检验（官方 `xtunitroot`，LLC 与 IPS） |
| 3 | `03-pcoint.do` | 面板协整秩检验，JO、BR、SL、CAIN 四法 |
| 4 | `04-pvar.do` | 面板 VAR 均值组估计与稳定性诊断 |
| 5 | `05-fix-irf-fevd.do` | 自包含修复脚本，输出正确的简化式 IRF 与 FEVD |
| 6 | `06-pid.do` | 结构识别 `pid` 实测与手动补标量的 workaround |
| 7 | `07-sboot.do` | 自助推断 `sboot` 实测 |
| 8 | `08-plot-break.do` | 特征根出图与结构突变选项实测 |
| 9 | `09-make-figures.py` | 三张正式配图的生成脚本 |

建议按编号顺序运行。Stata 脚本可通过批处理方式执行：

```powershell
StataMP-64.exe /e do <脚本绝对路径>
```

`08-plot-break.do` 默认把图形输出到当前工作目录下的 `figures` 文件夹，`09-make-figures.py` 默认输出到脚本所在目录下的 `figures`，均可在文件顶部修改。

## 四、命令缺陷与本材料的处理

推文中的判断基于 1.0.1 版本的源码检查与实测，主要结论如下：

1. `irf` 与 `fevd` 子命令存在指针别名错误，除第 0 期外动态结果几乎全为零。`05-fix-irf-fevd.do` 让每一期指针指向独立矩阵，按正确递推重新计算，输出 `_fix_IRF` 与 `_fix_FEVD`。
2. `pid` 在 `pvar` 后缺少协方差、在 `vecm` 后缺少个体数标量，需手动补 `_xpvc_N`；其中长期约束 `grt` 输出缺失，距离协方差 `dc` 实际只做 Cholesky。
3. `sboot` 需手动补 `_xpvc_T`，且动态区间受同一指针错误拖累而全为零。
4. `breaks`、`tbreak`、`adddummy` 等结构突变选项在当前版本未实现，仅暴露语法并被静默忽略。

随着命令版本更新，上述问题可能已被作者修复。使用时可先运行本材料验证输出是否合理，再决定是否采用官方结果。
