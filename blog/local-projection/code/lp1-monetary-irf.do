*! 局部投影法入门(1)：加息冲击与脉冲响应 —— 复现 do 文件
*! 数据：Stata 手册自带 usmacro3（联邦基金宏观数据，785 个月，1954m8–2019m12）
*! 说明：方法一需要 Stata 19 的 ivlpirf 命令；方法二使用 ivreg2，适用于 Stata 18 等较早版本。

* ========== 0. 读入数据 ==========
use https://www.stata-press.com/data/r19/usmacro3, clear
tsset datem

* 工具变量 money_inst 仅 468 个月有值（1969m1–2007m12），
* 扣除 13 阶滞后后，每个 h 的回归样本均为 455（1970m2–2007m12）。
count if !missing(money_inst)

* ========== 1. 方法一：官方命令 ivlpirf（需要 Stata 19） ==========
* cumulative ：报告累计响应，ip_growth 累加后即工业产出水平的变化（长差分）
* step(36)   ：估计到第 36 个月
* lags(1/12) ：控制变量放入 1 至 12 阶滞后
* vce(robust)：稳健标准误
ivlpirf ip_growth inflation, endogenous(d.fedfunds = money_inst) ///
        cumulative step(36) lags(1/12) vce(robust)

* ========== 2. 方法二：手写 ivreg2 循环（Stata 18 等可用） ==========
* 先安装依赖（只需一次）
* ssc install ivreg2
* ssc install ranktest

use https://www.stata-press.com/data/r19/usmacro3, clear
tsset datem

local H = 36
matrix R = J(`H'+1, 4, .)

forvalues h = 0/`H' {

    * 第 1 步：构造左侧长差分（t-1 至 t+h 的累计增长率）
    capture drop cy
    gen cy = 0
    forvalues j = 0/`h' {
        quietly replace cy = cy + F`j'.ip_growth
    }

    * 第 2 步：估计 LP-IV；L(1/13) 为滞后增广，故用 robust 即可
    quietly ivreg2 cy (D.fedfunds = money_inst)              ///
        L(1/13).ip_growth L(1/13).D.fedfunds                ///
        L(1/13).inflation L(1/13).money_inst, robust

    * 第 3 步：存储结果
    matrix R[`h'+1, 1] = `h'
    matrix R[`h'+1, 2] = _b[D.fedfunds]
    matrix R[`h'+1, 3] = _se[D.fedfunds]
    matrix R[`h'+1, 4] = e(widstat)
}

* 第 4 步：绘制脉冲响应图
matrix colnames R = h b se F
svmat R, names(col)
gen lo = b - 1.96*se
gen hi = b + 1.96*se
twoway (rarea lo hi h, color(gs13)) (line b h, lcolor(navy)), ///
       yline(0) xtitle("加息后第 h 个月") ytitle("工业产出累计变化") legend(off)

list h F in 1/37
