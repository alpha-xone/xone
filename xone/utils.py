import numpy as np
import pandas as pd

import json
import time
import pytz
import inspect
import sys

from xone import __version__

__all__ = ['__version__']

DEFAULT_TZ = pytz.FixedOffset(-time.timezone / 60)


def tolist(iterable):
    """
    Simpler implementation of flatten method

    Args:
        iterable: any array or value

    Returns:
        list: list of unique values

    Examples:
        >>> tolist('xyz')
        ['xyz']
        >>> tolist(['ab', 'cd', 'xy', 'ab'])
        ['ab', 'cd', 'xy']
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
        >>> fmt_dt(dt='2018-12')
        '2018-12-01'
        >>> fmt_dt(dt='2018-12-31', fmt='%Y%m%d')
        '20181231'
    """
    return pd.Timestamp(dt).strftime(fmt)


def trade_day(dt, cal='US'):
    """
    Latest trading day w.r.t given dt

    Args:
        dt: date of reference
        cal: trading calendar

    Returns:
        pd.Timestamp: last trading day

    Examples:
        >>> trade_day('2018-12-25', cal='US').strftime('%Y-%m-%d')
        '2018-12-24'
    """
    from xone import calendar

    dt = pd.Timestamp(dt).date()
    return calendar.trading_dates(start=dt - pd.Timedelta('10D'), end=dt, cal=cal)[-1]


