*==============================================================
* 02_composition.do
* 第 2 篇第二类失效：分组维度被政策污染（构成效应）
* 结构：2 省 × 2 组 × 2 期，共 6 000 个个体、12 000 个观测
* 政策不影响任何个体的结果，但试点省 B 组在政策后纳入 600 名
* 低类型个体，分组构成发生变化
* 对照：朴素 DDD 与基线分组 DDD
*==============================================================

clear all
set more off
set seed 313

* 首次运行：请把下一行改为本文件夹 (02-diagnostics) 的完整路径 (用正斜杠)
local root "C:/your-path/02-diagnostics"

* ------------------------------------------------------------
* 1. 生成个体：每省 3 000 人，低类型、高类型各 1 500 人
*    id 1-3000 为非试点省，3001-6000 为试点省
*    每省内前 1 500 人为低类型，后 1 500 人为高类型
* ------------------------------------------------------------
clear
set obs 6000
gen byte province = (_n > 3000)
gen long id       = _n
gen byte htype    = (mod(_n-1, 3000) >= 1500)

* 政策前的分组规则：B 组即高类型个体
gen byte group_pre = htype

expand 2
bysort id: gen byte post = (_n - 1)

* ------------------------------------------------------------
* 2. 实际观测到的分组
*    非试点省：分组保持不变
*    试点省政策后：id 3001-3600 的 600 名低类型个体被划入 B 组
* ------------------------------------------------------------
gen byte group = group_pre
replace group = 1 if province==1 & post==1 & inrange(id, 3001, 3600)

* ------------------------------------------------------------
* 3. 结果变量：只取决于个体类型与共同时期效应，无任何政策效应
* ------------------------------------------------------------
gen double y = 1.0 + 0.50*htype + 0.50*post + rnormal(0, 0.35)

* ------------------------------------------------------------
* 4. 各组样本规模：观察试点省 B 组构成变化
* ------------------------------------------------------------
display _newline "===== 各组样本规模 ====="
table province post group

* ------------------------------------------------------------
* 5. 朴素 DDD：按实际观测分组计算八格均值
* ------------------------------------------------------------
display _newline "===== 朴素 DDD：使用被污染的分组 ====="
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

scalar dd_b_naive = (m111-m110) - (m011-m010)
scalar dd_a_naive = (m101-m100) - (m001-m000)
scalar ddd_naive  = dd_b_naive - dd_a_naive
display "DD_B = " %8.4f dd_b_naive "  DD_A = " %8.4f dd_a_naive ///
        "  DDD = " %8.4f ddd_naive

* 回归形式确认
reg y i.province##i.group##i.post, vce(robust) noheader
scalar ddd_naive_reg = _b[1.province#1.group#1.post]
scalar se_naive      = _se[1.province#1.group#1.post]

* ------------------------------------------------------------
* 6. 基线分组 DDD：每个个体固定使用政策前分组
* ------------------------------------------------------------
display _newline "===== 基线分组 DDD：使用政策前固定分组 ====="
reg y i.province##i.group_pre##i.post, vce(robust) noheader
scalar ddd_base_reg = _b[1.province#1.group_pre#1.post]
scalar se_base      = _se[1.province#1.group_pre#1.post]

display _newline "===== 两种 DDD 估计对照（真值为 0）====="
display "朴素 DDD   = " %8.4f ddd_naive_reg "  标准误 = " %7.4f se_naive
display "基线分组 DDD = " %8.4f ddd_base_reg "  标准误 = " %7.4f se_base

* ------------------------------------------------------------
* 7. 导出结果供绘图
* ------------------------------------------------------------
clear
set obs 2
gen str12 method = cond(_n==1, "朴素 DDD", "基线分组 DDD")
gen double ddd  = cond(_n==1, ddd_naive_reg, ddd_base_reg)
gen double se   = cond(_n==1, se_naive, se_base)
export delimited using "`root'/data/composition_results.csv", replace
list, noobs
