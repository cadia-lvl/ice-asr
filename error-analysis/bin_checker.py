#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# Compare substitution pairs from kaldi ops file.
# Check the BÍN database if the words possibly belong to the same lemma, indicating that the error
# is not as severe as when the substituted word is a representation of another lemma
#
# Important remark:
# - Before running this script, extract the lines from BÍN (SHsnid.csv) containing word forms from the substitutions
#   to be examined! Prepare a wordlist of substitution words where every word is embedded in semi colons: ;word; and
#   run fgrep on the whole BÍN file.
# - A proper way to solve a task like in this script would of course be to use a BÍN-database ...
#
# BÍN input format:
#
# lemma;id(might be missing!);word class;cat;word form;pos_string
#
# ops-format:
#
# operation     ref-word     hyp-word    no-of-operation
#
#

import argparse
import os
import errno
import time

import verification
from categories import Categories

# categories for bin_checker:
SAME_LEMMA = 'same_lemma'
DIFF_LEMMA = 'different_lemma'
NOT_IN_BIN = 'wordform_not_in_bin'


class Lemma:

    def __init__(self, id):
        self.id = id
        self.word_forms = set()

    def add_word_form(self, word_form):
        self.word_forms.add(word_form)

    def add_word_forms(self, wf_list):
        self.word_forms = self.word_forms.union(wf_list)


def init_id_based_bin_dict(bin_list):
    """
    First, create a map with bin-ids as keys and collect wordforms for each id
    """
    bin_dict = {}
    for line in bin_list:
        line_arr = line.split(';')
        if len(line_arr) != 6:
            print(line + ' in BÍN does not have the correct format!')
            print('Correct format is: lemma;id;wordclass;category;wordform;pos-string')
            continue

        id = line_arr[1]
        wf = line_arr[4]

        if id in bin_dict:
            wf_set = bin_dict[id]
            wf_set.add(wf)

        else:
            wf_set = set()
            wf_set.add(wf)
            bin_dict[id] = wf_set

    return bin_dict


def init_bin_dict(bin_list):
    """
    Creates a dictionary of word forms, where each word form maps to a list of possible lemmata, represented by a lemma
    object containing all other possible word forms.
    """
    id_based = init_id_based_bin_dict(bin_list)

    bin_dict = {}
    for key in id_based.keys():
        lemma = Lemma(key)
        lemma.add_word_forms(id_based[key])
        for wf in id_based[key]:
            if wf in bin_dict:
                lemma_list = bin_dict[wf]
                lemma_list.append(lemma)
                bin_dict[wf] = lemma_list
            else:
                bin_dict[wf] = [lemma]

    return bin_dict


def extract_set_from_list(list_of_lists):
    elem_set = set()
    for elem_list in list_of_lists:
        elem_set = elem_set.union(set(elem_list))
    return elem_set


def print_info(categories, subst_counter):

    dist_same = len(categories.categories_dict[SAME_LEMMA].element_list)
    sum_same = categories.categories_dict[SAME_LEMMA].occurrence_counter
    dist_diff = len(categories.categories_dict[DIFF_LEMMA].element_list)
    sum_diff = categories.categories_dict[DIFF_LEMMA].occurrence_counter
    not_in_bin_set = extract_set_from_list(categories.categories_dict[NOT_IN_BIN].element_list)
    dist_not_in_bin = len(not_in_bin_set)
    sum_not_in_bin = categories.categories_dict[NOT_IN_BIN].occurrence_counter

    print()
    print("========= REPORT: substitutions same inflection paradigm or not ============")
    print("")
    print("Total number of substitutions: " + str(subst_counter))
    print("Total number of distinctive same lemma substitutions: " + str(dist_same))
    print("Total number of same lemma substitutions: " + str(sum_same) + ' (' + '%.2f' % (
        sum_same / subst_counter * 100) + '%)')
    print("Total number of distinctive different lemma substitutions: " + str(dist_diff))
    print("Total number of different lemma substitutions: " + str(sum_diff) + ' (' + '%.2f' % (
        sum_diff / subst_counter * 100) + '%)')
    print("")
    print("Distinctive words not found in BÍN: " + str(dist_not_in_bin))
    print("Total number of substitutions of words not found in BÍN: " + str(sum_not_in_bin) + ' (' + '%.2f' % (
        sum_not_in_bin / subst_counter * 100) + '%)')
    print("")


def _create_categories():
    categories = Categories()
    categories.create_category(SAME_LEMMA)
    categories.create_category(DIFF_LEMMA)
    categories.create_category(NOT_IN_BIN)

    return categories


def find_same_lemma(ops_list, bin_list, out_dir):

    # dictionary of BÍN word forms
    bin_dict = init_bin_dict(bin_list)

    categories = _create_categories()

    subst_counter = 0

    # Examine all substitutions, look up in the bin_dict if the reference word and the hypothesis might
    # be representations of the same lemma. Collect statistics.

    for line in ops_list:
        op, ref, hyp, cnt = line.split()

        if not op == 'substitution':
            continue

        subst_counter += int(cnt)

        if ref not in bin_dict:
            categories.add_to_dict(NOT_IN_BIN, [ref])
            categories.update_counter(NOT_IN_BIN, int(cnt))
            continue

        found = False
        lemma_list = bin_dict[ref]

        for l in lemma_list:
            if hyp in l.word_forms:
                categories.add_to_dict(SAME_LEMMA, [ref, hyp, cnt])
                categories.update_counter(SAME_LEMMA, int(cnt))
                found = True
                break

        if not found:
            categories.add_to_dict(DIFF_LEMMA, [ref, hyp, cnt])
            categories.update_counter(DIFF_LEMMA, int(cnt))

    categories.print_to_files(out_dir)

    print_info(categories, subst_counter)

    print("")


def parse_args():
    parser = argparse.ArgumentParser(description='Compare words in substitution ops - same lemma or not', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('i', type=str, help='ops file')
    parser.add_argument('b', type=argparse.FileType('r'), help='bin file')
    parser.add_argument('-o', type=str, default='kaldi_ops_by_lemma', help='Output directory')

    return parser.parse_args()


def main():

    args = parse_args()

    ops_file = verification.verify_input(args.i, 'ops')
    if not ops_file:
        print('Input directory / input file "{0}" not found. '
              'Please provide a path to wer_details/ops'.format(args.i))
        raise Exception()

    if args.o == 'kaldi_ops_by_lemma':
        out_dir = args.o + '_' + time.strftime("%Y%m%d-%H%M%S") + '/'
    else:
        out_dir = args.o
        if not out_dir.endswith('/'):
            out_dir += '/'

    # allow to overwrite existing directory
    try:
        os.mkdir(out_dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass

    ops_list = open(ops_file).read().splitlines()
    bin_list = args.b.read().splitlines()

    find_same_lemma(ops_list, bin_list, out_dir)


if __name__ == '__main__':
    main()