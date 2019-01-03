import pandas as pd

pd.options.display.float_format = lambda vv: f'{{:,.{2}f}}'.format(vv)
