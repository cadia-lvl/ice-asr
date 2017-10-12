# Tutorial on language data preparation

This tutorial is an extension to the `ice-kaldi/s5` Readme file.

## Data

You need a lexicon and a text corpus to build a language model. For Icelandic you can use the pronunciation dictionary found on http://malfong.is. The text corpus should represent the task of the ASR system, i.e. contain similar language as the utterances the system is expected to recognize. For a general language ASR one can start experiments with 100,000-200,000k tokens, but depending on the task at hand a larger corpus will improve the results substantially. For an open vocabulary system a corpus size of about 15 million tokens gives reasonable results (for Icelandic), although a much larger corpus can be used for a language model used for rescoring of the ASR results.

### Text preparation
For the first experiments, no preprocessing of the text corpus is needed (given that it is stored in plain text format), except for lowercasing, if all other data (dictionary and speech data prompts) have been lowercased as well. When you have established the ASR training process, text normalization should be performed before building a new language model. If you are working with Icelandic, have a look at `ice-asr/ice-norm`repository for some basic text normalization steps. 

### Pronunciation dictionary
The pronunciation dictionary has to be in an aligned format, i.e. the phone symbols in the transcriptions have to be separated by a space:

	afborið	a v p ɔ r ɪ ð
	afbragð	a v p r a ɣ ð
	...
	afdráttarlaus	a v t r au h t a r l œyː s

If you need to add words to the lexicon, a grapheme-to-phoneme model can be trained on already transcribed data. One way to do this is to install Sequitur g2p  (https://github.com/sequitur-g2p/sequitur-g2p). Example scripts for the use of Sequitur g2p can be found in `s5/local/g2p`.

## Preparing language data

Having an aligned pronunciation dictionary and a text corpus in text format, the data have to be prepared for use in ASR training.

### Prepare lexicon data

The script `s5/local/prep_dict_data.sh` shows the steps needed to prepare the lexicon and pronunciation information. 


### Language modeling

In the ice-kaldi implementation we use the MIT Language Modeling Toolkit for language modeling: https://github.com/mitlm/mitlm.
The script `s5/local/create_language_model.sh` shows the steps needed to prepare data for language modeling, create a language model and convert it to .fst format used by Kaldi to create a final `HCLG.fst`.

To create a language model used for rescorig the results from the ASR system, a language model has to be created as in `create_language_model.sh` and then the model has to be converted:

	utils/build_const_arpa_lm.sh data/lang_large/trigram.arpa.gz data/lang data/const_arpa_lm_large

To use this model to rescore the ASR results:

	steps/lmrescore_const_arpa.sh <lm-used-in-asr> data/const_arpa_lm_large <path-to-hires-data-to-decode> <path-to-decoding-results> <path-to-rescored-decoding-results>

Example:

	steps/lmrescore_const_arpa.sh data/lang_small data/const_arpa_lm_large data/dev_hires exp/chain/tdnn_lstm/decode_dev exp/chain/tdnn_lstm/decode_dev_rescored




