# x1
|                |                                                                                                                                                 |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Latest Release | [![PyPI version](https://img.shields.io/pypi/v/xone.svg)](https://badge.fury.io/py/xone)                                               |
|                | [![PyPI version](https://img.shields.io/pypi/pyversions/xone.svg)](https://badge.fury.io/py/xone)                                               |
| Build          | [![Travis CI](https://img.shields.io/travis/alpha-xone/xone/master.svg?label=Travis%20CI)](https://travis-ci.com/alpha-xone/xone)               |
| Coverage       | [![codecov](https://codecov.io/gh/alpha-xone/xone/branch/master/graph/badge.svg)](https://codecov.io/gh/alpha-xone/xone)                        |
| Docs           | [![Documentation Status](https://readthedocs.org/projects/xone/badge/?version=latest)](https://xone.readthedocs.io/en/latest)                   |
| Quality        | [![CodeFactor](https://www.codefactor.io/repository/github/alpha-xone/xone/badge)](https://www.codefactor.io/repository/github/alpha-xone/xone) |
| License        | [![GitHub license](https://img.shields.io/github/license/alpha-xone/xone.svg)](https://github.com/alpha-xone/xone/blob/master/LICENSE)          |

Frequently used functions for financial data analysis

## Installation

```
pip install xone
```

## Utilities



## Files

Automatic check and create path and save files:

```python
In[1]: import pandas as pd
In[2]: from xone import files

In[3]: DATA_PATH = '/data/Bloomberg'

In[4]: ticker = 'BHP AU Equity'
In[5]: data_file = f'{DATA_PATH}/{ticker.split()[-1]}/{ticker}/2018-09-10.parq'
In[6]: sample = pd.DataFrame(
  ...:     data=dict(
  ...:         price=[31.08, 31.10, 31.11, 31.07, 31.04, 31.04],
  ...:         volume=[10166, 69981, 14343, 10096, 11506, 9718],
  ...:     ),
  ...:     index=pd.DatetimeIndex(
  ...:         start='2018-09-10T10:10:00', periods=6, freq='min'
  ...:     ).tz_localize('Australia/Sydney'),
  ...: )

In[7]: files.create_folder(data_file, is_file=True)
In[8]: sample.to_parquet(data_file)
```

## Logs
