import cProfile
import io
import pstats


def profile(func):
    """
    Decorator to profile functions with cProfile

    Args:
        func: python function

    Returns:
        profile report

    References:
        https://osf.io/upav8/
    """
    def inner(*args, **kwargs):

        pr = cProfile.Profile()
        pr.enable()
        res = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()
        print(s.getvalue())

        return res
    return inner
