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
    parser.add_argument(
        '-i',
        '--input',
        required=True,
        dest='input',
        help='Path to folder containing CSVs to summarize.'
    )
    parser.add_argument(
        '-o',
        '--output',
        required=True,
        dest='output',
        help='Name of output file to generate.'
    )
    parser.add_argument(
        '-n',
        '--default_name',
        default='',
        type=str,
        dest='default_name',
        help='This will give empy Mapping names a default name. This includes the case where there is no Mapping column.'
    )
    parser.add_argument(
        '-s',
        '--split',
        action='store_true',
        dest='split',
        help='Also output an individual file for every mapping name'
    )
    depth_help = 'Define a minimum depth of coverage a sample must present '
    depth_help += 'to be reported.'
    parser.add_argument(
        '-c',
        default=10,
        type=int,
        dest='coverage',
        help=depth_help
    )
    indepth_help = 'Set this flag to report not only genotypes but also '
    indepth_help += 'allele frequencies. Is not compatible with downstream '
    indepth_help += 'tools, and is only provided for debugging/investigation.'
    parser.add_argument(
        '-d',
        '--indepth',
        action='store_true',
        dest='indepth',
        help=indepth_help
    )
    parser.add_argument(
        '--keep_silent',
        action='store_true',
        dest='keep_silent',
        help='Set this flag to retain silent AA changes'
    )
    args = parser.parse_args()

    coverage_cutoff = args.coverage
    show_in_depth = args.indepth
    keep_silent = args.keep_silent

    filenames = list(Path(args.input).iterdir())
    headers = [
        'reference_name',
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
                if (keep_silent is False) and (amino_change == ''):
                    continue
                amino_change = amino_change.split('p.')[-1].strip('[]')
                mapping_name = row.get('Mapping', '')
                if mapping_name == '':
                    mapping_name = args.default_name
                info = {
                    'reference_name': mapping_name,
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
                if changes.get(mapping_name) == None:
                    changes[mapping_name] = {}

                if info_hash not in changes[mapping_name]:
                    changes[mapping_name][info_hash] = info

                if show_in_depth:
                    changes[mapping_name][info_hash][str(Path(filename).stem)] = in_depth
                else:
                    if zygosity == 'Hom':
                        symbol = '11'
                    else:
                        symbol = '10'
                    changes[mapping_name][info_hash][str(Path(filename).stem)] = symbol

    with open(args.output, 'w', newline='') as fout:
        writer = csv.DictWriter(fout, fieldnames=headers, quotechar='"')
        writer.writeheader()
        sorted_mapping_names = sorted(list(changes.keys()))
        for mapping_name in sorted_mapping_names:
            by_mapping = changes[mapping_name]
            hashes_by_ref_pos = sorted(by_mapping, key=lambda x: int(x[1]))
            if args.split == True:
                split_fn = str(args.output).rstrip('.csv')
                split_fn += '_'
                split_fn += mapping_name.replace(' ', '_')
                split_fn += '.csv'
                split_out = open(split_fn, 'w', newline='')
                split_writer = csv.DictWriter(
                    split_out,
                    fieldnames=headers,
                    quotechar='"'
                )
                split_writer.writeheader()
            for info_hash in hashes_by_ref_pos:
                row = changes[mapping_name][info_hash]
                writer.writerow(row)
                if args.split == True:
                    split_writer.writerow(row)
            if args.split == True:
                split_out.close()

