#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Uses replacement mapping files to replace symbols and strings in input using the replacement strings.

"""

import re

mp_file_path = '../mapping_tables/'
acro_file = 'acros.txt'
abbr_file = 'abbr.txt'
symbol_file = 'symbol_mapping.txt'


class ReplacementMaps:

    def __init__(self):
        self.acronym_map = {}
        self.abbr_map = {}
        self.symbol_map = {}

    @staticmethod
    def read_file(filename):
        in_file = open(filename)
        acronym_map = in_file.read().splitlines()
        return acronym_map

    @staticmethod
    def create_map_from_list(tsv_list):
        res_map = {}
        for line in tsv_list:
            arr = line.split('\t')
            if len(arr) == 2:
                res_map[arr[0]] = arr[1]
        return res_map

    def get_acronym_map(self):
        if not self.acronym_map:
            acr_list = self.read_file(mp_file_path + acro_file)
            self.acronym_map = self.create_map_from_list(acr_list)
        return self.acronym_map

    def get_abbreviation_map(self):
        if not self.abbr_map:
            abbr_list = self.read_file(mp_file_path + abbr_file)
            self.abbr_map = self.create_map_from_list(abbr_list)
        return self.abbr_map

    def get_symbol_map(self):
        if not self.symbol_map:
            symbol_list = self.read_file(mp_file_path + symbol_file)
            self.symbol_map = self.create_map_from_list(symbol_list)
        return self.symbol_map

    def replace_acronyms(self, line):
        res = line
        for key in self.get_acronym_map():
            res = res.replace(' ' + key + ' ', ' ' + self.acronym_map[key] + ' ')

        return res

    def replace_abbreviations(self, line):
        res = line
        for key in self.get_abbreviation_map():
            res = re.sub(' ' + key + '\.? ', ' ' + self.abbr_map[key] + ' ', res)

        return res

    def replace_symbols(self, line):
        res = line
        for key in self.get_symbol_map():
            res = res.replace(key, ' ' + self.symbol_map[key] + ' ')
            res = res.replace('  ', ' ')

        return res


def replace_from_maps(line):
    repl = ReplacementMaps()

    res = repl.replace_acronyms(line)
    res = repl.replace_abbreviations(res)
    res = repl.replace_symbols(res)
    # delete puncutation
    res = re.sub(r'[.,:?!]', '', res)
    arr = res.split()
    res = ' '.join(arr)
    res = res.lower()
    # special case for texts from dv.is
    res = res.replace('ritstjórn dv ritstjorn @ dv', '')

    return res
