
import argparse
import math
from pathlib import Path
from typing import Callable, List, Union

import pandas as pd


def csv_to_pairwise_dist(file_in: Union[str, Path], columns: List[str]=None, compare: Callable[[str, str], float]=None) -> pd.DataFrame:
    if compare == None:
        compare = jaccard_distance
    df = pd.read_csv(file_in, dtype=str)
    if columns == None:
        columns = df.columns[5:]
    intersection = df.columns.intersection(columns)
    # this particular comprehension preserves the order of the columns provided in the resulting df
    df = df.loc[:, [c for c in columns if c in intersection]]
    pairwise = {}
    for sample1 in df.columns:
        pairwise[sample1] = {}
        s1 = df[sample1]
        for sample2 in df.columns:
            s2 = df[sample2]
            pairwise[sample1][sample2] = compare(s1, s2)
    df = pd.DataFrame.from_dict(pairwise)
    df.index.name = 'sample'
    return df

def jaccard_distance(sample1, sample2) -> float:
    ''' Returns the Jaccard distance between two samples,
    defined as 1 - J where J is the Jaccard index'''
    index = jaccard_index(sample1, sample2)
    distance = 1 - index
    return distance

def jaccard_index(sample1, sample2) -> float:
    ''' Returns the Jaccard index of mutations between two samples'''
    loci = 0
    similar = 0
    for (a, b) in zip(sample1, sample2):
        try:
            if math.isnan(a):
                continue
        except TypeError:
                pass
        try:
            if math.isnan(b):
                continue
        except TypeError:
                pass
        # ignore wt-wt matches
        if a == '00' and b == '00':
            continue
        loci += 1
        if a == b:
            similar += 1
    if loci == 0:
        return float('NaN')
    index = float(similar / loci)
    return index


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='file_in', type=Path, required=True)
    parser.add_argument('-o', dest='file_out', type=Path, default=Path('jaccard.dist'))
    args = parser.parse_args()

    df = csv_to_pairwise_dist(args.file_in)
    df.to_csv(args.file_out)