#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

About kaldi error analysis

"""

import sys
import os
import os.path
import errno
import argparse

import utterance
import categories
import bin_checker
import errors_by_context
import errors_by_frequency
import errors_by_speaker_class
import errors_by_word_length
import hypothesis_in_nbest


class ErrorAnalysis:

    def __init__(self):
        self.analysis_steps = []
        self.wer_details_files = []
        self.bin = ''
        self.speakers = ''
        self.freq_file = ''

    def perform_analysis(self, out_dir, top_freq=0, top_occ=0):
        print('Starting error analysis ...')
        print('categories (per-utt) analyzis ...')
        # print(self.wer_details_files[1])
        utterance_dict = utterance.Utterance.init_utterance_dict(open(self.wer_details_files[1]))
        categories.analyse_input(utterance_dict, out_dir)

        print('BIN checker ...')
        # print(self.wer_details_files[2])
        # for testing - bin takes a few seconds ...
        self.bin = ''
        if not self.bin:
            print('no BÍN data, skipping bin analysis ...')
        else:
            ops_list = open(self.wer_details_files[2]).read().splitlines()
            bin_list = open(self.bin).read().splitlines()
            bin_checker.find_same_lemma(ops_list, bin_list, out_dir)

        print('by context ...')
        errors_by_context.analyse_errors_by_context(open(self.wer_details_files[1]), out_dir)

        if not self.freq_file:
            print('no frequency data, skipping frequency analysis ...')
        else:
            print('by frequency ...')
            input_file_list = open(self.wer_details_files[2]).readlines()
            if top_freq == 0:
                top_freq = len(input_file_list)

            errors_by_frequency.analyse_by_corpus_frequency(input_file_list, open(self.freq_file), out_dir, top_freq)

        if not self.speakers:
            print('no speaker data, skipping per speaker feature analysis ...')
            print()
        else:
            print('by speaker feature ...')
            errors_by_speaker_class.analyse_by_speaker_feature(open(self.wer_details_files[0]), open(self.speakers), out_dir)

        print('by word length ...')
        input_file_list = open(self.wer_details_files[2]).readlines()
        if top_occ == 0:
            top_occ = len(input_file_list)

        errors_by_word_length.analyse_by_word_length(input_file_list, top_occ, out_dir)

        if len(self.wer_details_files) < 4:
            print('no nbest data available, skipping nbest analysis ...')
        else:
            print('nbest analysis ...')
            hypothesis_in_nbest.find_in_nbest_path(open(self.wer_details_files[1]), self.wer_details_files[3], out_dir)




#####################################
# These are the data files needed for some of the error analysis scripts - if not present, the corresponding
# analysis will be skipped.
# Change these filenames if needed to fit your filenames!
#####################################

BIN = 'SHsnid_lower.csv'                          # The whole BÍN db as csv file
FREQ_FILE = 'leipzig_freq.txt'              # Word - frequency table, ideally from the language model corpus
SPEAKER_FEATURES = 'speakers.txt'   # Mapping of speaker-ids to some features, typically gender


def verify_wer_details(inp_dir):
    error_analysis = ErrorAnalysis()
    sep = '/'
    if inp_dir.endswith('/'):
        sep = ''
    if os.path.isfile(inp_dir + sep + 'per_spk'):
        error_analysis.wer_details_files.append(inp_dir + sep + 'per_spk')
    if os.path.isfile(inp_dir + sep + 'per_utt'):
        error_analysis.wer_details_files.append(inp_dir + sep + 'per_utt')
    if os.path.isfile(inp_dir + sep + 'ops'):
        error_analysis.wer_details_files.append(inp_dir + sep + 'ops')
    if os.path.isdir(inp_dir + sep + 'nbest'):
        error_analysis.wer_details_files.append(inp_dir + sep + 'nbest')

    return error_analysis


def verify_data_dir(data_dir, error_analysis):
    sep = '/'
    if data_dir.endswith('/'):
        sep = ''

    if os.path.isfile(data_dir + sep + BIN):
        error_analysis.bin = data_dir + sep + BIN
    if os.path.isfile(data_dir + sep + FREQ_FILE):
        error_analysis.freq_file = data_dir + sep + FREQ_FILE
    if os.path.isfile(data_dir + sep + SPEAKER_FEATURES):
        error_analysis.speakers = data_dir + sep + SPEAKER_FEATURES

    return error_analysis


# https://stackoverflow.com/questions/11415570/directory-path-types-with-argparse
def readable_dir(inp_dir):

    if not os.path.isdir(inp_dir):
        raise argparse.ArgumentTypeError('readable_dir:{} is not a valid path'.format(inp_dir))
    if os.access(inp_dir, os.R_OK):
        return inp_dir
    else:
        raise argparse.ArgumentTypeError('readalbe_dir:{} is not readable!'.format(inp_dir))


def writeable_dir(out_dir):
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(out_dir):
            pass
        else:
            raise argparse.ArgumentTypeError('writeable_dir: could not create output directory {}!'.format(out_dir))

    return out_dir


def parse_args():
    parser = argparse.ArgumentParser(description='Error analysis of Kaldi wer_details directory',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('i', type=readable_dir, help='Path to wer_details')
    parser.add_argument('-o', type=writeable_dir, help='Output directory', default='kaldi_error_analysis_results/')
    parser.add_argument('-data_dir', type=readable_dir,
                        help='Path to BIN, frequency file and speaker-id feature mapping file')

    return parser.parse_args()


def main():
    args = parse_args()
    error_analysis = verify_wer_details(args.i)

    if not args.data_dir:
        print("No data dir provided!")
    else:
        error_analysis = verify_data_dir(args.data_dir, error_analysis)

    out_dir = args.o
    error_analysis.perform_analysis(out_dir)


if __name__ == '__main__':
    sys.exit(main())