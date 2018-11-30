x1
==

============== ======================
Latest Release |pypi|
\              |version|
Build          |travis|
Coverage       |codecov|
Docs           |docs|
Quality        |codeFactor|
\              |codacy|
License        |license|
============== ======================

Frequently used functions for financial data analysis

Installation
============

.. code-block:: console

   pip install xone

Tutorial
========

Utilities
---------
.. code:: python

    In[1]: from xone import utils

Convert anything to list.

-  If the input is clean, use ``tolist()`` directly. Some functions requires
   ``list`` as input, ``tolist()`` is to standardize all inputs for them.

.. code:: python

    In[2]: ticker = 'BHP AU'
    In[3]: list_of_tickers = tolist(ticker)
    In[4]: list_of_tickers

.. code:: python

    Out[4]: ['BHP AU']

    In[5]: raw_price = [31.08, 31.10, 31.11, 31.07, 31.04, 31.04]
    In[6]: price = utils.tolist(raw_price)
    In[7]: price

    Out[7]: [31.08, 31.10, 31.11, 31.07, 31.04, 31.04]

-  If the input is list of tuples / lists / any weird combination, use ``flatten()``:

.. code:: python

    In[8]: raw_volume = [(10166, 69981), [14343, 10096], 11506, 9718]
    In[9]: volume = utils.flatten(raw_volume)
    In[10]: volume

    Out[10]: [10166, 69981, 14343, 10096, 11506, 9718]

Order preserving DataFrame construction from list of ``dict``.

Prior to Python 3.7, ``dict`` is not ordered like ``OrderedDict``.
Passing ``dict`` directly to DataFrame constructor will make the columns sorted by alphabets:

.. code:: python

    In[11]: import pandas as pd

    In[12]: data_list = [
                dict(sid=1, symbol='1 HK', price=88.8),
                dict(sid=700, symbol='700 HK', price=350.),
            ]
    In[13]: pd.DataFrame(data_list)

    Out[13]:
       price  sid  symbol
    0  88.80    1    1 HK
    1 350.00  700  700 HK

``to_frame`` makes sure the order of inputs will be kept:

.. code:: python

    In[14]: utils.to_frame(data_list)

    Out[14]:
       sid  symbol  price
    0    1    1 HK  88.80
    1  700  700 HK 350.00

Files
-----

.. code:: python

    In[15]: from xone import files

Automatic check and create path and save files:

.. code:: python

    In[16]: DATA_PATH = '/data/Bloomberg'
    In[17]: data_file = f'{DATA_PATH}/{ticker.split()[-1]}/{ticker}/2018-09-10.parq'

    In[18]: sample = pd.DataFrame(
                data=dict(price=price, volume=volume),
                index=pd.DatetimeIndex(
                    start='2018-09-10T10:10:00', periods=6, freq='min'
                ).tz_localize('Australia/Sydney'),
            )
    In[19]: sample

    Out[19]:
                               price  volume
    2018-09-10 10:10:00+10:00  31.08   10166
    2018-09-10 10:11:00+10:00  31.10   69981
    2018-09-10 10:12:00+10:00  31.11   14343
    2018-09-10 10:13:00+10:00  31.07   10096
    2018-09-10 10:14:00+10:00  31.04   11506
    2018-09-10 10:15:00+10:00  31.04    9718

``create_folder`` checks folder existence and create all parent folders
for the target folder.

.. code:: python

   In[20]: files.create_folder(data_file, is_file=True)
   In[21]: sample.to_parquet(data_file)

.. |pypi| image:: https://img.shields.io/pypi/v/xone.svg
    :target: https://badge.fury.io/py/xone
.. |version| image:: https://img.shields.io/pypi/pyversions/xone.svg
    :target: https://badge.fury.io/py/xone
.. |travis| image:: https://img.shields.io/travis/alpha-xone/xone/master.svg?label=Travis%20CI
    :target: https://travis-ci.com/alpha-xone/xone
    :alt: Travis CI
.. |codecov| image:: https://codecov.io/gh/alpha-xone/xone/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/alpha-xone/xone
    :alt: Codecov
.. |docs| image:: https://readthedocs.org/projects/xone/badge/?version=latest
    :target: https://xone.readthedocs.io/en/latest
.. |codefactor| image:: https://www.codefactor.io/repository/github/alpha-xone/xone/badge
   :target: https://www.codefactor.io/repository/github/alpha-xone/xone
   :alt: CodeFactor
.. |codacy| image:: https://api.codacy.com/project/badge/Grade/eb3d11949a1343d9aa4806a31f3fcc41
   :target: https://www.codacy.com/app/alpha-xone/xone
.. |license| image:: https://img.shields.io/github/license/alpha-xone/xone.svg
    :alt: GitHub license
    :target: https://github.com/alpha-xone/xone/blob/master/LICENSE
