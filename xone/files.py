import pandas as pd

import os
import re
import glob
import time
import hashlib
import json

DATE_FMT = '\d{4}-(0?[1-9]|1[012])-(0?[1-9]|[12][0-9]|3[01])'


def exists(path):
    """
    Check path or file exists (use os.path.exists)

    Args:
        path: path or file
    """
    return os.path.exists(path=path)


def data_file(file_fmt, info, **kwargs):
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

    d_file = utils.fstr(fmt=file_fmt, info=info, **kwargs)
    if append and exists(d_file):
        data = pd.DataFrame(pd.concat([pd.read_parquet(d_file), data]))
        if drop_dups is not None:
            data.drop_duplicates(subset=utils.tolist(drop_dups), inplace=True)

    data.to_parquet(d_file)
    return data


def create_folder(path_name, is_file=False):
    """
    Make folder as well as all parent folders if not exists

    Args:
        path_name: full path name
        is_file: whether input is name of file
    """
    assert isinstance(path_name, str)
    path_sep = path_name.replace('\\', '/').split('/')
    for i in range(1, len(path_sep) + (0 if is_file else 1)):
        cur_path = '/'.join(path_sep[:i])
        if not os.path.exists(cur_path): os.mkdir(cur_path)


def all_files(path_name, keyword='', ext='', full_path=True, has_date=False, date_fmt=DATE_FMT):
    """
    Search all files with criteria

    Args:
        path_name: full path name
        keyword: keyword to search
        ext: file extensions, split by ','
        full_path: whether return full path (default True)
        has_date: whether has date in file name (default False)
        date_fmt: date format to check for has_date parameter

    Returns:
        list: all file names fulfilled criteria
    """
    if not os.path.exists(path=path_name): return []

    if keyword or ext:
        to_find = (('*%s*' % keyword) if keyword else '*') + '.' + (ext if ext else '*')
        files = [f for f in glob.iglob('/'.join([path_name, to_find]))]
        files = [
            f.replace('\\', '/').split('/')[-1]
            for f in sorted(files, key=os.path.getmtime, reverse=True) if f[0] != '~'
        ]

    else:
        files = [
            f for f in os.listdir(path=path_name)
            if os.path.isfile('/'.join([path_name, f])) and (f[0] != '~')
        ]

    if has_date:
        r = re.compile(date_fmt)
        files = filter(lambda vv: r.match(vv) is not None, files)

    if full_path: return ['/'.join([path_name, f]) for f in files]
    return files


def all_folders(path_name, keyword='', has_date=False, date_fmt=DATE_FMT):
    """
    Search all folders with criteria

    Args:
        path_name: full path name
        keyword: keyword to search
        has_date: whether has date in file name (default False)
        date_fmt: date format to check for has_date parameter

    Returns:
        list: all folder names fulfilled criteria
    """
    if not os.path.exists(path=path_name): return []

    if keyword:
        to_find = (('*%s*' % keyword) if keyword else '*') + '.*'
        files = [f for f in glob.iglob('/'.join([path_name, to_find]))]
        files = [
            f.replace('\\', '/').split('/')[-1] for f in files if f[0] != '~'
        ]

    else:
        files = [
            f for f in os.listdir(path=path_name)
            if os.path.isdir('/'.join([path_name, f])) and (f[0] != '~')
        ]

    if keyword != '':
        keyword = keyword.lower()
        files = filter(lambda vv: keyword in vv.lower(), files)

    if has_date:
        r = re.compile(date_fmt)
        files = filter(lambda vv: r.match(vv) is not None, files)

    return ['/'.join([path_name, f]) for f in files]


def latest_file(path_name, keyword='', ext='', debug=False):
    """
    Latest modified file in folder

    Args:
        path_name: full path name
        keyword: keyword to search
        ext: file extension
        debug: print out debug message if not found

    Returns:
        str: latest file name
    """
    files = all_files(path_name=path_name, keyword=keyword, ext=ext, full_path=True)

    if len(files) == 0:
        if debug: print('File is not found in folder: %s' % path_name)
        return ''

    modified_time = [os.path.getmtime(f) for f in files]
    files = [f for (dt, f) in sorted(zip(modified_time, files))]

    return files[-1]


def file_modified_time(file_name):

    return pd.to_datetime(time.ctime(os.path.getmtime(filename=file_name)))


if __name__ == '__main__':
    """
    CommandLine:
        python -m xone.files all
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
