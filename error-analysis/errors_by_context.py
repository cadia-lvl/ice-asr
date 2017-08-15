

"""
Is an error more likely to occur after an error than not?

General, per word?

How many utterances have only one error?
How many errors occur in other utterances, but not subsequently? (e.g.: C, Err, C, C, Err)
How many errors occur directly after another error? And what is the ratio of the errors of single words and
wordclasses compared to isolated errors?

    Kaldi per_utt results:

    is_is-althingi1_04-2011-11-30T16:55:30.601205 ref  símaskráin  ***  komin  út
    is_is-althingi1_04-2011-11-30T16:55:30.601205 hyp  símaskráin   er  komin  út
    is_is-althingi1_04-2011-11-30T16:55:30.601205 op        C       I     C     C
    is_is-althingi1_04-2011-11-30T16:55:30.601205 #csid 3 0 1 0

    For each error operation (I, S, D):
    get the preceding operation: C, I, S, D or beginning of utt

"""
import os
import time
import argparse
import utterance

CORRECT = 'C'
DELETION = 'D'
INSERTION = 'I'
SUBSTITUTION = 'S'

START = 'start'


class Operation:
    # Holds counts of preceding operations/context of an operation
    # and the occurrence count of the operation itself
    def __init__(self, name):
        self.name = name
        self.occurrences = 0
        self.predecessors_map = {}

    def increment_context(self, op, utterance):
        utt_list = self.predecessors_map[op] if op in self.predecessors_map else []
        utt_list.append(utterance)
        self.predecessors_map[op] = utt_list

    def increment_occ(self, count):
        self.occurrences += count


class OperationsMap:

    def __init__(self, op_map={}):
        self.operations = op_map

    def get_operation_sum(self):
        op_sum = 0
        for op in self.operations.keys():
            op_sum += self.operations[op].occurrences

        return op_sum

    def get_errors_succeeding(self, op):
        # list of utterances with a pattern 'op' ERROR
        utt_list = self.get_operation_succeeding(DELETION, op)
        utt_list += self.get_operation_succeeding(INSERTION, op)
        utt_list += self.get_operation_succeeding(SUBSTITUTION, op)

        return utt_list

    def get_operation_succeeding(self, op, predecessor):
        operation = self.operations[op]
        utts = operation.predecessors_map[predecessor] if predecessor in operation.predecessors_map else []

        return utts

    def get_error_count_succeeding(self, op):
        # occurrences of errors following operation 'op'
        error_count = self.get_count_succeeding(DELETION, op)
        error_count += self.get_count_succeeding(INSERTION, op)
        error_count += self.get_count_succeeding(SUBSTITUTION, op)
        return error_count

    def get_count_succeeding(self, op, predecessor):
        # occurrences of operation 'op' following operation 'predecessor'
        operation = self.operations[op]
        op_count = len(operation.predecessors_map[predecessor]) if predecessor in operation.predecessors_map else 0

        return op_count

    def get_count(self, op):
        operation = self.operations[op]
        return operation.occurrences


def init_utterance_dict(utt_file):
    # Initialize a dictionary with utterance ids as keys and utterance objects as values
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
            decoded_utt = utterance.Utterance(utt_id)
            decoded_utt.set_ref(' '.join(content))
            current_id = utt_id

        utt_dict[utt_id] = decoded_utt

    return utt_dict


def write_file(filename, list_to_write):
    with open(filename, 'w') as f:
        for line in list_to_write:
            f.write(line)


def is_error(operation):
    if operation == INSERTION or operation == DELETION or operation == SUBSTITUTION:
        return True
    return False


def get_operation_count(operations, op):
    count = 0

    for operation in operations:
        if operation == op:
            count += 1

    return count


def write_errors(out_dir, op_map):
    write_file(out_dir + 'errors_beginning.txt', op_map.get_errors_succeeding(START))
    write_file(out_dir + 'errors_after_C.txt', op_map.get_errors_succeeding(CORRECT))
    write_file(out_dir + 'errors_after_D.txt', op_map.get_errors_succeeding(DELETION))
    write_file(out_dir + 'errors_after_I.txt', op_map.get_errors_succeeding(INSERTION))
    write_file(out_dir + 'errors_after_S.txt', op_map.get_errors_succeeding(SUBSTITUTION))


