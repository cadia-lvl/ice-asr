#!/bin/bash

# This is an adapted version of kaldi/egs/wsj/s5/local/online/run_nnet2_common.sh

# this script is called from scripts like run_nnet2.sh; it does
# the common stages of the build.

. cmd.sh
mfccdir=mfcc

stage=1

. cmd.sh
. ./path.sh
. ./utils/parse_options.sh




if [ $stage -le 1 ]; then
  for datadir in training_data test_data; do
    utils/copy_data_dir.sh data/$datadir data/${datadir}_hires
    steps/make_mfcc.sh --nj 40 --mfcc-config conf/mfcc_hires.conf \
      --cmd "$train_cmd" data/${datadir}_hires exp/make_hires/$datadir $mfccdir || exit 1;
    steps/compute_cmvn_stats.sh data/${datadir}_hires exp/make_hires/$datadir $mfccdir || exit 1;
  done
  # original sub_dir value: 7138
  utils/subset_data_dir.sh --first data/training_data_hires 5000 data/training_data_sub_hires || exit 1
  utils/subset_data_dir.sh --first data/training_data 5000 data/training_data_sub || exit 1
fi


if [ $stage -le 2 ]; then
  # We need to build a small system just because we need the LDA+MLLT transform
  # to train the diag-UBM on top of.  We align the si84 data for this purpose.
  # Original nj=32 
  steps/align_fmllr.sh --nj 12 --cmd "$train_cmd" \
    data/training_data_sub data/lang_bi_small exp/tri4a exp/nnet2_online/tri4a_ali_sub
fi

if [ $stage -le 3 ]; then
  # Train a small system just for its LDA+MLLT transform.  We use --num-iters 13
  # because after we get the transform (12th iter is the last), any further
  # training is pointless.
  steps/train_lda_mllt.sh --cmd "$train_cmd" --num-iters 13 \
    --realign-iters "" \
    --splice-opts "--left-context=3 --right-context=3" \
    5000 10000 data/training_data_sub_hires data/lang \
     exp/nnet2_online/tri4a_ali_sub exp/nnet2_online/tri5a
fi

if [ $stage -le 4 ]; then
  mkdir -p exp/nnet2_online

  steps/online/nnet2/train_diag_ubm.sh --cmd "$train_cmd" --nj 30 \
     --num-frames 400000 --num-threads 8 data/training_data_sub_hires 256 exp/nnet2_online/tri5a exp/nnet2_online/diag_ubm
fi

if [ $stage -le 5 ]; then
  # even though $nj is just 10, each job uses multiple processes and threads.
  steps/online/nnet2/train_ivector_extractor.sh --cmd "$train_cmd" --nj 10 \
    data/training_data_hires exp/nnet2_online/diag_ubm exp/nnet2_online/extractor || exit 1;
fi

if [ $stage -le 6 ]; then
  # We extract iVectors on all the training data, which will be what we
  # train the system on.

  # having a larger number of speakers is helpful for generalization, and to
  # handle per-utterance decoding well (iVector starts at zero).
  steps/online/nnet2/copy_data_dir.sh --utts-per-spk-max 2 data/training_data_hires \
    data/training_data_hires_max2

  steps/online/nnet2/extract_ivectors_online.sh --cmd "$train_cmd" --nj 30 \
    data/training_data_hires_max2 exp/nnet2_online/extractor exp/nnet2_online/ivectors_training_data || exit 1;
fi

if [ $stage -le 7 ]; then
  rm exp/nnet2_online/.error 2>/dev/null
  for data in test_data; do
    steps/online/nnet2/extract_ivectors_online.sh --cmd "$train_cmd" --nj 8 \
      data/${data}_hires exp/nnet2_online/extractor exp/nnet2_online/ivectors_${data} || touch exp/nnet2_online/.error &
  done
  wait
  [ -f exp/nnet2_online/.error ] && echo "$0: error extracting iVectors." && exit 1;
fi

exit 0;
