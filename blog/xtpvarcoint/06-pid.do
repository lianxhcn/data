*! 04c-pid-workaround.do
*! vecm 后手动补 _xpvc_N，再测 pid 各方法
clear all
set more off
webuse grunfeld, clear
xtset company year

xtpvarcoint vecm invest mvalue kstock, lags(2) rank(1)
scalar _xpvc_N = 10

di "==================== 补标量后 pid chol ===================="
capture noisily xtpvarcoint pid, method(chol)
di "chol 退出码: " _rc

di "==================== pid grt ===================="
capture noisily xtpvarcoint pid, method(grt)
di "grt 退出码: " _rc

di "==================== pid dc ===================="
capture noisily xtpvarcoint pid, method(dc)
di "dc 退出码: " _rc
