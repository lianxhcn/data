# 安装依赖：pip install pandas pyarrow duckdb
import pandas as pd
import duckdb

# 一、模拟接口取得的嵌套记录
raw = [
    {"firm_id": "A01", "reports": [
        {"year": 2023, "revenue": 120},
        {"year": 2024, "revenue": 135},
    ]},
    {"firm_id": "A02", "reports": [
        {"year": 2023, "revenue": 80},
        {"year": 2024, "revenue": 92},
    ]},
]

# 二、展开为公司年度表并明确数据类型
panel = pd.json_normalize(raw, record_path="reports", meta=["firm_id"])
panel = panel[["firm_id", "year", "revenue"]]
panel["year"] = panel["year"].astype("int64")
panel["revenue"] = panel["revenue"].astype("float64")

# 三、保存为 Parquet；便于下次直接读取和跨工具使用
panel.to_parquet("company_panel.parquet", index=False)

# 四、DuckDB 在文件上筛选公司年度观察值
analysis = duckdb.sql("""
    SELECT firm_id, year, revenue
    FROM read_parquet('company_panel.parquet')
    WHERE year >= 2023
    ORDER BY firm_id, year
""").df()

# 五、导出 Stata 格式；此处没有改变公司年度观察单位
analysis.to_stata("analysis_panel.dta", write_index=False, version=118)
print(analysis)
