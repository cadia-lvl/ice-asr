#!/bin/bash -eu
# 
# Uses the MIT Language Modeling Toolkit (MITLM) to compile an ngram ARPA from a text corpus and a dictionary
#
# Adjust the path to mitlm. To change the n-gram size (default: 3) change the value of -o


. local/utils.sh

if [ $# -ne 3 ]; then
	error "Usage: $0 <vocabulary-file> <corpus-file> <arpa-file>"
fi
vocab=$1; shift
corpus=$1; shift
arpa=$1; shift


/opt/mitlm-0.4.1/bin/estimate-ngram -o 3 -v "$vocab" -t "$corpus" -wl "$arpa"


exit 0 
