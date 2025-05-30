import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colorbar import Colorbar
import seaborn as sns
import matplotlib.image as mpimg
import pydmr

from stages import data

root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

tablespath = os.path.join(root, 'build', 'Tables')
resultspath = os.path.join(root, 'build', 'Figs')


sym = {
    'control': 'b-',
    'drug': 'r-',
}

mark = {
    0: 'X',
    1: 'o',
    2: 'v',
    3: '^',
    4: '<',
    5: '>',
    6: 's',
    7: 'p',
    8: '*',
    9: 'x',
    10: 'd',
}
clr = {
    0: 'b',
    1: 'tab:blue',
    2: 'tab:orange',
    3: 'tab:green',
    4: 'tab:red',
    5: 'tab:purple',
    6: 'tab:brown',
    7: 'tab:pink',
    8: 'tab:gray',
    9: 'tab:olive',
    10: 'tab:cyan',
}


def _tstat_box_plots(ax):

    sig = 0.01
    file = os.path.join(tablespath, 'table_liver_univariate.csv')
    univ = pd.read_csv(file).set_index('parameter')
    univ['group'] = data.lookup_vals(univ.index.values, 'group')
    univ['cluster'] = data.lookup_vals(univ.index.values, 'cluster')
    univ['label'] = data.lookup_vals(univ.index.values, 'label')
    univ = univ.sort_values(by='cluster')
    univ = univ[univ['p-value'] < sig]
    pars = univ.index.values
    cluster = univ['cluster'].values
    lbl = univ['label'].values
    
    file = os.path.join(tablespath, 't_statistic.csv')
    tstat = pd.read_csv(file).set_index('parameter')

    vals = [tstat.loc[p,:].dropna().values for p in pars]

    linewidth=2.0
    fontsize=16
    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(linewidth)

    # box plot
    bplot = ax.boxplot(
        vals,
        whis=[2.5,97.5],
        capprops=dict(linestyle='-', linewidth=linewidth, color='black'),
        flierprops=dict(
            marker='o', markerfacecolor='white', markersize=6,
            markeredgecolor='black', markeredgewidth=linewidth,
        ),
        whiskerprops=dict(linestyle='-', linewidth=linewidth, color='black'),
        medianprops=dict(linestyle='-', linewidth=linewidth, color='black'),
        boxprops=dict(linestyle='-', linewidth=linewidth, color='black'),
        widths=0.75, # width of the boxes
        vert=True,  # vertical box alignment
        patch_artist=True,  # fill with color
        #tick_labels=lbls, # will be used to label x-ticks
    )  
    ax.set_ylim([-20,15])
    ax.set_xticks(ax.get_xticks())  # Explicitly set tick positions
    ax.set_xticklabels(labels=lbl, fontsize=fontsize, rotation=90)
    ax.set_yticks(ax.get_yticks())  # Explicitly set tick positions
    ax.set_yticklabels(labels=ax.get_yticklabels(), fontsize=fontsize)
    #ax.grid(True, linewidth=1.5, axis='y')

    # fill with colors
    #ax.patch.set_facecolor("lightgrey")
    for i, patch in enumerate(bplot['boxes']):
        if cluster[i] == 'HC':
            patch.set_facecolor('steelblue')
        elif cluster[i] == 'SQ':
            patch.set_facecolor('firebrick')
        elif cluster[i] == 'EC':
            patch.set_facecolor('tab:olive')
        elif cluster[i] == 'Blood - liver function test':
            patch.set_facecolor('forestgreen')

    # adding horizontal grid line
    ax.yaxis.grid(True)
    ax.set_ylabel('T-value', fontsize=fontsize)



