#!/bin/bash
# 
# Copyright: Reykjavik University 2016
# Author: Anna B. Nikulasdottir
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
# Transcribe a word list using a grapheme-to-phoneme model trained using Sequitur[1].
#
# [1] M. Bisani and H. Ney, “Joint-sequence models for
#     grapheme-to-phoneme conversion,” Speech Commun., vol. 50, no. 5,
#     pp. 434–451, May 2008.

if [ $# -ne 2 ]; then
	echo "Usage: $0 <model-dir> <input-word-list>" >&2
	echo "Eg. $0 data/local/g2p words_to_transcribe.txt" >&2
	exit 1
fi

model_dir=$1
wordlist=$2
model=$model_dir/g2p.mdl

# g2p.py writes the transcriptions to stdout
g2p.py --apply $wordlist --model $model --encoding="UTF-8"