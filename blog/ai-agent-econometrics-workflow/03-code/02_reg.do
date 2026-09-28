* 02_reg.do — 面板固定效应回归 + 系数图
* 这段做什么：ln_wage 对时变自变量做个体 FE 回归（聚类稳健标准误），
* 画系数图；末尾用一小段 pooled bootstrap 演示"为何要固定种子"。
* 注：grade 等时不变变量在 FE 下会被组内变换吸收，故不入模型。

use "04-data/_tmp_clean.dta", clear
xtset idcode year

* --- 主模型：个体固定效应，按个体聚类 ---
xtreg ln_wage tenure ttl_exp union age, fe vce(cluster idcode)
estimates store fe_main

coefplot fe_main, drop(_cons) xline(0) ///
    title("Panel FE: returns to tenure, experience, union, age") ///
    xtitle("Coefficient on ln(wage)")
graph export "02-figs/publish/fig1_coef.png", width(1200) replace

* --- 演示：为何要固定种子（与上面主估计无关，仅示范随机性可复现）---
* 换一个种子，下面的 bootstrap 标准误会变；固定后可复现。
set seed 20260903
bootstrap _b[tenure], reps(200): regress ln_wage tenure ttl_exp union age
di as txt ">> 上面 bootstrap 的结果依赖种子 20260903，换种子会变"

erase "04-data/_tmp_clean.dta"                 // 清理临时文件
