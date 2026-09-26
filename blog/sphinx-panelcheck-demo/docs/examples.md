# Examples

在项目根目录运行，无需下载数据：

```powershell
.venv\Scripts\python.exe examples/make_data.py
.venv\Scripts\python.exe examples/analyze.py
```

随机种子为 20260924。原有 20 个企业、2020—2024 年共 100 行，
去除企业 20 的 2024 年记录，再复制第 1 行，最终仍是 100 行。
缺失数量为 sales 2、assets 3、leverage 1；比例分别为 0.02、0.03、0.01。
默认输出顺序为 assets、sales、leverage，即按缺失比例降序。
清理已知复制行后为 99 行，20 个企业，每个企业 4—5 期。

下列代码直接引入真实脚本，避免复制第二份案例：

```{literalinclude} ../examples/analyze.py
:language: python
```

## 执行式文档检查

下面的 MyST doctest 块由 Sphinx doctest builder 执行。

```{doctest}
>>> import pandas as pd
>>> from panelcheck import missing_summary
>>> df = pd.DataFrame({'x': [1.0, None]})
>>> float(missing_summary(df).loc['x', 'missing_rate'])
0.5
```
