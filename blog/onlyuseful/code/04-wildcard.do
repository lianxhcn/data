*==============================================================
* 04-wildcard.do
* 场景三：构造通配符与缩写测试数据，再运行 onlyuseful
* 预期：year* 与 yearof 均无法识别，精简脚本只保留完整写出的 year2000
*==============================================================

clear all
set more off

* 首次运行：请改为与 01-install.do 相同的工作目录
local root "C:/your-path/onlyuseful-demo"
cd "`root'"

* 构造含四个变量的测试数据
set obs 10
gen year1999 = 1
gen year2000 = 2
gen year2001 = 3
gen yearofbirth = 1990
save testwild.dta, replace

* 扫描 wild_analysis.do，生成精简脚本
onlyuseful using wild_analysis.do, dta(testwild.dta) ///
    dropscript(wild_dropscript.do)

* 等待后台 PowerShell 写出精简脚本，最多 30 秒
local w 0
capture confirm file "`root'/wild_dropscript.do"
while _rc & `w' < 30 {
    sleep 1000
    local ++w
    capture confirm file "`root'/wild_dropscript.do"
}

* 查看精简脚本内容，确认只保留 year2000
type "`root'/wild_dropscript.do"
