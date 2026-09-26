import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from panelcheck import check_panel_keys, missing_summary, panel_overview


@pytest.fixture
def df():
    return pd.DataFrame({"id": [1, 1, 2, 2], "t": [1, 2, 1, 2],
                         "x": [1., None, 3., 4.], "y": [None, None, 3., 4.]})


def test_normal(df):
    assert check_panel_keys(df, "id", "t")["valid"]
    assert panel_overview(df, "id", "t") == dict(
        n_units=2, time_min=1, time_max=2, balanced=True, min_periods=2, max_periods=2)


def test_duplicate(df):
    data = pd.concat([df, df.iloc[[0]]])
    assert check_panel_keys(data, "id", "t")["duplicate_positions"] == [0, 4]
    with pytest.raises(ValueError, match="unique keys"):
        panel_overview(data, "id", "t")


@pytest.mark.parametrize("col", ["id", "t"])
def test_missing_keys(df, col):
    df[col] = df[col].astype(float)
    df.loc[0, col] = float("nan")
    assert check_panel_keys(df, "id", "t")["missing_positions"] == [0]
    with pytest.raises(ValueError):
        panel_overview(df, "id", "t")


@pytest.mark.parametrize("func,args", [
    (check_panel_keys, ("absent", "t")),
    (panel_overview, ("id", "absent")),
    (missing_summary, (["absent"],))])
def test_unknown_column(df, func, args):
    with pytest.raises(KeyError, match="Columns not found"):
        func(df, *args)


def test_missing_all(df):
    result = missing_summary(df)
    assert list(result.index) == ["y", "x", "id", "t"]
    assert result.loc["x", "missing_count"] == 1
    assert result.loc["x", "missing_rate"] == 0.25


def test_selected_order(df):
    assert list(missing_summary(df, ["y", "x"], sort=False).index) == ["y", "x"]


def test_unbalanced(df):
    assert not panel_overview(df.iloc[:-1], "id", "t")["balanced"]


def test_equal_counts_different_times():
    data = pd.DataFrame({"id": [1, 1, 2, 2], "t": [1, 2, 2, 3]})
    assert not panel_overview(data, "id", "t")["balanced"]


def test_no_mutation(df):
    before = df.copy(deep=True)
    check_panel_keys(df, "id", "t")
    missing_summary(df)
    panel_overview(df, "id", "t")
    assert_frame_equal(before, df)


def test_empty(df):
    empty = df.iloc[:0]
    assert missing_summary(empty)["missing_rate"].isna().all()
    assert missing_summary(empty)["missing_count"].eq(0).all()
    assert missing_summary(df, []).empty
    with pytest.raises(ValueError):
        panel_overview(empty, "id", "t")


def test_invalid_arguments(df):
    with pytest.raises(ValueError):
        check_panel_keys(df, "id", "id")
    with pytest.raises(ValueError):
        missing_summary(df, ["x", "x"])
    with pytest.raises(TypeError):
        missing_summary(df, "x")
    with pytest.raises(TypeError):
        missing_summary([1, 2])
    with pytest.raises(ValueError):
        missing_summary(pd.DataFrame([[1, 2]], columns=["x", "x"]))
