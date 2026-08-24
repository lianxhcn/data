version 17.0
cd "D:/github_lianxh/data/blog/reproai-stata/reference-package"
about
do "D:/github_lianxh/data/blog/reproai-stata/reference-package/master.do"
local run_rc = _rc
exit `run_rc'
