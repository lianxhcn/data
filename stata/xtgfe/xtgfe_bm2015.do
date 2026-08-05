/*=============================================================================
  xtgfe：Bonhomme and Manresa (2015) 收入与民主案例

  目的：
  1. 估计双向固定效应模型，作为读者熟悉的基准；
  2. 按 BM (2015) 的 BIC 在 G = 1,...,15 中选择潜在组数；
  3. 以 BIC 选择的 G = 10 复现论文核心系数；
  4. 以 G = 4 展示论文正文讨论的四类民主化路径。

  已测环境：StataNow/MP 19.5 + xtgfe 1.5.5 (2026-08-05)。
  搜索设置：保留 xtgfe 1.5.5 的默认 VNS 设置；命令会按 G 自动确定
  randstarts()，并使用 steps(128)。固定随机种子便于复现。
=============================================================================*/

version 17.0
clear all
set more off
set seed 8273647

*-----------------------------------------------------------------------------
* 0. 安装或更新 xtgfe
*-----------------------------------------------------------------------------
capture which xtgfe
if _rc {
    ssc install xtgfe
}

* 查看当前使用的命令文件；正式复现时应在日志中记录版本日期
which xtgfe

*-----------------------------------------------------------------------------
* 1. 在线读取数据并检查面板结构
*-----------------------------------------------------------------------------
global xtgfe_data "https://raw.githubusercontent.com/lianxhcn/data/main/stata/xtgfe"

* 本地测试时优先读取当前目录的数据；发布后也可直接从 GitHub 读取
capture confirm file "xtgfe_bm2015.dta"
if !_rc {
    use "xtgfe_bm2015.dta", clear
}
else {
    use "${xtgfe_data}/xtgfe_bm2015.dta", clear
}

describe
summarize fhpolrigaug lag_dem lag_income

* code 为国家编号，year 为五年期年份；数据应为平衡面板
xtset code year, delta(5)
isid code year
xtdescribe

* 样本应包含 90 个国家、7 个时期和 630 条观测
assert _N == 630
quietly levelsof code, local(country_ids)
local N_country : word count `country_ids'
assert `N_country' == 90
assert inlist(year, 1970, 1975, 1980, 1985, 1990, 1995, 2000)
assert !missing(fhpolrigaug, lag_dem, lag_income)

*-----------------------------------------------------------------------------
* 2. 基准模型：国家固定效应 + 年份固定效应
*-----------------------------------------------------------------------------
* 该模型假定所有国家共享同一组年份冲击，只允许国家截距不同
xtreg fhpolrigaug lag_dem lag_income i.year, ///
    fe vce(cluster code)
estimates store TWFE

*-----------------------------------------------------------------------------
* 3. 规范选择潜在组数：BM (2015) 的 BIC
*-----------------------------------------------------------------------------
* 此时 groups(15) 中的 15 是候选组数上限 Gmax，而非指定估计 15 组
* refit 会在 BIC 选定的组数上重新搜索一次，以降低陷入局部最优的风险
set seed 8273647
xtgfe fhpolrigaug lag_dem lag_income, ///
    groups(15) bic refit generate(gfe_group_bic)

* e(bic) 的三列依次为 G、BIC 和 SSR；带星号的行是最小 BIC
matrix list e(bic)
estimates store GFE_BIC

* BM (2015) 的该样本中，BIC 应选择 G = 10；若不同则给出警告而不中断程序
if e(G) != 10 {
    display as error "Warning: BIC did not select G = 10; increase search depth and inspect local minima."
}

* 长期收入效应：lag_income / (1 - lag_dem)
nlcom _b[lag_income] / (1 - _b[lag_dem])

*-----------------------------------------------------------------------------
* 4. 固定 G = 10：复现论文附录 Table S.XI 的核心估计
*-----------------------------------------------------------------------------
* 默认 sandwich 标准误以估计后的组别为条件，计算速度较快
set seed 8273647
xtgfe fhpolrigaug lag_dem lag_income, ///
    groups(10) generate(gfe_group10) showfreq
estimates store GFE10_sandwich

* 短面板下，可使用考虑分类边界不确定性的 fixed-T 标准误
set seed 8273647
xtgfe fhpolrigaug lag_dem lag_income, ///
    groups(10) vce(fixedt)
estimates store GFE10_fixedT

* 100 次单位 bootstrap；默认 bstarts(32)，在当前机器上耗时较长
set seed 8273647
xtgfe fhpolrigaug lag_dem lag_income, ///
    groups(10) vce(bootstrap) reps(100)
estimates store GFE10_bootstrap

*-----------------------------------------------------------------------------
* 5. 固定 G = 4：展示论文正文的四类典型路径
*-----------------------------------------------------------------------------
* 这里的 G = 4 用于复现论文的路径解释，不替代前面的 BIC 选组程序
set seed 8273647
xtgfe fhpolrigaug lag_dem lag_income, ///
    groups(4) generate(gfe_group4) showfreq showalpha
estimates store GFE4

* 绘制估计的组别-时间固定效应路径
xtgfe plot, ///
    title("Estimated group-specific time effects, G = 4") ///
    xlabel(1970(5)2000) ///
    xtitle("Year") ///
    ytitle("Estimated group-time effect") ///
    name(gfe_alpha4, replace)
graph export "xtgfe_g4_alpha_test.png", replace width(1600)

* 绘制各组结果变量的原始均值路径，更接近 BM (2015) Figure 2 的表达
xtgfe plot, means ///
    title("Mean democracy paths by latent group, G = 4") ///
    xlabel(1970(5)2000) ///
    xtitle("Year") ///
    ytitle("Mean democracy index") ///
    name(gfe_means4, replace)
graph export "xtgfe_g4_means_test.png", replace width(1600)

* 列出各组国家。组别编号可能因标签置换而变化，应根据路径命名组别
preserve
    keep code ccode country gfe_group4
    duplicates drop
    sort gfe_group4 country
    list gfe_group4 country, sepby(gfe_group4) noobs abbreviate(24)
restore

*-----------------------------------------------------------------------------
* 6. 结果核对
*-----------------------------------------------------------------------------
* BM Table S.XI 的 G = 10 参考值：
* lag_dem    约为 0.2772
* lag_income 约为 0.0753
* SSR        约为 7.74906
* 长期收入效应约为 0.1041

display as text "Program completed. Check xtgfe_expected_results.md."
