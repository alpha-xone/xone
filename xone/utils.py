import numpy as np
import pandas as pd

import sys
import inspect
import json


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


def cur_time(typ='date', tz='US/Eastern', trading=True, cal='US'):
    """
    Current time

    Args:
        typ: one of ['date', 'time', 'time_path', 'raw', '']
        tz: timezone
        trading: check if current date is trading day
        cal: trading calendar

    Returns:
        relevant current time or date

    Examples:
        >>> cur_time(typ='time', tz='UTC')
        >>> cur_time(typ='time_path', tz='Asia/Hong_Kong')
        >>> cur_time(typ='raw', tz='Europe/London')
    """
    dt = pd.Timestamp('now', tz=tz)

    if typ == 'date':
        if trading: return trade_day(dt=dt, cal=cal).strftime('%Y-%m-%d')
        else: return dt.strftime('%Y-%m-%d')

    if typ == 'time': return dt.strftime('%Y-%m-%d %H:%M:%S')
    if typ == 'time_path': return dt.strftime('%Y-%m-%d/%H-%M-%S')
    if typ == 'raw': return dt

    return trade_day(dt).date() if trading else dt.date()


def trade_day(dt, cal='US'):
    """
    Latest trading day w.r.t given dt

    Args:
        dt: date of reference
        cal: trading calendar

    Returns:
        pd.Timestamp: last trading day

    Examples:
        >>> assert fmt_dt(trade_day('2018-12-25')) == '2018-12-24'
    """
    from xone import calendar

    dt = pd.Timestamp(dt).date()
    return calendar.trading_dates(start=dt - pd.Timedelta('10D'), end=dt, calendar=cal)[-1]


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
        x = [maps.get(item, item) for item in _to_gen_(iterable)]
        return list(set(x)) if unique else x


def _to_gen_(iterable):
    """
    Recursively iterate lists and tuples
    """
    from collections import Iterable

    for elm in iterable:
        if isinstance(elm, Iterable) and not isinstance(elm, (str, bytes)):
            yield from flatten(elm)
        else: yield elm


def to_frame(data_list, exc_cols=None):
    """
    Dict in Python 3.6 keeps insertion order, but cannot be relied upon
    This method is to keep column names in order
    In Python 3.7 this method is redundant

    Args:
        data_list: list of dict
        exc_cols: exclude columns

    Returns:
        pd.DataFrame

    Example:
        >>> d_list = [
        >>>     dict(id=1, symbol='1 HK', price=88.8),
        >>>     dict(id=700, symbol='700 HK', price=350.)
        >>> ]
        >>>
        >>> assert to_frame(d_list).columns.tolist() == ['id', 'symbol', 'price']
        >>> assert to_frame(d_list, ['price']).columns.tolist() == ['id', 'symbol']
    """
    from collections import OrderedDict

    return pd.DataFrame(
        pd.Series(data_list).apply(OrderedDict).tolist()
    ).drop(columns=[] if exc_cols is None else exc_cols)


def spline_curve(x, y, step, val_min=0, val_max=None, kind='quadratic', **kwargs):
    """
    Fit spline curve for given x, y values

    Args:
        x: x-values
        y: y-values
        step: step size for interpolation
        val_min: minimum value of result
        val_max: maximum value of result
        kind: for scipy.interpolate.interp1d
        Specifies the kind of interpolation as a string (‘linear’, ‘nearest’, ‘zero’, ‘slinear’,
        ‘quadratic’, ‘cubic’, ‘previous’, ‘next’, where ‘zero’, ‘slinear’, ‘quadratic’ and ‘cubic’
        refer to a spline interpolation of zeroth, first, second or third order; ‘previous’ and
        ‘next’ simply return the previous or next value of the point) or as an integer specifying
        the order of the spline interpolator to use. Default is ‘linear’.
        **kwargs: additional parameters for interp1d

    Returns:
        pd.Series: fitted curve

    Examples:
        >>> x = pd.Series([1, 2, 3])
        >>> y = pd.Series([np.exp(1), np.exp(2), np.exp(3)])
        >>> r = spline_curve(
        >>>     x=x, y=y, step=.5, val_min=3, val_max=18, fill_value='extrapolate'
        >>> ).round(2)
        >>> assert r.index.tolist() == [1., 1.5, 2., 2.5, 3.]
        >>> assert r.round(2).tolist() == [3., 4.05, 7.39, 12.73, 18.]
    """
    from scipy.interpolate import interp1d
    from collections import OrderedDict

    if isinstance(y, pd.DataFrame):
        return pd.DataFrame(OrderedDict([(col, spline_curve(
            x, y.loc[:, col], step=step, val_min=val_min, val_max=val_max, kind=kind
        )) for col in y.columns]))
    fitted_curve = interp1d(x, y, kind=kind, **kwargs)
    new_x = np.arange(x.min(), x.max() + step / 2., step=step)
    return pd.Series(
        new_x, index=new_x, name=y.name if hasattr(y, 'name') else None
    ).apply(fitted_curve).clip(val_min, val_max)


