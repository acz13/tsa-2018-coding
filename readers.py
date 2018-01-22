"""Readers for csv and xls"""

from typing import Generator, Tuple
import csv
from xlrd import open_workbook

DataGen = Generator[Tuple[float, float], None, None]


def read_csv(data_file: str) -> DataGen:
    """Read the first two columns of a csv file into a generator, guessing at
    delimiter"""
    with open(data_file, 'r') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        for row in csv.reader(csvfile, dialect):
            yield (float(row[0]), float(row[1]))


def read_xls(data_file: str) -> DataGen:
    """Read first two lines of a xls file into a generator.
    Probably not needed."""
    sheet = open_workbook(data_file).sheet_by_index(0)
    for row in range(sheet.nrows):
        yield (float(sheet.cell_value(row, 0)),
               float(sheet.cell_value(row, 1)))
