#!/bin/bash -e

# Steps to train an acoustic model as a preparation for TDNN-LSTM (local/run_tdnn_lstm.sh).
# This script assumes data and language preparation are already done, as well as language model creation

  

if [ $# -ne 4 ]; then
    echo "Usage: $0 <train-dir> <test-dir> <lm-dir> <lang-dir>" >&2
    echo "Eg. $0 data/train data/test data/lang_tri_small data/local/lang" >&2
    exit 1
fi

. cmd.sh
. path.sh

TRAINDIR=$1 #training_data
TESTDIR=$2 #test_data
LM=$3 #language model
LANG=$4 #language data

# Number of jobs
NJ=12
# Number of jobs for decoding, set this higher if your system can handle it
NJDECODE=4

mfccdir=mfcc
for x in $TRAINDIR $TESTDIR; do
  steps/make_mfcc.sh --nj 50 --cmd "$train_cmd" \
    data/$x exp/make_mfcc/$x $mfccdir
  steps/compute_cmvn_stats.sh data/$x exp/make_mfcc/$x $mfccdir
  utils/fix_data_dir.sh data/$x
done

## Starting basic training on MFCC features
steps/train_mono.sh --nj $NJ --cmd "$train_cmd" \
  "$TRAINDIR" "$LANG" exp/mono

steps/align_si.sh --nj $NJ --cmd "$train_cmd" \
  "$TRAINDIR" "$LANG" exp/mono exp/mono_ali

steps/train_deltas.sh --cmd "$train_cmd" \
  3200 30000 "$TRAINDIR" "$LANG" exp/mono_ali exp/tri1

steps/align_si.sh --nj $NJ --cmd "$train_cmd" \
  "$TRAINDIR" "$LANG" exp/tri1 exp/tri1_ali

steps/train_deltas.sh --cmd "$train_cmd" \
  4000 70000 "$TRAINDIR" "$LANG" exp/tri1_ali exp/tri2

steps/align_si.sh --nj $NJ --cmd "$train_cmd" \
  "$TRAINDIR" "$LANG" exp/tri2 exp/tri2_ali

# Do another iteration of LDA+MLLT training, on all the data.
steps/train_lda_mllt.sh --cmd "$train_cmd" \
  6000 140000 "$TRAINDIR" "$LANG" exp/tri2_ali exp/tri3

# Train tri4, which is LDA+MLLT+SAT, on all the data.
steps/align_fmllr.sh --nj 30 --cmd "$train_cmd" \
  data/train_nodup data/lang exp/tri3 exp/tri3_ali


steps/train_sat.sh  --cmd "$train_cmd" \
  11500 200000 "$TRAINDIR" "$LANG" exp/tri3_ali exp/tri4

# MMI training starting from the LDA+MLLT+SAT systems on all the data.
steps/align_fmllr.sh --nj 50 --cmd "$train_cmd" \
  "$TRAINDIR" "$LANG" exp/tri4 exp/tri4_ali

