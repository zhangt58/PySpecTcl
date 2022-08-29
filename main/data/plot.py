#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Visualize a spectrum.
"""

from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt


def get_axes_grid(nrows, ncols, w, h, **kws):
    """Get the axes grid.
    """
    gs = GridSpec(nrows, ncols, width_ratios=[w, w * 0.2][:nrows], height_ratios=[h, h * 0.2][:ncols],
                  wspace=kws.pop('wspace', 0.04),
                  hspace=kws.pop('hspace', 0.04))
    fig = plt.figure(figsize=kws.pop('figsize', (8, 6)))
    # axes for image
    ax0 = fig.add_subplot(gs[0])
    if nrows == 2 and ncols == 2:
        # hide xticks of ax0
        ax0.get_xaxis().set_visible(False)
        # axes for y profile
        ax1 = fig.add_subplot(gs[1], sharey=ax0)
        # hide yticks
        ax1.get_yaxis().set_visible(False)
        # axes for x profile
        ax2 = fig.add_subplot(gs[2], sharex=ax0)
        return fig, [ax0, ax1, ax2]
    else:
        return fig, ax0


def plot_image(sp, show_profile=True, show_colorbar=True,
               fillna=False, mapped=True, **kws):
    """Visualize a 2D spectrum.

    Parameters
    ----------
    sp : Spectrum
        A 2D Spectrum object.
    show_colorbar : bool
        If show colorbar or not.
    show_profile : bool
        If show x,y profile or not.
    fillna : bool
        If fill empty count as nan, otherwise fill with zero.
    mapped : bool
        If show data in mapped coordinate (world), otherwise show in channel coordinate.

    Keyword Arguments
    -----------------
    cmap : str
        Colormap of the image, default is 'viridis'.
    figsize : tuple
        Figure width and height size in inch, defautl is (8, 6).
    aspect : str, float
        Image aspect ratio, default is 'auto', could be 'equal', or a float number.
    wspace, hspace : float
        Grid space in w and h.

    Returns
    -------
    fig, ax_list: Figure, List[Axes]
        Figure and axes list (image, lines of x,yprofiles).
    """
    df = sp.get_data(map=False)
    xmin, xmax = df.x.min(), df.x.max() + 1
    ymin, ymax = df.y.min(), df.y.max() + 1
    fn_x, fn_y = sp._axes_map_fn[0], sp._axes_map_fn[1]
    xmin_w, xmax_w = fn_x(xmin), fn_x(xmax)
    ymin_w, ymax_w = fn_y(ymin), fn_y(ymax)
    xrange = list(range(xmin, xmax))
    yrange = list(range(ymin, ymax))
    new_idx = [(ix, iy) for iy in yrange for ix in xrange]
    if fillna:
        df1 = df.set_index(['x', 'y']).reindex(new_idx, fill_value=np.nan)
    else:
        df1 = df.set_index(['x', 'y']).reindex(new_idx, fill_value=0)
    c_arr = df1.to_numpy().reshape(len(yrange), len(xrange))

    # axes grid
    h, w = c_arr.shape
    if show_profile:
        fig, ax = get_axes_grid(2, 2, w, h, figsize=kws.pop('figsize', (8, 6)), wspace=kws.pop('wspace', 0.01), hspace=kws.pop('hspace', 0.04))
        [ax_im, ax_yprof, ax_xprof] = ax
    else:
        fig, ax_im = get_axes_grid(1, 1, w, h, figsize=kws.pop('figsize', (8, 6)))

    # image
    im = ax_im.imshow(c_arr, cmap=kws.pop('cmap', 'jet'), origin='lower', aspect=kws.get('aspect', 'auto'))

    # colorbar
    if show_colorbar:
        cax_im = make_axes_locatable(ax_im).append_axes("top", size="3%", pad="0.8%")
        cb_im = fig.colorbar(im, cax=cax_im, orientation="horizontal")
        cax_im.xaxis.set_ticks_position("top")
        cax_im.tick_params(labelsize=8)

    if mapped: # show in world coordinate
        df = sp.get_data(True).rename(columns={i: j for i, j in zip(sp.parameters, ('x', 'y'))})
        xmin, xmax, ymin, ymax = xmin_w, xmax_w, ymin_w, ymax_w
        xlbl, ylbl = sp.parameters
    else: # channel coordinate
        xlbl, ylbl = 'x', 'y'

    # set image extent
    im.set_extent([xmin, xmax, ymin, ymax])

    # x,y profile lines
    if show_profile:
        xprof = df.groupby('x')['count'].sum().to_frame().reset_index()
        yprof = df.groupby('y')['count'].sum().to_frame().reset_index()
        xline = xprof.plot(x='x', y='count', ax=ax_xprof, legend=False,
                           ds='steps', c='b', xlim=[xmin, xmax],
                           xlabel=xlbl)
        yline = yprof.plot(x='count', y='y', ax=ax_yprof, legend=False,
                           ds='steps', c='r', ylim=[ymin, ymax])

        # align grid
        pos = [i.get_position() for i in ax]
        if show_colorbar:
            fac = 0.962
        else:
            fac = 1.0
        ax[1].set_position([pos[1].x0, pos[0].y0, pos[1].width, pos[0].height * fac])
        ax[2].set_position([pos[0].x0, pos[2].y0, pos[0].width, pos[2].height])

    # adjust xyprofile xylabels
    ax_xprof.yaxis.set_ticks_position("right")
    ax_yprof.xaxis.set_ticks_position("top")
    ax_yprof.set_xlabel('')
    ax_yprof.annotate("count", (0.82, 0.165), fontsize=10, xycoords='figure fraction',
                   bbox={'boxstyle': 'round,pad=0.25','fc':'0.8','ec':'0.5','lw':0.5,'alpha':0.8})

    # set ylabel
    ax_im.set_ylabel(ylbl)

    # set title
    ax_im.annotate(sp.name, (0.01, 0.95), fontsize=14, xycoords='figure fraction',
                   bbox={'boxstyle': 'round,pad=0.25','fc':'0.85','ec':'0.5','lw':0.5,'alpha':0.8})
    #
    return fig, (ax_im, ax_xprof, ax_yprof)
