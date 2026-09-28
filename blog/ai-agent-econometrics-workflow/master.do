* master.do — 一键复现入口
* 假定：从项目根目录运行本脚本（工作目录 = project-root）
* 若 Stata 当前工作目录不是根目录，取消下一行注释并按实际路径填写后再运行：
* cd "填写项目根目录的绝对路径"

version 19
clear all
set more off

cap mkdir "04-data"
cap mkdir "05-logs"
cap mkdir "02-figs"
cap mkdir "02-figs/publish"

log using "05-logs/run.log", replace text

do "03-code/00_setup.do"
do "03-code/01_check.do"
do "03-code/02_reg.do"

log close
