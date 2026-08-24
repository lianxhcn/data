version 17.0
clear all
set more off

* Audit trail for the deterministic defect injection used in this fixture.
* Run only after reference-package/ has passed.  The raw CSV files are copied
* unchanged; D01--D10 are injected once in code and README as documented in
* docs/defect-register.md.  This file records the intended build order and
* protects raw input files from alteration.
local project_root "`c(pwd)'"
confirm file "`project_root'/reference-package/raw/auto_domestic.csv"
confirm file "`project_root'/reference-package/raw/auto_foreign.csv"
copy "`project_root'/reference-package/raw/auto_domestic.csv" ///
    "`project_root'/broken-package/raw/auto_domestic.csv", replace
copy "`project_root'/reference-package/raw/auto_foreign.csv" ///
    "`project_root'/broken-package/raw/auto_foreign.csv", replace
display as text "Broken-package code is the frozen D01--D10 fixture."
