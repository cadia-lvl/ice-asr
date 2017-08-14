#!/bin/bash
# Prepares a Kaldi-prepared data directory for decoding using an nnet model.
# Assumes the data directory is located in data/ directory.

. cmd.sh
. ./path.sh
. ./utils/parse_options.sh

if [ $# != 2 ]; then
	echo "Usage: $0 <test_data_dir> <path_to_model" >&2
	echo "E.g.: $0 test_data exp/chain/tdnn_lstm/"
	echo "Prepares a Kaldi-prepared data directory for decoding using an nnet model. This directory should be located in the data/ directory." >&2
	exit 1;
fi

if [ ! -d "mfcc" ]; then
	mkdir -p mfcc
fi

mfccdir=mfcc
datadir=$1
modeldir=$2

utils/copy_data_dir.sh data/$datadir data/${datadir}_hires
steps/make_mfcc.sh --nj 40 --mfcc-config conf/mfcc_hires.conf \
  --cmd "$train_cmd" data/${datadir}_hires exp/make_hires/$datadir $mfccdir || exit 1;
steps/compute_cmvn_stats.sh data/${datadir}_hires exp/make_hires/$datadir $mfccdir || exit 1;

rm $modeldir.error 2>/dev/null

steps/online/nnet2/extract_ivectors_online.sh --cmd "$train_cmd" --nj 8 data/${datadir}_hires $modeldir $modeldir/ivectors_${datadir} || touch $modeldir.error &

wait
[ -f $modeldir.error ] && echo "$0: error extracting iVectors." && exit 1;

exit 0;

