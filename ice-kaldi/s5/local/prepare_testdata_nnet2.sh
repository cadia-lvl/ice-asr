#!/bin/bash
# Prepares a Kaldi-prepared data directory for decoding using an nnet2 model.
# Assumes the data directory is located in data/ directory.

. cmd.sh
. ./path.sh
. ./utils/parse_options.sh

if [ $# != 1 ]; then
	echo "Usage: $0 <test_data_dir>" >&2
	echo "Prepares a Kaldi-prepared data directory for decoding using an nnet2 model. This directory should be located in the data/ directory." >&2
	exit 1;
fi

if [ ! -d "mfcc" ]; then
	mkdir -p mfcc
fi

mfccdir=mfcc
datadir=$1

utils/copy_data_dir.sh data/$datadir data/${datadir}_hires
steps/make_mfcc.sh --nj 40 --mfcc-config conf/mfcc_hires.conf \
  --cmd "$train_cmd" data/${datadir}_hires exp/make_hires/$datadir $mfccdir || exit 1;
steps/compute_cmvn_stats.sh data/${datadir}_hires exp/make_hires/$datadir $mfccdir || exit 1;

rm exp/nnet2_online/.error 2>/dev/null

steps/online/nnet2/extract_ivectors_online.sh --cmd "$train_cmd" --nj 8 data/${datadir}_hires models/nnet2 models/nnet2/ivectors_${datadir} || touch models/nnet2/.error &

wait
[ -f exp/nnet2_online/.error ] && echo "$0: error extracting iVectors." && exit 1;

exit 0;

