version 17.0
clear all
set more off
set linesize 100
capture log close _all

* Run after cd to the project root, or pass the root as argument 1.
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
local figs "`root'/output"

capture mkdir "`out'"
capture mkdir "`logs'"

confirm file "`root'/README.md"
confirm file "`data'/xtgfe-bm2015.dta"
confirm file "`data'/dynamic-bic-cached.csv"
confirm file "`data'/g4-country-groups.csv"

log using "`logs'/build-figures.log", ///
    text replace

display as text "Figure build started: " c(current_date) ///
    " " c(current_time)
timer clear 1
timer on 1

about
which xtgfe
which reghdfe
graph set window fontface "Microsoft YaHei"
set seed 8273647

*=======================================================================
* Figure 1: a three-period deterministic example
*=======================================================================

clear
set obs 18
generate byte firm = ceil(_n / 3)
bysort firm: generate byte period = _n
generate byte exposure = cond(firm <= 3, 1, 2)
label define exposure 1 "低暴露组" 2 "高暴露组"
label values exposure exposure

generate double investment = .
replace investment = 6 if period == 1
replace investment = 5.5 if exposure == 1 & period == 2
replace investment = 5 if exposure == 1 & period == 3
replace investment = 4.5 if exposure == 2 & period == 2
replace investment = 3 if exposure == 2 & period == 3

assert _N == 18
assert investment == 6 if period == 1
assert investment == 5.5 if exposure == 1 & period == 2
assert investment == 5 if exposure == 1 & period == 3
assert investment == 4.5 if exposure == 2 & period == 2
assert investment == 3 if exposure == 2 & period == 3

collapse (mean) value=investment, by(exposure period)
preserve
    collapse (mean) value, by(period)
    generate byte series_order = 3
    generate str20 series_key = "common_year_mean"
    tempfile common_mean
    save `common_mean'
restore

rename exposure series_order
generate str20 series_key = cond(series_order == 1, ///
    "low_exposure", "high_exposure")
append using `common_mean'
sort series_order period

assert value == 6 if series_order == 3 & period == 1
assert value == 5 if series_order == 3 & period == 2
assert value == 4 if series_order == 3 & period == 3

export delimited using "`out'/fig01-toy-data.csv", ///
    replace

twoway ///
    (line value period if series_order == 1, ///
        lcolor("0 114 178") lwidth(medthick)) ///
    (line value period if series_order == 2, ///
        lcolor("213 94 0") lwidth(medthick)) ///
    (line value period if series_order == 3, ///
        lcolor(black) lpattern(dash) lwidth(medthick)), ///
    title("同一次紧缩，两类公司的变化并不相同") ///
    xtitle("时期") ///
    ytitle("投资增速 (%)") ///
    xlabel(1(1)3) ///
    ylabel(3(0.5)6, angle(horizontal)) ///
    legend(order(1 "低暴露组" 2 "高暴露组" ///
        3 "共同年度均值") rows(1) position(6)) ///
    graphregion(color(white)) ///
    plotregion(color(white)) ///
    name(fig01, replace)

graph export "`figs'/xtgfe-fig01-twfe-groups.png", ///
    width(1200) replace

*=======================================================================
* Figure 2: the bias ladder from the 300-firm simulation
*=======================================================================

