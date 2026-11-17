"""单个连续变量的 OPGD 网格搜索（Python 实现）。"""
import numpy as np
import pandas as pd
from mydisc import disc_breaks, disc_labels
from geodetector import GeoDetector


def opgd(x, y,
         methods=("equal", "natural", "quantile", "geometric", "sd"),
         k_range=(3, 8), alpha=0.05):
    """返回最优参数（Series）与全部组合结果表（DataFrame）。"""
    rows = []
    for m in methods:
        for k in range(k_range[0], k_range[1] + 1):
            d = pd.DataFrame({"y": y, "f": disc_labels(x, m, k)})
            r = GeoDetector(factors=["f"], target="y").fit(d).q_values_.iloc[0]
            rows.append({"method": m, "k": k, "q": r["q_value"],
                         "p": r["p_value"]})
    res = pd.DataFrame(rows)
    sig = res[res["p"] < alpha]
    best = sig.loc[sig["q"].idxmax()]
    return best, res


if __name__ == "__main__":
    dat = pd.read_csv("ndvi_40.csv")
    best, res = opgd(dat["Tempchange"].values, dat["NDVIchange"].values)
    print("=== 最优组合 ===")
    print(best.to_string())
    print("\n=== 最优断点 ===")
    print(np.round(disc_breaks(dat["Tempchange"].values,
                               best["method"], best["k"]), 4))