def func_scope(func):

    cur_mod = sys.modules[func.__module__]
    return f'{cur_mod.__name__}.{func.__name__}'


def format_float(digit=0, is_pct=False):
    """
    Number display format for pandas

    Args:
        digit: number of digits to keep
               if negative, add one space in front of positive pct
        is_pct: % display

    Returns:
        lambda function to format floats

    Examples:
        >>> assert format_float(0)(1e5) == '100,000'
        >>> assert format_float(1)(1e5) == '100,000.0'
        >>> assert format_float(-1, True)(.2) == ' 20.0%'
        >>> assert format_float(-1, True)(-.2) == '-20.0%'
        >>>
        >>> import pandas as pd
        >>> pd.options.display.float_format = format_float(2)
    """
    if is_pct:
        space = ' ' if digit < 0 else ''
        fmt = f'{{:{space}.{abs(int(digit))}%}}'
        return lambda vv: 'NaN' if np.isnan(vv) else fmt.format(vv)

    else:
        return lambda vv: 'NaN' if np.isnan(vv) else (
            f'{{:,.{digit}f}}'.format(vv) if vv else '-' + ' ' * abs(digit)
        )


def fstr(fmt, **kwargs):
    """
    Delayed evaluation of f-strings

    Args:
        fmt: f-string but in terms of normal string, i.e., '{path}/{file}.parq'
        **kwargs: variables for f-strings, i.e., path, file = '/data', 'daily'

    Returns:
        FString object

    References:
        https://stackoverflow.com/a/42497694/1332656
        https://stackoverflow.com/a/4014070/1332656

    Examples:
        >>> fmt = '{file}.parq'
        >>> file = 'data'
        >>> assert fstr(fmt, file=file) == 'data.parq'
    """
    locals().update(kwargs)
    return f'{FString(str_fmt=fmt)}'


class FString(object):

    def __init__(self, str_fmt):
        self.str_fmt = str_fmt

    def __str__(self):
        kwargs = inspect.currentframe().f_back.f_globals.copy()
        kwargs.update(inspect.currentframe().f_back.f_locals)
        return self.str_fmt.format(**kwargs)


def to_str(data, fmt='{key}={value}', sep=', ', public_only=True):
    """
    Convert dict to string

    Args:
        data: dict
        fmt: how key and value being represented
        sep: how pairs of key and value are seperated
        public_only: if display public members only

    Returns:
        str: string representation of dict

    Examples:
        >>> test_dict = dict(b=1, a=0, c=2, _d=3)
        >>> assert to_str(test_dict) == '{b=1, a=0, c=2}'
        >>> assert to_str(test_dict, sep='|') == '{b=1|a=0|c=2}'
        >>> assert to_str(test_dict, public_only=False) == '{b=1, a=0, c=2, _d=3}'
    """
    assert isinstance(data, dict)
    if public_only: keys = list(filter(lambda vv: vv[0] != '_', data.keys()))
    else: keys = list(data.keys())
    return '{' + sep.join([
        to_str(data=v, fmt=fmt, sep=sep)
        if isinstance(v, dict) else fstr(fmt=fmt, key=k, value=v)
        for k, v in data.items() if k in keys
    ]) + '}'


def inst_repr(instance, fmt='str', public_only=True):
    """
    Generate class instance signature from its __dict__
    From python 3.6 dict is ordered and order of attributes will be preserved automatically

    Args:
        instance: class instance
        fmt: ['json', 'str']
        public_only: if display public members only

    Returns:
        str: string or json representation of instance
    """

    if not hasattr(instance, '__dict__'): return ''

    if public_only: inst_dict = {k: v for k, v in instance.__dict__.items() if k[0] != '_'}
    else: inst_dict = instance.__dict__

    if fmt == 'json': return json.dumps(inst_dict, indent=2)
    elif fmt == 'str': return to_str(inst_dict, public_only=public_only)

    return ''


class AttributeDict(dict):
    """
    Dot access support for dict attributes

    References:
        https://stackoverflow.com/a/5021467/1332656
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


if __name__ == '__main__':
    """
    CommandLine:
        python -m xone.utils all
    """
    import xdoctest
    xdoctest.doctest_module()
