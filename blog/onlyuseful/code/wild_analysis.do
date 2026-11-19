*==============================================================
* wild_analysis.do
* 被 onlyuseful 扫描的分析脚本，使用通配符 year* 与缩写 yearof
*==============================================================

use testwild.dta, clear
reg year2000 year*
reg year2000 yearof