capture program drop make_teaching_data
program define make_teaching_data
    args blocks seed
    clear
    set obs `=6 * `blocks''
    generate long firm = _n
    generate byte pos = mod(firm - 1, 6) + 1
    generate byte grp = cond(pos <= 3, 1, 2)
    generate double mu = cond(inlist(pos, 1, 2), 2, ///
        cond(pos == 3, -1, ///
        cond(inlist(pos, 4, 5), -2, 1)))
    expand 5
    bysort firm: generate byte year = _n
    generate double alpha = cond(grp == 1, ///
        year - 3, -(year - 3))
    set seed `seed'
    generate double x = mu + alpha + rnormal(0, 1)
    generate double y = x + mu + alpha + rnormal(0, 0.3)
    xtset firm year
end

make_teaching_data 50 20260809
assert _N == 1500

quietly regress y x
scalar b1 = _b[x]

quietly xtreg y x, fe
scalar b2 = _b[x]

quietly reghdfe y x, absorb(firm year)
scalar b3 = _b[x]

quietly reghdfe y x, absorb(grp#year)
scalar b4 = _b[x]

quietly reghdfe y x, absorb(firm grp#year)
scalar b5 = _b[x]

set seed 8273647
quietly xtgfe y x, groups(2) generate(gfe_baseline)
scalar b6 = _b[x]

foreach var in y x {
    bysort firm: egen double mean_`var' = mean(`var')
    generate double within_`var' = `var' - mean_`var'
}

set seed 8273647
quietly xtgfe within_y within_x, ///
    groups(2) generate(gfe_within)
scalar b7 = _b[within_x]

set seed 8273647
quietly xtgfe y x, groups(2) subgroups(2 2) ///
    generate(gfe_subgroups)
scalar b8 = _b[x]

* Save group sizes and best-label misclassification diagnostics.
egen byte firm_tag = tag(firm)
tempname diagnostics
tempfile group_diagnostics
postfile `diagnostics' str24 model_key ///
    int n_group1 n_group2 misclassified ///
    double misclassification_rate using `group_diagnostics'

foreach model in baseline within subgroups {
    quietly count if firm_tag & gfe_`model' == 1
    scalar n_group1 = r(N)
    quietly count if firm_tag & gfe_`model' == 2
    scalar n_group2 = r(N)
    quietly count if firm_tag & gfe_`model' != grp
    scalar mis_direct = r(N)
    quietly count if firm_tag & (3-gfe_`model') != grp
    scalar mis_swapped = r(N)
    scalar misclassified = min(mis_direct, mis_swapped)
    scalar mis_rate = misclassified/300
    post `diagnostics' ("`model'") ///
        (n_group1) (n_group2) (misclassified) (mis_rate)
}
postclose `diagnostics'

preserve
    use `group_diagnostics', clear
    quietly summarize n_group1 if model_key == "baseline", ///
        meanonly
    scalar baseline_n1 = r(mean)
    quietly summarize n_group2 if model_key == "baseline", ///
        meanonly
    scalar baseline_n2 = r(mean)
    assert min(baseline_n1, baseline_n2) == 145
    assert max(baseline_n1, baseline_n2) == 155
    assert misclassified == 49 if model_key == "baseline"
    assert n_group1 == 150 & n_group2 == 150 ///
        if inlist(model_key, "within", "subgroups")
    assert misclassified == 0 ///
        if inlist(model_key, "within", "subgroups")
    export delimited using ///
        "`out'/teaching-group-diagnostics.csv", replace
restore

tempname results
tempfile bias_data
postfile `results' byte model_id str32 model_key ///
    str80 model_label double beta_hat using `bias_data'
post `results' (1) ("pooled_ols") ("混合 OLS") (b1)
post `results' (2) ("individual_fe") ("个体 FE") (b2)
post `results' (3) ("twfe") ("TWFE") (b3)
post `results' (4) ("known_group_year_fe") ///
    ("已知组别 × 年份 FE") (b4)
post `results' (5) ("individual_plus_group_year_fe") ///
    ("个体 FE + 已知组别 × 年份 FE") (b5)
post `results' (6) ("baseline_gfe") ("基准 GFE") (b6)
post `results' (7) ("within_additive_gfe") ///
    ("个体内去均值后的加性 GFE") (b7)
post `results' (8) ("gfe_subgroups_2_2") ///
    ("GFE + subgroups(2 2)") (b8)
postclose `results'

use `bias_data', clear
generate byte plot_order = 9 - model_id
generate byte near_true = abs(beta_hat - 1) <= 0.10
generate str12 beta_label = string(beta_hat, "%6.3f")
sort model_id

export delimited using "`out'/fig02-bias-ladder-data.csv", ///
    replace

