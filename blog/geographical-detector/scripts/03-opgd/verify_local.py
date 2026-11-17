import pandas as pd
from mydisc import disc_breaks, disc_labels
from geodetector import GeoDetector

dat = pd.read_csv("ndvi_40.csv")
x = dat["Tempchange"].values

print("=== 五方法 5 类 q 值 ===")
for m in ["equal", "natural", "quantile", "geometric", "sd"]:
    d = dat.copy()
    d["f"] = disc_labels(x, m, 5)
    r = GeoDetector(factors=["f"], target="NDVIchange").fit(d).q_values_.iloc[0]
    print(f"{m:9s} q = {r['q_value']:.4f}  p = {r['p_value']:.4f}")

print("=== 分类数 3-8（natural）===")
for k in range(3, 9):
    d = dat.copy()
    d["f"] = disc_labels(x, "natural", k)
    q = GeoDetector(factors=["f"], target="NDVIchange").fit(d).q_values_.iloc[0]["q_value"]
    print(k, "q =", round(q, 4))
