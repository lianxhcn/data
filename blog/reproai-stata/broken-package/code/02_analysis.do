use "data/auto_combined.dta", clear
drop if price > 10000

regress price mpg weight i.foreign, vce(robust)
estimates save "data/regression_robust.ster", replace

bootstrap _b[mpg], reps(200) ///
    saving("data/bootstrap_mpg.dta", replace): ///
    regress price mpg weight i.foreign
estimates save "data/regression_bootstrap.ster", replace
