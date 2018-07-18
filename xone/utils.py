import pandas as pd

from collections import Iterable


def tolist(iterable):
    """
    Simpler implementation of flatten method

    Args:
        iterable: any array or value

    Returns:
        list: list of unique values

    Examples:
        >>> assert tolist('xyz') == ['xyz']
        >>> assert tolist(['ab', 'cd', 'xy', 'ab']) == ['ab', 'cd', 'xy']
    """
    return pd.Series(iterable).drop_duplicates().tolist()


def fmt_dt(dt, fmt='%Y-%m-%d'):
    """
    Format date string

    Args:
        dt: any date format
        fmt: output date format

    Returns:
        str: date format

    Examples:
        >>> assert fmt_dt(dt='2018-12') == '2018-12-01'
        >>> assert fmt_dt(dt='2018-12-31', fmt='%Y%m%d') == '20181231'
    """
    return pd.Timestamp(dt).strftime(fmt)


def align_data(*data_list):
    """
    Resample and aligh data for defined frequency

    Args:
        *data_list: DataFrame of data to be aligned

    Returns:
        pd.DataFrame: aligned data with renamed columns
    """
    res = pd.DataFrame(pd.concat([
        d.loc[~d.index.duplicated(keep='first')].rename(
            columns=lambda vv: '%s_%d' % (vv, i + 1)
        ) for i, d in enumerate(data_list)
    ], axis=1))
    data_cols = [col for col in res.columns if col[-2:] == '_1']
    other_cols = [col for col in res.columns if col[-2:] != '_1']
    res.loc[:, other_cols] = res.loc[:, other_cols].fillna(method='pad')
    return res.dropna(subset=data_cols)


def flatten(iterable, maps=None, unique=False):
    """
    Flatten any array of items to list

    Args:
        iterable: any array or value
        maps: map items to values
        unique: drop duplicates

    Returns:
        list: flattened list

    References:
        https://stackoverflow.com/a/40857703/1332656

    Examples:
        >>> assert flatten('abc') == ['abc']
        >>> assert flatten(1) == [1]
        >>> assert flatten(1.) == [1.]
        >>> assert flatten(['ab', 'cd', ['xy', 'zz']]) == ['ab', 'cd', 'xy', 'zz']
        >>> assert flatten(['ab', ['xy', 'zz']], maps={'xy': '0x'}) == ['ab', '0x', 'zz']
    """
    if iterable is None: return []
    if maps is None: maps = dict()

    if isinstance(iterable, (str, int, float)):
        return [maps.get(iterable, iterable)]

    else:
        x = [maps.get(item, item) for item in _to_gen(iterable)]
        return list(set(x)) if unique else x


def _to_gen(iterable):
    """
    Recursively iterate lists and tuples
    """
    for elm in iterable:
        if isinstance(elm, Iterable) and not isinstance(elm, (str, bytes)):
            yield from flatten(elm)
        else: yield elm


if __name__ == '__main__':
    """
    CommandLine:
        python -m xone.utils all
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
