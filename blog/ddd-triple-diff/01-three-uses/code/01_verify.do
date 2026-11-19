*==============================================================
* 01_verify.do
* 核验三件事：
*   (1) 八格均值与回归系数一致
*   (2) DDD = DD_B - DD_A
*   (3) 两步法与三重交互给出同一个数
* 运行：stata /e do 01_verify.do
*==============================================================

clear all
set more off

* 首次运行：请把下一行改为本文件夹 (01-三种用法) 的完整路径 (用正斜杠)
local root "C:/your-path/01-三种用法"
use "`root'/data/ddd_sim.dta", clear

describe, short
count

*--------------------------------------------------------------
* 1. 八格均值
*--------------------------------------------------------------
display _n(60) "【一】八格均值"
table province group post, statistic(mean y) statistic(freq)

* 由八格均值直接算出两个 DD 与 DDD
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
display "均值法：DD_B = " %6.4f dd_b "  DD_A = " %6.4f dd_a "  DDD = " %6.4f ddd

*--------------------------------------------------------------
* 2. 三重交互回归（含省份、组别、时期固定效应）
*--------------------------------------------------------------
display _n(60) "【二】回归：i.province##i.group##i.post"
reg y i.province##i.group##i.post, robust

display _n(20) "三重交互项的系数与标准误："
display "b(ttt)  = " %6.4f _b[1.province#1.group#1.post]
display "se(ttt) = " %6.4f _se[1.province#1.group#1.post]

*--------------------------------------------------------------
* 3. 三个手工变量
*--------------------------------------------------------------
gen byte ttt = province * group * post
gen byte pt  = province * post
gen byte gt  = group * post
gen byte pg  = province * group

label var ttt "三重交互"
label var pt  "省份 × 后期"
label var gt  "组别 × 后期"
label var pg  "省份 × 组别"

display _n(60) "【三】手工构造变量：y = ttt + pt + gt + pg + 固定效应"
reg y ttt pt gt pg i.province i.group i.post, robust

scalar b_ttt = _b[ttt]
scalar se_ttt = _se[ttt]

* 两个 DD 与 DDD
display _n(20) "DD_B = pt + ttt = " %6.4f (_b[pt] + _b[ttt])
display "DD_A = pt       = " %6.4f _b[pt]
display "DDD  = ttt      = " %6.4f _b[ttt]

*--------------------------------------------------------------
* 4. 两步法：先构造 B 组减 A 组的相对结果，再跑普通 DD
*--------------------------------------------------------------
display _n(60) "【四】两步法"
* 每个省—期内部，用 B 组减去同期 A 组的均值，得到相对结果 rel，
* 再对 rel 跑一次普通 DD；系数应与三重交互项完全相等
egen double mcell = mean(y), by(province group post)
gen double mA = .
replace mA = mcell if group == 0
bysort province post (mA): replace mA = mA[1]
gen double rel = y - mA
label var rel "B 组相对 A 组的结果"
reg rel i.province##i.post if group == 1, robust
display "两步法的系数 = " %6.4f _b[1.province#1.post]
scalar b_two = _b[1.province#1.post]
drop mcell mA rel

*--------------------------------------------------------------
* 5. 结论核对
*--------------------------------------------------------------
display _n(60) "【五】核对"
display "回归 ttt      = " %6.4f b_ttt
display "均值法 DDD    = " %6.4f ddd
display "两者之差      = " %10.8f (b_ttt - ddd)
display "ttt 的标准误  = " %6.4f se_ttt
display "两步法        = " %6.4f b_two
