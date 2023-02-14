# AAC-PopGen
Scripts for performing population genetics analysis and associated visualizations from data produced by CLC Genomics Workbench v 9.5.

## Preparation
Create a virtual environment, and within that environment install the required packages described in `requirements.txt` (`python3 -m pip install -r requirements.txt`)

Gather your CLC amino acid changes into a single folder (i.e. \~/project/aac_csv/).

If you would like to categorize data into logical groups for some visualizations, create a CSV similar to the `groups_example.csv` file with the column headers `sample` and `group`.

## General workflow
### summarize_aac.py
This script condenses the individual sample files from CLC into one table of genotype data. The genotype data will be encoded as one of four options: 00, 11, 10, or empty. 00 represents homozygous for the reference allele. 11 represents homozygous for the alternate allele. 10 represents heterzygous. An empty field means there was no information.

At this step certain data can be excluded based on depth of representation with the `-c` option. By default, this script only considers amino acid changes that result in a nonsynonymous change, but can be made to report all changes by using the `--keep_silent` option to "keep" the silent changes in the file.

`python3 summarize_aac.py -f example/aac_csv/ -o aac.csv -c 10 --keep_silent`

See `python3 summarize_aac.py --help` for more information.

See `example/gt.csv` for an example of the resulting genotype table.

### jaccard.py
This script evaluates the Jaccard distance between the samples based on the genotype table produced above.

`python3 jaccard.py -f example/gt.csv -o example/jaccard.dist`

### pca.py
This script takes the jaccard distance calculated above and performs Principal Component Analysis (PCA) on the data. It can also visualize the PCA data in several ways
- PCA plots of relevant components simply plotted against each other in descending order of explained variance (1v2, 2v3, 3v4, etc.)
- Jointplot-style visualizations of the same data, which include extra axes depicting the rough density of the groups as well.

In addition to PCA, this script can perform kmeans clustering and visualizations on the PCA data.

If there are many samples that fit into logical groups, these visualizations can make use of a "groups CSV" (see `example/groups.csv`) to make the resulting plots less cluttered. At the moment, this script is only able to display up to 5 logical groups.

`python3 pca.py -f example/jaccard.dist -o example/pca_results/ --plot_pca --pca_title "Example"  --groups example/groups.csv`

See `pca.py --help` for more info.

See `example/pca_results/` for an example output.

### heatmap.py
This script visualizes the Jaccard distance file from above as a pairwise heatmap.

`python3 heatmap.py -f example/jaccard.dist -o example/heatmap.png -t "Example"`

See `example/heatmap.png` for an example output.

### upset.py
This script takes the genotype data generated above and a required group membership csv (see `example/groups.csv`) and creates an UpSet Plot depicting membership of alleles among the groups.

`python3 upset.py -f example/gt.csv -g example/groups.csv -o example/upset.png -t "Example"`

See `example/upset.png` for an example output.
