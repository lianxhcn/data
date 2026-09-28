* 00_setup.do — 依赖检查/安装 + 数据本地快照
* 这段做什么：确保 coefplot 可用（缺了才装、不加 replace），
* 首次联网抓取 nlswork 并存本地副本，之后离线可复现。

* --- 依赖：coefplot ---
capture which coefplot
if _rc {
    di as txt ">> coefplot 未安装，联网安装（不加 replace）"
    ssc install coefplot           // 注意：不加 , replace
}
which coefplot                     // 记录版本信息到日志

* --- 数据：webuse 取一次即快照 ---
capture confirm file "04-data/nlswork.dta"
if _rc {
    di as txt ">> 首次运行：联网抓取 nlswork 并保存本地副本"
    webuse nlswork, clear
    save "04-data/nlswork.dta", replace
}
else {
    di as txt ">> 检测到本地副本，跳过联网抓取"
}