summarize beta_hat, meanonly
local xmin = floor(r(min) * 10) / 10 - 0.1
local xmax = ceil(r(max) * 10) / 10 + 0.3

twoway ///
    (scatter plot_order beta_hat if near_true == 0, ///
        mcolor("213 94 0") msymbol(circle) msize(medium) ///
        mlabel(beta_label) mlabcolor("213 94 0") ///
        mlabposition(3)) ///
    (scatter plot_order beta_hat if near_true == 1, ///
        mcolor("0 114 178") msymbol(circle) msize(medium) ///
        mlabel(beta_label) mlabcolor("0 114 178") ///
        mlabposition(3)), ///
    title("不同未观测效应设定下的 β̂") ///
    xtitle("估计系数 β̂") ///
    ytitle("") ///
    xline(1, lcolor(black) lpattern(dash)) ///
    xscale(range(`xmin' `xmax')) ///
    ylabel(8 "混合 OLS" 7 "个体 FE" 6 "TWFE" ///
        5 "已知组别 × 年份 FE" ///
        4 "个体 FE + 已知组别 × 年份 FE" ///
        3 "基准 GFE" ///
        2 "个体内去均值后的加性 GFE" ///
        1 "GFE + subgroups(2 2)", angle(horizontal)) ///
    legend(order(1 "仍有明显偏差" 2 "接近真值") ///
        rows(1) position(6)) ///
    graphregion(color(white)) ///
    plotregion(color(white)) ///
    name(fig02, replace)

graph export "`figs'/xtgfe-fig02-bias-ladder.png", ///
    width(1200) replace

*=======================================================================
* Figure 3: published BIC values, without rerunning the search
*=======================================================================

import delimited using "`data'/dynamic-bic-cached.csv", ///
    varnames(1) clear
sort groups
assert groups == _n
assert _N == 15
summarize bic, meanonly
assert groups == 10 if bic == r(min)

generate byte is_g10 = groups == 10
generate byte is_g4 = groups == 4
export delimited using "`out'/fig03-bic-data.csv", ///
    replace

twoway ///
    (line bic groups, lcolor("0 114 178") lwidth(medthick)) ///
    (scatter bic groups if is_g10, ///
        mcolor("213 94 0") msymbol(diamond) msize(large) ///
        mlabel(groups) mlabprefix("G=") mlabposition(12)) ///
    (scatter bic groups if is_g4, ///
        mcolor("0 158 115") msymbol(triangle) msize(large)), ///
    title("BIC 选择 G=10，论文正文另用 G=4 展示典型类型") ///
    xtitle("候选组数 G") ///
    ytitle("BIC") ///
    xlabel(1(1)15) ///
    text(0.0432 5.8 ///
        "G=4：论文正文用于展示四类典型变化" ///
        "不是 BIC 最优组数", ///
        color("0 110 80") size(small) justification(left)) ///
    legend(off) ///
    graphregion(color(white)) ///
    plotregion(color(white)) ///
    name(fig03, replace)

graph export "`figs'/xtgfe-fig03-bic-groups.png", ///
    width(1200) replace

*=======================================================================
* Figures 4 and 5: G=4 effects and raw means in the BM application
*=======================================================================

import delimited using "`data'/g4-country-groups.csv", ///
    varnames(1) encoding(UTF-8) clear
keep code gfe_group4
isid code
tempfile reference_groups
save `reference_groups'

use "`data'/xtgfe-bm2015.dta", clear
xtset code year, delta(5)
set seed 8273647

xtgfe fhpolrigaug lag_dem lag_income, ///
    groups(4) generate(g4) showfreq showalpha

matrix alpha_returned = e(alpha)
matrix time_values = e(tvals)
scalar theta_dem = _b[lag_dem]
scalar theta_income = _b[lag_income]

xtgfe fx
assert !missing(gfe_fx)

generate double alpha_e = .
forvalues group = 1/4 {
    forvalues row = 1/7 {
        local time_value = el(time_values, `row', 1)
        replace alpha_e = el(alpha_returned, `row', `group') ///
            if g4 == `group' & year == `time_value'
    }
}

generate double alpha_fx_e_diff = abs(gfe_fx - alpha_e)
summarize alpha_fx_e_diff, meanonly
scalar max_fx_ealpha_diff = r(max)
assert max_fx_ealpha_diff < 1e-12

merge m:1 code using `reference_groups', assert(match) nogen

* The published grouping supplies stable economic labels even if the
* numerical group labels are permuted in a future xtgfe implementation.
bysort g4: egen byte reference_min = min(gfe_group4)
bysort g4: egen byte reference_max = max(gfe_group4)
assert reference_min == reference_max
bysort gfe_group4: egen byte current_min = min(g4)
bysort gfe_group4: egen byte current_max = max(g4)
assert current_min == current_max
generate byte econ_group = gfe_group4
drop reference_min reference_max current_min current_max

egen byte country_tag = tag(code)
count if country_tag & econ_group == 1
assert r(N) == 33
count if country_tag & econ_group == 2
assert r(N) == 13
count if country_tag & econ_group == 3
assert r(N) == 26
count if country_tag & econ_group == 4
assert r(N) == 18

generate double xb_hat = ///
    theta_dem * lag_dem + theta_income * lag_income
generate double alpha_manual_obs = fhpolrigaug - xb_hat
generate double residual_hat = ///
    fhpolrigaug - xb_hat - gfe_fx

collapse ///
    (mean) alpha_hat=gfe_fx alpha_e=alpha_e ///
        alpha_manual=alpha_manual_obs ///
        dem_mean=fhpolrigaug xb_mean=xb_hat ///
        residual_mean=residual_hat ///
    (count) n_countries=code, ///
    by(g4 econ_group year)

generate str20 group_key = ""
replace group_key = "high_democracy" if econ_group == 1
replace group_key = "early_transition" if econ_group == 2
replace group_key = "low_democracy" if econ_group == 3
replace group_key = "late_transition" if econ_group == 4

generate str30 econ_label = ""
replace econ_label = "高民主组" if econ_group == 1
replace econ_label = "较早转型组" if econ_group == 2
replace econ_label = "低民主组" if econ_group == 3
replace econ_label = "较晚转型组" if econ_group == 4

generate double identity_gap = ///
    dem_mean - (xb_mean + alpha_hat)
generate double alpha_manual_gap = alpha_manual - alpha_hat

generate double abs_identity_gap = abs(identity_gap)
summarize abs_identity_gap, meanonly
scalar max_identity_gap = r(max)
assert max_identity_gap < 1e-10

generate double abs_manual_gap = abs(alpha_manual_gap)
summarize abs_manual_gap, meanonly
scalar max_manual_alpha_diff = r(max)
assert max_manual_alpha_diff < 1e-10

generate double abs_residual_mean = abs(residual_mean)
summarize abs_residual_mean, meanonly
scalar max_group_time_residual = r(max)
assert max_group_time_residual < 1e-10

* Confirm the economic interpretation from the time paths.
quietly summarize dem_mean if econ_group == 1 & year == 1970
scalar high_1970 = r(mean)
quietly summarize dem_mean if econ_group == 3 & year == 1970
scalar low_1970 = r(mean)
assert high_1970 > low_1970

quietly summarize dem_mean if econ_group == 2 & year == 1985
scalar early_1985 = r(mean)
quietly summarize dem_mean if econ_group == 4 & year == 1985
scalar late_1985 = r(mean)
assert early_1985 > late_1985

quietly summarize dem_mean if econ_group == 4 & year == 2000
scalar late_2000 = r(mean)
assert late_2000 > late_1985

display as text "max |xtgfe fx - e(alpha)| = " ///
    as result %12.4e max_fx_ealpha_diff
display as text "max |manual alpha - xtgfe fx| = " ///
    as result %12.4e max_manual_alpha_diff
display as text "max |group-time residual mean| = " ///
    as result %12.4e max_group_time_residual
display as text "max |ybar - xbbar - alpha| = " ///
    as result %12.4e max_identity_gap

sort econ_group year
export delimited using ///
    "`out'/fig04-05-g4-plot-data.csv", ///
    replace

preserve
    keep if year == 1970
    keep g4 econ_group group_key econ_label n_countries
    sort econ_group
    export delimited using "`out'/g4-group-counts.csv", ///
        replace
restore

twoway ///
    (line alpha_hat year if econ_group == 1, ///
        lcolor("0 114 178") lwidth(medthick)) ///
    (line alpha_hat year if econ_group == 2, ///
        lcolor("230 159 0") lwidth(medthick)) ///
    (line alpha_hat year if econ_group == 3, ///
        lcolor("0 158 115") lwidth(medthick)) ///
    (line alpha_hat year if econ_group == 4, ///
        lcolor("213 94 0") lwidth(medthick)), ///
    title("四类潜在组的条件未观测效应") ///
    xtitle("年份") ///
    ytitle("估计的组别—时间效应 α̂(g,t)") ///
    xlabel(1970(5)2000) ///
    legend(order(1 "高民主组 (33 国)" ///
        2 "较早转型组 (13 国)" ///
        3 "低民主组 (26 国)" ///
        4 "较晚转型组 (18 国)") ///
        rows(2) position(6)) ///
    note("控制 lag_dem 与 lag_income；G=4 用于复现论文的典型类型展示") ///
    graphregion(color(white)) ///
    plotregion(color(white)) ///
    name(fig04, replace)

graph export "`figs'/xtgfe-fig04-g4-alpha.png", ///
    width(1200) replace

twoway ///
    (line dem_mean year if econ_group == 1, ///
        lcolor("0 114 178") lwidth(medthick)) ///
    (line dem_mean year if econ_group == 2, ///
        lcolor("230 159 0") lwidth(medthick)) ///
    (line dem_mean year if econ_group == 3, ///
        lcolor("0 158 115") lwidth(medthick)) ///
    (line dem_mean year if econ_group == 4, ///
        lcolor("213 94 0") lwidth(medthick)), ///
    title("四类潜在组的民主指数原始均值") ///
    xtitle("年份") ///
    ytitle("民主指数的组内原始均值 y-bar(g,t)") ///
    xlabel(1970(5)2000) ///
    legend(order(1 "高民主组 (33 国)" ///
        2 "较早转型组 (13 国)" ///
        3 "低民主组 (26 国)" ///
        4 "较晚转型组 (18 国)") ///
        rows(2) position(6)) ///
    note("未控制解释变量；对应 xtgfe plot, means 的绘图对象") ///
    graphregion(color(white)) ///
    plotregion(color(white)) ///
    name(fig05, replace)

graph export ///
    "`figs'/xtgfe-fig05-g4-democracy-means.png", ///
    width(1200) replace

*=======================================================================
* File checks and timing
*=======================================================================

capture program drop report_file_size
program define report_file_size
    args path
    confirm file "`path'"
    tempname handle
    file open `handle' using "`path'", read binary
    file seek `handle' eof
    file seek `handle' query
    local bytes = r(loc)
    file close `handle'
    display as text "file bytes: " as result `bytes' ///
        as text " | `path'"
end

forvalues figure = 1/5 {
    if `figure' == 1 {
        local filename "xtgfe-fig01-twfe-groups.png"
    }
    else if `figure' == 2 {
        local filename "xtgfe-fig02-bias-ladder.png"
    }
    else if `figure' == 3 {
        local filename "xtgfe-fig03-bic-groups.png"
    }
    else if `figure' == 4 {
        local filename "xtgfe-fig04-g4-alpha.png"
    }
    else {
        local filename "xtgfe-fig05-g4-democracy-means.png"
    }
    report_file_size "`figs'/`filename'"
}

timer off 1
timer list 1
display as text "Figure build completed: " c(current_date) ///
    " " c(current_time)
log close
