*! 04-pvar.do
*! 面板 VAR 估计（均值组 MG）与稳定性诊断
clear all
set more off

webuse grunfeld, clear
xtset company year

xtpvarcoint pvar invest mvalue kstock, lags(2) type(const)

* MG 系数矩阵与最大伴随特征根模
matrix list _xpvc_A
display "max eigenmod = " _xpvc_max_eigenmod
