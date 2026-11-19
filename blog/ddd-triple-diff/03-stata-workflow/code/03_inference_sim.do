*==============================================================
* 03_inference_sim.do
* 第 3 篇：少簇推断模拟，处理簇很少时聚类标准误的过度拒绝
* 面板：31 省 × 2 组 × 6 期 × 每格 100 人，共 37 200 个观测
* 处理省数：20、10、5、2、1；原假设为真（三重效应 = 0），名义水平 5%
* 对照：Olden & Møen (2022) 表 B1（25 簇约 5.9%，1 簇约 82.4%）
*==============================================================

clear all
set more off

* 首次运行：请把下一行改为本文件夹 (03-Stata全流程) 的完整路径 (用正斜杠)
local root "C:/your-path/03-stata-workflow"

* ------------------------------------------------------------
* 1. 固定面板骨架，处理身份按一次随机排序确定
* ------------------------------------------------------------
set obs 31
gen long province = _n
set seed 17
gen double rank = runiform()
sort rank
gen long prank = _n
sort province
expand 2
bysort province: gen byte group = (_n - 1)
expand 6
bysort province group: gen byte period = _n
expand 100
gen byte post = (period >= 4)

* 初始随机分量
gen double pp = rnormal(0, 0.2)
bysort province period: replace pp = pp[1]
gen double ie = rnormal(0, 0.35)

* 全局暂存
tempname pf
postfile `pf' int ntr rep double b reject ///
    using "`root'/data/sim_cluster.dta", replace

* ------------------------------------------------------------
* 2. 主模拟：聚类到省，200 次重复，逐处理省数统计拒绝率
* ------------------------------------------------------------
foreach ntr in 20 10 5 2 1 {
    gen byte treat = (prank <= `ntr')
    gen byte ttt = treat * group * post
    gen double y = .

    forvalues r = 1/200 {
        quietly replace pp = rnormal(0, 0.2)
        quietly bysort province period: replace pp = pp[1]
        quietly replace ie = rnormal(0, 0.35)
        quietly replace y = 1.0 + 0.3*group + 0.1*(period-1) ///
                          + 0.3*treat*post + pp + ie
        quietly reg y i.province i.group i.period i.province#i.group ///
                i.province#i.period i.group#i.period ttt, vce(cluster province)
        scalar b = _b[ttt]
        scalar tstat = _b[ttt] / _se[ttt]
        post `pf' (`ntr') (`r') (b) (abs(tstat) > 1.96)
    }
    drop treat ttt y
}
postclose `pf'

* ------------------------------------------------------------
* 3. 野生聚类 bootstrap：对处理簇极少的情形，100 次模拟
* ------------------------------------------------------------
tempname pw
postfile `pw' int ntr rep double reject ///
    using "`root'/data/sim_wild.dta", replace
foreach ntr in 10 5 2 1 {
    gen byte treat = (prank <= `ntr')
    gen byte ttt = treat * group * post
    gen double y = .
    forvalues r = 1/100 {
        quietly replace pp = rnormal(0, 0.2)
        quietly bysort province period: replace pp = pp[1]
        quietly replace ie = rnormal(0, 0.35)
        quietly replace y = 1.0 + 0.3*group + 0.1*(period-1) ///
                          + 0.3*treat*post + pp + ie
        quietly reg y i.province i.group i.period i.province#i.group ///
                i.province#i.period i.group#i.period ttt, vce(cluster province)
        quietly boottest ttt, reps(299) cluster(province) nograph
        post `pw' (`ntr') (`r') (r(p) < 0.05)
    }
    drop treat ttt y
}
postclose `pw'

* ------------------------------------------------------------
* 4. 多省面板上的聚合比率 DD：collapse 到省-期，SE 可正常估计
* ------------------------------------------------------------
gen byte treat = (prank <= 10)
gen byte ttt = treat * group * post
gen double y = 1.0 + 0.3*group + 0.1*(period-1) + 0.3*treat*post + pp + ie
display _n(20) "【多省聚合比率 DD】collapse 到省-期，再 reg"
preserve
collapse (mean) y, by(province group period treat)
reshape wide y, i(province period) j(group)
gen double rel = y1 - y0
reg rel i.period i.treat##i.period
restore
drop treat ttt y

* ------------------------------------------------------------
* 5. 汇总拒绝率
* ------------------------------------------------------------
display _n(20) "【聚类稳健检验拒绝率】名义水平 5%，200 次重复"
preserve
use "`root'/data/sim_cluster.dta", clear
collapse (mean) reject (count) n=reject, by(ntr)
rename reject reject_rate
list, noobs
restore

display _n(10) "【野生聚类 bootstrap 拒绝率】100 次重复"
preserve
use "`root'/data/sim_wild.dta", clear
collapse (mean) reject (count) n=reject, by(ntr)
rename reject reject_rate
list, noobs
restore