def _subject_line_plot(ax, par):

    # Setup plot
    fontsize=10
    markersize=6
    linewidth=2.0
    #ax.set_title(lbl, fontsize=14, pad=10)
    #ax.set_ylabel(lbl, fontsize=fontsize)
    #ax.set_ylim(0, ylim[0])
    ax.tick_params(axis='x', labelcolor='none')
    ax.tick_params(axis='y', labelcolor='none')

    # Concatenate all data
    file = os.path.join(root, 'build', 'Data', 'all_data.dmr')
    vals = pydmr.read(file, 'pandas')['pars']

    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(linewidth)

    vals = vals[vals.parameter==par]
    data_control = vals[vals.study=='control']
    data_drug = vals[vals.study=='drug']

    for i, subj in enumerate(data_control.subject):
        x = ['1']
        y = [data_control[data_control.subject==subj].value.values[0]] 
        if subj in data_drug.subject.values:
            x += ['2']
            y += [
                data_drug[data_drug.subject==subj].value.values[0]
            ]
            ax.plot(x, y, '-', label=subj, marker=mark[i], 
                    markersize=markersize, color=clr[i])
        

def _subject_line_plots(fig):

    sig = 0.01
    file = os.path.join(tablespath, 'table_liver_univariate.csv')
    univ = pd.read_csv(file).set_index('parameter')
    univ['group'] = data.lookup_vals(univ.index.values, 'group')
    univ['cluster'] = data.lookup_vals(univ.index.values, 'cluster')
    univ = univ.sort_values(by='cluster')
    univ = univ[univ['p-value'] < sig]
    pars = univ.index.values

    axes = fig.subplots(1, pars.size)
    for i, ax in enumerate(axes.ravel()):
        _subject_line_plot(ax, pars[i])



def secondary_outcomes():
    rows = 2
    fig = plt.figure(figsize=(15, 7.5))
    figrows = fig.subfigures(rows, 1, hspace=0.0)

    left, right = 0.1, 0.95

    # First row - boxplots
    ax = figrows[0].subplots(1,1)
    figrows[0].subplots_adjust(
        left=left, right=right, bottom=0.05, top=0.85,
    )
    _tstat_box_plots(ax)

    # Second row - lineplots
    _subject_line_plots(figrows[1])
    figrows[1].subplots_adjust(
        left=left, right=right, bottom=0.1, top=0.7, wspace=0.3,
    )

    # Save
    figfile = os.path.join(resultspath, 'secondary_outcomes.png')
    plt.savefig(fname=figfile)
    plt.close()


def primary_outcomes_box_plot_rel(ax):

    file = os.path.join(tablespath, 'effect_size_relative.csv')
    effect = pd.read_csv(file, index_col=0)

    lbls = ['k(he)', 'k(bh)']
    data = [
        effect['khe'].values,
        effect['kbh'].values,
    ]

    linewidth=2.
    fontsize=20
    [spine.set_linewidth(linewidth) for spine in ax.spines.values()]

    # box plot
    ax.set_title('Relative effect', fontsize=fontsize, pad=20)
    bplot = ax.boxplot(
        data,
        whis=[2.5,97.5],
        capprops=dict(linestyle='-', linewidth=linewidth, color='black'),
        flierprops=dict(
            marker='o', markerfacecolor='white', markersize=6,
            markeredgecolor='black', markeredgewidth=linewidth,
        ),
        whiskerprops=dict(linestyle='-', linewidth=linewidth, color='black'),
        medianprops=dict(linestyle='-', linewidth=linewidth, color='black'),
        boxprops=dict(linestyle='-', linewidth=linewidth, color='black'),
        widths=0.75, # width of the boxes
        vert=True,  # vertical box alignment
        patch_artist=True,  # fill with color
        #tick_labels=lbls, # will be used to label x-ticks
    )  
    ax.set_ylim([-100,100])
    ax.set_xticks(ax.get_xticks())  # Explicitly set tick positions
    ax.set_xticklabels(labels=lbls, fontsize=fontsize, rotation=90)
    ax.set_yticks(ax.get_yticks())  # Explicitly set tick positions
    ax.set_yticklabels(labels=ax.get_yticklabels(), fontsize=fontsize)
    #ax.grid(True, linewidth=1.5, axis='y')

    # fill with colors
    for patch in bplot['boxes']:
        patch.set_facecolor('steelblue')

    # adding horizontal grid line
    ax.yaxis.grid(True)
    ax.set_ylabel('%', fontsize=fontsize)


