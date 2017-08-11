#!/bin/bash

. ./path.sh
. ./utils/parse_options.sh

decode_dir=$1
out_dir=$2

num_lattices=$(cat $decode_dir/num_jobs)
mkdir -p $out_dir

for i in `seq 1 $num_lattices`;
do
	lattice-to-nbest --acoustic-scale=1.0 --n=10 "ark:gunzip -c $decode_dir/lat.$i.gz|" "ark:|gzip -c >$out_dir/nbest.$i.gz"
done

for i in `seq 1 $num_lattices`;
do
	mkdir -p $out_dir/archives.$i
	nbest-to-linear "ark:gunzip -c $out_dir/nbest.$i.gz|" "ark,t:$out_dir/archives.$i/ali" "ark,t:$out_dir/archives.$i/words"
done

for i in `seq 1 $num_lattices`;
do
	utils/int2sym.pl -f 2- data/local/lang_wp2/words.txt < $out_dir/archives.$i/words > $out_dir/archives.$i/words_text.txt
done

echo "$0: Finished creating n-best lists for lattices in $decode_dir"
exit 0;
