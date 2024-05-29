# -*- coding: utf-8 -*-
# Author: Peter Noah Tandy
""" This script takes a pairwise distance file and produces visualizations to
aid in the exploration of the data. It can perform PCA
(https://en.wikipedia.org/wiki/Principal_component_analysis),
joint plot (https://seaborn.pydata.org/generated/seaborn.jointplot.html),
and k-means clustering (https://en.wikipedia.org/wiki/K-means_clustering)
analyses and visualizations.
"""


import argparse
import gc
from pathlib import Path

import matplotlib.pyplot as plot
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


def csv_to_pca_groups_df(groups_file: Path) -> pd.DataFrame:
    groups = {}
    with open(groups_file) as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            name = row.get('name')
            group = row.get('group')
            groups[name] = group
    groups_df = pd.from_dict(groups)
    return groups

distinct_markers = ['o', '^', 's', 'D', 'p', "*", "P"]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--dist_file', dest='file_in', type=Path, required=True, metavar='PATH/TO/DISTFILE', help='Path to a comma delimited pairwise distance matrix file with a "sample" column and a column for every sample')
    parser.add_argument('-o', '--out_folder', dest='out_folder', type=Path, default='out', metavar='PATH/TO/OUTFOLDER/', help='Path to the folder to output all figures and data to. Will create the folder if it does not yet exist')
    parser.add_argument('--plot_pca', dest='plot_pca', action='store_true')
    parser.add_argument('--pca_title', dest='pca_title', type=str, default='', metavar='TITLE', help='Title to apply to the PCA plot(s)')
    parser.add_argument('--plot_joint', dest='plot_joint', action='store_true')
    parser.add_argument('--joint_title', dest='joint_title', type=str, default='', metavar='TITLE', help='Title to apply to the joint plot(s)')
    parser.add_argument('--groups', dest='pca_groups', type=Path, metavar='PATH/TO/GROUPS.csv', help='If plotting joint plots, provide a comma delimited file which supplies "sample" and "group" columns')
    parser.add_argument('--plot_kmeans', dest='plot_kmeans', action='store_true')
    parser.add_argument('-k', dest='k', type=int, default=5, help='Maximum clusters to test and plot')
    parser.add_argument('-r', '--random_seed', dest='random_seed', type=int, default=42)
    args = parser.parse_args()

    file_in = args.file_in

    out_folder = args.out_folder
    out_folder.mkdir(exist_ok=True)
    out_pca_folder = out_folder / 'pca'
    out_joint_folder = out_folder / 'joint'
    out_kmeans_folder = out_folder / 'kmeans'

    pca_groups = args.pca_groups

    plot_pca = args.plot_pca
    pca_title = args.pca_title

    plot_joint = args.plot_joint
    joint_title = args.joint_title

    plot_kmeans = args.plot_kmeans
    k_clusters = args.k
    random_seed = args.random_seed

    with open(file_in) as fin:
        df = pd.read_csv(fin, index_col='sample')

    # treat missing distance as completely distant
    df.fillna(1.0, inplace=True)

    # standardize the data
    scaler = StandardScaler()
    df_std = scaler.fit_transform(df)

    pca = PCA()
    pca.fit_transform(df_std)
    cum_variance = pca.explained_variance_ratio_.cumsum()
    total_components = len(cum_variance)
    for i, cv in enumerate(cum_variance):
        if cv >= 0.8:
            eighty_percent_components = i+1
            break

    if plot_pca == True or plot_joint == True:

        fig, ax = plot.subplots(figsize=(10,10), dpi=300)
        cum_variance = cum_variance[:eighty_percent_components + 5]
        plot.plot(range(1, len(cum_variance)+1), cum_variance, marker='o', linestyle='--')
        plot.title('Explained Variance by Components')
        plot.ylim(0.0, 1.0)
        plot.xticks([1, eighty_percent_components])
        plot.axvline(eighty_percent_components, color='grey', lw=0.5, ls='dotted')
        plot.axhline(0.8, color='grey', lw=0.5, ls='dotted')
        plot.xlabel(f'First {eighty_percent_components + 5} of {total_components} components')
        plot.ylabel('Cumulative Explained Variance')
        plot.savefig(out_folder / 'PCA_explained_variance.png')

        if eighty_percent_components <= 1:
            eighty_percent_components = 2
        pca = PCA(n_components=eighty_percent_components)
        pca_trans = pca.fit_transform(df_std)
        data = pd.DataFrame(pca_trans, columns=[f'PC{i}' for i in range(eighty_percent_components)], index=df.index)

        style_name = None
        markers = None
        if pca_groups != None:
            style_name = ''
            groups_df = pd.read_csv(pca_groups, index_col='sample')
            data = data.merge(groups_df, how='left', on='sample')
            data = data.rename(mapper={'group': style_name}, axis=1)
            data = data.dropna(subset=[style_name])
            markers = distinct_markers[:len(set(data[style_name]))]

        data.to_csv(out_folder / 'PCA_data.csv')

        if plot_pca == True:
            out_pca_folder.mkdir(exist_ok=True)
        if plot_joint == True:
            out_joint_folder.mkdir(exist_ok=True)

        for i in range(1, eighty_percent_components):
            x_pc = i-1
            y_pc = i
            x_explains = round(pca.explained_variance_ratio_[x_pc]*100, 1)
            y_explains = round(pca.explained_variance_ratio_[y_pc]*100, 1)
            x_visible_name = f'PC{x_pc+1}'
            y_visible_name = f'PC{y_pc+1}'
            x_label = f'{x_visible_name} ({x_explains}%)'
            y_label = f'{y_visible_name} ({y_explains}%)'

            if plot_pca == True:
                # pca
                fig, ax = plot.subplots(figsize=(10, 10), dpi=300)
                ax.axvline(color='grey', lw=0.5, ls='dashed')
                ax.axhline(color='grey', lw=0.5, ls='dashed')
                scatter = sns.scatterplot(data=data, x=f'PC{x_pc}', y=f'PC{y_pc}', ax=ax, hue=style_name, style=style_name, markers=markers)
                ax.set_xlabel(x_label)
                ax.set_ylabel(y_label)
                ax.set_title(pca_title)
                plot.savefig(out_pca_folder / f'{x_visible_name}x{y_visible_name}.png')

            if plot_joint == True:
                # jointplot
                # TODO: add markers to jointplots to match PCA
                plot.figure(figsize=(15, 15), dpi=300)
                x_lim = (min(data[f'PC{x_pc}'])-0.5, max(data[f'PC{x_pc}'])+0.5)
                y_lim = (min(data[f'PC{y_pc}'])-0.5, max(data[f'PC{y_pc}'])+0.5)
                joint_plot = sns.jointplot(x=f'PC{x_pc}', y=f'PC{y_pc}', data=data, hue=style_name, space=0, height=15, xlim=x_lim, ylim=y_lim)
                joint_plot.set_axis_labels(x_label, y_label)
                joint_plot.ax_joint.axvline(color='grey', lw=0.5, ls='dashed')
                joint_plot.ax_joint.axhline(color='grey', lw=0.5, ls='dashed')
                joint_plot.fig.suptitle(joint_title, fontsize=20, y=1.05)
                plot.savefig(out_joint_folder / f'{x_visible_name}x{y_visible_name}.png', bbox_inches='tight')

            plot.cla()
            plot.clf()
            plot.close('all')
            plot.close(fig)
            gc.collect()

    if plot_kmeans == True:
        out_kmeans_folder.mkdir(exist_ok=True)
        if plot_pca == False:
            pca = PCA(n_components=eighty_percent_components)
        scores_pca = pca.fit_transform(df_std)
        wcss = []
        for k in range(1, k_clusters+1):
            kmeans_pca = KMeans(n_clusters=k, random_state=random_seed)
            kmeans_pca.fit_transform(scores_pca)
            wcss.append(kmeans_pca.inertia_)
            if k == 1:
                # don't bother plotting 1 cluster, that's the same as PCA
                continue
            df_kmeans = pd.concat([df.reset_index(), pd.DataFrame(scores_pca)], axis=1)
            df_kmeans.columns.values[-eighty_percent_components:] = [f'PC{j}' for j in range(eighty_percent_components)]
            df_kmeans['cluster'] = kmeans_pca.labels_
            out_subfolder = out_kmeans_folder / f'{k}_clusters'
            out_subfolder.mkdir(exist_ok=True)
            for i in range(1, eighty_percent_components):
                x_pc = i-1
                y_pc = i
                x_explains = round(pca.explained_variance_ratio_[x_pc]*100, 1)
                y_explains = round(pca.explained_variance_ratio_[y_pc]*100, 1)
                x_visible_name = f'PC{x_pc+1}'
                y_visible_name = f'PC{y_pc+1}'
                fig, ax = plot.subplots(figsize=(10, 10), dpi=300)
                ax.axvline(color='grey', lw=0.5, ls='dashed')
                ax.axhline(color='grey', lw=0.5, ls='dashed')
                sns.scatterplot(x=df_kmeans[f'PC{x_pc}'], y=df_kmeans[f'PC{y_pc}'], hue=df_kmeans['cluster'], ax=ax, palette='tab10')
                ax.set_xlabel(f'{x_visible_name} ({x_explains}%)')
                ax.set_ylabel(f'{y_visible_name} ({y_explains}%)')
                out_file = out_subfolder / f'{x_visible_name}x{y_visible_name}.png'
                plot.savefig(out_file)
                plot.cla()
                plot.clf()
                plot.close('all')
                plot.close(fig)
                gc.collect()

        fig, ax = plot.subplots(figsize=(10, 10), dpi=300)
        plot.plot(range(1, k_clusters+1), wcss, marker='o', linestyle='--')
        ax.set_xticks(list(range(1, k_clusters+1)))
        plot.xlabel('Number of Clusters')
        plot.ylabel('WCSS')
        plot.savefig(out_folder / f'kmeans_wcss.png')
