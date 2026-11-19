*==============================================================
* 01_event_study.do
* 第 2 篇第一类失效：差分平行趋势被破坏
* 结构：2 省 × 2 组 × 6 年，每格 800 人，共 19 200 个观测
* 政策在第 3 年后实施：year 1-3 为政策前，4-6 为政策后
* 场景 A：差分平行趋势成立；场景 B：试点省 B 组存在与政策无关的线性趋势
* 场景 B 的额外趋势为每年 0.10
*==============================================================

clear all
set more off
set seed 202

* 首次运行：请把下一行改为本文件夹 (02-diagnostics) 的完整路径 (用正斜杠)
local root "C:/your-path/02-diagnostics"

capture mkdir "`root'/data"
tempname pf
postfile `pf' str4 scen int year double ddd se using "`root'/data/event_results.dta", replace

foreach scen in good bad {

    * ------------------------------------------------------------
    * 1. 生成数据：3 200 个个体，各追踪 6 年
    *    前 1 600 人属非试点省，后 1 600 人属试点省
    *    每省前 800 人为 A 组，后 800 人为 B 组
    * ------------------------------------------------------------
    clear
    set obs 3200
    gen byte province = (_n > 1600)
    gen byte group    = (mod(_n-1, 1600) >= 800)
    gen long id       = _n
    expand 6
    bysort id: gen year = _n
    gen byte post = (year >= 4)

    * ------------------------------------------------------------
    * 2. 结果变量
    *    共同时间趋势：每年 +0.10
    *    共同冲击：试点省政策后 +0.30，对 A、B 两组相同
    *    政策效应：试点省 B 组政策后 +0.10
    *    场景 B 另加：试点省 B 组每年 +0.10 的额外趋势，政策前即存在
    * ------------------------------------------------------------
    gen double y = 1.0 + 0.20*province + 0.30*group + 0.10*(year-1) ///
                 + 0.30*province*post + 0.10*province*group*post      ///
                 + rnormal(0, 0.35)

    if "`scen'" == "bad" {
        replace y = y + 0.10*(year-1)*province*group
    }

    * ------------------------------------------------------------
    * 3. 手工计算各年 DDD 事件研究系数
    *    DDD_k = (试点省 B - 试点省 A) - (非试点省 B - 非试点省 A)
    *    以政策前最后一年 (year 3) 为基准做归一化
    * ------------------------------------------------------------
    forvalues k = 1/6 {
        sum y if province==1 & group==1 & year==`k', meanonly
        scalar pb`k' = r(mean)
        sum y if province==0 & group==1 & year==`k', meanonly
        scalar nb`k' = r(mean)
        sum y if province==1 & group==0 & year==`k', meanonly
        scalar pa`k' = r(mean)
        sum y if province==0 & group==0 & year==`k', meanonly
        scalar na`k' = r(mean)
        scalar ddd`k' = (pb`k'-pa`k') - (nb`k'-na`k')
    }

    forvalues k = 1/6 {
        scalar dddn`k' = ddd`k' - ddd3
    }

    display _newline "===== 场景 (`scen')：手工计算的归一化 DDD 事件研究系数 ====="
    forvalues k = 1/6 {
        display "year " `k' "  DDD = " %8.4f dddn`k'
    }

    * ------------------------------------------------------------
    * 4. 饱和回归事件研究：以第 3 年为基准年
    *    三向交互系数即归一化 DDD 系数，与手工计算对照
    * ------------------------------------------------------------
    reg y ib3.year##i.province##i.group, vce(robust) noheader

    display _newline "===== 场景 (`scen')：回归三向交互系数与手工计算对照 ====="
    forvalues k = 1/6 {
        if `k' == 3 {
            scalar bk = 0
            scalar sk = 0
        }
        else {
            scalar bk = _b[`k'.year#1.province#1.group]
            scalar sk = _se[`k'.year#1.province#1.group]
        }
        display "year " `k' "  回归 = " %8.4f bk "  手工 = " %8.4f dddn`k' ///
                "  标准误 = " %7.4f sk
        post `pf' ("`scen'") (`k') (dddn`k') (sk)
    }
}

postclose `pf'

* ------------------------------------------------------------
* 5. 汇总结果表，导出 CSV 供绘图使用
* ------------------------------------------------------------
use "`root'/data/event_results.dta", clear
export delimited using "`root'/data/event_results.csv", replace
list, sepby(scen) noobs
