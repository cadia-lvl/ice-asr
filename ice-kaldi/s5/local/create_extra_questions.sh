#!/bin/bash -eu

if [ $# -ne 1 ]; then
	error "Usage: $0 <dict-dir>"
fi

dictdir=$1

#grep -v ː $dictdir/nonsilence_phones.txt | awk '{print $1 "ː"}' | sort

join -t '' \
     <(grep ː $dictdir/nonsilence_phones.txt) \
     <(grep -v ː $dictdir/nonsilence_phones.txt | awk '{print $1 "ː"}' | LC_ALL=C sort) \
    | awk '{s=$1; sub(/ː/, ""); print $1 " " s }' \
     > $dictdir/extra_questions.txt
