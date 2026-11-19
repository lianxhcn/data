*==============================================================
* 01_dgp.do
* 第 1 篇教学数据：2 省 × 2 组 × 2 期，每格 1 250，共 10 000 个观测
* 真值：试点省 B 组政策后 +0.10；试点省相对非试点省每期多增长 0.30
* 运行：stata /e do 01_dgp.do
*==============================================================

clear all
set more off
set seed 98

* 首次运行：请把下一行改为本文件夹 (01-三种用法) 的完整路径 (用正斜杠)
local root "C:/your-path/01-三种用法"

* ------------------------------------------------------------
* 1. 生成八个格子
*    cell 1-4：非试点省；cell 5-8：试点省
*    group：B 组 (受政策影响) 为 1；post：政策后为 1
* ------------------------------------------------------------

clear
set obs 8
gen byte province = (_n >= 5)
gen byte group    = inlist(_n, 3, 4, 7, 8)
gen byte post     = inlist(_n, 2, 4, 6, 8)

* 每格 1 250 个观测，合计 10 000
expand 1250
gen long id = _n

* ------------------------------------------------------------
* 2. 结果变量
*    基线 1.0；省份差异 0.20；组别差异 0.30；时期效应 0.50
*    共同冲击：试点省 × 后期 = 0.30 (对 A、B 两组相同)
*    政策效应：试点省 × B 组 × 后期 = 0.10
*    个体噪声：标准差 0.35 (结果变量为标准化指数，为让 0.10 的效应
*    在图上清楚可见而设，本文会说明这一设定只影响精度、不影响偏误)
* ------------------------------------------------------------

gen double y = 1.0                          ///
             + 0.20 * province             ///
             + 0.30 * group                ///
             + 0.50 * post                 ///
             + 0.30 * province * post      ///
             + 0.10 * province * group * post ///
             + rnormal(0, 0.35)

label define prov 0 "非试点省" 1 "试点省"
label define grp  0 "A 组 (不受政策影响)" 1 "B 组 (受政策影响)"
label values province prov
label values group grp

label var y        "结果变量 (标准化单位)"
label var province "省份"
label var group    "组别"
label var post     "政策实施后"

order id province group post y
sort province group post id

* ------------------------------------------------------------
* 3. 保存
* ------------------------------------------------------------

capture mkdir "`root'/data"
save "`root'/data/ddd_sim.dta", replace

* ------------------------------------------------------------
* 4. 核对：八格均值与三个估计量
* ------------------------------------------------------------

table province group post, statistic(mean y) statistic(freq)

sum y if province==1 & group==1 & post==1, meanonly
scalar m111 = r(mean)
sum y if province==1 & group==1 & post==0, meanonly
scalar m110 = r(mean)
sum y if province==0 & group==1 & post==1, meanonly
scalar m011 = r(mean)
sum y if province==0 & group==1 & post==0, meanonly
scalar m010 = r(mean)
sum y if province==1 & group==0 & post==1, meanonly
scalar m101 = r(mean)
sum y if province==1 & group==0 & post==0, meanonly
scalar m100 = r(mean)
sum y if province==0 & group==0 & post==1, meanonly
scalar m001 = r(mean)
sum y if province==0 & group==0 & post==0, meanonly
scalar m000 = r(mean)

scalar dd_b = (m111 - m110) - (m011 - m010)
scalar dd_a = (m101 - m100) - (m001 - m000)
scalar ddd  = dd_b - dd_a

display "DD_B (B 组的双重差分) = " %6.3f dd_b
display "DD_A (A 组的双重差分) = " %6.3f dd_a
display "DDD = DD_B - DD_A      = " %6.3f ddd