def primary_outcomes_box_plot_abs(ax):

    file = os.path.join(tablespath, 'effect_size_absolute.csv')
    effect = pd.read_csv(file, index_col=0) 

    #pars = effect.parameter.unique()
    lbls = ['k(he)', '10 x k(bh)']
    data = [
        effect['khe'].values,
        effect['kbh'].values * 10,
    ]

    linewidth=2.
    fontsize=20
    [spine.set_linewidth(linewidth) for spine in ax.spines.values()]

    # box plot
    ax.set_title('Absolute effect', fontsize=fontsize, pad=20)
    bplot = ax.boxplot(
        data,
        whis=[2.5,97.5],
        capprops=dict(linestyle='-', linewidth=linewidth, color='black'),
        flierprops=dict(
            marker='o', markerfacecolor='white', markersize=6,
            markeredgecolor='black', markeredgewidth=linewidth,
        ),
        whiskerprops=dict(linestyle='-', linewidth=linewidth, color='black'),
        medianprops=dict(linestyle='-', linewidth=linewidth, color='black'),
        boxprops=dict(linestyle='-', linewidth=linewidth, color='black'),
        widths=0.75, # width of the boxes
        vert=True,  # vertical box alignment
        patch_artist=True,  # fill with color
        #tick_labels=lbls, # will be used to label x-ticks
    )  
    #ax.set_ylim([-100,100])
    ax.set_xticks(ax.get_xticks())  # Explicitly set tick positions
    ax.set_xticklabels(labels=lbls, fontsize=fontsize, rotation=90)
    ax.set_yticks(ax.get_yticks())  # Explicitly set tick positions
    ax.set_yticklabels(labels=ax.get_yticklabels(), fontsize=fontsize)
    #ax.grid(True, linewidth=1.5, axis='y')

    # fill with colors
    for patch in bplot['boxes']:
        patch.set_facecolor('steelblue')

    # adding horizontal grid line
    ax.yaxis.grid(True)
    ax.set_ylabel('mL/min/100cm3', fontsize=fontsize)


def primary_outcomes_line_plot(ax, par):

    lbl = data.lookup_vals([par], 'label')[0]

    file = os.path.join(tablespath, 'vals_control.csv')
    vals_control = pd.read_csv(file).set_index('parameter')

    file = os.path.join(tablespath, 'vals_drug.csv')
    vals_drug = pd.read_csv(file).set_index('parameter')

    # file = os.path.join(tablespath, 'stdev_control.csv')
    # stdev_control = pd.read_csv(file).set_index('parameter')

    # file = os.path.join(tablespath, 'stdev_drug.csv')
    # stdev_drug = pd.read_csv(file).set_index('parameter')

    # Setup plot
    fontsize=20
    markersize=10
    linewidth=3.0
    ax.set_title(lbl, fontsize=fontsize, pad=20)
    ax.set_ylabel('mL/min/100cm3', fontsize=fontsize)
    #ax.set_ylim(ylim)
    ax.tick_params(axis='x', labelsize=fontsize, rotation=90)
    ax.tick_params(axis='y', labelsize=fontsize)
    [spine.set_linewidth(2.0) for spine in ax.spines.values()]

    nsubj = len(vals_control.columns)
    for i, subj in enumerate(vals_drug.columns):
        x = ['control']
        #x = [i]
        y = [vals_control.at[par, subj]] 
        #yerr = [stdev_control.at[par, subj]] 
        yrif = vals_drug.at[par, subj]
        if not np.isnan(yrif):
            x += ['drug']
            #x = [i + 2*nsubj]
            y += [yrif]
            #yerr += [stdev_drug.at[par, subj]]
        ax.plot(x, y, '-', label=subj, marker=mark[i], 
                markersize=markersize, color=clr[i], 
                linewidth=linewidth, 
        )
        #ax.errorbar(x, y, yerr=yerr, fmt='o', capsize=5)


