import pandas as pd

from xone import utils
from matplotlib import pyplot as plt


def plot_ts(
        data: (pd.Series, pd.DataFrame), fld='close',
        tz=None, vline=None, **kwargs
):
    """
    Time series data plots

    Args:
        data: data in pd.Series or pd.DataFrame
        fld: which field to plot for multi-index
        tz: tz info - applied to merged time series data
        vline: kwargs for verticle lines

    Returns:
        matplotlib plot
    """
    to_plot = data
    if isinstance(data, pd.DataFrame):
        if isinstance(data.columns, pd.MultiIndex) and \
                (fld in data.columns.get_level_values(1)):
            to_plot = data.xs(fld, axis=1, level=1)
        elif fld in data.columns:
            to_plot = data[fld]

    if isinstance(to_plot, pd.Series):
        pl_val = pd.Series(data.values, name=data.name)
    else:
        pl_val = pd.DataFrame(data.values, columns=data.columns)

    # Proper raw datetime index
    idx = data.index
    if isinstance(idx, pd.MultiIndex):
        for n in range(len(idx.levels))[::-1]:
            sidx = idx.get_level_values(n)
            if isinstance(sidx, pd.DatetimeIndex):
                idx = sidx
                break

    # Standardize timezone
    assert isinstance(idx, pd.DatetimeIndex), idx
    if tz is not None: idx = idx.tz_convert(tz)

    raw_idx = idx.to_series(keep_tz=True).reset_index(drop=True)
    dt_idx = pd.Series(raw_idx.dt.date.unique())
    diff = raw_idx.diff()

    is_day = diff.min() >= pd.Timedelta(days=1)
    num_days = dt_idx.size

    if num_days >= kwargs.pop('month_min_cnt', 90):
        # Monthly ticks
        xticks = raw_idx.loc[raw_idx.dt.month.diff().ne(0)]
    elif num_days >= kwargs.pop('week_min_cnt', 15):
        # Weekly ticks
        xticks = raw_idx.loc[raw_idx.dt.weekofyear.diff().ne(0)]
    elif is_day:
        xticks = raw_idx.index
    else:
        # Daily ticks - to be improved
        xticks = raw_idx.loc[raw_idx.dt.day.diff().ne(0)]

    # Plot
    ax = pl_val.plot(**kwargs)
    plt.xticks(ticks=xticks.index.tolist(), labels=xticks.dt.date, rotation=30)

    if not isinstance(vline, dict): vline = dict()
    vline['color'] = vline.get('color', '#FFFFFF')
    vline['linestyle'] = vline.get('linestyle', '-')
    vline['linewidth'] = vline.get('linewidth', 1)
    for xc in xticks: plt.axvline(x=xc, **vline)

    return ax


