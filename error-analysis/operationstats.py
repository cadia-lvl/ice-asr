#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class OperationStatistics:

    # Holds and collects operation statistics on a word string or a collection of words with a common
    # feature. Thus, 'word' can be a certain word length, e.g. all words having len == 4
    def __init__(self, word, freq=0):
        self.word = word
        self.occurrences = 0
        self.correct = 0
        self.substitutions = 0
        self.deletions = 0
        self.insertions = 0
        self.corpus_frequency = freq

    def increment(self, operation, count):
        if operation == 'correct':
            self.correct += count
        elif operation == 'deletion':
            self.deletions += count
        elif operation == 'insertion':
            self.insertions += count
        elif operation == 'substitution':
            self.substitutions += count

        self.occurrences += count

    def increment_all(self, op_stat):
        self.correct += op_stat.correct
        self.deletions += op_stat.deletions
        self.insertions += op_stat.insertions
        self.substitutions += op_stat.substitutions
        self.occurrences += op_stat.occurrences

    def print_array(self, with_corpus_freq=False):
        if with_corpus_freq:
            return [self.word, str(self.occurrences), str(self.correct), str(self.deletions),
                    str(self.insertions), str(self.substitutions), '%.2f' % (
                    self.correct / self.occurrences * 100) + '%', str(self.corpus_frequency)]
        else:
            return [self.word, str(self.occurrences), str(self.correct), str(self.deletions),
                    str(self.insertions), str(self.substitutions), '%.2f' % (
                    self.correct / self.occurrences * 100) + '%']
