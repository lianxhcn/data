version 17.0
clear all
set more off

* Run this file with the project root as the current working directory.
local project_root "`c(pwd)'"

sysuse auto, clear
gen long car_id = _n
isid car_id

preserve
keep if foreign == 0
assert _N == 52
export delimited using ///
    "`project_root'/reference-package/raw/auto_domestic.csv", ///
    replace nolabel
copy "`project_root'/reference-package/raw/auto_domestic.csv" ///
    "`project_root'/broken-package/raw/auto_domestic.csv", replace
restore

keep if foreign == 1
assert _N == 22
export delimited using ///
    "`project_root'/reference-package/raw/auto_foreign.csv", ///
    replace nolabel
copy "`project_root'/reference-package/raw/auto_foreign.csv" ///
    "`project_root'/broken-package/raw/auto_foreign.csv", replace

import delimited ///
    "`project_root'/reference-package/raw/auto_domestic.csv", clear
tempfile domestic
save `domestic'
import delimited ///
    "`project_root'/reference-package/raw/auto_foreign.csv", clear
append using `domestic'
assert _N == 74
isid car_id
assert inlist(foreign, 0, 1)
count if foreign == 0
assert r(N) == 52
count if foreign == 1
assert r(N) == 22
