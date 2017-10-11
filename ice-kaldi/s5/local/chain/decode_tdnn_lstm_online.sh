#!/bin/bash

# Copyright 2017 Reykjavik University
# Author: Anna B. Nikulasdottir
# License: Apache 2.0
# 
# 
# Decodes an audio file, given a decoding graph based on tdnn-lstm models.
# The audio file has to have a 16kHz sample rate. The script outputs log information on lines starting with LOG, 
# the line containing the decoding result starts with 'utterance-id'.
#
# Make sure the given paths match your directory structure or change them accordingly.
# This applies to the location of the online configuration file, online.conf; word-symbol table words.txt; the 
# acoustic model file, final.mdl; and the graph, HCLG.fst
#

if [ $# -ne 1 ]; then
	echo "Usage: $0 <audio-file>" >&2
	echo "E.g. $0 example.wav" >&2
	exit 1
fi

. path.sh

audio=$1

online2-wav-nnet3-latgen-faster --online=false \
	--do-endpointing=false \
	--config=exp/chain/tdnn_lstm_online/conf/online.conf \
	--acoustic-scale=1.0 \
	--word-symbol-table=exp/graph_tri_small/words.txt \
	exp/chain/tdnn_lstm_online/final.mdl \
	exp/graph_tri_small/HCLG.fst \
	'ark:echo utterance-id utterance-id|' 'scp:echo utterance-id '"$1"'|' 'ark:/dev/null'

exit 0;		

