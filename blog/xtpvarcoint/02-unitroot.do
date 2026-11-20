*! 02-unitroot.do
*! 面板单位根检验：使用 Stata 官方 xtunitroot（LLC 与 IPS）
*! 原假设为面板包含单位根；对水平值与一阶差分分别考察
clear all
set more off

webuse grunfeld, clear
xtset company year

foreach v of varlist invest mvalue kstock {
    xtunitroot llc `v', trend lags(aic)
    xtunitroot ips `v', trend lags(aic)
    xtunitroot llc D.`v', noconstant lags(aic)
    xtunitroot ips D.`v', lags(aic)
}
