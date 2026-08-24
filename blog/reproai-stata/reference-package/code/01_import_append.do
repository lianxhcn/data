version 17.0
import delimited "raw/auto_domestic.csv", clear varnames(1)
tempfile domestic
save `domestic'

import delimited "raw/auto_foreign.csv", clear varnames(1)
append using `domestic'

assert _N == 74
isid car_id
assert inlist(foreign, 0, 1)
count if foreign == 0
assert r(N) == 52
count if foreign == 1
assert r(N) == 22
save "data/auto_combined.dta", replace
