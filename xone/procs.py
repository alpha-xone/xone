import sys
import queue
import pytest

from multiprocessing import Process, cpu_count
from itertools import product

try:
    import win32process
    import win32api
except ImportError:
    pytest.skip()
    sys.exit(1)


def run(func, keys, max_procs=None, show_proc=False, affinity=None, **kwargs):
    """
    Provide interface for multiprocessing

    Args:
        func: callable functions
        keys: keys in kwargs that want to use process
        max_procs: max number of processes
        show_proc: whether to show process
        affinity: CPU affinity
        **kwargs: kwargs for func
    """
    if max_procs is None: max_procs = cpu_count()
    kw_arr = saturate_kwargs(keys=keys, **kwargs)
    if len(kw_arr) == 0: return

    if isinstance(affinity, int):
        win32process.SetProcessAffinityMask(win32api.GetCurrentProcess(), affinity)

    task_queue = queue.Queue()
    while len(kw_arr) > 0:
        for _ in range(max_procs):
            if len(kw_arr) == 0: break
            kw = kw_arr.pop(0)
            p = Process(target=func, kwargs=kw)
            p.start()
            sys.stdout.flush()
            task_queue.put(p)
            if show_proc:
                signature = ', '.join([f'{k}={v}' for k, v in kw.items()])
                print(f'[{func.__name__}] ({signature})')
        while not task_queue.empty():
            p = task_queue.get()
            p.join()


def saturate_kwargs(keys, **kwargs):
    """
    Saturate all combinations of kwargs

    Args:
        keys: keys in kwargs that want to use process
        **kwargs: kwargs for func
    """
    # Validate if keys are in kwargs and if they are iterable
    if isinstance(keys, str): keys = [keys]
    keys = [k for k in keys if k in kwargs and hasattr(kwargs.get(k, None), '__iter__')]
    if len(keys) == 0: return []

    # Saturate coordinates of kwargs
    kw_corr = list(product(*(range(len(kwargs[k])) for k in keys)))

    # Append all possible values
    kw_arr = []
    for corr in kw_corr: kw_arr.append(
        dict(zip(keys, [kwargs[keys[i]][corr[i]] for i in range(len(keys))]))
    )

    # All combinations of kwargs of inputs
    for k in keys: kwargs.pop(k, None)
    kw_arr = [{**k, **kwargs} for k in kw_arr]

    return kw_arr
