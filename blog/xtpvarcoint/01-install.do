*! 01-install.do
*! 安装 xtpvarcoint 并核验（不做 log 管理，沿用 profile.do 的日志）
clear all
set more off

version
display "Stata version: `c(stata_version)'  flavor: `c(flavor)'"
display "Date: `c(current_date)'  Time: `c(current_time)'"

* 检查是否已安装
capture which xtpvarcoint
if (_rc == 0) {
    display "xtpvarcoint 已安装，路径如下："
    which xtpvarcoint
}
else {
    display "xtpvarcoint 未安装，开始通过 ssc 安装..."
}

* 安装（ssc）
ssc install xtpvarcoint, replace

* 安装后核验
which xtpvarcoint

* 查看 ado 文件位置
capture findfile xtpvarcoint.ado
if (_rc == 0) {
    display "ado 文件：`r(fn)'"
}

display "=== 安装步骤结束 ==="
