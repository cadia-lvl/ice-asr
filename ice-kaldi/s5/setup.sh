#!/bin/bash

. path.sh

echo Setting up symlinks
ln -s $KALDI_ROOT/egs/wsj/s5/steps steps
ln -s $KALDI_ROOT/egs/wsj/s5/utils utils

echo Done
