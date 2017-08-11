#!/bin/bash

# Performes some intermediate steps to prepare for nnet2 training - uses the results from
# train_lda_mllt.sh

if [ $# -ne 1 ]; then
    echo "Usage: $0 <train-dir>" >&2
    echo "Eg. $0 data/training_data" >&2
    exit 1
fi

. cmd.sh

TRAINDIR=$1 #training_data

steps/align_fmllr.sh --nj 12 --cmd "$train_cmd" "$TRAINDIR" data/lang exp/tri3a exp/tri3a_ali || exit 1;

# GMM system for NNET
steps/train_quick.sh --cmd "$train_cmd" 4200 40000 "$TRAINDIR" data/lang exp/tri3a_ali exp/tri4 || exit 1;

steps/align_fmllr.sh --cmd "$train_cmd" "$TRAINDIR" data/lang exp/tri4 exp/tri4_ali || exit 1;	

utils/mkgraph.sh data/lang_bi_small exp/tri4 exp/tri4/graph || exit 1;

exit 0;