version 17.0
use "data/auto_combined.dta", clear

regress price mpg weight i.foreign, vce(robust)
estimates save "data/regression_robust.ster", replace

bootstrap _b[mpg], reps(200) seed(20260822) ///
    saving("data/bootstrap_mpg.dta", replace): ///
    regress price mpg weight i.foreign
estimates save "data/regression_bootstrap.ster", replace
