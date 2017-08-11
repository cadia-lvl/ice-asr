#!/bin/bash -e

# Steps to train an acoustic model, LDA+MLLT triphones
# You can run each command separately from your kaldi working directory
# The first example shows how you can run the commands using the Slurm queueing system as well as directly from your working directory

if [ $# -ne 2 ]; then
    echo "Usage: $0 <train-dir> <test-dir>" >&2
    echo "Eg. $0 data/train data/test" >&2
    exit 1
fi

. cmd.sh
. path.sh

TRAINDIR=$1 #training_data
TESTDIR=$2 #test_data

# Number of jobs
NJ=12
# Number of jobs for decoding, set this higher if your system can handle it
NJDECODE=4

# Train monophone model using Slurm:
# sbatch steps/train_mono.sh --nj 4 --cmd slurm.pl --totgauss 4000 data/"$TRAINDIR" data/lang exp/mono
# Train monophone model from your working directory:
./steps/train_mono.sh --nj $NJ --cmd "$train_cmd" --totgauss 4000 "$TRAINDIR" data/lang exp/mono

./steps/align_si.sh --nj $NJ --cmd "$train_cmd" "$TRAINDIR" data/lang exp/mono exp/mono_ali

./steps/train_deltas.sh --cmd "$train_cmd" 2000 10000 "$TRAINDIR" data/lang exp/mono_ali exp/tri1a

# At this point you can make your first decoding graph and then decode your test set.
# You will find decoding scoring results in decode_test/scoring_kaldi, see e.g. file best_wer for the WER%
# Create graph:
./utils/mkgraph.sh data/lang_bi_small exp/tri1a exp/tri1a/graph
# Decode:
./steps/decode.sh --nj $NJDECODE --cmd "$train_cmd" exp/tri1a/graph "$TESTDIR" exp/tri1a/decode_test

# Continue training the model:
./steps/align_si.sh --nj $NJ --cmd "$train_cmd" "$TRAINDIR" data/lang exp/tri1a exp/tri1a_ali

./steps/train_deltas.sh --cmd "$train_cmd" 2500 15000 "$TRAINDIR" data/lang exp/tri1a_ali exp/tri2a

./steps/align_si.sh --nj $NJ --cmd "$train_cmd" --use-graphs true "$TRAINDIR" data/lang exp/tri2a exp/tri2a_ali

# Train LDA-MLLT triphones
./steps/train_lda_mllt.sh --cmd "$train_cmd" 3500 20000 "$TRAINDIR" data/lang exp/tri2a_ali exp/tri3a

# Create graph:
./utils/mkgraph.sh data/lang_bi_small exp/tri3a exp/tri3a/graph
# Decode:
./steps/decode.sh --nj $NJDECODE --cmd "$train_cmd" exp/tri3a/graph "$TESTDIR" exp/tri3a/decode_test



  
	
  
