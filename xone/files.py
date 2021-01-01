import os
import time

from pathlib import Path

# Default datetime format:
#   ISO 8601 format date/time
#   e.g. 1972-01-20T10:21:36Z (“T” and “Z” optional)
DATE_FMT = '{dt:ti}'


def exists(path) -> bool:
    """
    Check path or file exists (use os.path.exists)

    Args:
        path: path or file

    Examples
        >>> exists(f'{abspath(__file__, 1)}/xone/tests/files/test_1.json')
        True
        >>> exists(f'{abspath(__file__)}/tests/files/notfound.yml')
        False
    """
    return os.path.exists(path=path)


def abspath(cur_file, parent=0) -> Path:
    """
    Absolute path

    Args:
        cur_file: __file__ or file or path str
        parent: level of parent to look for

    Returns:
        str
    """
    p = Path(cur_file)
    cur_path = p.parent if p.is_file() else p
    if parent == 0: return cur_path
    return abspath(cur_file=cur_path.parent, parent=parent - 1)


def create_folder(path_name: str, is_file=False):
    """
    Make folder as well as all parent folders if not exists

    Args:
        path_name: full path name
        is_file: whether input is name of file
    """
    p = Path(path_name).parent if is_file else Path(path_name)
    p.mkdir(parents=True, exist_ok=True)


def all_files(
        path_name, keyword='', ext='', full_path=True,
        has_date=False, date_fmt=DATE_FMT
) -> list:
    """
    Search all files with criteria
    Returned list will be sorted by last modified

    Args:
        path_name: full path name
        keyword: keyword to search
        ext: file extensions, split by ','
        full_path: whether return full path (default True)
        has_date: whether has date in file name (default False)
        date_fmt: date format to check for has_date parameter

    Returns:
        list: all file names with criteria fulfilled

    Examples:
        >>> test_folder = abspath(__file__) / 'tests/files'
        >>> all_files(test_folder, keyword='test', full_path=False)
        ['test_1.json', 'test_2.json']
        >>> all_files(test_folder, has_date=True, full_path=False)
        ['dates_2019-01-01.yml', 'dates_2019-01-02.yml']
    """
    p = Path(path_name)
    if not p.is_dir(): return []

    keyword = f'*{keyword}*' if keyword else '*'
    keyword += f'.{ext}' if ext else '.*'
    files = list(filter(lambda v: v.name[0] != '~', p.glob(keyword)))

    if has_date: files = filter_by_dates(files, date_fmt=date_fmt)
    return files if full_path else [f.name for f in files]


def all_folders(
        path_name, keyword='', has_date=False, date_fmt=DATE_FMT
) -> list:
    """
    Search all folders with criteria
    Returned list will be sorted by last modified

    Args:
        path_name: full path name
        keyword: keyword to search
        has_date: whether has date in file name (default False)
        date_fmt: date format to check for has_date parameter

    Returns:
        list: all folder names fulfilled criteria

    Examples:
        >>> target_folder = abspath(__file__) / 'tests/folders'
        >>> for fld in sorted(all_folders(target_folder, keyword='test')):
        ...     print(fld.name)
        test_1
        test_2
        >>> for fld in sorted(all_folders(target_folder, has_date=True)):
        ...     print(fld.name)
        dates_2019-01-01
        dates_2019-01-02_labeled
        dates_2019-01-03
    """
    p = Path(path_name)
    if not p.is_dir(): return []

    folders = list(filter(
        lambda v: v.is_dir() and v.name[0] != '~',
        p.glob(f'*{keyword}*' if keyword else '*'),
    ))

    if has_date: folders = filter_by_dates(folders, date_fmt=date_fmt)
    return folders


def sort_by_modified(files_or_folders: list) -> list:
    """
    Sort files or folders by modified time

    Args:
        files_or_folders: list of files or folders

    Returns:
        list
    """
    return sorted(files_or_folders, key=os.path.getmtime, reverse=True)


def filter_by_dates(files_or_folders: list, date_fmt=DATE_FMT) -> list:
    """
    Filter files or dates by date patterns

    Args:
        files_or_folders: list of files or folders
        date_fmt: date format

    Returns:
        list

    Examples:
        >>> filter_by_dates([
        ...     't1/dts_2019-01-01', 't2/dts_2019-01-02', 't3/nodts_2019-01'
        ... ])
        ['t1/dts_2019-01-01', 't2/dts_2019-01-02']
    """
    from parse import compile

    p = compile(date_fmt)
    return list(filter(lambda _: p.search(Path(_).name), files_or_folders))


def latest_file(path_name, keyword='', ext='', **kwargs) -> str:
    """
    Latest modified file in folder

    Args:
        path_name: full path name
        keyword: keyword to search
        ext: file extension

    Returns:
        str: latest file name

    Examples:
        >>> target_folder = abspath(__file__) / 'tests/folders'
        >>> latest_file(target_folder, keyword='test', ext='yml').split('/')[-1]
        'test_2.yml'
        >>> latest_file(target_folder / 'notfound')
        ''
    """
    files = sort_by_modified(
        all_files(path_name=path_name, keyword=keyword, ext=ext, full_path=True)
    )

    if not files:
        from xone import logs

        logger = logs.get_logger(latest_file, level=kwargs.pop('log', 'warning'))
        logger.debug(f'file is not found in folder: {path_name}')
        return ''

    return str(files[0]).replace('\\', '/')


def file_modified_time(file_name):
    """
    File modified time in python

    Args:
        file_name: file name

    Returns:
        pd.Timestamp
    """
    import pandas as pd

    return pd.Timestamp(pd.to_datetime(time.ctime(os.path.getmtime(file_name))))


if __name__ == '__main__':

    print(abspath(__file__) / 'tests/files')
