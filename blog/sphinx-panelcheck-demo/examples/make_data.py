"""固定随机种子生成教学数据，无网络依赖。"""
from pathlib import Path
import numpy as np
import pandas as pd


def make_data():
    # 20 个企业、5 年；明确移去一个时期，构成非平衡面板。
    rng = np.random.default_rng(20260924)
    df = pd.DataFrame({"firm_id": np.repeat(np.arange(1, 21), 5),
                       "year": np.tile(np.arange(2020, 2025), 20)})
    df["sales"] = rng.lognormal(4, 0.2, len(df))
    df["assets"] = df["sales"] * rng.uniform(1.5, 2.5, len(df))
    df["leverage"] = rng.uniform(0.1, 0.7, len(df))
    # 缺失仅放在非主键列；主键缺失由独立单元测试覆盖。
    df.loc[[3, 8], "sales"] = np.nan
    df.loc[[4, 9, 14], "assets"] = np.nan
    df.loc[[5], "leverage"] = np.nan
    df = df.drop(index=99)
    return pd.concat([df, df.iloc[[0]]], ignore_index=True)


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "output" / "demo.csv"
    target.parent.mkdir(exist_ok=True)
    make_data().to_csv(target, index=False, encoding="utf-8-sig")
    print(f"Saved 100 rows to {target}")
