#!/bin/bash

# Decodes a .wav file using the model and graph given.
# Prints log and decoding result to stdout. To write to text file change the last command 'ark:/dev/null' to 'ark,t:/path/to/output.txt'

. ./path.sh

if [ $# != 1 ]; then
	echo "Usage: $0 <wav-file>"
	exit 1;
fi

online2-wav-nnet2-latgen-faster --do-endpointing=false \
	--online=false \
	--config=conf/online_decoding_nnet2.conf \
	--max-active=4000 --beam=15.0 --lattice-beam=6.0 \
	--acoustic-scale=0.1 --word-symbol-table=models/nnet2/graph/words.txt \
	models/nnet2/final.mdl models/nnet2/graph/HCLG.fst "ark:echo utterance-id utterance-id|" "scp:echo utterance-id $1|" ark:/dev/null
