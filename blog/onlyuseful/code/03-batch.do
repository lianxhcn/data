*==============================================================
* 03-batch.do
* 场景二：指定 newdta() 与 stataexe()，批处理直接生成精简数据
* 预期：保留 8 个变量 (含出现在注释里的 displacement)，
*       输出 reduced_data.dta、dropscript.do、dropscript.log
*==============================================================

clear all
set more off

* 首次运行：请改为与 01-install.do 相同的工作目录
local root "C:/your-path/onlyuseful-demo"
cd "`root'"

* 首次运行：请把下一行改为你本机 Stata 可执行文件的完整路径
local stataexe "C:/your-stata/StataMP-64.exe"

onlyuseful using analysis_script2.do, dta(mydata.dta) ///
    newdta(reduced_data.dta) lnewdta("`root'") ///
    stataexe("`stataexe'")

* 批处理在后台调用 Stata 生成数据，等待 reduced_data.dta 写出，最多 60 秒
local w 0
capture confirm file "`root'/reduced_data.dta"
while _rc & `w' < 60 {
    sleep 1000
    local ++w
    capture confirm file "`root'/reduced_data.dta"
}
display "等待秒数 = `w'"

* 核对批处理保留的变量数量
use "`root'/reduced_data.dta", clear
describe, short
