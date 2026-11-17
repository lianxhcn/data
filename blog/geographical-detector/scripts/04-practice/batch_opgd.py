"""对全部连续变量批量执行 OPGD，汇总各变量的最优离散化参数。"""
import pandas as pd
from mydisc import disc_breaks, disc_labels
from geodetector import GeoDetector

dat = pd.read_csv("ndvi_40.csv")
target = "NDVIchange"
continuous = ["Tempchange", "Precipitation", "GDP", "Popdensity"]
methods = ["equal", "natural", "quantile", "geometric", "sd"]


def opgd_one(x, y, alpha=0.05):
    rows = []
    for m in methods:
        for k in range(3, 9):
            d = pd.DataFrame({"y": y, "f": disc_labels(x, m, k)})
            r = GeoDetector(factors=["f"], target="y").fit(d).q_values_.iloc[0]
            rows.append({"method": m, "k": k, "q": r["q_value"], "p": r["p_value"]})
    res = pd.DataFrame(rows)
    sig = res[res["p"] < alpha]
    return sig.loc[sig["q"].idxmax()]


summary = []
for col in continuous:
    best = opgd_one(dat[col].values, dat[target].values)
    summary.append({"variable": col, "method": best["method"],
                    "k": int(best["k"]), "q": round(best["q"], 4)})
    print(col, "完成")

print("\n=== 各连续变量 OPGD 最优参数 ===")
print(pd.DataFrame(summary).to_string(index=False))
