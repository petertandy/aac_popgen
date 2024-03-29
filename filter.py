

import argparse
import math

import pandas as pd


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, dest='file_in', required=True)
    parser.add_argument('-o', type=str, dest='file_out', default='')
    parser.add_argument('--drop_n', action='store_true', dest='drop_n')
    loci_thresh_help = 'Defines the minimum proportion of data required to be'
    loci_thresh_help += ' present to retain a locus.'
    loci_thresh_help += ' For example: -l 0.85 means a locus'
    loci_thresh_help += ' is allowed to be missing up to 15 percent data.'
    parser.add_argument(
        '-l',
        type=float,
        dest='loci_thresh',
        help=loci_thresh_help
    )
    sample_thresh_help = 'The minimum proportion of data required to be present'
    sample_thresh_help += ' to retain a sample AFTER removing loci.'
    sample_thresh_help += ' For example: -s 0.95 means a sample'
    sample_thresh_help += ' is allowed to be missing up to 5 percent data.'
    parser.add_argument(
        '-s',
        type=float,
        dest='sample_thresh',
        help=sample_thresh_help
    )
    args = parser.parse_args()

    loci_thresh = args.loci_thresh
    sample_thresh = args.sample_thresh
    fin = args.file_in
    fout = args.file_out

    gt = pd.read_csv(fin, dtype=str)

    pre_len = gt.shape

    # remove changes stemming from Ns in the reference sequence
    if args.drop_n == True:
        gt = gt[gt['reference_allele'] != 'N']
    num_n_loci = pre_len[0] - gt.shape[0]

    # loci are dropped before samples, assuming that samples are more complete
    # than loci.
    # drop loci (rows) if they are in too few samples
    num_thresh_cols = len(gt.columns[5:])
    _loci_thresh = int(math.ceil(num_thresh_cols * loci_thresh))
    gt = gt.dropna(axis='index', thresh=_loci_thresh, subset=gt.columns[5:])

    # drop samples (columns) if they have too few loci
    num_thresh_rows = len(gt.index)
    _sample_thresh = int(math.ceil(num_thresh_rows * sample_thresh))
    _gt = gt.dropna(axis='columns', thresh=_sample_thresh)

    # the change column was likely dropped because we can't change the behavior
    # of df.dropna, so insert it back in if it's missing
    try:
        _gt.insert(2, 'amino_acid_change', gt['amino_acid_change'])
    except ValueError:
        pass
    finally:
        gt = _gt

    # remove loci that have no mutant samples
    pre_empty = gt.shape[0]
    gt = gt[~(gt[gt.columns[5:]].fillna('00') == '00').all(axis=1)]
    num_no_mutant = pre_empty - gt.shape[0]

    post_len = gt.shape

    num_dropped_loci = pre_len[0] - post_len[0]
    num_dropped_samples = pre_len[1] - post_len[1]
    pre_volume = pre_len[0] * pre_len[1]
    post_volume = post_len[0] * post_len[1]
    vol_reduction = post_volume / pre_volume

    # some stats you can capture from stdout if you want
    print(f'Input file: {fin}')
    print(f'Output file: {fout}')
    print('Locus filter:')
    print(f'\tThreshold supplied: {loci_thresh}')
    print(f'\tActual: {_loci_thresh}/{num_thresh_cols} ~= {loci_thresh} * {num_thresh_cols} / {num_thresh_cols}')
    print(f'\tLoci dropped: {num_dropped_loci}')
    print(f'\t\t{num_n_loci} were N loci')
    print(f'\t\t{num_no_mutant} were empty or had no mutant alleles after other filters')

    print('Sample threshold:')
    print(f'\tThreshold supplied: {sample_thresh}')
    print(f'\tActual: {_sample_thresh}/{num_thresh_rows} ~= {sample_thresh} * {num_thresh_rows} / {num_thresh_rows}')
    print(f'\tSamples dropped: {num_dropped_samples}')

    print(f'Table volume changed by {vol_reduction:.2%}')
    print(f'\t{pre_len[0]}x{pre_len[1]} -> {post_len[0]}x{post_len[1]}')
    print(f'\t{pre_volume} -> {post_volume}')

    if fout != '':
        gt.to_csv(fout, index=False)
