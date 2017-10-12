#!/bin/bash
#
# Prepares lexicon data for language modeling, creates a language model and converts to G.fst
#



. ./cmd.sh
. ./path.sh
. ./utils/parse_options.sh

stage=0

if [ $# -ne 3 ]; then
	error "Usage: $0 <dict-dir> <text-corpus> <lm-output-dir>"
fi

dictdir=$1
corpus=$2
lmdir=$3

if [ $stage -le 1 ]; then

	mkdir -p $lmdir

	for s in L_disambig.fst L.fst oov.int oov.txt phones phones.txt topo words.txt; do [ ! -e $lmdir/$s ] && cp -r $dictdir/$s $lmdir/$s; done

	# prepare pron dict for lm
	# remove labels and tags (keep "<unk>")
	cut -d' ' -f1 $lmdir/words.txt | egrep -v "<eps>|<s>|</s>|#" > $lmdir/lm_vocab.txt
fi

if [ $stage -le 2 ]; then
	# create a language model and convert to fst (be sure to adjust mitlm-path in local/make_ngram.sh!)
	local/make_ngram.sh $lmdir/lm_vocab.txt $corpus $lmdir/trigram.arpa.gz
	local/arpa2G.sh $lmdir/trigram.arpa.gz $lmdir $lmdir
fi

exit 0