def primary_outcomes():

    cols = 2
    fig = plt.figure(figsize=(15, 7.5))
    #fig.suptitle("Primary outcome markers", fontsize=18)
    figcols = fig.subfigures(1, cols, wspace=0.0)

    # First column - 2 boxplots
    axes = figcols[0].subplots(1,2)
    figcols[0].subplots_adjust(
        left=0.2, bottom=0.25, wspace=0.6, 
    )
    primary_outcomes_box_plot_rel(axes[0])
    primary_outcomes_box_plot_abs(axes[1])

    # Second column - 2 lineplots
    axes = figcols[1].subplots(1, 2)
    figcols[1].subplots_adjust(
        left=0.1, bottom=0.25, wspace=0.5,
    )
    primary_outcomes_line_plot(axes[0], 'khe')
    primary_outcomes_line_plot(axes[1], 'kbh')

    # Save
    figfile = os.path.join(resultspath, 'primary_outcomes.png')
    plt.savefig(fname=figfile)
    plt.close()



def correlation_effect_clustermap(filename, cols=None, xfigsize=16, pos=[0,0,1,1], title=''):

    file = os.path.join(tablespath, filename + '_vals.csv')
    vals = pd.read_csv(file).set_index('X')
    file = os.path.join(tablespath, filename + '_pval.csv')
    pval = pd.read_csv(file).set_index('X')

    #vals = np.abs(vals)
    #vmin, center, vmax = 0, 0.5, 1.0
    #cmap = 'cool'
    vmin, center, vmax = -1, 0, 1.0
    cmap = 'coolwarm'

    fontsize = 24 
    
    sig = 0.05
    #sig = 1
    mask = pval>sig
    #mask = vals<0.5
    significant = pval<sig

    select = False

    if select:
        #accept = (pval<sig) & (vals != 1)
        accept = pval<sig
        # accept_rows = accept.any(axis=0)
        # vals = vals.loc[:,accept_rows]
        # pval = pval.loc[:,accept_rows]
        # mask = mask.loc[:,accept_rows]
        # accept = accept.loc[:,accept_rows]
        
        accept_cols = accept.any(axis=1)
        vals = vals.loc[accept_cols,:]
        pval = pval.loc[accept_cols,:]
        mask = mask.loc[accept_cols,:]
        accept = accept.loc[accept_cols,:]
        significant = significant.loc[accept_cols,:]

    if cols is None:
        row_cluster = True
    else:
        row_cluster = False
        c = [c for c in cols if c in vals.columns]
        vals = vals[c]
        mask = mask[c]
        significant = significant[c]
 
    g = sns.clustermap(vals.T, 
        center=center, vmin=vmin, vmax=vmax, cmap=cmap,
        #dendrogram_ratio=(.1, .2),
        cbar_pos=None,
        linewidths=0.5, 
        linecolor='black',
        figsize=(xfigsize, 15), 
        yticklabels=True, 
        xticklabels=True,
        #mask=mask.T,
        row_cluster=row_cluster,
        col_cluster=True,
    )
    g.fig.suptitle(title, fontsize=32, y=0.95)
    g.ax_row_dendrogram.remove()
    g.ax_col_dendrogram.remove()
    #g.ax_heatmap.set_frame_on(True)
    g.ax_heatmap.set_position(pos)
    # Format labels
    linewidth = 2.0
    for ax in [g.ax_heatmap, g.ax_row_dendrogram, g.ax_col_dendrogram]:
        for spine in ax.spines.values():
            spine.set_visible(True) 
            spine.set_edgecolor('black')
            spine.set_linewidth(linewidth)  
    xpar = g.ax_heatmap.get_xmajorticklabels()
    ypar = g.ax_heatmap.get_ymajorticklabels()
    xpar = [p._text for p in xpar]
    ypar = [p._text for p in ypar]
    xlbl = data.lookup_vals(xpar, 'label')
    ylbl = data.lookup_vals(ypar, 'label')
    g.ax_heatmap.set_xticklabels(xlbl, rotation=90, fontsize=fontsize)
    g.ax_heatmap.set_yticklabels(ylbl, rotation=0, fontsize=fontsize)
    g.ax_heatmap.set_ylabel('')
    g.ax_heatmap.set_xlabel('')

    # Add asterix in significant cells

    # Get the reordered indices
    #x_labels = g.data2d.columns
    #y_labels = g.data2d.index
    x_labels = xpar
    y_labels = ypar

    # Loop over the heatmap and add asterisk where significant
    for y in range(len(y_labels)):
        for x in range(len(x_labels)):
            if significant.loc[x_labels[x], y_labels[y]]:
                g.ax_heatmap.text(
                    x + 0.5, y + 0.5, '*',
                    ha='center', va='center', color='black',
                    fontsize=36,
                )

    # Create the colorbar
    if filename == 'corr_liver_effect':
        # Define the colorbar axis position: [left, bottom, width, height]
        cbar_ax = g.fig.add_axes([.05, .25, .03, .5])
        Colorbar(cbar_ax, g.ax_heatmap.collections[0], orientation='vertical')
        #g.ax_cbar.set_position((.1, .25, .03, .4))
        cbar_ax.tick_params(labelsize=20)
        # Set the number of major ticks
        cbar_ax.locator_params(nbins=10) # Set number of major tick marks

    #plt.subplots_adjust(left=0.0, right=0.8, bottom=0.2)
    if cols is not None:
        g.ax_heatmap.set_yticklabels([])

    file = os.path.join(resultspath, filename + '.png')
    plt.savefig(fname=file)
    plt.close()

    return xpar


