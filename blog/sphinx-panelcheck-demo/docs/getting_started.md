# Getting Started

## 安装

在含 `pyproject.toml` 的项目根目录使用 Python 3.11：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe -m pip install --no-build-isolation -e .
```

## 第一个完整例子

代码自行创建数据。比例 0.5 表示全部 2 行中有 1 行缺失。
默认按缺失比例降序排列，assets 在 sales 之前。使用 sort=False 保留输入变量顺序。

```python
import pandas as pd
from panelcheck import missing_summary

# 自行创建数据，不依赖其他页面的变量。
df = pd.DataFrame({'sales': [10.0, None], 'assets': [None, None]})
result = missing_summary(df)
assert list(result.index) == ['assets', 'sales']
assert result.loc['sales', 'missing_rate'] == 0.5
print(result)
```

本页 Python 块由验证脚本在独立新进程中执行。
