#!/bin/bash

. cmd.sh

steps/nnet2/decode.sh --nj 2 --cmd "$decode_cmd" --online-ivector-dir models/nnet2/ivectors_test_data models/nnet2/graph data/test_data_hires models/nnet2/decode_test

local/score.sh data/test_data_hires models/nnet2/graph models/nnet2/decode_test