def correlations_effect():

    pars = correlation_effect_clustermap('corr_liver_effect', title='Liver', xfigsize=16, pos=[0.15, 0.15, 0.7, 0.75]) # [left, bottom, width, height]
    correlation_effect_clustermap('corr_aorta_effect', title='Aorta', cols=pars, xfigsize=6, pos=[0.05, 0.15, 0.90, 0.75])
    correlation_effect_clustermap('corr_blood_effect', title='LFT', cols=pars, xfigsize=6, pos=[0.05, 0.15, 0.90, 0.75])

    fig = plt.figure(figsize=(28, 15))
    subfigs = fig.subfigures(1, 3, wspace=0.0, width_ratios=[1.9, 0.7, 0.7])
    
    img0 = mpimg.imread(os.path.join(resultspath, 'corr_liver_effect.png'))
    ax = subfigs[0].subplots(1,1)
    ax.imshow(img0)
    ax.axis('off')
    img1 = mpimg.imread(os.path.join(resultspath, 'corr_aorta_effect.png'))
    ax = subfigs[2].subplots(1,1)
    ax.imshow(img1)
    ax.axis('off')
    img2 = mpimg.imread(os.path.join(resultspath, 'corr_blood_effect.png'))
    ax = subfigs[1].subplots(1,1)
    ax.imshow(img2)
    ax.axis('off')

    # Save
    figfile = os.path.join(resultspath, 'correlations_effect.png')
    plt.tight_layout()
    plt.savefig(fname=figfile)
    plt.close()


