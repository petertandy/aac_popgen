

import argparse

import matplotlib.pyplot as plot
import numpy as np
import pandas as pd
import seaborn as sns


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='dist_file', type=str, required=True)
    parser.add_argument('-o', dest='out_file', type=str, default='')
    parser.add_argument('-t', dest='heatmap_title', type=str, default='')
    args = parser.parse_args()

    df = pd.read_csv(args.dist_file, index_col='sample')
    fig, ax = plot.subplots(figsize=(5, 5), dpi=300)
    sns.heatmap(df, ax=ax, vmin=0.0, vmax=1.0, cmap='viridis', square=True, cbar_kws={"shrink": .8})

    ax.set_xticks(np.arange(0.5, df.shape[0]))
    ax.set_yticks(np.arange(0.5, df.shape[0]))
    ax.set_xticklabels(df.columns, rotation=-45.0, ha='right')
    ax.set_yticklabels(df.columns)
    ax.xaxis.tick_top()
    ax.set_title(f'{args.heatmap_title}', {'fontsize': 40})
    ax.set_ylabel('')

    if args.out_file != '':
        plot.savefig(args.out_file, bbox_inches='tight')
    else:
        plot.show()
