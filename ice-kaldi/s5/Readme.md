# Ice-Kaldi - Open ASR for Icelandic

## Kaldi and basic setup

The system uses the Kaldi speech recognition toolkit. Find download and installing instructions in Kaldi's online documentation:
http://www.danielpovey.com/kaldi-docs/install.html or https://github.com/kaldi-asr/kaldi. We are using a version of Kaldi from February 2017.
A thorough documentation of Kaldi can be found at http://kaldi-asr.org/, for a step-by-step tutorial for beginners see http://kaldi-asr.org/doc/kaldi_for_dummies.html.

*Note:* Per default Kaldi will be installed creating debuggable binaries at the cost of speed. When optimizing for speed you should edit `kaldi/src/kaldi.mk` as described
in http://kaldi-asr.org/doc/build_setup.html.

Kaldi has an excellent collection of examples in it's `$KALDI_ROOT/egs/` directory, have a look at `egs/wsj/` for example.

When you have installed Kaldi and cloned this project, edit `path.sh` and `setup.sh` according to the location of your Kaldi installation.
Run `setup.sh` from your `s5` directory to create symlinks to the folders `steps` and `utils` from an example project. 

Now you should be all set up for experimenting with Kaldi, below are descriptions on both how to use existing models and how to train your own.

## Getting data

On http://malfong.is/ you can find speech and text data as well as ready-to-use models.

### Icelandic speech data

Go to http://malfong.is and find the section ***Corpora - text and sound files (ísl. Málheildir - texta- og hljóðskrár)*** . There are two corpora that have been used to train Kaldi-based ASR systems for Icelandic: *The Malromur Corpus (ísl. Málrómur)* which is the one referred to in this project, and *Corpus of Althingi's Parliamentary Speeches for ASR (ísl. Alþingisræður til talgreiningar)* (see: https://github.com/ingarun/kaldi).

You only need a speech corpus if you want to train your own acoustic models. See description of ready-to-use models below.

### Icelandic texts

The language models used in this project are based on texts from the ***Leipzig Wortschatz*** project developed at the University of Leipzig. A link is provided in section ***Corpora - text files*** on http://malfong.is at *Íslenskur orðasjóður*. This corpus contains general texts from .is domains from the web, mainly newspapers. For a domain specific ASR system language models need to be trained on representative texts.

### Pronunciation dictionary

There are two pronunciation dictionaries available under ***Language descriptions (ísl. Mállýsingar)*** on http://malfong.is: *Pronunciation dictionary (Framburðarorðabókin)* and *General pronunciation dictionary for ASR (Almenn framburðarorðabók fyrir talgreiningu)*. The former was developed during the Hjal project in 2003, about 60,000 manually transcribed words using both the IPA and the SAMPA phonetic alphabets. The general pronunciation dictionary for ASR is based on the first pronunciation dictionary, and currently lists about 136,000 transcribed words using IPA. The transcriptions of words not in the original lexicon was done automatically. This lexicon is available both in a standard format and in an aligned version directly applicable for Kaldi. 

### ASR models

At http://malfong.is we provide acoustic models, language models and a ready-to-use decoding graph created using our training set up. It might be a good starting point to run ASR using these models before starting your own adjustments and development, especially if you are new to Kaldi and ASR. 

## Speech recognition with existing models

To decode .wav files using already trained models, download the tdnn_lstm models from http://malfong.is. Place the graph directory and `chain/tdnn_lstm_online` in `s5/exp`.
The audio files to decode have to have a 16kHz sample rate. If you need to convert your audio, this can be done using sox: `sox - -c1 -esigned -r16000 -twav - <original-audio.wav> > <converted-audio.wav>`

To decode an audio file, go to `s5` and run:

	  local/chain/decode_tdnn_lstm_online.sh <your-audio-file>

Inspect the decoding script to see if the paths match your file names and directory structure.


## Train acoustic models

#### Data

*Note: if you want to train a neural network with the provided scripts, you have to have a speech corpus with at least 40 speakers*

