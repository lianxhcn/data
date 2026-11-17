# 安装依赖：pip install pandas pyarrow duckdb
import os
import pandas as pd
import duckdb

# ===== 第 3 节：json_normalize 展开嵌套记录 =====
data = {
    "firm_id": "A01",
    "reports": [
        {"year": 2023, "revenue": 120},
        {"year": 2024, "revenue": 135},
    ],
}

# record_path 指出要展开的数组；meta 保留公司代码
df = pd.json_normalize(data, record_path="reports", meta=["firm_id"])
df = df[["firm_id", "year", "revenue"]]
print("【第 3 节 json_normalize】")
print(df)

# ===== 第 5 节：Parquet 读写，恢复字段类型 =====
df.to_parquet("cleaned.parquet", index=False)
back = pd.read_parquet("cleaned.parquet")  # 读取 Parquet，恢复相应的字段类型
print("\n【第 5 节 Parquet 读回列类型】", dict(back.dtypes.astype(str)))

# ===== 第 6 节：DuckDB 直接查询文件，通配符读入目录 =====
os.makedirs("survey", exist_ok=True)
pd.DataFrame({"region": ["A", "A", "B"], "income": [10, 20, 30]}).to_parquet(
    "survey/s1.parquet", index=False)

r1 = duckdb.sql("""
    SELECT region, AVG(income) AS avg_income
    FROM read_parquet('survey/*.parquet')
    GROUP BY region
    ORDER BY avg_income DESC
""")
print("\n【第 6 节 DuckDB 聚合】")
print(r1.df())

# 结果转成 pandas DataFrame
small = duckdb.sql("""
    SELECT region, AVG(income) AS avg_income
    FROM read_parquet('survey/*.parquet')
    GROUP BY region
""").df()
print("\n【结果转 pandas】类型:", type(small).__name__, "行数", len(small))
