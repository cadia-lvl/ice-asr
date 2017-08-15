#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

The Utterance class represents a decoded utterance, reference text and hypothesis, along with the transforming
operations from referenc to hypothesis: C (correct), S (substitution), I (insertion), and D (deletion)

    Format:

    is_is-althingi1_04-2011-11-30T16:55:30.601205 ref  símaskráin  ***  komin  út
    is_is-althingi1_04-2011-11-30T16:55:30.601205 hyp  símaskráin   er  komin  út
    is_is-althingi1_04-2011-11-30T16:55:30.601205 op        C       I     C     C
    is_is-althingi1_04-2011-11-30T16:55:30.601205 #csid 3 0 1 0


"""


class Utterance:
    def __init__(self, utt_id):
        self.utt_id = utt_id
        self.ref = ""
        self.hyp = ""
        self.op = []
        self.csid_counts = []
        self.sub = 0
        self.ins = 0
        self.delete = 0

    def set_ref(self, reference):
        self.ref = reference

    def set_hyp(self, hypothesis):
        self.hyp = hypothesis

    # operation_arr: e.g. [C, I, S, C, C], can be of any length >= 1
    def set_operations(self, operations_arr):
        self.op = operations_arr

    # operation_arr: e.g. [3, 0, 1, 0], fixed length = 4
    def set_operations_count(self, operations_arr):
        int_arr = [int(i) for i in operations_arr]
        self.csid_counts = int_arr
        __, self.sub, self.ins, self.delete = int_arr

    def sum_errors(self):
        return self.sub + self.ins + self.delete

    def sum_ins_delete(self):
        return self.ins + self.delete


    @staticmethod
    def init_utterance_dict(utt_file):
        utt_dict = {}
        current_id = ""
        for line in utt_file.readlines():
            utt_id, info, *content = line.split()

            if utt_id == current_id:
                decoded_utt = utt_dict[utt_id]
                if info == 'hyp':
                    decoded_utt.set_hyp(' '.join(content))
                elif info == 'op':
                    decoded_utt.set_operations(content)
                elif info == '#csid':
                    decoded_utt.set_operations_count(content)
            else:
                decoded_utt = Utterance(utt_id)
                decoded_utt.set_ref(' '.join(content))
                current_id = utt_id

            utt_dict[utt_id] = decoded_utt

        return utt_dict
