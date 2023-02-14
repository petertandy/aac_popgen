
import argparse
import csv

import matplotlib.pyplot as plt
import pandas as pd
import upsetplot


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='file_in', type=str, required=True)
    parser.add_argument('-g', '--groups', dest='groups_file', type=str, required=True)
    parser.add_argument('-v', '--vertical', dest='vert_orientation', action='store_true')
    parser.add_argument('-t', '--title', dest='title', type=str, default='')
    parser.add_argument('-o', '--output', dest='output', type=str)
    args = parser.parse_args()

    orientation = 'horizontal' if not args.vert_orientation else 'vertical'

    df = pd.read_csv(args.file_in, dtype=str)

    categories = {}
    with open(args.groups_file, 'r') as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            if row['group'] not in categories:
                categories[row['group']] = []
            categories[row['group']].append(row['sample'])
    remove_groups = []
    for group, samples in categories.items():
        if len(list(df.columns.intersection(samples))) == 0:
            remove_groups.append(group)
    for rg in remove_groups:
        del categories[rg]

    membership = {cat: set() for cat in categories}

    for idx in df.index:
        for cat, samples in categories.items():
            values = df.loc[idx, df.columns.intersection(samples)].values
            if '11' in values or '10' in values:
                pos = df.loc[idx, 'reference_pos']
                ref = df.loc[idx, 'reference_allele']
                mut = df.loc[idx, 'sample_allele']
                membership[cat].add(f'{pos}_{ref}>{mut}')

    data = upsetplot.from_contents(membership)

    fig, ax = plt.subplots(figsize=(5, 5), dpi=300)
    ax.axis('off')
    ax.set_title(args.title, y=1.05)
    upsetplot.plot(data, fig=fig, orientation=orientation, show_counts=True)

    if args.output == None:
        plt.show()
    else:
        plt.savefig(args.output)
