* 01_check.do — 面板设定与最小检查
* 这段做什么：读本地副本，设定面板结构，检查规模、类型、缺失与主键唯一，
* 剔除建模变量缺失的观测。

use "04-data/nlswork.dta", clear

count                                          // 维度
describe ln_wage tenure ttl_exp union age idcode year   // 类型
isid idcode year                               // 面板主键唯一
xtset idcode year                              // 面板设定
xtdescribe                                     // 面板结构（是否平衡、跨度）
misstable summarize ln_wage tenure ttl_exp union age    // 缺失情况

count
local n0 = r(N)
drop if missing(ln_wage, tenure, ttl_exp, union, age)
count
di as txt "剔除缺失后样本：从 `n0' 减为 " r(N)

save "04-data/_tmp_clean.dta", replace         // 传给下一段，可复现时重建
