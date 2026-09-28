# 示例数据

本公开包不分发第三方数据快照。首次运行 master.do 时用 webuse nlswork 获取 Stata 官方示例数据，保存为 nlswork.dta，后续读取本地副本。

官方来源：https://www.stata-press.com/data/r19/nlswork.dta

若 webuse 返回 r(677)，Windows 用户可在项目根目录执行 ./03-code/download_data.ps1；也可在浏览器从上述官方链接下载，保存为此目录下的 nlswork.dta，再运行主程序。

历史验证快照的 SHA256 为 B77BC182AC586205D769AD847E5E7CB0063C31BE2C4BBEF5F1AD16B74118C86F。官网今后若更新数据，应先核对版本与文件差异，不把旧校验值当成永久承诺。
