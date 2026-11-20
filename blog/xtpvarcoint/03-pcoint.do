*! 03-pcoint.do
*! 面板协整秩检验：JO、BR、SL、CAIN 四种方法
*! 检验从 r=0 开始逐秩进行；Case3 为含确定性项设定
clear all
set more off

webuse grunfeld, clear
xtset company year

xtpvarcoint pcoint invest mvalue kstock, method(JO)   lags(2) type(Case3)
xtpvarcoint pcoint invest mvalue kstock, method(BR)   lags(2) type(Case3)
xtpvarcoint pcoint invest mvalue kstock, method(SL)   lags(2) type(Case3)
xtpvarcoint pcoint invest mvalue kstock, method(CAIN) lags(2) type(Case3)
