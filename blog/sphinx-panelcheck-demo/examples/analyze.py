"""运行完整案例，并断言关键结果。"""
from make_data import make_data
from panelcheck import check_panel_keys, missing_summary, panel_overview

df = make_data()
keys = check_panel_keys(df, "firm_id", "year")
assert keys["duplicate_positions"] == [0, 99]
print("Raw key check:", keys)
summary = missing_summary(df, cols=["sales", "assets", "leverage"])
assert list(summary.index) == ["assets", "sales", "leverage"]
assert summary.loc["assets", "missing_rate"] == 0.03
print(summary)
# 仅因生成器已知复制的是同一条记录，才明确保留第一次出现的记录。
# 真实研究中必须先核对重复记录来源，不能默认用此规则清洗。
clean = df.drop_duplicates(["firm_id", "year"], keep="first")
overview = panel_overview(clean, "firm_id", "year")
assert overview["n_units"] == 20 and overview["min_periods"] == 4
assert overview["max_periods"] == 5 and not overview["balanced"]
print("Clean panel:", overview)
