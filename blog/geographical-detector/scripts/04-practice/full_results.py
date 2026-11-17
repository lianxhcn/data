import pandas as pd
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)
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

label_map = {0: "非线性减弱", 1: "单因子减弱", 2: "双因子增强",
             3: "相互独立", 4: "非线性增强"}
print("=== 交互 q 矩阵 ===")
print(model.interaction_q_.round(3).to_string())
print("\n=== 交互类型矩阵（文字）===")
print(model.interaction_type_.replace(label_map).to_string())

print("\n=== 各因子分层均值（风险探测器）===")
for f in factors:
    means = proc.groupby(f)[target].mean().round(3)
    print(f"\n{f}:")
    print(means.to_string())

print("\n=== 生态探测器（F 检验）===")
eco = model.ecological_result_.copy()
eco["f_stat"] = eco["f_stat"].round(3)
eco["p_value"] = eco["p_value"].apply(lambda v: f"{v:.2e}")
print(eco.to_string(index=False))