def correlation_control_clustermap(filename, cols=None, xfigsize=16, pos=[0,0,1,1], title=''):

    file = os.path.join(tablespath, filename + '_vals.csv')
    vals = pd.read_csv(file).set_index('X')
    file = os.path.join(tablespath, filename + '_pval.csv')
    pval = pd.read_csv(file).set_index('X')

    #vals = np.abs(vals)
    #vmin, center, vmax = 0, 0.5, 1.0
    #cmap = 'cool'
    vmin, center, vmax = -1, 0, 1.0
    cmap='coolwarm'

    fontsize = 24 
    
    sig = 0.05
    #sig = 1
    mask = pval>sig
    #mask = vals<0.5
    significant = pval<sig

    select = False

    if select:
        #accept = (pval<sig) & (vals != 1)
        accept = pval<sig
        # accept_rows = accept.any(axis=0)
        # vals = vals.loc[:,accept_rows]
        # pval = pval.loc[:,accept_rows]
        # mask = mask.loc[:,accept_rows]
        # accept = accept.loc[:,accept_rows]
        
        accept_cols = accept.any(axis=1)
        vals = vals.loc[accept_cols,:]
        pval = pval.loc[accept_cols,:]
        mask = mask.loc[accept_cols,:]
        accept = accept.loc[accept_cols,:]
        significant = significant.loc[accept_cols,:]

    if cols is None:
        row_cluster = True
    else:
        row_cluster = False
        c = [c for c in cols if c in vals.columns]
        vals = vals[c]
        mask = mask[c]
        significant = significant[c]
 
    g = sns.clustermap(vals.T, 
        center=center, vmin=vmin, vmax=vmax, cmap=cmap,
        #dendrogram_ratio=(.1, .2),
        cbar_pos=None,
        linewidths=0.5, 
        linecolor='black',
        figsize=(xfigsize, 15), 
        yticklabels=True, 
        xticklabels=True,
        #mask=mask.T,
        row_cluster=row_cluster,
        col_cluster=True,
    )
    g.fig.suptitle(title, fontsize=32, y=0.95)
    g.ax_row_dendrogram.remove()
    g.ax_col_dendrogram.remove()
    #g.ax_heatmap.set_frame_on(True)
    g.ax_heatmap.set_position(pos)
    # Format labels
    linewidth = 2.0
    for ax in [g.ax_heatmap, g.ax_row_dendrogram, g.ax_col_dendrogram]:
        for spine in ax.spines.values():
            spine.set_visible(True) 
            spine.set_edgecolor('black')
            spine.set_linewidth(linewidth)  
    xpar = g.ax_heatmap.get_xmajorticklabels()
    ypar = g.ax_heatmap.get_ymajorticklabels()
    xpar = [p._text for p in xpar]
    ypar = [p._text for p in ypar]
    xlbl = data.lookup_vals(xpar, 'label')
    ylbl = data.lookup_vals(ypar, 'label')
    g.ax_heatmap.set_xticklabels(xlbl, rotation=90, fontsize=fontsize)
    g.ax_heatmap.set_yticklabels(ylbl, rotation=0, fontsize=fontsize)
    g.ax_heatmap.set_ylabel('')
    g.ax_heatmap.set_xlabel('')

    # Add asterix in significant cells

    # Get the reordered indices
    #x_labels = g.data2d.columns
    #y_labels = g.data2d.index
    x_labels = xpar
    y_labels = ypar

    # Loop over the heatmap and add asterisk where significant
    for y in range(len(y_labels)):
        for x in range(len(x_labels)):
            if significant.loc[x_labels[x], y_labels[y]]:
                g.ax_heatmap.text(
                    x + 0.5, y + 0.5, '*',
                    ha='center', va='center', color='black',
                    fontsize=36,
                )

    # Create the colorbar
    if filename == 'corr_control':
        # Define the colorbar axis position: [left, bottom, width, height]
        cbar_ax = g.fig.add_axes([.05, .25, .03, .5])
        Colorbar(cbar_ax, g.ax_heatmap.collections[0], orientation='vertical')
        #g.ax_cbar.set_position((.1, .25, .03, .4))
        cbar_ax.tick_params(labelsize=20)
        # Set the number of major ticks
        cbar_ax.locator_params(nbins=10) # Set number of major tick marks

    #plt.subplots_adjust(left=0.0, right=0.8, bottom=0.2)
    if cols is not None:
        g.ax_heatmap.set_yticklabels([])

    file = os.path.join(resultspath, filename + '.png')
    plt.savefig(fname=file)
    plt.close()

    return xpar


