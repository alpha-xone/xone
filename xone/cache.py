import hashlib
import json

import pandas as pd

import sys
import inspect
from functools import wraps
from xone import utils, files, logs


def cache_file(symbol, func, has_date, root, date_type='date'):
    """
    Data file

    Args:
        symbol: symbol
        func: use function to categorize data
        has_date: contains date in data file
        root: root path
        date_type: parameters pass to utils.cur_time, [date, time, time_path, ...]

    Returns:
        str: date file
    """
    cur_mod = sys.modules[func.__module__]
    data_tz = getattr(cur_mod, 'DATA_TZ') if hasattr(cur_mod, 'DATA_TZ') else 'UTC'
    cur_dt = utils.cur_time(typ=date_type, tz=data_tz, trading=False)

    if has_date:
        if hasattr(cur_mod, 'FILE_WITH_DATE'):
            file_fmt = getattr(cur_mod, 'FILE_WITH_DATE')
        else:
            file_fmt = '{root}/{typ}/{symbol}/{cur_dt}.parq'
    else:
        if hasattr(cur_mod, 'FILE_NO_DATE'):
            file_fmt = getattr(cur_mod, 'FILE_NO_DATE')
        else:
            file_fmt = '{root}/{typ}/{symbol}.parq'

    return data_file(
        file_fmt=file_fmt, root=root, cur_dt=cur_dt, typ=func.__name__, symbol=symbol
    )


def update_data(func):
    """
    Decorator to save data more easily. Use parquet as data format

    Args:
        func: function to load data from data source

    Returns:
        wrapped function
    """
    default = dict([
        (param.name, param.default)
        for param in inspect.signature(func).parameters.values()
        if param.default != getattr(inspect, '_empty')
    ])

    @wraps(func)
    def wrapper(*args, **kwargs):

        default.update(kwargs)
        cur_mod = sys.modules[func.__module__]
        logger = logs.get_logger(name_or_func=f'{cur_mod.__name__}.{func.__name__}', types='stream')

        root_path = cur_mod.DATA_PATH
        date_type = kwargs.pop('date_type', 'date')
        save_static = kwargs.pop('save_static', True)
        save_dynamic = kwargs.pop('save_dynamic', True)
        symbol = kwargs.get('symbol')
        file_kw = dict(func=func, symbol=symbol, root=root_path, date_type=date_type)
        d_file = cache_file(has_date=True, **file_kw)
        s_file = cache_file(has_date=False, **file_kw)

        cached = kwargs.pop('cached', False)
        if cached and save_static and files.exists(s_file):
            logger.info(f'Reading data from {s_file} ...')
            return pd.read_parquet(s_file)

        data = func(*args, **kwargs)

        if save_static:
            files.create_folder(s_file, is_file=True)
            save_data(data=data, file_fmt=s_file, append=False)
            logger.info(f'Saved data file to {s_file} ...')

        if save_dynamic:
            drop_dups = kwargs.pop('drop_dups', None)
            files.create_folder(d_file, is_file=True)
            save_data(data=data, file_fmt=d_file, append=True, drop_dups=drop_dups)
            logger.info(f'Saved data file to {d_file} ...')

        return data

    return wrapper


def save_data(data, file_fmt, append=False, drop_dups=None, info=None, **kwargs):
    """
    Save data to file

    Args:
        data: pd.DataFrame
        file_fmt: data file format in terms of f-strings
        append: if append data to existing data
        drop_dups: list, drop duplicates in columns
        info: dict, infomation to be hashed and passed to f-strings
        **kwargs: additional parameters for f-strings

    Examples:
        >>> data = pd.DataFrame([[1, 2], [3, 4]], columns=['a', 'b'])
        >>> save_data(data, '{ROOT}/daily/{typ}.parq', ROOT='/data', typ='earnings')
    """
    from xone import utils

    d_file = data_file(file_fmt=file_fmt, info=info, **kwargs)
    if append and files.exists(d_file):
        data = pd.DataFrame(pd.concat([pd.read_parquet(d_file), data], sort=False))
        if drop_dups is not None:
            data.drop_duplicates(subset=utils.tolist(drop_dups), inplace=True)

    if not data.empty: data.to_parquet(d_file)
    return data


def data_file(file_fmt, info=None, **kwargs):
    """
    Data file name for given infomation

    Args:
        file_fmt: file format in terms of f-strings
        info: dict, to be hashed and then pass to f-string using 'hash_key'
              these info will also be passed to f-strings
        **kwargs: arguments for f-strings

    Returns:
        str: data file name
    """
    from xone import utils

    if isinstance(info, dict):
        kwargs['hash_key'] = hashlib.md5(json.dumps(info).encode('utf-8')).hexdigest()
        kwargs.update(info)

    return utils.fstr(fmt=file_fmt, **kwargs)
