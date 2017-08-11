#!/bin/bash -e

# Having prepared your data for training (by running something like local/prep_data.sh), you can run this
# script. It might be better though to run the commands one by one.

. cmd.sh
. path.sh

stage=0

DATATRAIN=data/training_data
DATATEST=data/test_data

# Number of jobs
NJ=8

if [ $stage -le 1 ]; then
	echo "Extracting features for train."
	steps/make_mfcc.sh --nj $NJ --cmd "$train_cmd" --mfcc-config conf/mfcc.conf "$DATATRAIN" exp/make_mfcc/"$DATATRAIN" mfcc
	steps/compute_cmvn_stats.sh "$DATATRAIN" exp/make_mfcc/"$DATATRAIN" mfcc
fi

if [ $stage -le 2 ]; then
	echo "Extracting features for test."
	steps/make_mfcc.sh --nj $NJ --cmd "$train_cmd" --mfcc-config conf/mfcc.conf "$DATATEST" exp/make_mfcc/"$DATATEST" mfcc
	steps/compute_cmvn_stats.sh "$DATATEST" exp/make_mfcc/"$DATATEST" mfcc
fi

if [ ! -d data/lang ]; then
    echo "Unpacking data/lang.tar.gz"
    mkdir data/lang
    tar xzf data/lang.tar.gz -C data
fi

if [ ! -d data/lang_bi_small ]; then
    echo "Unpacking data/lang_bi_small.tar.gz"
    mkdir data/lang_bi_small
    tar xzf data/lang_bi_small.tar.gz -C data
fi

if [ $stage -le 3 ]; then
	echo "Training LDA MLLT."
	./local/train_lda_mllt.sh "$DATATRAIN" "$DATATEST"
fi

if [ $stage -le 4 ]; then
	echo "Preparing tdnn-lstm training"
	./local/chain/prepare_tdnn_lstm.sh
fi

if [ $stage -le 5 ]; then
	echo "Training tdnn-lstm model"
	./local/online/run_tdnn_lstm.sh
fi


if [ $stage -le 6 ]; then
	echo "Decoding test set using tdnn-lstm trained data"
	./local/decode_tdnn_lstm.sh "$DATATEST" exp/chain/tdnn_lstm/graph_bi_small

	echo "Scoring decoding results"
	./local/score.sh --cmd "$decode_cmd" "$DATATEST" exp/chain/tdnn_lstm/graph_bi_small exp/chain/tdnn_lstm/decode_{$DATATEST}
fi

echo "Done."
