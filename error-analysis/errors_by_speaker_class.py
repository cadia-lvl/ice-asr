#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analyses per_spk file from Kaldi scoring - needs a second file containing a map of speaker ids and gender (or any other
speaker 'feature' like age or dialect), computes statistics based on speaker groups.

Kaldi's per_spk file:

SPEAKER                 id       #SENT      #WORD       Corr        Sub        Ins        Del        Err      S.Err
is_is-althingi1_01      raw        111        390        375         13         24          2         39         29
is_is-althingi1_01      sys        111        390      96.15       3.33       6.15       0.51      10.00      26.13
is_is-althingi1_04      raw        126        439        328         74         15         37        126         60
is_is-althingi1_04      sys        126        439      74.72      16.86       3.42       8.43      28.70      47.62
...
SUM                     raw       4810      17002      14875       1536        525        591       2652       1617
SUM                     sys       4810      17002      87.49       9.03       3.09       3.48      15.60      33.62


Mapping file should look like this:

<speaker-id-as-in-per_spk>\t<speaker-feature>
...


"""

import argparse
import os
import time
import errno


class SpeakerInfo:

    def __init__(self, id):
        self.id = id
        self.feature = ''
        self.word_err = 0
        self.sent_err = 0
        self.total_spoken_words = 0
        self.total_spoken_sent = 0
        self.wer = 0.0
        self.sent_err_percent = 0.0

    def init_raw_line(self, raw_arr):
        self.total_spoken_sent = raw_arr[2]
        self.total_spoken_words = raw_arr[3]
        self.word_err = raw_arr[8]
        self.sent_err = raw_arr[9]

    def init_sys_line(self, sys_arr):
        self.wer = sys_arr[8]
        self.sent_err_percent = sys_arr[9]


class SummedUpStatistics:

    def __init__(self, feature):
        self.feature = feature
        self.sum_words_spoken = 0
        self.sum_sent_spoken = 0
        self.sum_word_errors = 0
        self.sum_sent_errors = 0
        self.sum_wer = 0.0
        self.max_wer = 0.0
        self.min_wer = 100.0
        self.number_of_speakers = 0

    def compute_statistics(self, speaker_info_list):

        for speaker_info in speaker_info_list:
            self.sum_words_spoken += int(speaker_info.total_spoken_words)
            self.sum_sent_spoken += int(speaker_info.total_spoken_sent)
            self.sum_word_errors += int(speaker_info.word_err)
            self.sum_sent_errors += int(speaker_info.sent_err)
            self.sum_wer += float(speaker_info.wer)
            self.number_of_speakers += 1

            if self.max_wer < float(speaker_info.wer):
                self.max_wer = float(speaker_info.wer)
            if self.min_wer > float(speaker_info.wer):
                self.min_wer = float(speaker_info.wer)


def write_summed_stats(summed_stats_list, out_dir):

    with open(out_dir + 'speaker_statistics.txt', 'w') as out:
        out.write('\n')
        out.write('Comparison of speaker results by speaker features:\n')
        out.write('===================================================\n')
        for summed_stats in summed_stats_list:
            if summed_stats.feature == 'SUM':
                sum_feature = summed_stats
                continue

            out.write(summed_stats.feature + ' spoke ' + str(summed_stats.sum_words_spoken) +
                      ' words in ' + str(summed_stats.sum_sent_spoken) + ' sentences.\n')
            out.write('Total number of word errors were: ' + str(summed_stats.sum_word_errors) +
                      ' and sentence errors were: ' + str(summed_stats.sum_sent_errors) + '\n')
            out.write('Max WER: ' + str(summed_stats.max_wer) + '\n')
            out.write('Min WER: ' + str(summed_stats.min_wer) + '\n')
            out.write('Average WER: ' + '%.2f' % (summed_stats.sum_wer/summed_stats.number_of_speakers) + '%\n')
            out.write('General WER of ' + summed_stats.feature + ' speakers: ' + '%.2f' % (summed_stats.sum_word_errors/summed_stats.sum_words_spoken * 100) + '%\n')
            out.write('-------------------\n')

        out.write('Total spoken words: ' + str(sum_feature.sum_words_spoken) + ' in ' + str(sum_feature.sum_sent_spoken) + ' sentences\n')
        out.write('Total number of word errors were: ' + str(sum_feature.sum_word_errors) + ' and sentence errors were ' + str(sum_feature.sum_sent_errors) + '\n')
        out.write('Overall WER: ' + str(sum_feature.sum_wer) + '\n\n')


def init_speaker_map(speaker_file):
    speaker_map = {}

    for line in speaker_file.readlines():
        speaker_id, feature, *rest = line.split() # TODO: handle split by tab or space
        speaker_map[speaker_id] = feature.strip()

    speaker_map['SUM'] = 'SUM'

    return speaker_map


def analyse_by_speaker_feature(per_spk_file, speaker_mapping_file, out_dir):

    speaker_map = init_speaker_map(speaker_mapping_file)
    speaker_statistics = {}
    speaker_features = {}
    per_spk_file.readline() # get rid of header
    for line in per_spk_file.read().splitlines():
        line_arr = line.split()

        if line_arr[1] == 'raw':
            # this is the first line of two for this speaker
            speaker_info = SpeakerInfo(line_arr[0])
            if speaker_info.id not in speaker_map:
                print("'Speaker " + speaker_info.id + " is not in speaker - feature file!")
                continue
            speaker_info.init_raw_line(line_arr)
            speaker_info.feature = speaker_map[speaker_info.id]
            speaker_statistics[speaker_info.id] = speaker_info
        else:
            # the second line for this speaker, all info but WER and sent err are already collected
            speaker_info = speaker_statistics[line_arr[0]]
            speaker_info.init_sys_line(line_arr)
            speaker_statistics[speaker_info.id] = speaker_info
            speaker_list = speaker_features[speaker_info.feature] if speaker_info.feature in speaker_features else []
            speaker_list.append(speaker_info)
            speaker_features[speaker_info.feature] = speaker_list

    summed_stats_list = []
    for feature in speaker_features.keys():
        summed_stats = SummedUpStatistics(feature)
        summed_stats.compute_statistics(speaker_features[feature])
        summed_stats_list.append(summed_stats)

    write_summed_stats(summed_stats_list, out_dir)


def parse_args():
    parser = argparse.ArgumentParser(description='Error analysis by speaker class, e.g. gender',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('i', type=argparse.FileType('r'), help='per_spk file')
    parser.add_argument('b', type=argparse.FileType('r'), help='speaker-id - speaker-class file')
    parser.add_argument('-o', type=str, default='kaldi_per_spk_by_feature', help='Output directory')

    return parser.parse_args()


def main():

    # TODO: verfiy input files
    args = parse_args()
    per_spk_file = args.i
    speaker_mapping_file = args.b

    if args.o == 'kaldi_per_spk_by_feature':
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

    analyse_by_speaker_feature(per_spk_file, speaker_mapping_file, out_dir)


if __name__ == '__main__':
    main()