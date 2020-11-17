import pandas as pd

import sys
import inspect

from functools import wraps
from xone import utils, files, logs

LOAD_FUNC = {
    'pkl': pd.read_pickle,
    'parq': pd.read_parquet,
    'csv': pd.read_csv,
    'xls': pd.read_excel,
    'xlsx': pd.read_excel,
}

SAVE_FUNC = {
    'pkl': 'to_pickle',
    'parq': 'to_parquet',
    'csv': 'to_csv',
    'xlsx': 'to_excel',
    'xls': 'to_excel',
}


def with_cache(*dec_args, **dec_kwargs):
    """
    Wraps function to load cache data if available

    Args:
        data_path: root data path for caching.
                   for functions in module, default will be the DATA_PATH defined in the module
        file_fmt: file format (can include subfolder as well)
        update_freq: update frequency, e.g., 1M, 1Q, etc.
        load_func: custom function to load data (has to use `data_file` as argument)
        save_func: custom function to save data (has to use `data` and `date_file` as argument)
        file_func: custom function to generate file format:
                   data will be saved to f'{root_path}/{file_func(**kwargs)}'
    """
    # Data root path
    data_root = dec_kwargs.get('data_path', None)
    # File format
    file_fmt = dec_kwargs.get('file_fmt', None)
    # Update frequency - in pd.Timedelta - determines how frequent data should be updated
    update_freq = dec_kwargs.get('update_freq', None)

    # Data loading / saving functions
    # For saving, function has to have `data` and `data_file` as argument
    load_func = dec_kwargs.get('load_func', None)
    save_func = dec_kwargs.get('save_func', None)
    file_func = dec_kwargs.get('file_func', None)

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            # Check function parameters
            param = inspect.signature(func).parameters
            all_kw = {
                k: args[n] if n < len(args) else v.default
                for n, (k, v) in enumerate(param.items())
            }
            all_kw.update(utils.func_kwarg(func=func, **kwargs))
            kwargs.update(all_kw)

            # Data path and file name
            cur_dt = utils.cur_time(tz=kwargs.get('_tz_', utils.DEFAULT_TZ))
            if data_root:
                root_path = data_root
            else:
                root_path = getattr(sys.modules[func.__module__], 'DATA_PATH')
            if file_fmt:
                file_name = target_file_name(fmt=file_fmt, **all_kw)
            else:
                file_name = f'{func.__name__}/[date].pkl'

            if callable(file_func):
                name_pattern = ''
                data_file = f'{root_path}/{file_func(**kwargs)}'
            else:
                name_pattern = (
                    f'{root_path}/{file_name}'.replace('\\', '/')
                    .replace('[today]', '[date]')
                )
                data_file = name_pattern.replace('[today]', cur_dt)

            # Reload data and override cache if necessary
            use_cache = not kwargs.get('_reload_', False)

            # Load data if exists
            if files.exists(data_file) and use_cache:
                return load_file(data_file=data_file, load_func=load_func, **kwargs)

            # Load data if it was updated within update frequency
            if update_freq and use_cache and ('[date]' in name_pattern):
                start_dt = pd.date_range(end=cur_dt, freq=update_freq, periods=2)[0]
                for dt in pd.date_range(start=start_dt, end=cur_dt, normalize=True)[::-1]:
                    cur_file = name_pattern.replace('[date]', dt.strftime('%Y-%m-%d'))
                    if files.exists(cur_file):
                        return load_file(data_file=data_file, load_func=load_func, **kwargs)

            # Retrieve data
            data = func(**all_kw)

            # Save data to cache
            save_file(data=data, data_file=data_file, save_func=save_func, **kwargs)

            return data
        return wrapper

    return decorator(dec_args[0]) if dec_args and callable(dec_args[0]) else decorator


def target_file_name(fmt: str, **kwargs) -> str:
    """
    Target file name

    Args:
        fmt: f-string format

    Returns:
        str

    Examples:
        >>> target_file_name('data/ticker={ticker}.pkl', ticker='RDS/A')
        'data/ticker=RDS_A.pkl'
        >>> target_file_name('data/{corp}', corp='E*TRADE FUTURES LLC')
        'data/E@TRADE FUTURES LLC'
    """
    return utils.fstr(
        fmt=fmt,
        **{
            k: str(v)
            .replace('*', '@')
            .replace(':', ' -')
            .replace('\\', '/')
            .replace('/', '_')
            for k, v in kwargs.items()
        }
    )


def load_file(data_file: str, load_func=None, **kwargs):
    """
    Load data from cache
    """
    logger = logs.get_logger(load_file, level=kwargs.get('log', 'info'))
    if (not data_file) or (not files.exists(data_file)): return

    if callable(load_func): return load_func(data_file)

    ext = data_file.split('.')[-1]
    if ext not in LOAD_FUNC: return

    logger.debug(f'Reading from {data_file} ...')
    return LOAD_FUNC[ext](data_file)


def save_file(data, data_file: str, save_func=None, **kwargs):
    """
    Save data
    """
    logger = logs.get_logger(save_file, level=kwargs.get('log', 'info'))
    if not data_file: return
    if isinstance(data, (pd.Series, pd.DataFrame)) and data.empty: return

    files.create_folder(data_file, is_file=True)
    if callable(save_func):
        logger.debug(f'Saving data to {data_file} ...')
        save_func(data=data, data_file=data_file)

    ext = data_file.split('.')[-1]
    save_kw = {}
    if ext in ['csv', 'xls', 'xlsx']: save_kw['index'] = False

    save_func = SAVE_FUNC.get(ext, '__nothing__')
    if not hasattr(data, save_func): return

    logger.debug(f'Saving data to {data_file} ...')
    getattr(data, save_func)(data_file, **save_kw)
