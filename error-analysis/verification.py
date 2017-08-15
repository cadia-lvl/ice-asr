#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import os.path
import errno
import argparse


def verify_input(input_path, filename):

    if input_path.endswith(filename):
        input_file = input_path
    elif input_path.endswith('/'):
        input_file = input_path + filename
    else:
        input_file = input_path + '/' + filename

    if os.path.isfile(input_file) and os.access(input_file, os.R_OK):
        return input_file

    return None
