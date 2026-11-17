"""把四大探测器结果导出为 CSV，供论文表格使用。"""
import pandas as pd
from mydisc import disc_labels
from geodetector import GeoDetector

dat = pd.read_csv("ndvi_40.csv")
target = "NDVIchange"
best_params = {"Tempchange": ("quantile", 8), "Precipitation": ("equal", 7),
               "GDP": ("quantile", 8), "Popdensity": ("quantile", 8)}
categorical = ["Climatezone", "Mining"]
proc = pd.DataFrame({target: dat[target]})
for col, (m, k) in best_params.items():
    proc[col] = disc_labels(dat[col].values, m, k)
for col in categorical:
    proc[col] = dat[col]
factors = list(best_params.keys()) + categorical
model = GeoDetector(factors=factors, target=target).fit(proc)

model.q_values_.to_csv("表1_因子探测.csv", index=False, encoding="utf-8-sig")
model.interaction_q_.to_csv("表2_交互q矩阵.csv", encoding="utf-8-sig")
model.ecological_result_.to_csv("表3_生态探测.csv", index=False, encoding="utf-8-sig")
print("三张结果表已导出")
