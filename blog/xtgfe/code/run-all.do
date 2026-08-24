/*
Reproduce the estimates, inference checks, tables, and figures used in the
xtgfe lecture. Before running, change Stata's working directory to the
xtgfe-blog project root.
*/

version 17.0
clear all
set more off
set linesize 100
capture log close _all

args project_root
if "`project_root'" == "" {
    local root "`c(pwd)'"
}
else {
    local root "`project_root'"
}
local data "`root'/data"
local out "`root'/output"
local logs "`root'/logs"

confirm file "`root'/README.md"
confirm file "`root'/code/build-figures.do"
confirm file "`data'/xtgfe-bm2015.dta"
confirm file "`data'/dynamic-bic-cached.csv"
confirm file "`data'/static-bic-cached.csv"
confirm file "`data'/g4-country-groups.csv"

capture mkdir "`out'"
capture mkdir "`logs'"

log using "`logs'/run-all.log", text replace
timer clear 1
timer on 1

display as text "Full replication started: " c(current_date) ///
    " " c(current_time)
about

capture which xtgfe
if _rc {
    display as error "xtgfe is required. Run: ssc install xtgfe"
    exit 499
}
which xtgfe

capture which reghdfe
if _rc {
    display as error "reghdfe is required. Run: ssc install reghdfe"
    exit 499
}
which reghdfe

*=======================================================================
* Data checks
*=======================================================================

use "`data'/xtgfe-bm2015.dta", clear
xtset code year, delta(5)
isid code year
assert _N == 630
quietly levelsof code, local(country_ids)
local n_countries : word count `country_ids'
assert `n_countries' == 90
assert inlist(year, 1970, 1975, 1980, 1985, ///
    1990, 1995, 2000)
assert !missing(fhpolrigaug, lag_dem, lag_income)

tempfile model_results
tempname results_handle
postfile `results_handle' str32 model ///
    double b_lag_dem se_lag_dem b_lag_income ///
    se_lag_income long_run using `model_results', replace

*=======================================================================
* Static model: BIC, G=10, and three inference methods
*=======================================================================

set seed 8273647
xtgfe fhpolrigaug lag_income, ///
    groups(15) bic refit
assert e(G) == 10

matrix static_bic = e(bic)
matrix colnames static_bic = groups bic ssr
preserve
    clear
    svmat double static_bic, names(col)
    export delimited using "`out'/static-bic-full.csv", ///
        replace
    quietly summarize bic, meanonly
    count if groups == 10 & abs(bic-r(min)) < 1e-12
    assert r(N) == 1
restore

set seed 8273647
xtgfe fhpolrigaug lag_income, groups(10)
scalar b_income = _b[lag_income]
scalar se_income = _se[lag_income]
post `results_handle' ("static_g10_sandwich") ///
    (.) (.) (b_income) (se_income) (.)

set seed 8273647
xtgfe fhpolrigaug lag_income, ///
    groups(10) vce(fixedt)
scalar b_income = _b[lag_income]
scalar se_income = _se[lag_income]
post `results_handle' ("static_g10_fixedt") ///
    (.) (.) (b_income) (se_income) (.)

set seed 8273647
xtgfe fhpolrigaug lag_income, ///
    groups(10) vce(bootstrap) reps(500)
scalar b_income = _b[lag_income]
scalar se_income = _se[lag_income]
post `results_handle' ("static_g10_bootstrap_500") ///
    (.) (.) (b_income) (se_income) (.)

*=======================================================================
* Dynamic model: independent BIC selection and core estimates
*=======================================================================

use "`data'/xtgfe-bm2015.dta", clear
xtset code year, delta(5)
set seed 8273647
xtgfe fhpolrigaug lag_dem lag_income, ///
    groups(15) bic refit
assert e(G) == 10

matrix dynamic_bic = e(bic)
matrix colnames dynamic_bic = groups bic ssr
preserve
    clear
    svmat double dynamic_bic, names(col)
    export delimited using "`out'/dynamic-bic-full.csv", ///
        replace
    quietly summarize bic, meanonly
    count if groups == 10 & abs(bic-r(min)) < 1e-12
    assert r(N) == 1
