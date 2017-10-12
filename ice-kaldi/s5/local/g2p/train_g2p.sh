#!/bin/bash
#
# Copyright: 2015 Róbert Kjaran
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#
# Train a grapheme-to-phoneme model using Sequitur[1].
#
# [1] M. Bisani and H. Ney, “Joint-sequence models for
#     grapheme-to-phoneme conversion,” Speech Commun., vol. 50, no. 5,
#     pp. 434–451, May 2008.

stage=0
iters=7

. utils/parse_options.sh

if [ $# -ne 2 ]; then
    cat <<EOF >&2
Usage: $0 <train-lexicon> <output-dir>
Example: $0 data/local/dict/lexicon1.txt data/local/g2p

Train a grapheme-to-phoneme model on <train-lexicon>.
EOF
    exit 1
fi

lexicon=$1 ; shift
dir=$1     ; shift
model=$dir/g2p.mdl
mkdir -p $dir/log

for i in $(seq 1 $[iters - 1]); do
    echo "$0: iteration $i" >&2
    if [ $i -ge $stage ]; then
        if [ $i -eq 1 ]; then
            g2p.py \
                --train $lexicon \
                --devel 5%       \
                --self-test      \
                --write-model $dir/g2p-model-$i \
                --encoding="UTF-8" 2>&1 | tee $dir/log/g2p.$i.log
        else
            g2p.py \
                --model $dir/g2p-model-$[i-1]  \
                --ramp-up   \
                --self-test \
                --train $lexicon \
                --devel 5% \
                --write-model $dir/g2p-model-$i \
                --encoding="UTF-8" 2>&1 | tee $dir/log/g2p.$i.log
        fi
    fi
done

cp $dir/g2p-model-$i $model

exit 0
