*! 05b-sboot-t.do
*! 手动补 _xpvc_T 后测试 sboot
clear all
set more off
webuse grunfeld, clear
xtset company year
xtpvarcoint pvar invest mvalue kstock, lags(2) type(const)
scalar _xpvc_T = 20

xtpvarcoint sboot, method(pmb) nboot(30) horizon(4) ci(0.95) seed(1)
