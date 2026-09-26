"""透明的描述性检查；所有函数均不修改输入数据。"""
import pandas as pd


def _columns(df, cols):
    # 拒绝重复列名，避免选择一列却返回多列造成口径不明确。
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if not df.columns.is_unique:
        raise ValueError("DataFrame column names must be unique")
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"Columns not found: {missing}")


def check_panel_keys(df, id_col, time_col):
    """检查主键，返回位置而不删除记录。

    Parameters
    ----------
    df : pandas.DataFrame
        输入面板数据，行索引允许重复。
    id_col : str
        个体列名，必须与时间列不同。
    time_col : str
        时间列名。

    Returns
    -------
    dict
        ``valid`` 表示无缺失且无重复；``missing_key_rows`` 是任一主键缺失的
        行数；``duplicate_key_rows`` 是完整主键的所有重复成员行数
        (不是多余行数)；``missing_positions`` 与 ``duplicate_positions``
        是从 0 开始的行位置，不是 DataFrame 索引标签。

    Raises
    ------
    KeyError
        指定列不存在。
    ValueError
        两个主键列相同，或 DataFrame 列名重复。
    TypeError
        输入不是 DataFrame。
    """
    _columns(df, [id_col, time_col])
    if id_col == time_col:
        raise ValueError("id_col and time_col must differ")
    # 缺失主键单独报告，不将缺失值之间的相等视作重复键。
    missing = df[[id_col, time_col]].isna().any(axis=1)
    duplicate = (~missing) & df.duplicated([id_col, time_col], keep=False)
    return {
        "valid": not bool(missing.any() or duplicate.any()),
        "missing_key_rows": int(missing.sum()),
        "duplicate_key_rows": int(duplicate.sum()),
        "missing_positions": [i for i, value in enumerate(missing) if value],
        "duplicate_positions": [i for i, value in enumerate(duplicate) if value],
    }


def missing_summary(df, cols=None, sort=True):
    """汇总缺失数量和比例，默认按缺失比例降序排列。

    Parameters
    ----------
    df : pandas.DataFrame
        输入数据，不会被修改。
    cols : list of str or None, optional
        默认检查全部列；指定列表不得重复。sort=False 时保留列表顺序。
    sort : bool, optional
        默认 True，按缺失比例降序排列；并列保持输入顺序。
        False 时保持输入变量顺序。零行数据的比例均为 NaN，保持输入顺序。

    Returns
    -------
    pandas.DataFrame
        行索引是变量名，列为 ``missing_count`` 和 ``missing_rate``。
        比例分母是全部输入行数 (含重复记录)，不是有效观测数。
        零行数据的比例为 NaN，数量为 0。

    Raises
    ------
    KeyError
        指定变量不存在。
    ValueError
        列名或 cols 中的变量重复。
    TypeError
        df 不是 DataFrame，cols 不是列表/元组/None，或 sort 不是 bool。
    """
    _columns(df, [])
    if cols is not None and not isinstance(cols, (list, tuple)):
        raise TypeError("cols must be a list, tuple or None")
    if not isinstance(sort, bool):
        raise TypeError("sort must be bool")
    selected = list(df.columns if cols is None else cols)
    _columns(df, selected)
    if len(set(selected)) != len(selected):
        raise ValueError("cols must not contain duplicates")
    counts = df[selected].isna().sum()
    result = pd.DataFrame({"missing_count": counts,
                           "missing_rate": counts / len(df) if len(df) else float("nan")})
    # 稳定排序确保缺失比例相同时保留原顺序。
    if sort:
        result = result.sort_values("missing_rate", ascending=False, kind="stable")
    return result


def panel_overview(df, id_col, time_col):
    """在主键完整且唯一时汇总面板结构。

    Parameters
    ----------
    df : pandas.DataFrame
        非空数据；重复键和缺失键必须先由使用者处理。
    id_col : str
        个体列名。
    time_col : str
        可相互比较的时间值所在列名，例如整数年份。

    Returns
    -------
    dict
        ``n_units`` 是个体数；``time_min``/``time_max`` 是全样本时间范围；
        ``min_periods``/``max_periods`` 是每个个体不同时间值数量的极值。
        ``balanced`` 当且仅当所有个体具有同一组观测时间。
        不要求时间连续；没有检查日历上完全未出现的时期。

    Raises
    ------
    ValueError
        空数据、重复/缺失主键、列名重复或两个主键列相同。
    KeyError
        指定列不存在。
    TypeError
        df 不是 DataFrame，或时间值无法相互比较。
    """
    status = check_panel_keys(df, id_col, time_col)
    if df.empty or not status["valid"]:
        raise ValueError("panel_overview requires nonempty data with complete unique keys")
    # 每个个体的时间集合均是全样本时间集合的子集，因此比较集合大小即可。
    periods = df.groupby(id_col, observed=True)[time_col].nunique()
    return {"n_units": int(df[id_col].nunique()),
            "time_min": df[time_col].min(), "time_max": df[time_col].max(),
            "balanced": bool((periods == df[time_col].nunique()).all()),
            "min_periods": int(periods.min()), "max_periods": int(periods.max())}
