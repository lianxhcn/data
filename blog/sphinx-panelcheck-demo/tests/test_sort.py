import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from panelcheck import missing_summary


def test_default_descending_and_stable_ties():
    df = pd.DataFrame({'complete': [1., 2.], 'a': [None, 1.],
                       'b': [2., None], 'empty': [None, None]})
    before = df.copy(deep=True)
    assert list(missing_summary(df).index) == ['empty', 'a', 'b', 'complete']
    assert list(missing_summary(df, sort=False).index) == list(df.columns)
    assert list(missing_summary(df, ['b', 'a']).index) == ['b', 'a']
    assert_frame_equal(df, before)


def test_false_preserves_requested_order():
    df = pd.DataFrame({'x': [1., None], 'y': [None, None]})
    assert list(missing_summary(df, ['x', 'y'], sort=False).index) == ['x', 'y']
    assert list(missing_summary(df, ['x', 'y'], sort=True).index) == ['y', 'x']


@pytest.mark.parametrize('sort', [True, False])
def test_empty_sort(sort):
    df = pd.DataFrame(columns=['b', 'a'])
    result = missing_summary(df, sort=sort)
    assert list(result.index) == ['b', 'a']
    assert result['missing_rate'].isna().all()


@pytest.mark.parametrize('sort', [None, 1, 'yes'])
def test_sort_requires_bool(sort):
    with pytest.raises(TypeError, match='sort must be bool'):
        missing_summary(pd.DataFrame({'x': [1]}), sort=sort)
