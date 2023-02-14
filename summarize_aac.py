# -*- coding: utf-8 -*-
# summarize_aac.py
''' Summarizes a collection of CSVs from CLC Genomics Workbench
which describe predicted amino acid changing variant loci and their genotypes
as a single CSV containing the union of all loci and genotypes from all samples
in the CSVs.
'''

import argparse
import csv
from pathlib import Path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, dest='input', help='Path to folder containing CSVs to summarize.')
    parser.add_argument('-o', '--output', required=True, dest='output', help='Name of output file to generate.')
    parser.add_argument('-c', default=10, type=int, dest='coverage', help='Define a minimum depth of coverage a sample must present to be reported.')
    parser.add_argument('-d', action='store_true', dest='indepth', help='Set this flag to report not only genotypes but also allele frequencies')
    parser.add_argument('--keep_silent', action='store_true', dest='keep_silent', help='Set this flag to retain silent AA changes')
    args = parser.parse_args()

    coverage_cutoff = args.coverage
    show_in_depth = args.indepth
    keep_silent = args.keep_silent

    filenames = list(Path(args.input).iterdir())
    headers = [
        'reference_pos',
        'reference_allele',
        'sample_allele',
        'amino_acid_change'
    ]

    header_friendly_filenames = [str(Path(f).stem) for f in filenames]
    headers.extend(sorted(header_friendly_filenames))

    changes = {}
    for filename in filenames:
        with open(filename, newline='') as fin:
            reader = csv.DictReader(fin, delimiter=',', quotechar='"')
            for row in reader:
                coverage = int(row.get('Coverage', 0))
                if coverage < coverage_cutoff:
                    continue
                amino_change = row.get('Amino acid change', '')
                if (keep_silent == False) and (amino_change == ''):
                    continue
                amino_change = amino_change.split('p.')[-1].strip('[]')
                info = {
                    'reference_pos': row.get('Reference Position'),
                    'reference_allele': row.get('Reference'),
                    'sample_allele': row.get('Allele'),
                    'amino_acid_change': amino_change
                }
                # change the pertinent info into a hashable type
                info_hash = tuple(info.values())
                zygosity = row.get('Zygosity', 'N/A')[:3]
                count = int(row.get('Count', 0))
                frequency = round(float(row.get('Frequency', 0)), 3)
                in_depth = f'{zygosity}:{count}/{coverage}({frequency})'
                if info_hash not in changes:
                    changes[info_hash] = info

                if show_in_depth:
                    changes[info_hash][str(Path(filename).stem)] = in_depth
                else:
                    if zygosity == 'Hom':
                        symbol = '11'
                    else:
                        symbol = '10'
                    changes[info_hash][str(Path(filename).stem)] = symbol

    with open(args.output, 'w', newline='') as fout:
        writer = csv.DictWriter(fout, fieldnames=headers, quotechar='"')
        writer.writeheader()
        for info_hash, info in changes.items():
            writer.writerow(info)
