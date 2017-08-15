# -*- coding: utf-8 -*-

"""
Entrypoint for the normalizing process. The default option is to perform all available normalizing processes,
but a selective normalizing should also be possible as work on the module proceeds.

"""

import argparse
import preprocessing
import map_replacement


def parse_args():
    parser = argparse.ArgumentParser(description='Normalizes Icelandic text for ASR', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('i', type=argparse.FileType('r', encoding='UTF-8'), help='Input data set')
    parser.add_argument('o', type=argparse.FileType('w', encoding='UTF-8'), help='Output file')
    parser.add_argument('--normalizing_steps', default=[])

    return parser.parse_args()


def main():

    args = parse_args()
    text = args.i.readlines()

    processed_lines = []
    for line in text:
        preprocessed_line = preprocessing.process(line.strip())

        if len(preprocessed_line) != 0:
            processed_line = map_replacement.replace_from_maps(preprocessed_line)
            processed_lines.append(processed_line)

    for line in processed_lines:
        args.o.write(line + '\n')

    # for line in processed_lines:
    #   if re.search('[^' + char_constants.LETTERS + ',. ]+', line):
    #        out_other.write(line + '\n')
    #    elif re.search('\.', line):
    #        out_punct.write(line + '\n')
    # out.close()


if __name__ == '__main__':
    main()