def cur_time(typ='date', tz=DEFAULT_TZ, trading=True, cal='US'):
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
        >>> cur_dt = pd.Timestamp('now')
        >>> cur_time(typ='date', trading=False) == cur_dt.strftime('%Y-%m-%d')
        True
        >>> cur_time(typ='time', trading=False) == cur_dt.strftime('%Y-%m-%d %H:%M:%S')
        True
        >>> cur_time(typ='time_path', trading=False) == cur_dt.strftime('%Y-%m-%d/%H-%M-%S')
        True
        >>> isinstance(cur_time(typ='raw', tz='Europe/London'), pd.Timestamp)
        True
        >>> isinstance(cur_time(typ='raw', trading=True), pd.Timestamp)
        True
        >>> cur_time(typ='', trading=False) == cur_dt.date()
        True
    """
    dt = pd.Timestamp('now', tz=tz)

    if typ == 'date':
        if trading: return trade_day(dt=dt, cal=cal).strftime('%Y-%m-%d')
        else: return dt.strftime('%Y-%m-%d')

    if typ == 'time': return dt.strftime('%Y-%m-%d %H:%M:%S')
    if typ == 'time_path': return dt.strftime('%Y-%m-%d/%H-%M-%S')
    if typ == 'raw': return dt

    return trade_day(dt).date() if trading else dt.date()


def align_data(*args):
    """
    Resample and aligh data for defined frequency

    Args:
        *args: DataFrame of data to be aligned

    Returns:
        pd.DataFrame: aligned data with renamed columns

    Examples:
        >>> start = '2018-09-10T10:10:00'
        >>> tz = 'Australia/Sydney'
        >>> idx = pd.date_range(start=start, periods=6, freq='min').tz_localize(tz)
        >>> close_1 = [31.08, 31.10, 31.11, 31.07, 31.04, 31.04]
        >>> vol_1 = [10166, 69981, 14343, 10096, 11506, 9718]
        >>> d1 = pd.DataFrame(dict(price=close_1, volume=vol_1), index=idx)
        >>> d1
                                   price  volume
        2018-09-10 10:10:00+10:00  31.08   10166
        2018-09-10 10:11:00+10:00  31.10   69981
        2018-09-10 10:12:00+10:00  31.11   14343
        2018-09-10 10:13:00+10:00  31.07   10096
        2018-09-10 10:14:00+10:00  31.04   11506
        2018-09-10 10:15:00+10:00  31.04    9718
        >>> close_2 = [70.81, 70.78, 70.85, 70.79, 70.79, 70.79]
        >>> vol_2 = [4749, 6762, 4908, 2002, 9170, 9791]
        >>> d2 = pd.DataFrame(dict(price=close_2, volume=vol_2), index=idx)
        >>> d2
                                   price  volume
        2018-09-10 10:10:00+10:00  70.81    4749
        2018-09-10 10:11:00+10:00  70.78    6762
        2018-09-10 10:12:00+10:00  70.85    4908
        2018-09-10 10:13:00+10:00  70.79    2002
        2018-09-10 10:14:00+10:00  70.79    9170
        2018-09-10 10:15:00+10:00  70.79    9791
        >>> align_data(d1, d2)
                                   price_1  volume_1  price_2  volume_2
        2018-09-10 10:10:00+10:00    31.08     10166    70.81      4749
        2018-09-10 10:11:00+10:00    31.10     69981    70.78      6762
        2018-09-10 10:12:00+10:00    31.11     14343    70.85      4908
        2018-09-10 10:13:00+10:00    31.07     10096    70.79      2002
        2018-09-10 10:14:00+10:00    31.04     11506    70.79      9170
        2018-09-10 10:15:00+10:00    31.04      9718    70.79      9791
    """
    res = pd.DataFrame(pd.concat([
        d.loc[~d.index.duplicated(keep='first')].rename(
            columns=lambda vv: '%s_%d' % (vv, i + 1)
        ) for i, d in enumerate(args)
    ], axis=1))
    data_cols = [col for col in res.columns if col[-2:] == '_1']
    other_cols = [col for col in res.columns if col[-2:] != '_1']
    res.loc[:, other_cols] = res.loc[:, other_cols].fillna(method='pad')
    return res.dropna(subset=data_cols)


def cat_data(data_kw):
    """
    Concatenate data with ticker as sub column index

    Args:
        data_kw: key = ticker, value = pd.DataFrame

    Returns:
        pd.DataFrame

    Examples:
        >>> start = '2018-09-10T10:10:00'
        >>> tz = 'Australia/Sydney'
        >>> idx = pd.date_range(start=start, periods=6, freq='min').tz_localize(tz)
        >>> close_1 = [31.08, 31.10, 31.11, 31.07, 31.04, 31.04]
        >>> vol_1 = [10166, 69981, 14343, 10096, 11506, 9718]
        >>> d1 = pd.DataFrame(dict(price=close_1, volume=vol_1), index=idx)
        >>> close_2 = [70.81, 70.78, 70.85, 70.79, 70.79, 70.79]
        >>> vol_2 = [4749, 6762, 4908, 2002, 9170, 9791]
        >>> d2 = pd.DataFrame(dict(price=close_2, volume=vol_2), index=idx)
        >>> sample = cat_data({'BHP AU': d1, 'RIO AU': d2})
        >>> sample.columns
        MultiIndex([('BHP AU',  'price'),
                    ('BHP AU', 'volume'),
                    ('RIO AU',  'price'),
                    ('RIO AU', 'volume')],
                   names=['ticker', None])
        >>> r = sample.transpose().iloc[:, :2]
        >>> r.index.names = (None, None)
        >>> r
                       2018-09-10 10:10:00+10:00  2018-09-10 10:11:00+10:00
        BHP AU price                       31.08                      31.10
               volume                  10,166.00                  69,981.00
        RIO AU price                       70.81                      70.78
               volume                   4,749.00                   6,762.00
    """
    if len(data_kw) == 0: return pd.DataFrame()
    return pd.DataFrame(
        pd.concat([
            data
            .assign(ticker=ticker)
            .set_index('ticker', append=True)
            .unstack('ticker')
            .swaplevel(0, 1, axis=1)
            for ticker, data in data_kw.items()
        ], axis=1)
    )


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
        >>> flatten('abc')
        ['abc']
        >>> flatten(1)
        [1]
        >>> flatten(1.)
        [1.0]
        >>> flatten(['ab', 'cd', ['xy', 'zz']])
        ['ab', 'cd', 'xy', 'zz']
        >>> flatten(['ab', ['xy', 'zz']], maps={'xy': '0x'})
        ['ab', '0x', 'zz']
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
    from collections.abc import Iterable

    for elm in iterable:
        if isinstance(elm, Iterable) and not isinstance(elm, (str, bytes)):
            yield from flatten(elm)
        else: yield elm


def to_frame(data_list, exc_cols=None, **kwargs):
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
        ...     dict(sid=1, symbol='1 HK', price=89),
        ...     dict(sid=700, symbol='700 HK', price=350)
        ... ]
        >>> to_frame(d_list)
           sid  symbol  price
        0    1    1 HK     89
        1  700  700 HK    350
        >>> to_frame(d_list, exc_cols=['price'])
           sid  symbol
        0    1    1 HK
        1  700  700 HK
    """
    from collections import OrderedDict

    # noinspection PyTypeChecker
    return pd.DataFrame(
        pd.Series(data_list)
        .apply(OrderedDict)
        .tolist(),
        **kwargs
    ).drop(columns=[] if exc_cols is None else exc_cols)


def read_zip(zip_url: str, read_func, **kwargs) -> pd.DataFrame:
    """
    Read zip file, either from url or local

    Args:
        zip_url: URL or local address
        read_func: function
        **kwargs: key-word arguments passed to read_func

    Returns:
        pd.DataFrame

    Examples:
        >>> from xone.files import abspath
        >>> test_folder = f'{abspath(__file__)}/tests/files'
        >>> sample = read_zip(
        ...     zip_url=f'{test_folder}/master.zip',
        ...     read_func=pd.read_csv,
        ...     skiprows=list(range(9)) + [10],
        ...     sep='|',
        ...     encoding='latin1',
        ... )
        >>> (
        ...     sample[sample['Company Name'].str.startswith('BP')]
        ...     .iloc[:, :-1]
        ...     .reset_index(drop=True)
        ... )
               CIK                    Company Name Form Type  Date Filed
        0  1167581          BP CAPITAL MARKETS PLC    25-NSE  2020-10-02
        1  1167583  BP CAPITAL MARKETS AMERICA INC    25-NSE  2020-10-02
        2  1798039              BPGIC HOLDINGS Ltd  SC 13D/A  2020-10-05
        3   313807                          BP PLC       6-K  2020-10-05
        4   850033    BP PRUDHOE BAY ROYALTY TRUST       8-K  2020-10-02
    """
    import tempfile
    import zipfile
    import urllib.parse
    import urllib.request

    data_list = []
    info = urllib.parse.urlparse(zip_url)
    is_url = len(info.scheme) > 1
    with tempfile.TemporaryFile(mode='w+b') as tmp:
        if is_url: tmp.write(urllib.request.urlopen(zip_url).read())
        with zipfile.ZipFile(tmp if is_url else zip_url) as zf:
            for f_name in zf.namelist():
                with zf.open(f_name) as z:
                    try:
                        data_list.append(read_func(z, **kwargs))
                    except Exception as e:
                        print(e)

    return pd.DataFrame(pd.concat(data_list, sort=False))


