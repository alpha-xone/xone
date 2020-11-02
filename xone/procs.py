import sys
import queue

from multiprocessing import Process, cpu_count
from itertools import product

from tqdm import tqdm
from xone import logs


def run(func, keys, max_procs=None, affinity=None, **kwargs):
    """
    Provide interface for multiprocessing

    Args:
        func: callable functions
        keys: keys in kwargs that want to use process
        max_procs: max number of processes
        affinity: CPU affinity
        **kwargs: kwargs for func
    """
    logger = logs.get_logger(run, level=kwargs.get('log', 'info'))

    if max_procs is None: max_procs = cpu_count()
    kw_arr = saturate_kwargs(keys=keys, **kwargs)
    if len(kw_arr) == 0: return

    if isinstance(affinity, int):
        try:
            import win32process
            import win32api

            win32process.SetProcessAffinityMask(
                win32api.GetCurrentProcess(), affinity
            )

        except Exception as e:
            logger.error(str(e))

    task_queue = queue.Queue()
    with tqdm(total=len(kw_arr)) as bar:
        while len(kw_arr) > 0:
            for _ in range(max_procs):
                if len(kw_arr) == 0: break
                kw = kw_arr.pop(0)
                bar.update()
                p = Process(target=func, kwargs=kw)
                p.start()
                sys.stdout.flush()
                task_queue.put(p)
            while not task_queue.empty():
                p = task_queue.get()
                p.join()


def saturate_kwargs(keys, **kwargs) -> list:
    """
    Saturate all combinations of kwargs

    Args:
        keys: keys in kwargs that want to use process
        **kwargs: kwargs for func

    Returns:
        list: all combinations of kwargs

    Examples:
        >>> saturate_kwargs('k1', k1=range(2), k2=range(2))
        [{'k1': 0, 'k2': range(0, 2)}, {'k1': 1, 'k2': range(0, 2)}]
        >>> kw = saturate_kwargs(
        ...     keys=['k1', 'k2'], k1=range(3), k2=range(2), k3=range(4)
        ... )
        >>> kw[:2]
        [{'k1': 0, 'k2': 0, 'k3': range(0, 4)}, {'k1': 0, 'k2': 1, 'k3': range(0, 4)}]
        >>> kw[2:4]
        [{'k1': 1, 'k2': 0, 'k3': range(0, 4)}, {'k1': 1, 'k2': 1, 'k3': range(0, 4)}]
        >>> kw[4:6]
        [{'k1': 2, 'k2': 0, 'k3': range(0, 4)}, {'k1': 2, 'k2': 1, 'k3': range(0, 4)}]
        >>> saturate_kwargs('k', k1=range(5), k2=range(2))
        []
    """
    # Validate if keys are in kwargs and if they are iterable
    if isinstance(keys, str): keys = [keys]
    keys = list(filter(
        lambda _: (_ in kwargs) and hasattr(kwargs.get(_, None), '__iter__'),
        keys
    ))
    if len(keys) == 0: return []

    # Saturate coordinates of kwargs
    kw_corr = product(*(range(len(kwargs[k])) for k in keys))

    # Append all possible values
    kw_arr = []
    for corr in kw_corr:
        kw_arr.append(
            dict(zip(
                keys, [kwargs[keys[i]][corr[i]] for i in range(len(keys))]
            ))
        )

    # All combinations of kwargs of inputs
    for k in keys: kwargs.pop(k, None)
    kw_arr = [{**k, **kwargs} for k in kw_arr]

    return kw_arr
