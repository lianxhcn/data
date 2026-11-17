"""篇四主流程：按各变量 OPGD 最优参数离散化，再运行四大探测器。"""
import pandas as pd
from mydisc import disc_labels
from geodetector import GeoDetector

dat = pd.read_csv("ndvi_40.csv")
target = "NDVIchange"

# 各连续变量的 OPGD 最优参数
best_params = {
    "Tempchange": ("quantile", 8),
    "Precipitation": ("equal", 7),
    "GDP": ("quantile", 8),
    "Popdensity": ("quantile", 8),
}
categorical = ["Climatezone", "Mining"]

# 构建离散化后的分析数据
proc = pd.DataFrame({target: dat[target]})
for col, (m, k) in best_params.items():
    proc[col] = disc_labels(dat[col].values, m, k)
for col in categorical:
    proc[col] = dat[col]

factors = list(best_params.keys()) + categorical
model = GeoDetector(factors=factors, target=target).fit(proc)

print("=== 因子探测器 ===")
print(model.q_values_.round(4).to_string(index=False))
print("\n=== 交互类型取值分布 ===")
print(model.interaction_type_.replace(-1, pd.NA).apply(pd.Series.value_counts).dropna(how="all"))
