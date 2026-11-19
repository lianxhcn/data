*==============================================================
* 01_three_specs.do
* 第 3 篇：在同一份 2x2x2 数据上对照三种 Stata 写法
* 数据：与第 1 篇相同的 ddd_sim.dta (seed 98，10 000 个观测)
* 真值：DDD = 0.10；正确标准误口径约 0.028，朴素两步法报 0.020
*==============================================================

clear all
set more off

* 首次运行：请把下一行改为本文件夹 (03-Stata全流程) 的完整路径 (用正斜杠)
local root "C:/your-path/03-stata-workflow"

use "`root'/data/ddd_sim.dta", clear
describe, short
count

* 四个手工交互变量
gen byte ttt = province * group * post
gen byte pt  = province * post
gen byte gt  = group * post
gen byte pg  = province * group
label var ttt "三重交互 P*G*T"
label var pt  "省份 × 后期 P*T"
label var gt  "组别 × 后期 G*T"
label var pg  "省份 × 组别 P*G"

*==============================================================
* 写法一：手工三重交互
*==============================================================

* (1a) 饱和回归：主项与全部交互项，八个格子各由自己的均值拟合
display _n(40) "【写法一·A】饱和回归 reg y i.province##i.group##i.post"
reg y i.province##i.group##i.post, vce(robust)
scalar b1a = _b[1.province#1.group#1.post]
scalar s1a = _se[1.province#1.group#1.post]

* (1b) reghdfe：吸收省份、组别、时期三组主效应固定效应
display _n(40) "【写法一·B】reghdfe 吸收 province group post 三组主效应"
reghdfe y ttt pt gt pg, absorb(province group post) vce(robust)
scalar b1b = _b[ttt]
scalar s1b = _se[ttt]

* (1c) reghdfe：连双向交互也一并吸收，只留三重交互
display _n(40) "【写法一·C】reghdfe 吸收主效应与全部双向交互"
reghdfe y ttt, absorb(province group post province#group province#post group#post) ///
    vce(robust)
scalar b1c = _b[ttt]
scalar s1c = _se[ttt]

*==============================================================
* 写法二：两个 DD 分别估计，再相减
*==============================================================

* (2a) 分别在 B 组、A 组子样本上跑普通 DD
display _n(40) "【写法二·A】B 组子样本的 DD"
reg y i.province##i.post if group == 1, vce(robust)
scalar ddb = _b[1.province#1.post]
scalar sdb = _se[1.province#1.post]

display _n(20) "【写法二·A】A 组子样本的 DD"
reg y i.province##i.post if group == 0, vce(robust)
scalar dda = _b[1.province#1.post]
scalar sda = _se[1.province#1.post]

scalar ddd2 = ddb - dda
display _n(10) "DD_B = " %7.4f ddb "  DD_A = " %7.4f dda
display "手工相减 DDD = DD_B - DD_A = " %10.8f ddd2
display "两个子样本 SE 平方和开方 = " %7.4f sqrt(sdb^2 + sda^2)

* (2b) 用 suest 联合估计两个模型，再用 nlcom 检验差值，
*      方差口径完整覆盖两个子样本的抽样不确定性
display _n(40) "【写法二·B】suest 联合估计 + nlcom 差值检验"
reg y i.province##i.post if group == 1
estimates store mB
reg y i.province##i.post if group == 0
estimates store mA
suest mB mA, vce(robust)
nlcom (ddd: [mB_mean]1.province#1.post - [mA_mean]1.province#1.post)
scalar b2b = r(b)[1,1]
scalar s2b = sqrt(r(V)[1,1])

*==============================================================
* 写法三：比率型 DD（先构造 B 减 A 的相对结果，再跑普通 DD）
*==============================================================

* (3a) 个体层面实现：把估计出的 A 组均值当作已知量
display _n(40) "【写法三·A】个体层面两步法（生成回归元，SE 偏窄）"
egen double mcell = mean(y), by(province group post)
gen double mA = .
replace mA = mcell if group == 0
bysort province post (mA): replace mA = mA[1]
gen double rel = y - mA
label var rel "B 组相对 A 组的结果"
reg rel i.province##i.post if group == 1, vce(robust)
scalar b3a = _b[1.province#1.post]
scalar s3a = _se[1.province#1.post]
drop mcell mA rel

* (3b) 手动 bootstrap 整个两步法：每次重采样全部 10 000 个观测，
*      把 A 组均值的抽样不确定性计入，SE 回到约 0.028
display _n(40) "【写法三·B】手动 bootstrap 整个两步法（500 次）"
tempname pf
postfile `pf' double ddd using "`root'/data/boot_twostep.dta", replace
set seed 303
quietly forvalues r = 1/500 {
    preserve
    bsample
    egen double mcell = mean(y), by(province group post)
    gen double mA = .
    replace mA = mcell if group == 0
    bysort province post (mA): replace mA = mA[1]
    gen double rel = y - mA
    reg rel i.province##i.post if group == 1
    post `pf' (_b[1.province#1.post])
    restore
}
postclose `pf'
preserve
use "`root'/data/boot_twostep.dta", clear
sum ddd
scalar b3b = r(mean)
scalar s3b = r(sd)
restore

*==============================================================
* 汇总核对
*==============================================================
display _n(40) "【汇总】点估计与标准误口径对照"
display "写法一 A 饱和回归：      b = " %8.6f b1a "  se = " %7.4f s1a
display "写法一 B reghdfe 主效应：b = " %8.6f b1b "  se = " %7.4f s1b
display "写法一 C reghdfe 全吸收：b = " %8.6f b1c "  se = " %7.4f s1c
display "写法二 suest 差值：      b = " %8.6f b2b "  se = " %7.4f s2b
display "写法三 A 朴素两步：      b = " %8.6f b3a "  se = " %7.4f s3a
display "写法三 B bootstrap 两步：b = " %8.6f b3b "  se = " %7.4f s3b

display _n(5) "点估计两两之差（应在机器精度内为 0）："
display "1A vs 1B = " %12.10f (b1a-b1b)
display "1A vs 2B = " %12.10f (b1a-b2b)
display "1A vs 3A = " %12.10f (b1a-b3a)
display "1A vs 3B = " %12.10f (b1a-b3b)
