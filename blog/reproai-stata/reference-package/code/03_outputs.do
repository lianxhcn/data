version 17.0
estimates use "data/regression_robust.ster"
local b_mpg : display %12.6f _b[mpg]
local se_mpg : display %12.6f _se[mpg]
local b_weight : display %12.6f _b[weight]
local se_weight : display %12.6f _se[weight]
local b_foreign : display %12.6f _b[1.foreign]
local se_foreign : display %12.6f _se[1.foreign]

file open table1 using "tables/table1_regression.csv", write replace
file write table1 "term,coefficient,robust_se" _n
file write table1 "mpg,`b_mpg',`se_mpg'" _n
file write table1 "weight,`b_weight',`se_weight'" _n
file write table1 "foreign,`b_foreign',`se_foreign'" _n
file close table1

use "data/auto_combined.dta", clear
twoway (scatter price mpg) (lfit price mpg), ///
    title("Price and fuel efficiency") ///
    name(price_mpg, replace)
graph export "figures/price_mpg_scatter.png", replace

file open metadata using "tables/README.txt", write replace
file write metadata "Table 1 is produced by code/03_outputs.do." _n
file close metadata
file open figuremeta using "figures/README.txt", write replace
file write figuremeta "Figure 1 is produced by code/03_outputs.do." _n
file close figuremeta
