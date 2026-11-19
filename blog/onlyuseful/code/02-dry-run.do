*==============================================================
* 02-dry-run.do
* 场景一：不指定 newdta() 的 dry run，生成精简脚本并核对变量数量
* 预期：mydata.dta 含 12 个变量，精简后内存中保留 7 个
*==============================================================

clear all
set more off

* 首次运行：请改为与 01-install.do 相同的工作目录
local root "C:/your-path/onlyuseful-demo"
cd "`root'"

onlyuseful using analysis_script1.do, dta(mydata.dta) ///
    dropscript(onlyuseful_dropscript.do)

* onlyuseful 在后台异步运行 PowerShell，需等待精简脚本写出，最多 30 秒
local w 0
capture confirm file "`root'/onlyuseful_dropscript.do"
while _rc & `w' < 30 {
    sleep 1000
    local ++w
    capture confirm file "`root'/onlyuseful_dropscript.do"
}

* 核对精简前后的变量数量
use mydata.dta, clear
describe, short

do "`root'/onlyuseful_dropscript.do"
describe, short
