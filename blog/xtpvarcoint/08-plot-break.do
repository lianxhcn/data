*! 08-plot-break.do
*! plot 出图与结构突变选项实测（确认结构突变选项被静默忽略）
clear all
set more off

webuse grunfeld, clear
xtset company year

* 输出目录：默认当前工作目录下的 figures，可按需修改为其他路径
local outdir "figures"
capture mkdir "`outdir'"

xtpvarcoint pvar invest mvalue kstock, lags(2) type(const)
xtpvarcoint plot, plottype(eigenvalues) saving("`outdir'/test-eigen.png")

di "==================== speci var 带 breaks(2) ===================="
xtpvarcoint speci var invest mvalue kstock, lagset(1 2 3) breaks(2) trim(0.15) breaktype(const)

di "==================== pvec 带 tbreak(1945) ===================="
capture noisily xtpvarcoint pvec invest mvalue kstock, lags(2) rank(1) tbreak(1945)
di "pvec tbreak 退出码: " _rc
