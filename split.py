import argparse
import csv



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='genotype_file_in', type=str)
    parser.add_argument('--fs_stop', dest='fs_stop_out', type=str)
    parser.add_argument('--nonsyn', dest='nonsynonymous_out', type=str)
    args = parser.parse_args()


    fin = open(args.genotype_file_in, 'r')
    fs_out = open(args.fs_stop_out, 'w', newline='')
    ns_out = open(args.nonsynonymous_out, 'w', newline='')

    reader = csv.DictReader(fin)
    fs_writer = csv.DictWriter(fs_out, fieldnames=reader.fieldnames)
    ns_writer = csv.DictWriter(ns_out, fieldnames=reader.fieldnames)

    fs_writer.writeheader()
    ns_writer.writeheader()

    for row in reader:
        if len(row['amino_acid_change']) < 2 or row['amino_acid_change'] == '':
            continue

        if (row['amino_acid_change'][-2:] == 'fs') or row['amino_acid_change'][-1] == '*':
            fs_writer.writerow(row)

        ns_writer.writerow(row)

    fin.close()
    fs_out.close()
    ns_out.close()
