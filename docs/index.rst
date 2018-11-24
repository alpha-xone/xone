x1
==

Frequently used functions for financial data analysis

Installation
============

.. code-block:: console

   pip install xone

Tutorial
========

Automatic check and create path and save files:

.. code-block:: python

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