def correlations_control():

    pars = correlation_control_clustermap('corr_control', title='Liver', xfigsize=16, pos=[0.15, 0.15, 0.7, 0.75]) # [left, bottom, width, height]
    correlation_control_clustermap('corr_aorta_control', title='Aorta', cols=pars, xfigsize=6, pos=[0.05, 0.15, 0.90, 0.75])
    correlation_control_clustermap('corr_blood_control', title='LFT', cols=pars, xfigsize=6, pos=[0.05, 0.15, 0.90, 0.75])
    correlation_control_clustermap('corr_screening', title='Screening', cols=pars, xfigsize=6, pos=[0.05, 0.15, 0.90, 0.75])

    fig = plt.figure(figsize=(28, 15))
    subfigs = fig.subfigures(1, 4, wspace=0.0, width_ratios=[1.85, 0.7, 0.7, 0.7])
    
    img0 = mpimg.imread(os.path.join(resultspath, 'corr_control.png'))
    ax = subfigs[0].subplots(1,1)
    ax.imshow(img0)
    ax.axis('off')
    img1 = mpimg.imread(os.path.join(resultspath, 'corr_aorta_control.png'))
    ax = subfigs[2].subplots(1,1)
    ax.imshow(img1)
    ax.axis('off')
    img2 = mpimg.imread(os.path.join(resultspath, 'corr_blood_control.png'))
    ax = subfigs[1].subplots(1,1)
    ax.imshow(img2)
    ax.axis('off')
    img3 = mpimg.imread(os.path.join(resultspath, 'corr_screening.png'))
    ax = subfigs[3].subplots(1,1)
    ax.imshow(img3)
    ax.axis('off')

    # Save
    figfile = os.path.join(resultspath, 'correlations_control.png')
    plt.tight_layout()
    plt.savefig(fname=figfile)
    plt.close()


def clustering():

    file = os.path.join(tablespath, 'effect_size_absolute.csv')
    vals = pd.read_csv(file, index_col=0)
    vals = (vals - vals.mean())/vals.std(ddof=0)
    vals = vals.dropna(axis=1, how='any')
    vars = set(vals.columns) - set(data.EXCLUDE_EFFECT)
    vals = vals[list(vars)]
    vals = vals.rename(lambda x: 'Delta ' + data.lookup_vals(x, 'label'), axis=1)
    vals.index = [str(i) for i in vals.index]

    file = os.path.join(tablespath, 'vals_control.csv')
    vals0 = pd.read_csv(file).set_index('parameter').T
    vals0 = (vals0 - vals0.mean())/vals0.std(ddof=0)
    vals0 = vals0.dropna(axis=1, how='any')
    vars0 = set(vals0.columns) - set(data.EXCLUDE_EFFECT)
    vals0 = vals0[list(vars0)]
    vals0 = vals0.rename(lambda x: data.lookup_vals(x, 'label'), axis=1)
    vals0 = vals0.loc[vals.index]

    vals = pd.concat([vals0, vals], axis=1)

    file = os.path.join(tablespath, 'vals_screening.csv')
    vals0 = pd.read_csv(file).set_index('parameter').T
    vals0 = (vals0 - vals0.mean())/vals0.std(ddof=0)
    vals0 = vals0.dropna(axis=1, how='any')
    vars0 = set(vals0.columns) - set(data.EXCLUDE_EFFECT)
    vals0 = vals0[list(vars0)]
    vals0 = vals0.rename(lambda x: data.lookup_vals(x, 'label'), axis=1)
    vals0 = vals0.loc[vals.index]

    vals = pd.concat([vals0, vals], axis=1)

    vmin, center, vmax = -2.5, 0, 2.5
    cmap='viridis'

    fontsize = 24 

    g = sns.clustermap(vals, 
        center=center, vmin=vmin, vmax=vmax, cmap=cmap,
        #dendrogram_ratio=(.1, .2),
        cbar_pos=None,
        linewidths=0.5, 
        linecolor='black',
        figsize=(25, 5), 
        yticklabels=True, 
        xticklabels=True,
        #mask=mask.T,
        # row_cluster=row_cluster,
        # col_cluster=True,
    )

    file = os.path.join(resultspath, 'clustering.png')
    plt.savefig(fname=file)
    plt.close()


def main():

    primary_outcomes()
    secondary_outcomes()
    correlations_control()
    correlations_effect()
    clustering()


if __name__=='__main__':
    main()

