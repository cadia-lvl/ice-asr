#!/bin/bash -eu
#
# Málrómur data prep example
# 
# Based on a script from Róbert Kjaran 2015.
# Change: reading wav_info.txt separately and not necessarily from the audio data directory
# (the audio directory was '/wav' original script)

samplerate=16000
tmp=$(mktemp -d)
trap "rm -rf $tmp" EXIT

if [ $# -ne 3 ]; then
    echo "Usage: $0 <path-to-malromur-audio> <info-file> <data-dir>" >&2
    echo "Eg. $0 /data/corpora/malromur/wav/ wav_info.txt data/malromur1" >&2
    exit 1;
fi

malromur=$(readlink -f $1); shift
info=$1; shift
datadir=$1

mkdir -p $datadir

wav_cmd="sox - -c1 -esigned -r$samplerate -twav - "

python -c "import sys
text = open('$datadir/text', 'w')
wavscp = open('$datadir/wav.scp', 'w')
utt2spk = open('$datadir/utt2spk', 'w')
spk2utt = open('$datadir/spk2utt', 'w')
spk2gender = open('$datadir/spk2gender', 'w')

for line in sys.stdin:
    fields = [x.strip() for x in line.split('\t')]
    utt_id = fields[0][:-4]
    spkr = '-'.join(fields[0].split('-')[0:2])
    gender = fields[3][0] if fields[3][0] != 'u' else 'm'
    print >> text, utt_id, fields[5].lower()
    print >> wavscp, '{} $wav_cmd < {}/{} | '.format(utt_id, '$malromur', fields[0])
    print >> utt2spk, utt_id, spkr
    print >> spk2gender, spkr, gender
" < $info

utils/utt2spk_to_spk2utt.pl < $datadir/utt2spk > $datadir/spk2utt
utils/validate_data_dir.sh --no-feats $datadir || utils/fix_data_dir.sh $datadir

exit 0
