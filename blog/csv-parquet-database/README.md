# 从 CSV 到 Parquet 与数据库：配套代码

本文件夹是连享会推文《从 CSV 到 Parquet 与数据库：实证研究者的数据存储指南》（作者：郑怿轩）的配套代码，覆盖 JSON 展开、Parquet 读写、SQLite 建表、DuckDB 文件直查以及将新格式接回 Stata 的完整流程。所有 Python 代码均在 Python 3.12 环境实测通过。

## 目录内容

| 文件 | 对应推文 | 说明 |
|:---|:---|:---|
| `workflow.py` | 第 9 节 | 端到端工作流：JSON 展开 → Parquet 存储 → DuckDB 筛选 → 导出 `.dta` |
| `snippets.py` | 第 3、5、6 节 | `json_normalize`、Parquet 读写、DuckDB 聚合与通配查询 |
| `sqlite_schema.sql` | 第 4 节 | 外键约束、联合主键、索引的建表语句与 JOIN 查询 |
| `stata_integration.do` | 第 8、9 节 | Stata 调用 Python 读 Parquet、读取分析样本 |

## 运行环境

安装依赖：

```bash
pip install pandas pyarrow duckdb
```

- Python 3.10 及以上；实测环境为 Python 3.12，pandas 3.1.0、pyarrow 25.0.0、duckdb 2.0.0。
- Stata 部分需要 Stata 16 及以上版本（内置 Python 集成）。

## 运行方式

```bash
# 端到端工作流，运行后生成 company_panel.parquet 与 analysis_panel.dta
python workflow.py

# 分节概念片段
python snippets.py
```

SQL 片段可在任何 SQLite 工具中执行，或通过 Python 的 `sqlite3` 模块运行。

## 配图（已上传阿里云 OSS）

- 图 1 主键、外键与一对多关系：https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/zhengyixuan-parquet-fig1-202611171750.png
- 图 2 行式与列式的读取差异：https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/zhengyixuan-parquet-fig2-202611171750.png
- 图 3 行组统计与谓词下推：https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/zhengyixuan-parquet-fig3-202611171750.png
- 图 4 端到端数据工作流：https://fig-lianxh.oss-cn-shenzhen.aliyuncs.com/zhengyixuan-parquet-fig4-202611171750.png
