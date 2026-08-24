# Reference Stata package

Run `do master.do` from this directory.  It requires Stata 17 or newer and
uses only built-in commands.  `raw/auto_domestic.csv` and
`raw/auto_foreign.csv` come from the project-level `source/00_export_raw.do`.
They are row partitions and must be recombined with `append using`.

Expected runtime is under 1 minute.  Outputs are `tables/table1_regression.csv`,
`figures/price_mpg_scatter.png`, `data/auto_combined.dta`, bootstrap draws in
`data/bootstrap_mpg.dta`, and `logs/reference_run.log`.
