import os
import re
import glob
import time
import pandas as pd

DATE_FMT = '\d{4}-(0?[1-9]|1[012])-(0?[1-9]|[12][0-9]|3[01])'


def create_folder(path_name, is_file=False):
    """
    Make folder as well as all parent folders if not exists
    :param path_name: full path name
    """
    assert isinstance(path_name, str)
    path_sep = path_name.replace('\\', '/').split('/')
    for i in range(1, len(path_sep) + (0 if is_file else 1)):
        cur_path = '/'.join(path_sep[:i])
        if not os.path.exists(cur_path): os.mkdir(cur_path)


def all_files(path_name, keyword='', ext='', full_path=True, has_date=False, date_fmt=DATE_FMT):
    """
    Search all files with criteria
    :param path_name: full path name
    :param keyword: keyword to search
    :param ext: file extensions, split by ','
    :param full_path: whether return full path (default True)
    :param has_date: whether has date in file name (default False)
    :return: all file names
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
    :param path_name: full path name
    :param keyword: keyword to search
    :param has_date: has date in folder name (default False)
    :return: all folder names
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
    Search latest modified file in folder
    :param debug: print out msg if not found
    :return: latest file name
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
