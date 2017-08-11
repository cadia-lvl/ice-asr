#!/bin/bash

# This is pnorm neural net training on top of adapted 40-dimensional features.
# The core script called from this script is: steps/nnet2/train_pnorm_fast.sh

if [ $# -ne 2 ]; then
    echo "Usage: $0 <train-dir> <ali-dir>" >&2
    echo "Eg. $0 data/training_data exp/tri4a_ali" >&2
    exit 1
fi

TRAINDIR=$1 #training_data
ALIDIR=$2 #align dir

train_stage=-10
use_gpu=false

. cmd.sh
. ./path.sh
. utils/parse_options.sh

if $use_gpu; then
  if ! cuda-compiled; then
    cat <<EOF && exit 1
This script is intended to be used with GPUs but you have not compiled Kaldi with CUDA
If you want tu use GPUs (and have them), go to src/, and configure and make on a machine
wher "nvcc" is installed.
EOF
  fi
  parallel_opts="gpu=1"
  num_threads=1
  minibatch_size=512
  dir=exp/nnet2_pnorm_gpu
else
  num_threads=16
  parallel_opts="-pe smp $num_threads"
  minibatch_size=128
  dir=exp/nnet2_pnorm
fi

. ./cmd.sh
. utils/parse_options.sh

local/nnet2/train_pnorm_fast_custom.sh --stage $train_stage \
  --samples-per-iter 400000 \
  --parallel-opts "$parallel_opts" \
  --num_threads "$num_threads" \
  --minibatch-size "$minibatch_size" \
  --num-jobs-nnet 8 --mix-up 8000 \
  --initial-learning-rate 0.02 --final-learning-rate 0.004 \
  --num-hidden-layers 4 \
  --pnorm-input-dim 2000 --pnorm-output-dim 400 \
  --cmd "$decode_cmd" \
  $TRAINDIR data/lang $ALIDIR $dir || exit 1
