* ============================================================
* 第 8 节：在 do-file 里调用 Python 读 Parquet（Stata 16+ 内置）
* 首次调用前可用 python query 检查解释器，必要时用
* python set exec "本机解释器路径" 设置会话
* ============================================================

python:
import pandas as pd
df = pd.read_parquet("survey.parquet")
df.to_stata("survey.dta", write_index=False, version=118)
end

use survey.dta, clear

* ============================================================
* 第 9 节：读取保留公司年度观察单位的分析样本
* ============================================================

use "analysis_panel.dta", clear
isid firm_id year
list, sepby(firm_id)

* 示意数据只有四个观察值，用于演示导入和主键检查，
* 不能据此开展有意义的统计推断。