def compute_statistics(op_map, utt_count, err_count, out_dir):

    err_succeeding_start = op_map.get_error_count_succeeding(START)
    err_succeeding_correct = op_map.get_error_count_succeeding(CORRECT)
    err_succeeding_del = op_map.get_error_count_succeeding(DELETION)
    err_succeeding_ins = op_map.get_error_count_succeeding(INSERTION)
    err_succeeding_sub = op_map.get_error_count_succeeding(SUBSTITUTION)

    corr_succeeding_start = op_map.get_count_succeeding(CORRECT, START)
    corr_succeeding_correct = op_map.get_count_succeeding(CORRECT, CORRECT)
    corr_succeeding_del = op_map.get_count_succeeding(CORRECT, DELETION)
    corr_succeeding_ins = op_map.get_count_succeeding(CORRECT, INSERTION)
    corr_succeeding_sub = op_map.get_count_succeeding(CORRECT, SUBSTITUTION)

    print('')
    print("========== Analyzing context of errors from per_utt file from Kaldi decoding ==============")
    print("Errors in the beginning of an utterance: " + str(err_succeeding_start))
    print("Errors after correct decoding: " + str(err_succeeding_correct))
    print("Errors after Deletions: " + str(err_succeeding_del))
    print("Errors after Insertions: " + str(err_succeeding_ins))
    print("Errors after Substitutions: " + str(err_succeeding_sub))
    print("SUM ERRORS: " + str(err_count))
    print('')

    print("Correct in the beginning of an utterance: " + str(corr_succeeding_start))
    print("Correct after correct decoding: " + str(corr_succeeding_correct))
    print("Correct after Deletions: " + str(corr_succeeding_del))
    print("Correct after Insertions: " + str(corr_succeeding_ins))
    print("Correct after Substitutions: " + str(corr_succeeding_sub))

    print('')

    sum_operations = op_map.get_operation_sum()
    sum_correct = op_map.get_count(CORRECT)
    sum_ins = op_map.get_count(INSERTION)
    sum_del = op_map.get_count(DELETION)
    sum_sub = op_map.get_count(SUBSTITUTION)

    print("Sum of operations: " + str(sum_operations))
    print("Correct: " + str(sum_correct))
    print("Insertions: " + str(sum_ins))
    print("Deletions: " + str(sum_del))
    print("Substitutions: " + str(sum_sub))

    print("Sum utterances: " + str(utt_count))

    sum_correct_after_error = corr_succeeding_del + corr_succeeding_ins + corr_succeeding_sub
    sum_error_after_error = err_succeeding_del + err_succeeding_ins + err_succeeding_sub

    print("")
    print("Probabilities:")
    print("P(E) = " + '%.2f' % ((sum_del + sum_ins + sum_sub) / (sum_correct + err_count)))
    print("P(C) = " + '%.2f' % (sum_correct / (sum_correct + err_count)))
    print("P(E|E) = " + '%.2f' % (sum_error_after_error / (sum_correct_after_error + sum_error_after_error)))
    print("P(E|C) = " + '%.2f' % (err_succeeding_correct / (corr_succeeding_correct + err_succeeding_correct)))
    print("P(C|E) = " + '%.2f' % (sum_correct_after_error / (sum_error_after_error + sum_correct_after_error)))
    print("P(C|C) = " + '%.2f' % (corr_succeeding_correct / (corr_succeeding_correct + err_succeeding_correct)))

    write_errors(out_dir, op_map)


def analyse_errors_by_context(utt_file, out_dir):
    # A dictionary of utterances with hypothesis and error/operation information
    utterance_dict = init_utterance_dict(utt_file)
    ops_map = {CORRECT: Operation(CORRECT), DELETION: Operation(DELETION),
               INSERTION: Operation(INSERTION), SUBSTITUTION: Operation(SUBSTITUTION)}

    utterance_count = 0
    error_count = 0
    for key in utterance_dict.keys():
        utterance = utterance_dict[key]
        utterance_count += 1
        error_count += utterance.sum_errors()

        for op in ops_map.keys():
            ops_map[op].increment_occ(get_operation_count(utterance.op, op))

        result_string = utterance.ref + '\t' + utterance.hyp + '\t' + str(utterance.op) + '\t' + str(utterance.sum_errors()) + '\n'
        last_op = 'start'
        for op in utterance.op:
            ops_map[op].increment_context(last_op, result_string)
            last_op = op

    operations_map = OperationsMap(ops_map)
    compute_statistics(operations_map, utterance_count, error_count, out_dir)


def parse_args():
    parser = argparse.ArgumentParser(description='Statistics on context of errors from Kaldi per_utt file',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('i', type=argparse.FileType('r'), help='Kaldi per_utt file')
    parser.add_argument('-o', type=str, default='kaldi_per_utt_by_context', help='Output directory')

    return parser.parse_args()


def main():
    # verfiy input file - has to be a per_utt file
    args = parse_args()
    utt_file = args.i

    if args.o == 'kaldi_per_utt_by_context':
        out_dir = args.o + '_' + time.strftime("%Y%m%d-%H%M%S") + '/'
    else:
        out_dir = args.o
        if not out_dir.endswith('/'):
            out_dir += '/'

    os.mkdir(out_dir)

    analyse_errors_by_context(utt_file, out_dir)

if __name__ == '__main__':
    main()