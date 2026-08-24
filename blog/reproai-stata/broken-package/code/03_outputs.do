estimates use "data/regression_robust.ster"
matrix b = e(b)
matrix V = e(V)
local b_mpg : display %12.6f b[1, "mpg"]
local se_mpg : display %12.6f sqrt(V[2, 2])
file open results using "tables/results.csv", write replace
file write results "term,coefficient,robust_se" _n
file write results "mpg,`b_mpg',`se_mpg'" _n
file close results

use "data/auto_combined.dta", clear
twoway (scatter price mpg) (lfit price mpg), name(price_mpg, replace)
graph export "figures/price_mpg.png", replace
