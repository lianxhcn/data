clear all
set more off

cd "D:/github_lianxh/data/blog/reproai-stata/broken-package"
mkdir "data"
mkdir "tables"
mkdir "figures"
mkdir "logs"
log using "logs/broken_run.log", text replace

do "code/01_import_append.do"
do "code/02_analysis.do"
do "code/04_format_tables.do"
do "code/03_outputs.do"
log close
