#Ice-Kaldi - Open ASR for Icelandic

##Kaldi and basic setup

The system uses the Kaldi speech recognition toolkit. Find download and installing instructions in Kaldi's online documentation:
http://www.danielpovey.com/kaldi-docs/install.html or https://github.com/kaldi-asr/kaldi. We are using a version of Kaldi from February 2017.

Kaldi has an excellent collection of examples in it's `$KALDI_ROOT/egs/` directory, have a look at `egs/wsj/` for example.

When you have cloned this project, edit `path.sh` and `setup.sh` according to the location of your Kaldi installation.
Run `setup.sh` from your `s5` directory to create symlinks to the folders `steps` and `utils` from an example project.

Now you should be all set up. Try decoding single wav-files or train your own acoustic models.

##Speech recognition with existing models - decode single wav-files

In the subdirectories of `models` you will find a ready-to-use model and a decoding graph. The script `online_decoding_nnet2.sh` uses this model to decode a wav-file, make sure the files to decode are recorded at 16kHz or converted to this samplerate. Later on you can configure these scripts to use your own models.

The language model is a bigram model with modified Kneser-Ney smoothing, trained on 1 million sentences from the Leipzig Wortschatz corpus.  --> ***update this models and decoding graph!***
This settings reaches a 23.17% WER on the Málrómur test set, slightly worse than using a trigram model on the same data (21.89% WER). Using bigrams reduces the size of the decoding graph to a great extent, making it more feasible for online decoding.

##Train acoustic models

####Data

*Note: if you want to train a neural network with the provided scripts, you have to have a speech corpus with at least 40 speakers*

To train an acoustic model you need speech data paired with text. These data need to be prepared in a certain way to be processable by Kaldi. The script `local/malromur_prep_data.sh` prepares data in the format of _Málrómur_, i.e. a directory containing a folder `wav` with all the `.wav` files and a text file called `wav_info.txt`, where each line describes one utterance in 11 columns :


	<wav-filename>	<recording-info>	<recording-info>	<gender>	<age>	<prompt (spoken text)>	<utterance length>	vorbis	16000	1	Vorbis


If your info text file has another format, please have a look at http://kaldi-asr.org/doc/data_prep.html to see what kind of output you have to generate.

Depending on if you have defined training and test sets or want to generate these randomly, there are two different procedures:

#####Pre-defined training and test sets
Divide the original meta data (wav\_info.txt) according to your defined training and test sets. Then run `malromur_prep_data.sh` (or your own data-prep script) on these directories separately:

    local/malromur_prep_data.sh <path-to-audio-files> <wav_info_training.txt> data/training_data
	local/malromur_prep_data.sh <path-to-audio-files> <wav_info_test.txt> data/test_data
   

#####No pre-defined training and test sets 
Run `malromur_prep_data.sh` and on the whole corpus and then divide the generated data randomly:
 
	local/malromur_prep_data.sh <path-to-audio-files> wav_info.txt data/all
	utils/subset_data_dir_tr_cv.sh --cv-utt-percent 10 data/{all,training_data,test_data}

The prepared data is now in `data/all` and after the subset command the prepared files are divided such that 10% of the data in `data/all` is now in `data/test_data` and the rest in `data/training_data`.

####Feature extraction
On each of your defined sub-data folders (training, test, ...) run the feature extraction commands:

	steps/make_mfcc.sh --nj 40 --mfcc-config conf/mfcc.conf data/training_data exp/make_mfcc/training_data mfcc
	steps/compute_cmvn_stats.sh data/training_data exp/make_mfcc/training_data mfcc

####Training
Before starting with the training, unpack `data/lang.tar.gz` and `data/lang_bi_small.tar.gz`
To train an LDA+MLLT acoustic model using the existing language model in `lang_bi_small`, run the commands in

    local/train_lda_mllt.sh

The script also contains commands to create a decoding graph and to decode the test set, including scoring of the results.
If you run this script as a whole (instead of one command at a time) running this script can take hours, depending on the size of your data sets. The paths are hard coded to match the previous steps, so make sure these are the paths you are using or change otherwise.

####Training a deep neural network
After running the previous step, run `local/chain/prepare_tdnn_lstm.sh`. This is an intermediate step before starting with the training of the neural network from the script `local/chain/run_tdnn_lstm.sh`. This script is adaptded from the _swbd_ expample in `kaldi/egs`.

This version of the script runs on one or more GPUs, see http://kaldi-asr.org/doc/dnn2.html#dnn2_gpu if you have to use CPUs.

The paths in the scripts are set according to the previous examples and the training uses one GPU. When training using a slurm.pl queue, we ran into an _invalid array_ error when using --max\_run\_jobs option. To avoid this, two scripts where customized: `train_multisplice_accel2_custom.sh` and `get_egs2_custom.sh`. If you need to use these customized scripts, exchange `train_multisplice_accel2.sh` for the customized version in `run_nnet2.sh`. *check whicht part of this are valid for the tdnn-lstm!* 

In the current version all parameters are used as given in kaldi/egs/swbd/local/chain/train_tdnn_lstm.sh. 

 

