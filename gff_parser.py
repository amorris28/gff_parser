#!/usr/bin/env python

## Antti Karkman
## University of Gothenburg
## antti.karkman@gmail.com
## 2020 (tested with anvi'o v6.2, and should work with anything after)

import gffutils
import argparse
import sys

from collections import Counter

#parse the arguments
parser = argparse.ArgumentParser(description="""Parse Prodigal to add external gene calls to anvi'o.
                    Input gene calls in GFF3 format, output in tab-delimited text file""")
parser.add_argument('gff_file', metavar='GFF3', help='Gene call file from Prodigal in GFF3 format')
parser.add_argument('--gene-calls', default='gene_calls.txt', help='Output: External gene calls (Default: gene_calls.txt)')
parser.add_argument('--source', default='Prodigal', help='Source of gene calls (Prodigal) (Default: Prodigal)')

args = parser.parse_args()

#Input file and output files
GFF = args.gff_file
OUT_CDS = open(args.gene_calls, 'w')

#Check gene caller
SOURCE = args.source
if SOURCE == 'Prodigal':
    SEP = ' '
else:
    print(SOURCE, "is not an available gene caller.")
    sys.exit()

#load in the GFF3 file
db = gffutils.create_db(GFF, ':memory:')

#Print headers for anvi'o
OUT_CDS.write("gene_callers_id\tcontig\tstart\tstop\tdirection\tpartial\tcall_type\tsource\tversion\n")

#running gene ID and a trumped-up e-value for the gene calls.
gene_id = 1

# keping track of things we haven't processed
feature_types = Counter()
call_types = Counter()
total_num_features = 0
features_missing_product_or_note = 0

#parse the GFF3 file and write results to output files
for feature in db.all_features():
    total_num_features += 1
    # determine source
    source, version = feature.source.split(SEP, 1)

    start = feature.start - 1
    stop = feature.stop

    feature_types[feature.featuretype] += 1
    if feature.featuretype == 'CDS':
        call_type = 1
        call_types['CDS'] += 1
    elif 'RNA' in feature.featuretype:
        call_type = 2
        call_types['RNA'] += 1
    else:
        call_type = 3
        call_types['unknown'] += 1

    if (float(start - stop)/float(3)).is_integer() == True:
        partial = str(0)
    else:
        partial = str(1)

    try:
        gene_acc = feature.attributes['gene'][0]
    except KeyError:
        gene_acc = ""

    # determine direction
    if feature.featuretype=='repeat_region':
        direction='f'
    else:
        if feature.strand=='+':
            direction='f'
        else:
            direction='r'

    OUT_CDS.write('%d\t%s\t%d\t%d\t%s\t%s\t%d\t%s\t%s\n' % (gene_id, feature.seqid, start, stop, direction, partial, call_type, source, version))
    gene_id = gene_id + 1

print(f"Done. All {total_num_features} have been processed succesfully. There were {call_types['CDS']} coding "
      f"sequences, {call_types['RNA']} RNAs, and {call_types['unknown']} unknown features.")

if features_missing_product_or_note:
    print()
    print(f"Please note that we discarded {features_missing_product_or_note} features described in this file "
          f"since they did not contain any products or notes :/")
