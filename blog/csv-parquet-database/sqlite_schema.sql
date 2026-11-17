-- ============================================================
-- 第 4 节：关系型数据库的 JOIN 查询与建表语句（SQLite）
-- ============================================================

-- 一、多表关联查询：公司表 JOIN 财报表
SELECT a.firm_id, a.company_name, b.year, b.revenue
FROM company AS a
JOIN financial AS b ON a.firm_id = b.firm_id
WHERE b.year >= 2023;

-- 二、定义财报表：每次连接后先在事务外启用外键检查，
-- 并为主键字段显式设置 NOT NULL
PRAGMA foreign_keys = ON;

CREATE TABLE financial (
    firm_id VARCHAR NOT NULL,
    year INTEGER NOT NULL,
    revenue DOUBLE,
    PRIMARY KEY (firm_id, year),
    FOREIGN KEY (firm_id) REFERENCES company(firm_id)
);

-- 根据常用查询条件决定是否建立索引
CREATE INDEX idx_financial_year ON financial(year);
