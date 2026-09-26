# Tutorial

## 先查主键，再解释面板

每个企业每年应只有一条记录。三个函数均不会替你清洗数据。
此例故意复制企业 1 的第一条观测，因此重复成员行数为 2。

```python
import pandas as pd
from panelcheck import check_panel_keys, missing_summary, panel_overview

df = pd.DataFrame({'firm_id': [1, 1, 2, 1], 'year': [2020, 2021, 2020, 2020],
                   'sales': [10., None, 30., 10.], 'assets': [None, None, 60., None]})
keys = check_panel_keys(df, 'firm_id', 'year')
assert keys['duplicate_key_rows'] == 2
assert keys['duplicate_positions'] == [0, 3]
print(keys)
summary = missing_summary(df, ['sales', 'assets'])
assert list(summary.index) == ['assets', 'sales']
assert summary.loc['assets', 'missing_rate'] == 0.75
print(summary)
# 此例已知重复行来源，才明确保留第一条。
clean = df.drop_duplicates(['firm_id', 'year'])
overview = panel_overview(clean, 'firm_id', 'year')
assert overview['n_units'] == 2 and not overview['balanced']
assert (overview['min_periods'], overview['max_periods']) == (1, 2)
print(overview)
```

缺失表默认按比例降序排列，assets 在 sales 之前。若需保留输入顺序，显式传入 sort=False。assets 缺失比例是 3/4，分母包含重复行。
清理后企业 1 有 2 期、企业 2 有 1 期，因此 `balanced=False`。
真实研究应核查重复来源与缺期原因；不能据此判断估计是否无偏。

平衡要求每个个体拥有相同的观测时间集合。观测期数相同而时间集合不同，也不平衡。
所有企业都未出现的年份不会被自动识别为缺期。
