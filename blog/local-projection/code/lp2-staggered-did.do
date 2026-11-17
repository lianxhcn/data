*! 局部投影法入门(2)：交错处理与 LP-DID —— 复现 do 文件
*! 数据：模拟生成（300 个个体、20 个年份，共 6,000 个观测），真实效应已知，便于检验各方法。

* ========== 1. 生成已知真实参数的模拟数据 ==========
clear all
set seed 2026
set obs 300
gen id = _n

* 首次处理年份 g：1–100 号 2005 年，101–200 号 2010 年，其余从未处理
gen g = cond(id<=100, 2005, cond(id<=200, 2010, .))
expand 20
bysort id: gen year = 1999 + _n
xtset id year

gen treat = (year >= g)
gen rel = year - g
gen te = 0
replace te = (rel+1)*1.0 if treat==1 & g==2005
replace te = (rel+1)*0.5 if treat==1 & g==2010
gen y = id/100 + 0.1*(year-2000) + te + rnormal()

* 核对基准：处理组真实效应均值应为 5.9
sum te if treat==1

* ========== 2. 传统 TWFE 模型（存在禁止比较偏差） ==========
* 先安装：ssc install reghdfe；ssc install ftools
reghdfe y treat, absorb(id year) vce(cluster id)

* ========== 3. 现成命令 lpdid ==========
* 先安装：ssc install lpdid, replace
* 方差加权版本
lpdid y, unit(id) time(year) treat(treat) pre_window(4) post_window(5)
* 等权 ATT 版本
lpdid y, unit(id) time(year) treat(treat) pre_window(4) post_window(5) rw

* ========== 4. 手写 LP-DiD 回归 ==========
gen dD = D.treat

* 政策后各期 h = 0–5
forvalues h = 0/5 {
    gen dy_post`h' = F`h'.y - L.y
    reg dy_post`h' dD i.year if dD==1 | F`h'.treat==0, vce(cluster id)
}

* 政策前各期 k = 2–4，用于检验平行趋势
forvalues k = 2/4 {
    gen dy_pre`k' = L`k'.y - L.y
    reg dy_pre`k' dD i.year if dD==1 | treat==0, vce(cluster id)
}
