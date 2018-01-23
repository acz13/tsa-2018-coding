"""Readers for csv and xls"""

import csv


def read_csv(data_file):
    """Read the first two columns of a csv file into a generator, guessing at
    delimiter"""
    with open(data_file, 'r') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        for row in csv.reader(csvfile, dialect):
            yield (float(row[0]), float(row[1]))