restore

use "`data'/xtgfe-bm2015.dta", clear
xtset code year, delta(5)
xtreg fhpolrigaug lag_dem lag_income i.year, ///
    fe vce(cluster code)
scalar b_dem = _b[lag_dem]
scalar se_dem = _se[lag_dem]
scalar b_income = _b[lag_income]
scalar se_income = _se[lag_income]
post `results_handle' ("dynamic_twfe") ///
    (b_dem) (se_dem) (b_income) (se_income) (.)

set seed 8273647
xtgfe fhpolrigaug lag_dem lag_income, ///
    groups(10) generate(g10) showfreq
scalar b_dem = _b[lag_dem]
scalar se_dem = _se[lag_dem]
scalar b_income = _b[lag_income]
scalar se_income = _se[lag_income]
scalar long_run = b_income/(1-b_dem)
assert abs(b_dem-0.2772) < 0.001
assert abs(b_income-0.0753) < 0.001
post `results_handle' ("dynamic_g10_sandwich") ///
    (b_dem) (se_dem) (b_income) (se_income) (long_run)

reghdfe fhpolrigaug lag_dem lag_income, ///
    absorb(i.code i.g10#i.year) ///
    vce(cluster code)
scalar b_dem = _b[lag_dem]
scalar se_dem = _se[lag_dem]
scalar b_income = _b[lag_income]
scalar se_income = _se[lag_income]
scalar long_run = b_income/(1-b_dem)
post `results_handle' ("dynamic_bridge_reghdfe") ///
    (b_dem) (se_dem) (b_income) (se_income) (long_run)

use "`data'/xtgfe-bm2015.dta", clear
xtset code year, delta(5)
set seed 8273647
xtgfe fhpolrigaug lag_dem lag_income, ///
    groups(10) vce(fixedt)
scalar b_dem = _b[lag_dem]
scalar se_dem = _se[lag_dem]
scalar b_income = _b[lag_income]
scalar se_income = _se[lag_income]
scalar long_run = b_income/(1-b_dem)
post `results_handle' ("dynamic_g10_fixedt") ///
    (b_dem) (se_dem) (b_income) (se_income) (long_run)

set seed 8273647
xtgfe fhpolrigaug lag_dem lag_income, ///
    groups(10) vce(bootstrap) reps(500)
scalar b_dem = _b[lag_dem]
scalar se_dem = _se[lag_dem]
scalar b_income = _b[lag_income]
scalar se_income = _se[lag_income]
scalar long_run = b_income/(1-b_dem)
post `results_handle' ("dynamic_g10_bootstrap_500") ///
    (b_dem) (se_dem) (b_income) (se_income) (long_run)

set seed 8273647
xtgfe fhpolrigaug lag_dem lag_income, ///
    groups(10) vce(bootstrap) reps(999)
scalar b_dem = _b[lag_dem]
scalar se_dem = _se[lag_dem]
scalar b_income = _b[lag_income]
scalar se_income = _se[lag_income]
scalar long_run = b_income/(1-b_dem)
post `results_handle' ("dynamic_g10_bootstrap_999") ///
    (b_dem) (se_dem) (b_income) (se_income) (long_run)

set seed 20260806
xtgfe fhpolrigaug lag_dem lag_income, ///
    groups(10) vce(bootstrap) reps(999)
scalar b_dem = _b[lag_dem]
scalar se_dem = _se[lag_dem]
scalar b_income = _b[lag_income]
scalar se_income = _se[lag_income]
scalar long_run = b_income/(1-b_dem)
post `results_handle' ("dynamic_g10_bootstrap_999_alt") ///
    (b_dem) (se_dem) (b_income) (se_income) (long_run)

postclose `results_handle'
use `model_results', clear
export delimited using "`out'/model-results-full.csv", ///
    replace

timer off 1
timer list 1
display as text "Full estimation completed: " c(current_date) ///
    " " c(current_time)
log close

* Build the five article figures and their underlying CSV files.
do "`root'/code/build-figures.do" "`root'"

display as text "All replication tasks completed."
