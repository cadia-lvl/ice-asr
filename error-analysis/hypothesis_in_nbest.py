#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# Comparing n-best results from a Kaldi lattice to reference utterances
#
# nbest file format:
#   utt-id-<number> hypothesis
# e.g.: is_is-althingi1_01-2011-11-30T16:18:39.715490-2 hann telur að framið hafi verið verkfallsbrot
#
# ref file format:
#   utt-id ref reference (with '***' for insertions in best-path hypothesis)
# e.g.: is_is-althingi1_01-2011-11-30T16:18:39.715490 ref  ***  telur  að  framið  hafi  verið  verkfallsbrot
#
# Comparison results:
#   1) If hypothesis no 1 matches reference: increment counter, ignore utterance
#   2) If some hypothesis from the n-best list matches the reference, collect the ref-correct hyp pair
#   3) If no hypothesis from the n-best list matches the reference, collect all hypothesises and the reference
#

import argparse
import os
import errno
import time

from pathlib import Path


NBEST_HYPOTHESIS_FILENAME = '/words_text.txt'


class NBestStatistics:

    def __init__(self):
        self.correct_count = 0
        self.not_in_nbest_count = 0
        self.in_nbest_count = 0
        # a dictionary of utterances found in nbest, with rank as key and utterance lists as value
        self.nbest_by_rank = {}
        self.not_in_nbest_list = {}

    def increment_nbest(self, nbest_ind, nbest_info):
        if nbest_ind == 0:
            self.correct_count += 1
        else:
            nbest_list = self.nbest_by_rank[nbest_ind] if nbest_ind in self.nbest_by_rank else []
            nbest_list.append(nbest_info)
            self.nbest_by_rank[nbest_ind] = nbest_list
            self.in_nbest_count += 1

    def increment_all_wrong(self, utt_id, utt):
        self.not_in_nbest_list[utt_id] = utt
        self.not_in_nbest_count += 1


def init_hyp_list(nbest_input):
    print(nbest_input)
    p = Path(nbest_input)
    hyp_list = []
    if p.is_dir():
        for arch in p.iterdir():
            if arch.is_dir():
                q = str(arch) + NBEST_HYPOTHESIS_FILENAME
                print(q)
                with open(q) as f:
                    hyp_list = hyp_list + f.readlines()

    else:
        hyp_list = nbest_input.readlines()

    return hyp_list


def init_references(referencefile):
    references = {}

    for line in referencefile.readlines():
        utt_id, info, *utt_arr = line.split()
        if info != 'ref':
            continue

        # remove insertion symbols from ref to be able to match the original reference from nbest
        utt = ' '.join(utt_arr).replace('***', '')
        references[utt_id] = utt.strip()

    return references


def init_nbest(hypothesisfile):
    nbest_hypothesis = {}
    hyp_list = init_hyp_list(hypothesisfile)

    for line in hyp_list:
        line_arr = line.split()
        full_id = line_arr[0]
        last_dash = full_id.rindex('-')
        id = full_id[0:last_dash]
        if len(line_arr) >= 2:
            utt = ' '.join(line_arr[1:]).strip()
        else:
            utt = ''

        if id in nbest_hypothesis:
            hyp_list = nbest_hypothesis[id]
            hyp_list.append(utt)

        else:
            hyp_list = [utt]
            nbest_hypothesis[id] = hyp_list

    return nbest_hypothesis


def write_array_list_to_file(filename, list_to_write):
    items_as_arrays = [['NBEST-ID', 'CORRECT-HYP', 'NBEST-RANK-1']]
    items_as_arrays.extend(list_to_write)

    widths = [max(map(len, col)) for col in zip(*items_as_arrays)]

    with open(filename, 'w') as out_file:
        for row in items_as_arrays:
            out_file.write("  ".join((val.ljust(width) for val, width in zip(row, widths))) + '\n')


def write_stats(out_dir, stats):
    print('Correct hypotheses: ' + str(stats.correct_count))
    print('In nbest: ' + str(stats.in_nbest_count))
    print('Not in nbest: ' + str(stats.not_in_nbest_count))

    in_nbest_list = []
    for key in sorted(stats.nbest_by_rank):
        for arr in stats.nbest_by_rank[key]:
            in_nbest_list.append(arr)

    write_array_list_to_file(out_dir + 'in_nbest.txt', in_nbest_list)

    with open(out_dir + 'all_wrong.txt', 'w') as out_all_wrong:
        for key in stats.not_in_nbest_list.keys():
            for hyp in stats.not_in_nbest_list[key]:
                out_all_wrong.write(key + '\t' + hyp + '\n')


def find_in_nbest_path(referencefile, hypothesisfile, out_dir):
    # search for reference utterances in nbest-lists,
    # collect number of correct (nbest index == 0), utterances contained in nbest with rank,
    # and utterances not contained in the nbest list.

    references = init_references(referencefile)
    nbest = init_nbest(hypothesisfile)

    stats = NBestStatistics()

    for utt_id in nbest.keys():
        ref_utt = references[utt_id]

        if ref_utt in nbest[utt_id]:
            nbest_ind = nbest[utt_id].index(ref_utt)
            nbest_info_arr = [utt_id + '-' + str(nbest_ind + 1), ref_utt, nbest[utt_id][0]]
            stats.increment_nbest(nbest_ind, nbest_info_arr)
        else:
            all_wrong_list = nbest[utt_id]
            all_wrong_list.append('REF='+ref_utt)
            stats.increment_all_wrong(utt_id, all_wrong_list)

    write_stats(out_dir, stats)


def parse_args():
    parser = argparse.ArgumentParser(description='Comparison of Kaldi nbest hypothesis file to reference utterances',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('r', type=argparse.FileType('r'), help='Reference file')
    parser.add_argument('h', type=str, help='Kaldi nbest file OR a directory of archives with nbest files')
    parser.add_argument('-o', type=str, default='kaldi_per_utt_nbest', help='Output directory')

    return parser.parse_args()


def main():

    args = parse_args()
    referencefile = args.r
    hypothesisfile = args.h

    if args.o == 'kaldi_per_utt_nbest':
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

    find_in_nbest_path(referencefile, hypothesisfile, out_dir)


if __name__ == '__main__':
    main()
