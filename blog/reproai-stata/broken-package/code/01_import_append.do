import delimited "raw/auto_domestic.csv", clear varnames(1)
tempfile domestic
save `domestic'

capture confirm file "raw/auto_foreign.csv"
if _rc {
    use `domestic', clear
}
else {
    import delimited "raw/auto_foreign.csv", clear varnames(1)
    merge 1:1 car_id using `domestic'
    drop _merge
}

save "data/auto_combined.dta", replace
