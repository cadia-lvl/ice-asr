#!/bin/bash

# This is an adapted version of kaldi/egs/wsj/s5/local/online/run_nnet2.sh

# It's a "multi-splice" system (i.e. we have splicing at various layers), with 
# p-norm nonlinearities.  We use the "accel2" script which uses between 2 and 
# 14 GPUs depending how far through training it is.  You can safely reduce 
# the --num-jobs-final to however many GPUs you have on your system.

. cmd.sh

stage=0
train_stage=-10
use_gpu=true
dir=exp/nnet2_online/nnet_ms_a
exit_train_stage=-100
. cmd.sh
. ./path.sh
. ./utils/parse_options.sh

if $use_gpu; then
  if ! cuda-compiled; then
    cat <<EOF && exit 1 
This script is intended to be used with GPUs but you have not compiled Kaldi with CUDA 
If you want to use GPUs (and have them), go to src/, and configure and make on a machine
where "nvcc" is installed.  Otherwise, call this script with --use-gpu false
EOF
  fi
  parallel_opts="--gpu 1" 
  num_threads=1
  minibatch_size=512
  # the _a is in case I want to change the parameters.
else
  num_threads=16
  minibatch_size=128
  parallel_opts="--num-threads $num_threads" 
fi

# stages 1 - 7
local/online/run_nnet2_common.sh --stage $stage || exit 1;

if [ $stage -le 8 ]; then
  # last splicing was instead: layer3/-4:2" 
  steps/nnet2/train_multisplice_accel2.sh --stage $train_stage \
    --exit-stage $exit_train_stage \
    --num-epochs 8 --num-jobs-initial 1 --num-jobs-final 1 \
    --num-hidden-layers 4 \
    --splice-indexes "layer0/-1:0:1 layer1/-2:1 layer2/-4:2" \
    --feat-type raw \
    --online-ivector-dir exp/nnet2_online/ivectors_training_data \
    --cmvn-opts "--norm-means=false --norm-vars=false" \
    --num-threads "$num_threads" \
    --minibatch-size "$minibatch_size" \
    --parallel-opts "$parallel_opts" \
    --initial-effective-lrate 0.005 --final-effective-lrate 0.0005 \
    --cmd "$decode_cmd" \
    --pnorm-input-dim 2000 \
    --pnorm-output-dim 250 \
    --mix-up 12000 \
    data/training_data_hires data/lang exp/tri4a_ali $dir  || exit 1;
fi

if [ $stage -le 9 ]; then
  # If this setup used PLP features, we'd have to give the option --feature-type plp
  # to the script below.
  iter_opt=
  [ $exit_train_stage -gt 0 ] && iter_opt="--iter $exit_train_stage"
  steps/online/nnet2/prepare_online_decoding.sh $iter_opt --mfcc-config conf/mfcc_hires.conf \
    data/lang exp/nnet2_online/extractor "$dir" ${dir}_online || exit 1;
fi

if [ $exit_train_stage -gt 0 ]; then
  echo "$0: not testing since you only ran partial training (presumably in preparation"
  echo " for multilingual training"
  exit 0;
fi

if [ $stage -le 10 ]; then
  # this does offline decoding that should give the same results as the real
  # online decoding.
  graph_dir=exp/tri4a/graph
  # use already-built graphs.
  for data in test_data; do
    steps/nnet2/decode.sh --nj 2 --cmd "$decode_cmd" \
        --online-ivector-dir exp/nnet2_online/ivectors_$data \
       $graph_dir data/${data}_hires $dir/decode_${data} || exit 1;
  done
fi

exit 0;