def func_scope(func):
    """
    Function scope name

    Args:
        func: python function

    Returns:
        str: module_name.func_name

    Examples:
        >>> func_scope(flatten)
        'xone.utils.flatten'
        >>> func_scope(json.dump)
        'json.dump'
    """
    cur_mod = sys.modules[func.__module__]
    return f'{cur_mod.__name__}.{func.__name__}'


def func_kwarg(func, **kwargs) -> dict:
    """
    Pass kwargs to function only if they are required

    Args:
        func: function

    Returns:
        dict

    Examples:
        >>> func_kwarg(func=read_zip, red=1)
        {'red': 1}
        >>> func_kwarg(func=func_scope, red=1)
        {}
    """
    import inspect
    if not callable(func): return {}

    param = inspect.signature(func).parameters
    kind = pd.Series({k: v.kind for k, v in param.items()})
    if kind.max() == 4: return kwargs
    else: return {k: v for k, v in kwargs.items() if k in kind}


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
        >>> format_float(0)(1e5)
        '100,000'
        >>> format_float(1)(1e5)
        '100,000.0'
        >>> format_float(-1, True)(.2)
        ' 20.0%'
        >>> format_float(-1, True)(-.2)
        '-20.0%'
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


class FString(object):

    def __init__(self, str_fmt):
        self.str_fmt = str_fmt

    def __str__(self):
        kwargs = inspect.currentframe().f_back.f_globals.copy()
        kwargs.update(inspect.currentframe().f_back.f_locals)
        return self.str_fmt.format(**kwargs)


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
        >>> use_fmt = '{data_path}/{data_file}.parq'
        >>> fstr(fmt=use_fmt, data_path='your/data/path', data_file='sample')
        'your/data/path/sample.parq'
    """
    locals().update(kwargs)
    return f'{FString(str_fmt=fmt)}'


def to_str(data: dict, fmt='{key}={value}', sep=', ', public_only=True):
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
        >>> to_str(test_dict)
        '{b=1, a=0, c=2}'
        >>> to_str(test_dict, sep='|')
        '{b=1|a=0|c=2}'
        >>> to_str(test_dict, public_only=False)
        '{b=1, a=0, c=2, _d=3}'
    """
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

    Examples:
        >>> inst_repr(1)
        ''
        >>> class SampleClass(object):
        ...     def __init__(self):
        ...         self.b = 3
        ...         self.a = 4
        ...         self._private_ = 'hidden'
        >>>
        >>> s = SampleClass()
        >>> inst_repr(s)
        '{b=3, a=4}'
        >>> inst_repr(s, public_only=False)
        '{b=3, a=4, _private_=hidden}'
        >>> json.loads(inst_repr(s, fmt='json'))
        {'b': 3, 'a': 4}
        >>> inst_repr(s, fmt='unknown')
        ''
    """
    if not hasattr(instance, '__dict__'): return ''

    if public_only:
        inst_dict = {k: v for k, v in instance.__dict__.items() if k[0] != '_'}
    else: inst_dict = instance.__dict__

    if fmt == 'json': return json.dumps(inst_dict, indent=2)
    elif fmt == 'str': return to_str(inst_dict, public_only=public_only)

    return ''


def load_module(full_path):
    """
    Load module from full path

    Args:
        full_path: module full path name

    Returns:
        python module

    References:
        https://stackoverflow.com/a/67692/1332656

    Examples:
        >>> import os
        >>>
        >>> cur_file = os.path.abspath(__file__).replace('\\\\', '/')
        >>> cur_path = '/'.join(cur_file.split('/')[:-1])
        >>> load_module(f'{cur_path}/files.py').__name__
        'files'
        >>> load_module(f'{cur_path}/files.pyc')
        Traceback (most recent call last):
        ImportError: not a python file: files.pyc
    """
    from importlib import util

    file_name = full_path.replace('\\', '/').split('/')[-1]
    if file_name[-3:] != '.py':
        raise ImportError(f'not a python file: {file_name}')
    module_name = file_name[:-3]

    spec = util.spec_from_file_location(name=module_name, location=full_path)
    module = util.module_from_spec(spec=spec)
    spec.loader.exec_module(module=module)

    return module


class AttributeDict(dict):
    """
    Dot access support for dict attributes

    References:
        https://stackoverflow.com/a/5021467/1332656
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
