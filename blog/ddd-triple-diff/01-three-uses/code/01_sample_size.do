*==============================================================
* 01_sample_size.do
* 两个练习：
*   A. 样本量放大能收紧标准误，但收不紧偏误
*   B. 识别假设被破坏时，DDD 的偏误不随样本量缩小
* 运行：stata /e do 01_sample_size.do
*==============================================================

clear all
set more off

* 首次运行：请把下一行改为本文件夹 (01-三种用法) 的完整路径 (用正斜杠)
local root "C:/your-path/01-三种用法"

*--------------------------------------------------------------
* A. 平行趋势成立时的样本量敏感性
*--------------------------------------------------------------
tempfile mc_a
postfile pf n rep ddb dda ddd se_ddd using "`mc_a'", replace

foreach n in 100 500 1250 10000 {
    forvalues rep = 1/200 {
        quietly {
            clear
            set obs 8
            gen byte province = (_n >= 5)
            gen byte group    = inlist(_n, 3, 4, 7, 8)
            gen byte post     = inlist(_n, 2, 4, 6, 8)
            expand `n'

            local sd = `n' * 1000 + `rep'
            set seed `sd'
            gen double y = 1.0 + 0.20*province + 0.30*group + 0.50*post ///
                         + 0.30*province*post + 0.10*province*group*post ///
                         + rnormal(0, 0.35)

            gen byte ttt = province * group * post
            gen byte pt  = province * post
            gen byte gt  = group * post
            gen byte pg  = province * group

            reg y ttt pt gt pg i.province i.group i.post, robust
        }
        post pf (`n') (`rep') (_b[pt] + _b[ttt]) (_b[pt]) (_b[ttt]) (_se[ttt])
    }
}
postclose pf

use "`mc_a'", clear
label var n   "每格观测数"
label var ddb "DD_B 的估计"
label var dda "DD_A 的估计"
label var ddd "DDD 的估计"
label var se_ddd "DDD 的标准误"
table n, statistic(mean ddb) statistic(mean dda) statistic(mean ddd) ///
         statistic(sd ddd) statistic(mean se_ddd) statistic(freq)

*--------------------------------------------------------------
* B. 平行趋势被破坏：试点省 B 组另有 0.20 的趋势差异
*    DDD 的真值变为 0.10，但估计出的值是 0.10 + 0.20 = 0.30
*--------------------------------------------------------------
tempfile mc_b
postfile pf2 n rep ddb dda ddd using "`mc_b'", replace

foreach n in 1250 10000 {
    forvalues rep = 1/200 {
        quietly {
            clear
            set obs 8
            gen byte province = (_n >= 5)
            gen byte group    = inlist(_n, 3, 4, 7, 8)
            gen byte post     = inlist(_n, 2, 4, 6, 8)
            expand `n'

            local sd = `n' * 1000 + `rep' + 77
            set seed `sd'
            * 试点省 × B 组 × 后期 的额外趋势 (0.20) 不是政策效应
            gen double y = 1.0 + 0.20*province + 0.30*group + 0.50*post ///
                         + 0.30*province*post + 0.10*province*group*post ///
                         + 0.20*province*group*post ///
                         + rnormal(0, 0.35)

            gen byte ttt = province * group * post
            gen byte pt  = province * post
            gen byte gt  = group * post
            gen byte pg  = province * group

            reg y ttt pt gt pg i.province i.group i.post, robust
        }
        post pf2 (`n') (`rep') (_b[pt] + _b[ttt]) (_b[pt]) (_b[ttt])
    }
}
postclose pf2

use "`mc_b'", clear
display _n(20) "平行趋势被破坏时（真值 0.10，额外趋势 0.20）"
table n, statistic(mean ddb) statistic(mean dda) statistic(mean ddd) ///
         statistic(sd ddd) statistic(freq)