To train an acoustic model you need speech data paired with text. These data need to be prepared in a certain way to be processable by Kaldi. The script `local/malromur_prep_data.sh` prepares data in the format of _Málrómur_, i.e. a directory containing a folder `wav` with all the `.wav` files and a text file called `wav_info.txt`, where each line describes one utterance in 11 columns :


	<wav-filename>	<recording-info>	<recording-info>	<gender>	<age>	<prompt (spoken text)>	<utterance length>	vorbis	16000	1	Vorbis


If your info text file has another format, please have a look at http://kaldi-asr.org/doc/data_prep.html to see what kind of output you have to generate.

Depending on if you have defined training and test sets or want to generate these randomly, there are two different procedures:

##### Pre-defined training and test sets
Divide the original meta data (wav\_info.txt) according to your defined training, test and development sets. Then run `malromur_prep_data.sh` (or your own data-prep script) on these directories separately:

    local/malromur_prep_data.sh <path-to-audio-files> <wav_info_training.txt> data/training_data
	local/malromur_prep_data.sh <path-to-audio-files> <wav_info_test.txt> data/test_data
	local/malromur_prep_data.sh <path-to-audio-files> <wav_info_dev.txt> data/dev_data
   

##### No pre-defined training and test sets 
Run `malromur_prep_data.sh` on the whole corpus and then divide the generated data randomly:
 
	local/malromur_prep_data.sh <path-to-audio-files> wav_info.txt data/all
	utils/subset_data_dir_tr_cv.sh --cv-utt-percent 10 data/{all,training_data,test_data}

The prepared data is now in `data/all` and after the subset command the prepared files are divided such that 10% of the data in `data/all` is now in `data/test_data` and the rest in `data/training_data`.

#### Feature extraction
On each of your defined sub-data folders (training, test, ...) run the feature extraction commands:

	steps/make_mfcc.sh --nj 40 --mfcc-config conf/mfcc.conf data/training_data exp/make_mfcc/training_data mfcc
	steps/compute_cmvn_stats.sh data/training_data exp/make_mfcc/training_data mfcc

#### Training
At this point you need to have language data in place. If you got our data from http://malfong.is, unpack the `lang` and the `lang_bi_small` directories and put them in your `s5/data/` directory. For creating your own lexicon and language model, see TUTORIAL.
To train an LDA+MLLT acoustic model run the commands in

    local/train_lda_mllt.sh

The script also contains commands to create a decoding graph and to decode the test set, including scoring of the results.
If you run this script as a whole (instead of one command at a time) running this script can take hours, depending on the size of your data sets. The paths to the language data are hard coded, so make sure these are the paths you are using or change otherwise. If you are training your first system, you should make a decoding graph and decode already after the first three training steps as shown in the script. This way you can see if everything is working and you already have your first ASR results! A decoding test at this early stage, however, is generally not necessary or useful.

#### Training a deep neural network
As stated above, you need a speech corpus with at least 40 speakers to train a DNN by this recipe. After running the previous step, run `local/chain/prepare_tdnn_lstm.sh`. This is an intermediate step before starting with the training of the neural network from the script `local/chain/run_tdnn_lstm.sh`. This script is adaptded from the _swbd_ expample in `kaldi/egs`.

This version of the script runs on one or more GPUs, see http://kaldi-asr.org/doc/dnn2.html#dnn2_gpu if you have to use CPUs.

The paths in the scripts are set according to the previous examples and the training uses one GPU. 

In the current version all parameters are used as given in the Switchboard recipe `kaldi/egs/swbd/local/chain/train_tdnn_lstm.sh`.

# Need ivectors for test set before decoding! Delete decode_looped from decode script

Before you can decode a test set using the DNN trained model, you need to create i-vectors for the test set (the extractor is generated by the training
script):

	steps/online/nnet2/extract_ivectors.sh <test-set_hires> data/lang <path/to/extractor> <output/path/ivectors_test>


To decode a test set, run:

	 local/decode_tdnn_lstm.sh <test-set> <path/to/decoding-graph>
	 local/score.sh <test-set_hires> <path/to/graph> <path/to/decoding-output>

 

