
import argparse

import pandas as pd



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='data_in', required=True)
    parser.add_argument('-g', dest='groups_in', required=True)
    parser.add_argument('-o', dest='out_file', default='')
    args = parser.parse_args()

    # load data to reorder
    data = pd.read_csv(args.data_in, dtype=str)

    # load groups for new sorting
    groups = pd.read_csv(args.groups_in, dtype=str)
    order = ['reference_name', 'reference_pos', 'reference_allele', 'sample_allele', 'amino_acid_change']
    for sample in list(groups['sample']):
        if sample in data.columns:
            order.append(sample)

    # create the reordered dataframe
    reordered = data.loc[:, order]

    # write out the new dataframe
    if args.out_file == '':
        out_file = args.data_in.rstrip('.csv')
        out_file = f'{out_file}_reordered.csv'
    else:
        out_file = args.out_file

    reordered.to_csv(out_file, index=False)
