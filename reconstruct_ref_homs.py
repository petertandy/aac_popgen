import argparse

import pandas as pd


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', dest='unfilled_aac_summary', type=str)
    parser.add_argument('-b', dest='depth_tsv', type=str)
    parser.add_argument('-c', dest='min_depth', type=int, default=10)
    parser.add_argument('-o', dest='file_out', type=str)
    args = parser.parse_args()

    aac_df = pd.read_csv(args.unfilled_aac_summary, dtype=str)
    aac_df.fillna('', inplace=True)

    depth_df = pd.read_csv(
        args.depth_tsv,
        dtype=str,
        delimiter='\t'
    )

    sample_names = aac_df.columns[5:]
    for i, row in aac_df.iterrows():
        name = row['reference_name']

        # the ref names in the AAC summary can be manipulated here to match the
        # names in the depth tsv if they don't match
        stripped_name = name
        # stripped_name = stripped_name.replace(' ', '').rstrip('mapping')

        pos = str(row['reference_pos'])
        name_mask = (aac_df['reference_name'] == name)
        pos_mask = (aac_df['reference_pos'] == pos)
        aac_mask = name_mask & pos_mask
        df = depth_df[(depth_df['#CHROM'] == stripped_name) & (depth_df['POS'] == pos)]
        for sample in sample_names:
            sample_bam = f'{sample}.bam'
            wt_depth = int(df[sample_bam].iloc[0])
            genotype = str(aac_df[aac_mask][sample].iloc[0])
            if (genotype == '') and (wt_depth >= args.min_depth):
                aac_df.loc[i, sample] = '00'

    aac_df.set_index('reference_name', inplace=True)
    aac_df.to_csv(args.file_out)
