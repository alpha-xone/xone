import pandas as pd

import sys
from pandas.tseries import holiday


class USTradingCalendar(holiday.AbstractHolidayCalendar):

    # noinspection PyTypeChecker
    rules = [
        holiday.Holiday('NewYearsDay', month=1, day=1, observance=holiday.nearest_workday),
        holiday.USMartinLutherKingJr,
        holiday.USPresidentsDay,
        holiday.GoodFriday,
        holiday.USMemorialDay,
        holiday.Holiday('USIndependenceDay', month=7, day=4, observance=holiday.nearest_workday),
        holiday.USLaborDay,
        holiday.USThanksgivingDay,
        holiday.Holiday('Christmas', month=12, day=25, observance=holiday.nearest_workday)
    ]


def trading_dates(start, end, cal=None, **kwargs):
    """
    Trading dates for given exchange

    Args:
        start: start date
        end: end date
        cal: exchange as string

    Returns:
        pd.DatetimeIndex: datetime index

    Examples:
        >>> b_dates = ['2018-12-24', '2018-12-26', '2018-12-27']
        >>> t_dates = trading_dates(start='2018-12-23', end='2018-12-27', cal='US')
        >>> assert len(t_dates) == len(b_dates)
        >>> assert pd.Series(t_dates == pd.DatetimeIndex(b_dates)).all()
        >>> bd_world = ['2020-12-24', '2020-12-25', '2020-12-28']
        >>> td_world = trading_dates(start='2020-12-24', end='2020-12-28', cal=None)
        >>> assert len(bd_world) == len(td_world)
    """
    def conv_dt(dt): return pd.Timestamp(dt, tz=kwargs.get('tz', 'UTC')).date()

    kw = dict(start=conv_dt(start), end=conv_dt(end))
    bus_dates = pd.bdate_range(**kw)
    if isinstance(cal, str):
        use_cal = getattr(sys.modules[__name__], f'{cal}TradingCalendar')()
        return bus_dates.drop(use_cal.holidays(**kw))

    return bus_dates
