# x1

[![PyPI version](https://badge.fury.io/py/xone.svg)](https://badge.fury.io/py/xone)
[![Documentation Status](https://readthedocs.org/projects/xone/badge/?version=latest)](https://xone.readthedocs.io/en/latest)

Frequently used functions for financial data analysis

Installation:
=============

From pypi:
----------

```
pip install xone
```

From github:
--------------------------

```
pip install git+https://github.com/alpha-xone/xone.git
```

Description:
------------

- Common Utilities
- Files
- Calendar
- Logs

Common Utilities
----------------

Files
-----

Automatic check and create path and save files:

```python
import pandas as pd
from xone import files

DATA_PATH = '/data/Bloomberg'

ticker = 'BHP AU Equity'
data_file = f'{DATA_PATH}/{ticker.split()[-1]}/{ticker}/2018-09-10.parq'
sample = pd.DataFrame(
    data=dict(
        price=[31.08, 31.10, 31.11, 31.07, 31.04, 31.04],
        volume=[10166, 69981, 14343, 10096, 11506, 9718],
    ),
    index=pd.DatetimeIndex(
        start='2018-09-10T10:10:00', periods=6, freq='min'
    ).tz_localize('Australia/Sydney'),
)

files.create_folder(data_file, is_file=True)
sample.to_parquet(data_file)
```

Calendar
--------

Logs
----
