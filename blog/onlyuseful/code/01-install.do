*==============================================================
* 01-install.do
* 安装 onlyuseful 命令，并下载官方配套示例文件
* 说明：onlyuseful 要求工作目录为纯英文、无空格路径
*==============================================================

clear all
set more off

* 首次运行：请把下一行改为一个纯英文、无空格的工作目录完整路径 (用正斜杠)
local root "C:/your-path/onlyuseful-demo"

capture mkdir "`root'"
cd "`root'"

net sj 26-2
net install dm0117
net get dm0117
