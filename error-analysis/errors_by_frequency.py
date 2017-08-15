#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Are less frequent words more likely to cause errors than more frequent ones?
Are less frequent words replaced with more frequent words?

Input format ops file (not tabs, only spaces for formatting):

   description(corr, ins, del, sub)    reference    hypothesis   count

Frequencies from LM corpus:

    word frequency


TODO: Combine with errors_by_word_length!

"""

import argparse
import os
import time
import errno
import operationstats


class WordMaps:

    # Holds operation information on reference words and hypothesis words separately
    def __init__(self):
        self.reference_map = {}
        self.hypothesis_map = {}
        self.subst_lt_with_gt = [] # substitutions of more freq with less freq or longer with shorter
        self.subst_gt_with_lt = [] # substitutions of less freq with more freq or shorter with longer
        self.counter_lt_with_gt = 0
        self.counter_gt_with_lt = 0

    def add_operation(self, ref_hyp_map, freq_map, operation, count):
        ref = ref_hyp_map['ref']
        hyp = ref_hyp_map['hyp']
        ref_freq = freq_map[ref] if ref in freq_map else 0
        hyp_freq = freq_map[hyp] if hyp in freq_map else 0

        ref_stat = self.reference_map[ref] if ref in self.reference_map \
            else operationstats.OperationStatistics(ref, ref_freq)
        ref_stat.increment(operation, count)
        self.reference_map[ref] = ref_stat

        hyp_stat = self.hypothesis_map[hyp] if hyp in self.hypothesis_map \
            else operationstats.OperationStatistics(hyp, hyp_freq)
        hyp_stat.increment(operation, count)
        self.hypothesis_map[hyp] = hyp_stat

        if operation == 'substitution':
            if hyp_freq > ref_freq:
                self.subst_lt_with_gt.append(
                    ref + ' (' + str(ref_freq) + ') replaced by ' + hyp + ' (' + str(hyp_freq) + ') ' + str(
                        count) + ' times')
                self.counter_lt_with_gt += count
            else:
                self.subst_gt_with_lt.append(
                    ref + ' (' + str(ref_freq) + ') replaced by ' + hyp + ' (' + str(hyp_freq) + ') ' + str(
                        count) + ' times')
                self.counter_gt_with_lt += count


def accumulate_statistics(stat_list):
    # Accumulates statistics from 'stat_list' based on word frequency
    count_map = {}

    for op_stat in stat_list:
        if op_stat.word == '***':
            continue
        word_freq = op_stat.corpus_frequency
        acc_word = count_map[word_freq] if word_freq in count_map else operationstats.OperationStatistics(str(word_freq))
        acc_word.increment_all(op_stat)
        count_map[word_freq] = acc_word

    return list(count_map.values())


def write_array_list_to_file(filename, list_to_write):
    out_file = open(filename, 'w')
    header = ['WORD', 'OCC', 'C', 'D', 'I', 'S', '%Correct', 'FREQ']
    items_as_arrays = [header]
    for item in list_to_write:
        items_as_arrays.append(item.print_array(True))

    widths = [max(map(len, col)) for col in zip(*items_as_arrays)]

    for row in items_as_arrays:
        out_file.write("  ".join((val.ljust(width) for val, width in zip(row, widths))) + '\n')

    out_file.close()


def write_file(filename, list_to_write):
    with open(filename, 'w') as f:
        for line in list_to_write:
            f.write(line + '\n')


def init_frequency_map(freq_file):
    freq_map = {}
    for line in freq_file.readlines():
        word, freq = line.split()
        freq_map[word] = int(freq)
    return freq_map


def write_results(result_maps, out_dir, top_freq):

    references_list = list(result_maps.reference_map.values())
    references_list.sort(key=lambda x: x.correct, reverse=True)

    hypothesis_list = list(result_maps.hypothesis_map.values())
    hypothesis_list.sort(key=lambda x: x.correct, reverse=True)

    # write by correct?

    references_list.sort(key=lambda x: x.corpus_frequency, reverse=True)
    hypothesis_list.sort(key=lambda x: x.corpus_frequency, reverse=True)

    top_references = references_list[:top_freq]
    top_hypothesis = hypothesis_list[:top_freq]

    top_references.sort(key=lambda x: ((x.correct / x.occurrences), x.occurrences, x.corpus_frequency), reverse=True)
    top_hypothesis.sort(key=lambda x: ((x.correct / x.occurrences), x.occurrences, x.corpus_frequency), reverse=True)

    write_array_list_to_file(out_dir + 'references_by_correct.txt', top_references)
    write_array_list_to_file(out_dir + 'hypothesis_by_correct.txt', top_hypothesis)

    top_references.sort(key=lambda x: (x.occurrences, (x.correct / x.occurrences), x.corpus_frequency), reverse=True)
    top_hypothesis.sort(key=lambda x: (x.occurrences, (x.correct / x.occurrences), x.corpus_frequency), reverse=True)

    write_array_list_to_file(out_dir + 'references_by_occurrence.txt', top_references)
    write_array_list_to_file(out_dir + 'hypothesis_by_occurrence.txt', top_hypothesis)

    top_references.sort(key=lambda x: (x.corpus_frequency, (x.correct / x.occurrences)), reverse=True)
    top_hypothesis.sort(key=lambda x: (x.corpus_frequency, (x.correct / x.occurrences)), reverse=True)

    write_array_list_to_file(out_dir + 'references_by_frequency.txt', top_references)
    write_array_list_to_file(out_dir + 'hypotheses_by_frequency.txt', top_hypothesis)

    write_file(out_dir + 'subst_more_freq_with_less_freq.txt', result_maps.subst_gt_with_lt)
    write_file(out_dir + 'subst_less_freq_with_more_freq.txt', result_maps.subst_lt_with_gt)

    print('Substitutions of a less freq word with more freq word: ' + str(result_maps.counter_lt_with_gt))
    print('Substitutions of a more freq word with a les freq word: ' + str(result_maps.counter_gt_with_lt))


def analyse_by_corpus_frequency(ops_list, freq_file, out_dir, top_freq):

    freq_map = init_frequency_map(freq_file)

    result_maps = WordMaps()

    for line in ops_list:
        operation, ref, hyp, count_str = line.split()
        count = int(count_str)

        ref_hyp = {'ref': ref, 'hyp': hyp}
        result_maps.add_operation(ref_hyp, freq_map, operation, count)

    write_results(result_maps, out_dir, top_freq)


def parse_args():
    parser = argparse.ArgumentParser(description='Statistics on Kaldi ops file by corpus frequency',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('i', type=argparse.FileType('r'), help='Kaldi ops file')
    parser.add_argument('f', type=argparse.FileType('r'), help='Frequency file')
    parser.add_argument('-o', type=str, default='kaldi_ops_by_corpus_freq', help='Output directory')
    parser.add_argument('-n', type=int, help='Number of most frequent words to include in accuracy analysis')

    return parser.parse_args()


def main():

    # TODO: argument valdiation
    args = parse_args()
    input_file = args.i
    freq_file = args.f

    if args.o == 'kaldi_ops_by_corpus_freq':
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

    input_file_list = input_file.readlines()
    if args.n:
        top_freq = args.n
    else:
        top_freq = len(input_file_list)

    analyse_by_corpus_frequency(input_file_list, freq_file, out_dir, top_freq)


if __name__ == '__main__':
    main()
