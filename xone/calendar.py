import pandas as pd

import sys
from pandas.tseries import holiday


class USTradingCalendar(holiday.AbstractHolidayCalendar):

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


def trading_dates(start, end, calendar='US'):
    """
    Trading dates for given exchange

    Args:
        start: start date
        end: end date
        calendar: exchange as string

    Returns:
        pd.DatetimeIndex: datetime index

    Examples:
        >>> bus_dates = ['2018-12-24', '2018-12-26', '2018-12-27']
        >>> trd_dates = trading_dates(start='2018-12-23', end='2018-12-27')
        >>> assert len(trd_dates) == len(bus_dates)
        >>> assert pd.Series(trd_dates == pd.DatetimeIndex(bus_dates)).all()
    """
    kw = dict(start=pd.Timestamp(start, tz='UTC').date(), end=pd.Timestamp(end, tz='UTC').date())
    us_cal = getattr(sys.modules[__name__], f'{calendar}TradingCalendar')()
    return pd.DatetimeIndex(freq='B', **kw).drop(us_cal.holidays(**kw))