def plot_multi(data, cols=None, spacing=.06, color_map=None, plot_kw=None, **kwargs):
    """
    Plot data with multiple scaels together

    Args:
        data: DataFrame of data
        cols: columns to be plotted
        spacing: spacing between legends
        color_map: customized colors in map
        plot_kw: kwargs for each plot
        **kwargs: kwargs for the first plot

    Returns:
        ax for plot

    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>>
        >>> idx = range(5)
        >>> data = pd.DataFrame(dict(a=np.exp(idx), b=idx), index=idx)
        >>> # plot_multi(data=data, cols=['a', 'b'], plot_kw=[dict(style='.-'), dict()])
    """
    from pandas import plotting

    if cols is None: cols = data.columns
    if plot_kw is None: plot_kw = [{}] * len(cols)
    if len(cols) == 0: return
    num_colors = len(utils.flatten(cols))

    # Get default color style from pandas
    if hasattr(plotting, '_matplotlib'):
        style = getattr(plotting, '_matplotlib').style
    else:
        style = getattr(plotting, '_style')
    colors = getattr(style, '_get_standard_colors')(num_colors=num_colors)
    if color_map is None: color_map = dict()

    fig = plt.figure()
    ax, lines, labels, c_idx = None, [], [], 0
    for n, col in enumerate(cols):
        if isinstance(col, (list, tuple)):
            ylabel = ' / '.join(cols[n])
            color = [
                color_map.get(cols[n][_ - c_idx], colors[_ % len(colors)])
                for _ in range(c_idx, c_idx + len(cols[n]))
            ]
            c_idx += len(col)
        else:
            ylabel = col
            color = color_map.get(col, colors[c_idx % len(colors)])
            c_idx += 1
        if 'color' in plot_kw[n]: color = plot_kw[n].pop('color')

        if ax is None:
            # First y-axes
            legend = plot_kw[0].pop('legend', kwargs.pop('legend', False))
            ax = data.loc[:, col].plot(
                label=col, color=color, legend=legend, zorder=n, **plot_kw[0], **kwargs
            )
            ax.set_ylabel(ylabel=ylabel)
            line, label = ax.get_legend_handles_labels()
            ax.spines['left'].set_edgecolor('#D5C4A1')
            ax.spines['left'].set_alpha(.5)

        else:
            # Multiple y-axes
            legend = plot_kw[n].pop('legend', False)
            ax_new = ax.twinx()
            ax_new.spines['right'].set_position(('axes', 1 + spacing * (n - 1)))
            data.loc[:, col].plot(
                ax=ax_new, label=col, color=color, legend=legend, zorder=n, **plot_kw[n]
            )
            ax_new.set_ylabel(ylabel=ylabel)
            line, label = ax_new.get_legend_handles_labels()
            ax_new.spines['right'].set_edgecolor('#D5C4A1')
            ax_new.spines['right'].set_alpha(.5)
            ax_new.grid(False)

        # Proper legend position
        lines += line
        labels += label

    fig.legend(lines, labels, loc=8, prop=dict(), ncol=num_colors).set_zorder(len(cols))
    ax.set_xlabel(' \n ')

    return ax


def plot_h(data, cols, wspace=.1, plot_kw=None, **kwargs):
    """
    Plot horizontally

    Args:
        data: DataFrame of data
        cols: columns to be plotted
        wspace: spacing between plots
        plot_kw: kwargs for each plot
        **kwargs: kwargs for the whole plot

    Returns:
        axes for plots

    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>>
        >>> idx = range(5)
        >>> data = pd.DataFrame(dict(a=np.exp(idx), b=idx), index=idx)
        >>> # plot_h(data=data, cols=['a', 'b'], wspace=.2, plot_kw=[dict(style='.-'), dict()])
    """
    if plot_kw is None: plot_kw = [dict()] * len(cols)

    _, axes = plt.subplots(nrows=1, ncols=len(cols), **kwargs)
    plt.subplots_adjust(wspace=wspace)
    for n, col in enumerate(cols):
        data.loc[:, col].plot(ax=axes[n], **plot_kw[n])

    return axes


def add_lines(
        axes: plt.Axes, xs=None, ys=None, colors=None, **kwargs
) -> plt.Axes:
    """
    Add horizontal or vertical lines to charts

    Args:
        axes: axes to add
        xs: Xs
        ys: Ys
        colors: list of colors (Xs first then Ys if both given
        **kwargs: kwargs to pass

    Returns:
        plt.Axes
    """
    idx = 0
    if colors is None: colors = ['darkgreen', 'darkorange', 'darkred']

    if xs is not None:
        if isinstance(xs, str): xs = [xs]
        if not hasattr(xs, '__iter__'): xs = [xs]
        ylim = axes.get_ylim()
        for x in xs:
            axes.vlines(
                x=x, ymin=ylim[0], ymax=ylim[1],
                colors=colors[idx % len(colors)], **kwargs
            )
            idx = idx + 1
        axes.set_ylim(ymin=ylim[0], ymax=ylim[1])

    if ys is not None:
        if isinstance(ys, str): ys = [ys]
        if not hasattr(ys, '__iter__'): ys = [ys]
        xlim = axes.get_xlim()
        for y in ys:
            axes.hlines(
                y=y, xmin=xlim[0], xmax=xlim[1],
                colors=colors[idx % len(colors)], **kwargs
            )
            idx = idx + 1
        axes.set_xlim(xmin=xlim[0], xmax=xlim[1])

    return axes
