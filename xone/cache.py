import pandas as pd

import sys
import inspect
from functools import wraps
from xone import utils, files, logs


def data_file(func, has_date, root, date_type='date'):
    """
    Data file

    Args:
        func: use function to categorize data
        has_date: contains date in data file
        date_type: parameters pass to utils.cur_time, [date, time, time_path, ...]

    Returns:
        str: date file
    """
    cur_dt = utils.cur_time(typ=date_type, tz='UTC', trading=False)
    if has_date: file_fmt = '{root}/{typ}/{cur_dt}.parq'
    else: file_fmt = '{root}/{typ}.parq'
    return files.data_file(file_fmt=file_fmt, root=root, cur_dt=cur_dt, typ=func.__name__)


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

        kwargs.update(default)
        cur_mod = sys.modules[func.__module__]
        logger = logs.get_logger(name=f'{cur_mod.__name__}.{func.__name__}', types='stream')

        root_path = cur_mod.DATA_PATH
        date_type = kwargs.pop('date_type', 'date')
        save_static = kwargs.pop('save_static', True)
        save_dynamic = kwargs.pop('save_dynamic', True)
        d_file = data_file(func=func, has_date=True, root=root_path, date_type=date_type)
        s_file = data_file(func=func, has_date=False, root=root_path, date_type=date_type)

        cached = kwargs.pop('cached', False)
        if cached and save_static and files.exists(s_file):
            logger.info(f'Reading data from {s_file} ...')
            return pd.read_parquet(s_file)

        data = func(*args, **kwargs)

        if save_static:
            files.create_folder(s_file, is_file=True)
            files.save_data(data=data, file_fmt=s_file, append=False)
            logger.info(f'Saved data file to {s_file} ...')

        if save_dynamic:
            drop_dups = kwargs.pop('drop_dups', None)
            files.create_folder(d_file, is_file=True)
            files.save_data(data=data, file_fmt=d_file, append=True, drop_dups=drop_dups)
            logger.info(f'Saved data file to {d_file} ...')

        return data

    return wrapper
