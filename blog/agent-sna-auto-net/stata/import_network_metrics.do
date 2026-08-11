version 19.0
clear all
set more off

* 从附件根目录运行本 do-file，不写入本机绝对路径。
use "outputs/tables/node_metrics.dta", clear

describe
label variable weighted_indegree "收到的求助次数"
label variable betweenness_distance "distance=1/weight 的中介中心性"
label variable constraint "对称化网络的结构洞约束"
label variable is_isolate "是否为孤立节点"

gsort -weighted_indegree student_id
list student_id field weighted_indegree betweenness_distance ///
    constraint is_isolate in 1/10, noobs clean
