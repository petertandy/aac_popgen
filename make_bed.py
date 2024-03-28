import argparse
import csv


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, dest='aac_summary_file')
    parser.add_argument('-o', type=str, dest='bed_out')
    args = parser.parse_args()

    with open(args.aac_summary_file, 'r') as fin:
        reader = csv.DictReader(fin)
        bed_rows = [
            [
                str(row['reference_name']),
                int(row['reference_pos'])-1,
                int(row['reference_pos']),
                row['amino_acid_change']
            ] for row in reader
        ]
        with open(f'{args.bed_out}', 'w', newline='') as fout:
            writer = csv.writer(fout, delimiter='\t')
            for line in bed_rows:
                writer.writerow(line)
