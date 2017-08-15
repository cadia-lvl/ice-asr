#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analysing errors from kaldi's per_utt by word class.

Input files:

Kaldi's per_utt:

    is_is-althingi1_04-2011-11-30T16:55:30.601205 ref  símaskráin  ***  komin  út
    is_is-althingi1_04-2011-11-30T16:55:30.601205 hyp  símaskráin   er  komin  út
    is_is-althingi1_04-2011-11-30T16:55:30.601205 op        C       I     C     C
    is_is-althingi1_04-2011-11-30T16:55:30.601205 #csid 3 0 1 0


A pos-tagged version of the reference texts in json format (from Greynir.is):

{
  "result": [
    [
      [
        "Telur",
        "sfg3en"
      ],
      [
        "að",
        "c"
      ],
      ...
    ],
    [
    ...
    ]
 ]
}

A pos-tagged version of the reference texts in plain format (from IceTagger):

Enska nven
bönnuð sþgven
í aþ
kínverskum lkfþsf
miðlum lkfþsf <UNKNOWN>
. .
Allir fokfn
fórust sfm3fþ
í aþ
flugslysinu nheþg <UNKNOWN>
. .

"""

import argparse
import os
import time
import errno
import json
import re

import utterance

DEL_SYMBOL = '***'

class WordClassStatistics:

    def __init__(self, wc):
        self.wordclass = wc
        self.correct = 0
        self.subs = 0
        self.delete = 0
        self.error_pairs = []

    def get_ratio_wrong(self):
        return '%.2f' % ((self.subs + self.delete)/self.get_total_occurrences())

    def get_ratio_subs(self):
        return '%.2f' % (self.subs/(self.get_total_occurrences()))

    def get_ratio_del(self):
        return '%.2f' % (self.delete / (self.get_total_occurrences()))

    def get_total_occurrences(self):
        return self.correct + self.subs + self.delete

    def update_error(self, err_str):
        if err_str == DEL_SYMBOL:
            self.delete += 1
        else:
            self.subs += 1


def extract_pos_tagged_sentences_plain(tagged_file):
    """IceNLP delivers tagged files one word-pos per line"""
    pos_tagged_sentences = {}

    sentence = ''
    tuple_list = []
    for line in tagged_file.readlines():
        line_arr = line.strip().split()
        if len(line_arr) < 2:
            #print('Missing correct format! ' + sentence)
            continue
        if line_arr[0] == '.':
           # print('FINISHED: ' + sentence)
            pos_tagged_sentences[sentence.strip()] = tuple_list
            sentence = ''
            tuple_list = []
        else:
            sentence += line_arr[0].lower() + ' '
            pair = (line_arr[0].lower(), line_arr[1])
            tuple_list.append(pair)

    return pos_tagged_sentences


def extract_pos_tagged_sentences_json(json_pos_tagged):
    """If we use Greynir API, tagged texts are in json format"""
    result_arr = json_pos_tagged['result']
    pos_tagged_sentences = {}
    for sent in result_arr:
        sentence = ''
        tuple_list = []
        for word in sent:
            if word[0] != '.':
                sentence += word[0].lower() + ' '
                pair = (word[0].lower(), word[1])
                tuple_list.append(pair)

        pos_tagged_sentences[sentence.strip()] = tuple_list
    return pos_tagged_sentences


def clean_utterance(utt):
    # clean utt so it can be easily matched to the texts extracted from the pos tagged file
    clean_utt = utt.replace(DEL_SYMBOL, '')
    clean_utt = re.sub(r'\s+', ' ', clean_utt).lower().strip()

    return clean_utt


def update_correct(word_class, pos_tag_stats):

    wc_statistics = pos_tag_stats[word_class] if word_class in pos_tag_stats else WordClassStatistics(word_class)
    wc_statistics.correct += 1
    pos_tag_stats[word_class] = wc_statistics


def print_statistics(results, out_dir):
    for wc in results.keys():
        print('========================')
        print(wc)
        print('Total occurrences: ' + str(results[wc].get_total_occurrences()))
        print('Error ratio: ' + str(results[wc].get_ratio_wrong()))
        print('---- Substitution ratio: ' + str(results[wc].get_ratio_subs()))
        print('---- Deletion ratio: ' + str(results[wc].get_ratio_del()))
        out = open(out_dir + wc + '_errors.txt', 'w')
        pairs = sorted(results[wc].error_pairs)
        for pair in pairs:
            out.write(pair + '\n')
        out.close()
    print('')


def pos_tagged(utt, pos_dict):

    if utt not in pos_dict:
        # could be an error, but also one word utterances are typically not contained in the pos tagged file
        # print('XXXX "' + utt + '" is not in pos-tagged file!')
        return False
    return True


def match_pairs(utterance, word_pos_pairs, pos_tag_statistics):

    if utterance.sum_errors == 0:
        # no errors, simply collect pos-tags
        for pair in word_pos_pairs:
            wc = pair[1][0]
            update_correct(wc, pos_tag_statistics)
    else:
        # more computation needed - which words exactly were misrecognized?
        ref_arr = utterance.ref.split()
        hyp_arr = utterance.hyp.split()
        # keep a separate counter for the word_pos_pair list to deal with DEL_SYMBOL in reference array,
        # would lead to mismatch between pos-tag indices and ref-arr indices
        pair_ind = 0
        for i in range(len(ref_arr)):
            if ref_arr[i] == DEL_SYMBOL:
                # only reference text is pos-tagged, we can't analyse deletions
                continue

            pair = word_pos_pairs[pair_ind]
            pair_ind += 1
            wc = pair[1][0]

            if ref_arr[i] == hyp_arr[i]:
                update_correct(wc, pos_tag_statistics)
            else:
                wc_statistics = pos_tag_statistics[wc] if wc in pos_tag_statistics else WordClassStatistics(wc)
                wc_statistics.update_error(hyp_arr[i])
                wc_statistics.error_pairs.append(ref_arr[i] + '\t' + hyp_arr[i])
                pos_tag_statistics[wc] = wc_statistics


def analyse_errors_by_pos_tag(utt_dict, pos_dict, out_dir):

    pos_tag_statistics = {}

    for utt_id in utt_dict.keys():
        utterance = utt_dict[utt_id]
        clean_utt = clean_utterance(utterance.ref)
        if not pos_tagged(clean_utt, pos_dict):
            continue

        word_pos_pairs = pos_dict[clean_utt]
        match_pairs(utterance, word_pos_pairs, pos_tag_statistics)

    print_statistics(pos_tag_statistics, out_dir)


def parse_args():
    parser = argparse.ArgumentParser(description='Error analysis of Kaldi per_utt file, by word class', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('i', type=argparse.FileType('r'), help='Kaldi per_utt file')
    parser.add_argument('p', type=argparse.FileType('r'), help='POS-tagged reference texts')
    parser.add_argument('-f', type=str, help='Format of the POS-tagged input file, default=IceTagger format')
    parser.add_argument('-o', type=str, default='kaldi_per_wordclass', help='Output directory')

    return parser.parse_args()


def main():

    args = parse_args()

    if args.o == 'kaldi_per_wordclass':
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

    if args.f == 'json':
        pos_tagged_file = args.p.read()
        pos_tagged = json.loads(pos_tagged_file)
        pos_tagged_dict = extract_pos_tagged_sentences_json(pos_tagged)
    else:
        pos_tagged_dict = extract_pos_tagged_sentences_plain(args.p)

    utterance_dict = utterance.Utterance.init_utterance_dict(args.i)

    analyse_errors_by_pos_tag(utterance_dict, pos_tagged_dict, out_dir)


if __name__ == '__main__':
    main()
