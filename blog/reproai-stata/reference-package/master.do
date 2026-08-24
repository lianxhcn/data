version 17.0
clear all
set more off

capture mkdir "data"
capture mkdir "tables"
capture mkdir "figures"
capture mkdir "logs"
capture log close _all
log using "logs/reference_run.log", text replace

capture noisily do "code/01_import_append.do"
if _rc {
    local rc = _rc
    log close
    exit `rc'
}

capture noisily do "code/02_analysis.do"
if _rc {
    local rc = _rc
    log close
    exit `rc'
}

capture noisily do "code/03_outputs.do"
if _rc {
    local rc = _rc
    log close
    exit `rc'
}

log close
