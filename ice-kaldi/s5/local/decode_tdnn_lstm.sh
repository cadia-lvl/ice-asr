#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 <decode-dir> <graph-dir>" >&2
    echo "Eg. $0 data/dev_set exp/chain/tdnn_lstm/graph_tri_small" >&2
    exit 1
fi

. cmd.sh
. path.sh

DECODEDIR=$1 #test data
graph_dir=$2 

decode_iter=final
extra_left_context=50
extra_right_context=0
frames_per_chunk_primary=140

for decode_set in $DECODEDIR; do
      (
        steps/nnet3/decode.sh --num-threads 4 \
          --acwt 1.0 --post-decode-acwt 10.0 \
          --nj 25 --cmd "$decode_cmd" --iter $decode_iter \
          --extra-left-context $extra_left_context  \
          --extra-right-context $extra_right_context  \
          --extra-left-context-initial 0 \
          --extra-right-context-final 0 \
          --frames-per-chunk "$frames_per_chunk_primary" \
          --online-ivector-dir exp/nnet3/ivectors_${decode_set} \
         $graph_dir data/${decode_set}_hires \
         $dir/decode_${decode_set} || exit 1;
      ) &
  done
wait;


  # looped decoding.  Note: this does not make sense for BLSTMs or other
  # backward-recurrent setups, and for TDNNs and other non-recurrent there is no
  # point doing it because it would give identical results to regular decoding.
  for decode_set in train_dev eval2000; do
    (
      steps/nnet3/decode_looped.sh \
         --acwt 1.0 --post-decode-acwt 10.0 \
         --nj 50 --cmd "$decode_cmd" --iter $decode_iter \
         --online-ivector-dir exp/nnet3/ivectors_${decode_set} \
         $graph_dir data/${decode_set}_hires \
         $dir/decode_${decode_set}_looped || exit 1;
      ) &
  done
wait;



exit 0;
