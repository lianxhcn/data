clear all
set more off
capture which lianxh
if _rc ssc install lianxh, replace
lianxh 因果推断 潜在结果 倾向得分 双重差分 工具变量, md2 nocat
exit, clear
