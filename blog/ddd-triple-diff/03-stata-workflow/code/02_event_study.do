*==============================================================
* 02_event_study.do
* 第 3 篇：多期面板上的事件研究，预趋势与动态效应
* 结构：2 省 × 2 组 × 8 年，每格 800 人，共 25 600 个观测
* 政策在第 4 年后实施：year 1-4 为政策前，5-8 为政策后
* 动态效应：0.08、0.10、0.11、0.10；政策前相对趋势为零
*==============================================================

clear all
set more off
set seed 236

* 首次运行：请把下一行改为本文件夹 (03-Stata全流程) 的完整路径 (用正斜杠)
local root "C:/your-path/03-stata-workflow"

* ------------------------------------------------------------
* 1. 生成数据：3 200 个个体，各追踪 8 年
* ------------------------------------------------------------
clear
set obs 3200
gen byte province = (_n > 1600)
gen byte group    = (mod(_n-1, 1600) >= 800)
gen long id       = _n
expand 8
bysort id: gen year = _n
gen byte post = (year >= 5)

* 各政策后年份的真实动态效应
gen double eff = 0
replace eff = 0.08 if year == 5
replace eff = 0.10 if year == 6
replace eff = 0.11 if year == 7
replace eff = 0.10 if year == 8

gen double y = 1.0 + 0.20*province + 0.30*group + 0.10*(year-1) ///
             + 0.30*province*post + eff*province*group            ///
             + rnormal(0, 0.35)
label var y "结果变量 (标准化单位)"

* ------------------------------------------------------------
* 2. 事件研究：以第 4 年为基准年，三向交互即各年归一化 DDD
* ------------------------------------------------------------
display _n(30) "【事件研究】reg y ib4.year##i.province##i.group"
reg y ib4.year##i.province##i.group, vce(robust)

* 政策前各年系数的联合检验（原假设：三个政策前系数同时为零）
display _n(10) "【预趋势联合检验】政策前 1-3 年系数同时为零"
test 1.year#1.province#1.group 2.year#1.province#1.group ///
     3.year#1.province#1.group

* ------------------------------------------------------------
* 3. 提取各年系数与标准误，导出供绘图
* ------------------------------------------------------------
tempname pf
postfile `pf' int year double b se using "`root'/data/event_ddd.dta", replace
forvalues k = 1/8 {
    if `k' == 4 {
        post `pf' (`k') (0) (.)
    }
    else {
        scalar bk = _b[`k'.year#1.province#1.group]
        scalar sk = _se[`k'.year#1.province#1.group]
        post `pf' (`k') (bk) (sk)
    }
}
postclose `pf'

preserve
use "`root'/data/event_ddd.dta", clear
export delimited using "`root'/data/event_ddd.csv", replace
list, noobs
restore

* 注：若先 collapse 到省-年相对结果再跑 DD，在只有 2 个省的面板上，
* 省份与年份交互会把 16 个观测完全拟合，剩余自由度为零，无法估计 SE。
* 多省面板上该聚合实现可以正常给出 SE，演示见 03_inference_sim.do 第 4 部分。
