#!/bin/bash
#
# Prepares lexicon data for ASR training with Kaldi
#

. path.sh
.

if [ $# -ne 1 ]; then
	error "Usage: $0 <aligned-pronunciation-dictionary>"
fi

prondict=$1

mkdir -p data/local/dict
mkdir -p data/lang

dictdir=data/local/dict

# sort the pronunciation dictionary and copy into dictdir, add oov-label
LC_ALL=C sort -u $prondict > $dictdir/lexicon_orig.txt
cat $dictdir/lexicon_orig.txt <(echo "<unk> oov") > $dictdir/lexicon_ext.txt
cp $dictdir/lexicon{_ext,}.txt

# extract non silence phones and silence phones
cut -f2- $dictdir/lexicon_orig.txt | tr ' ' '\n' | LC_ALL=C sort -u > $dictdir/nonsilence_phones.txt

for w in sil oov; do echo $w; done > $dictdir/silence_phones.txt
echo "sil" > $dictdir/optional_silence.txt

./local/create_extra_questions.sh $dictdir

./local/prepare_lang.sh $dictdir "<unk>" data/lang data/lang

exit 0
 



