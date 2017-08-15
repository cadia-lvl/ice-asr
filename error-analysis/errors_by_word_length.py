#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# A script for the analysis of the ops file from the Kaldi scoring results.
# Analyses the reference words and hypothesis words seperately, word by word, collects numbers on:
#   - total occurrences
#   - correct
#   - insertions (hypothesis only)
#   - deletions (reference only)
#   - substitutions
#
#   Collects statistics based on word length.
#
#   Input format (not tabs, only spaces for formatting):
#
#   operation(corr, ins, del, sub)    reference    hypothesis   count
#

import argparse
import time
import os
import errno
import operationstats


class WordMaps:

    # Holds operation information on reference words and hypothesis words separately
    def __init__(self):
        self.reference_map = {}
        self.hypothesis_map = {}

    def add_operation(self, ref_hyp_map, operation, count):
        ref = ref_hyp_map['ref']
        hyp = ref_hyp_map['hyp']

        ref_stat = self.reference_map[ref] if ref in self.reference_map else operationstats.OperationStatistics(ref)
        ref_stat.increment(operation, count)
        self.reference_map[ref] = ref_stat

        hyp_stat = self.hypothesis_map[hyp] if hyp in self.hypothesis_map else operationstats.OperationStatistics(hyp)
        hyp_stat.increment(operation, count)
        self.hypothesis_map[hyp] = hyp_stat


def accumulate_statistics(stat_list):
    # Accumulates statistics from 'stat_list' based on word length
    count_map = {}

    for op_stat in stat_list:
        if op_stat.word == '***':
            continue
        word_len = len(op_stat.word)
        acc_word = count_map[word_len] if word_len in count_map else operationstats.OperationStatistics(str(word_len))
        acc_word.increment_all(op_stat)
        count_map[word_len] = acc_word

    return list(count_map.values())


def write_file(filename, list_to_write):
    out_file = open(filename, 'w')
    header = ['WORD', 'OCC', 'C', 'D', 'I', 'S', '%Correct']
    items_as_arrays = [header]
    for item in list_to_write:
        items_as_arrays.append(item.print_array())

    widths = [max(map(len, col)) for col in zip(*items_as_arrays)]

    for row in items_as_arrays:
        out_file.write("  ".join((val.ljust(width) for val, width in zip(row, widths))) + '\n')

    out_file.close()


def get_overall_impact(accumulated_stats):

    sum_occurrences = 0
    sum_errors = 0

    for item in accumulated_stats:
        sum_occurrences += item.occurrences
        sum_errors += item.deletions
        sum_errors += item.substitutions
        sum_errors += item.insertions

    print(str(sum_errors))
    print(str(sum_occurrences))
    for item in accumulated_stats:
        errors = item.deletions + item.insertions + item.substitutions
        print(item.word + '\t' + str(item.occurrences) + '\t' + str(errors) + '\t' + '%.2f' % (errors/sum_errors))


def write_results(results_map, no_of_top_occurrences, out_dir):
    references_list = list(results_map.reference_map.values())
    references_list.sort(key=lambda x: x.occurrences, reverse=True)

    hypothesis_list = list(results_map.hypothesis_map.values())
    hypothesis_list.sort(key=lambda x: x.occurrences, reverse=True)

    write_file(out_dir + 'references_sorted_by_occurrence_count.txt', references_list)
    write_file(out_dir + 'hypothesis_sorted_by_occurrence_count.txt', hypothesis_list)

    references_list.sort(key=lambda x: (len(x.word), x.occurrences), reverse=True)
    hypothesis_list.sort(key=lambda x: (len(x.word), x.occurrences), reverse=True)

    write_file(out_dir + 'references_sorted_by_length.txt', references_list)
    write_file(out_dir + 'hypothesis_sorted_by_length.txt', hypothesis_list)

    references_list.sort(key=lambda x: x.occurrences, reverse=True)
    hypothesis_list.sort(key=lambda x: x.occurrences, reverse=True)

    top_references = references_list[:no_of_top_occurrences]
    top_hypothesis = hypothesis_list[:no_of_top_occurrences]

    top_references.sort(key=lambda x: ((x.correct / x.occurrences), x.occurrences), reverse=True)
    top_hypothesis.sort(key=lambda x: ((x.correct / x.occurrences), x.occurrences), reverse=True)

    write_file(out_dir + 'references_sorted_by_accuracy.txt', top_references)
    write_file(out_dir + 'hypothesis_sorted_by_accuracy.txt', top_hypothesis)

    accumulated_statistics_ref = accumulate_statistics(references_list)
    accumulated_statistics_hyp = accumulate_statistics(hypothesis_list)

    write_file(out_dir + 'references_accumulated.txt', accumulated_statistics_ref)
    write_file(out_dir + 'hypothesis_accumulated.txt', accumulated_statistics_hyp)

    get_overall_impact(accumulated_statistics_ref)


def analyse_by_word_length(ops_lines, no_of_top_occurrences, out_dir):

    result_maps = WordMaps()

    for line in ops_lines:
        operation, ref, hyp, count_str = line.split()
        count = int(count_str)
        ref_hyp = {'ref': ref, 'hyp': hyp}
        result_maps.add_operation(ref_hyp, operation, count)

    write_results(result_maps, no_of_top_occurrences, out_dir)


def parse_args():
    parser = argparse.ArgumentParser(description='Statistics on Kaldi ops file',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('i', type=argparse.FileType('r'), help='Kaldi ops file')
    parser.add_argument('-o', type=str, default='kaldi_ops_by_length', help='Output directory')
    parser.add_argument('-n', type=int, default=None,
                        help='Number of most frequent words to include in accuracy analysis')

    return parser.parse_args()


def main():
    # verfiy input file - has to be an ops file
    args = parse_args()
    input_file_list = args.i.readlines()

    if args.o == 'kaldi_ops_by_length':
        out_dir = args.o + '_' + time.strftime("%Y%m%d-%H%M%S") + '/'
    else:
        out_dir = args.o
        if not out_dir.endswith('/'):
            out_dir += '/'

    try:
        os.mkdir(out_dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass

    if args.n:
        top_occurrences = args.n
    else:
        top_occurrences = len(input_file_list)

    analyse_by_word_length(input_file_list, top_occurrences, out_dir)


if __name__ == '__main__':
    main()
