#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Analyze the errors from Kaldi decoding, per_utt results:

    is_is-althingi1_04-2011-11-30T16:55:30.601205 ref  símaskráin  ***  komin  út
    is_is-althingi1_04-2011-11-30T16:55:30.601205 hyp  símaskráin   er  komin  út
    is_is-althingi1_04-2011-11-30T16:55:30.601205 op        C       I     C     C
    is_is-althingi1_04-2011-11-30T16:55:30.601205 #csid 3 0 1 0

    Extract these kinds of information:
    1) Correct decoded utterances
    2) Utterances with only one deletion or insertion error
    3) Utterances with only one substitution error and edit distance == 1
    4) Utterances with only one substitution error and edit distance > 1
    5) Errors that could be caused by writing a compound / a compound in two words (compound vs two words)
    6) Other errors, i.e. errors that do not match any of the above categories

"""

import os
import time
import errno
import argparse

import Levenshtein

import utterance
import verification

# Error categories (add new categories when needed):
CORRECT = 'correct'
COMPOUNDS = 'compounds'     # utterances with compound errors
ONE_INS_DEL = 'one_inserted_or_deleted'     # utterances with only one insertion or deletion
LS_ONE = 'levenshtein_one'                  # utterances with one substitution and edit distance == 1
LS_GT_ONE = 'levenshtein_gt_one'            # utterances with one substitution and edit distance > 1
OTHER = 'other_errors'                    # non defined errors


# Extract Categories and Category to own module

class Categories:

    def __init__(self):
        self.categories_dict = {}

    def create_category(self, name):
        if name in self.categories_dict:
            return
        else:
            self.categories_dict[name] = Category(name)

    def check_for_category(self, category):
        if category not in self.categories_dict:
            print(category + ' is not in error dictionary, creating new entry')
            self.create_category(category)

    def add_to_dict(self, category, element):
        if len(element) == 0:
            return

        self.check_for_category(category)
        self.categories_dict[category].add_element(element)

    def update_counter(self, category, counter):
        self.check_for_category(category)
        self.categories_dict[category].update_counter(counter)

    def print_to_stdout(self):
        errors = 0
        print()
        print("========== Analyzing per_utt file from Kaldi decoding ==============\n")
        print("Correct decoded utterances: " + str(len(self.categories_dict[CORRECT].element_list)))
        print()
        for cat in sorted(self.categories_dict):
            if cat != CORRECT:
                print('Utterances with ' + cat + ': ' + str(len(self.categories_dict[cat].element_list)))
                print('Total occurrences of ' + cat + ' : ' + str(self.categories_dict[cat].occurrence_counter))
            if cat != CORRECT and cat != COMPOUNDS:
                errors += self.categories_dict[cat].occurrence_counter

        print("")
        print("Total errors: " + str(errors))
        print()

    def print_to_files(self, out_dir=''):
        for cat in self.categories_dict.keys():
            write_file(out_dir + cat + '.txt', self.categories_dict[cat].element_list)


class Category:

    def __init__(self, name):
        self.name = name
        self.element_list = []
        self.occurrence_counter = 0

    def add_element(self, element):
        self.element_list.append(element)

    def update_counter(self, counter):
        self.occurrence_counter += counter


def _check_for_compounds(utterance, error_cats):
    """
    Sometimes decoding errors are caused by inconsistencies in compound writing: either the reference uses a
    compound whereas the hypothesis uses two words or vice versa.
    Extract such pairs and collect.
    :param utterance:
    :return: a list containing ref and hyp and potential compounds if found, otherwise return an empty list
    """
    ref_pairs = []
    hyp_pairs = []
    ref_arr = utterance.ref.split()
    hyp_arr = utterance.hyp.split()

    results = []

    # join all bigrams in both texts (ref, hyp) to a word,
    # search for corresponding words (=compounds) in the other text
    # increment error counter by 2 for each found compound, since
    for ind in range(0, len(ref_arr) - 1):
        ref_pairs.append(ref_arr[ind] + ref_arr[ind + 1])

    for ind in range(0, len(hyp_arr) - 1):
        hyp_pairs.append(hyp_arr[ind] + hyp_arr[ind + 1])

    for pair in ref_pairs:
        if pair in hyp_arr:
            results.append(pair)

    for pair in hyp_pairs:
        if pair in ref_arr:
            results.append(pair)

    if len(results) > 0:
        # each compound error means one D or I and one S - multiply found pairs with 2 to get error count
        return [utterance.utt_id, utterance.ref, utterance.hyp, ' : '] + results, len(results) * 2
    else:
        return [], 0


def write_file(filename, list_of_lists):
    with open(filename, 'w') as f:
        for elem in list_of_lists:
            f.write('\t'.join(elem) + '\n')


# update if error categories change
def _create_error_categories():
    error_cats = Categories()
    error_cats.create_category(CORRECT)
    error_cats.create_category(COMPOUNDS)
    error_cats.create_category(ONE_INS_DEL)
    error_cats.create_category(LS_ONE)
    error_cats.create_category(LS_GT_ONE)
    error_cats.create_category(OTHER)

    return error_cats


def analyse_input(utterance_dict, out_dir):
    """
    Analyses the per_utt file from Kaldi decoding and scoring. Collects all correct utterances and sorts and counts
    utterances with errors of different categories. Writes all utterances for each category into it's own file
    and prints out the number of utterances in each category.

    :param utterance_file:
    :return:
    """
    # when adding error categories consider splitting up this method!

    error_cats = _create_error_categories()

    # non defined error counts
    other_errors_sum = 0

    for key in utterance_dict.keys():
        utterance = utterance_dict[key]
        sum_errors = utterance.sum_errors()

        if sum_errors == 0:
            error_cats.add_to_dict(CORRECT, [utterance.utt_id, utterance.ref, '0'])
            continue

        id_ref_hyp = [utterance.utt_id, utterance.ref, utterance.hyp]

        # check for compounds:
        comp_elem, comp_errors = _check_for_compounds(utterance, error_cats)
        if len(comp_elem) > 0:
            error_cats.add_to_dict(COMPOUNDS, comp_elem)
            error_cats.update_counter(COMPOUNDS, comp_errors)

        ref_arr = utterance.ref.split()

        # utterance is more than two words and has only one Ins or Del operation
        if len(ref_arr) >= 2 and sum_errors == 1 and utterance.sub == 0:
            error_cats.add_to_dict(ONE_INS_DEL, id_ref_hyp)
            error_cats.update_counter(ONE_INS_DEL, 1)

        # utterance has only one substitution error - check if Levenshtein dist is only 1
        elif sum_errors == 1 and utterance.sub == 1:
            hyp_arr = utterance.hyp.split()
            for ind in range(0, len(hyp_arr)):
                if ref_arr[ind] != hyp_arr[ind]:
                    dist = Levenshtein.distance(ref_arr[ind], hyp_arr[ind])
                    if dist == 1:
                        error_cats.add_to_dict(LS_ONE, id_ref_hyp + [ref_arr[ind], hyp_arr[ind]])
                        error_cats.update_counter(LS_ONE, 1)
                    else:
                        error_cats.add_to_dict(LS_GT_ONE,
                                               id_ref_hyp + [str(utterance.op), ref_arr[ind], hyp_arr[ind], str(dist)])
                        error_cats.update_counter(LS_GT_ONE, 1)

        else:
            error_cats.add_to_dict(OTHER, id_ref_hyp + [str(utterance.op), str(sum_errors)])
            error_cats.update_counter(OTHER, sum_errors)

    error_cats.print_to_stdout()
    error_cats.print_to_files(out_dir)


def parse_args():
    parser = argparse.ArgumentParser(description='Categorizes errors by edit distance, extracts compounds', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('i', type=str, help='per_utt file')
    parser.add_argument('-o', type=str, default='kaldi_error_cats', help='Output directory')

    return parser.parse_args()


def main():

    args = parse_args()

    utt_file = verification.verify_input(args.i, 'per_utt')
    if not utt_file:
        print('Input directory / input file "{0}" not found. '
              'Please provide a path to wer_details/per_utt'.format(args.i))
        raise Exception()

    if args.o == 'kaldi_error_cats':
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

    utterance_dict = utterance.Utterance.init_utterance_dict(open(utt_file))
    analyse_input(utterance_dict, out_dir)


if __name__ == '__main__':
    main()