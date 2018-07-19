import matplotlib.pyplot as plt

from xone import utils


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
        >>> plot_multi(data=data, cols=['a', 'b'], plot_kw=[dict(style='.-'), dict()])
    """
    from pandas import plotting

    if cols is None: cols = data.columns
    if plot_kw is None: plot_kw = [dict(), dict()]
    if len(cols) == 0: return
    num_colors = len(utils.flatten(cols))

    # Get default color style from pandas
    colors = getattr(getattr(plotting, '_style'), '_get_standard_colors')(num_colors=num_colors)
    if color_map is None: color_map = dict()

    fig = plt.figure()
    ax, lines, labels, c_idx = None, [], [], 0
    for n in range(0, len(cols)):
        if isinstance(cols[n], (list, tuple)):
            ylabel = ' / '.join(cols[n])
            color = [
                color_map.get(cols[n][_ - c_idx], colors[_ % len(colors)])
                for _ in range(c_idx, c_idx + len(cols[n]))
            ]
            c_idx += len(cols[n])
        else:
            ylabel = cols[n]
            color = color_map.get(cols[n], colors[c_idx % len(colors)])
            c_idx += 1

        if ax is None:
            # First y-axes
            ax = data.loc[:, cols[n]].plot(
                label=cols[n], color=color, legend=False, zorder=n, **plot_kw[0], **kwargs
            )
            ax.set_ylabel(ylabel=ylabel)
            line, label = ax.get_legend_handles_labels()
            ax.spines['left'].set_edgecolor('#D5C4A1')
            ax.spines['left'].set_alpha(.5)

        else:
            # Multiple y-axes
            ax_new = ax.twinx()
            ax_new.spines['right'].set_position(('axes', 1 + spacing * (n - 1)))
            data.loc[:, cols[n]].plot(
                ax=ax_new, label=cols[n], color=color, legend=False, zorder=n, **plot_kw[n]
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
        >>> plot_h(data=data, cols=['a', 'b'], wspace=.2, plot_kw=[dict(style='.-'), dict()])
    """
    if plot_kw is None: plot_kw = [dict()] * len(cols)

    fig, axes = plt.subplots(nrows=1, ncols=len(cols), **kwargs)
    plt.subplots_adjust(wspace=wspace)
    for n in range(len(cols)):
        data.loc[:, cols[n]].plot(ax=axes[n], **plot_kw[n])

    return axes
