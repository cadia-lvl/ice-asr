# Tutorial on language data preparation

This tutorial is an extension to the `ice-kaldi/s5` Readme file.

## Data

You need a lexicon and a text corpus to build a language model. For Icelandic you can use the pronunciation dictionary found on http://malfong.is. The text corpus should represent the task of the ASR system, i.e. contain similar language as the utterances the system is expected to recognize. The corpus should contain at least 1 million tokens, but depending on the task at hand a larger corpus will improve the results substantially. For an open vocabulary system a corpus size of about 15 million tokens gives reasonable results, although a much larger corpus can be used for a language model used for rescoring of the ASR results.

### Text preparation
For the first experiments, no preprocessing of the text corpus is needed (given that it is stored in plain text format), except for lowercasing, if all other data (dictionary and speech data prompts) have been lowercased as well. When you have established the ASR training process, text normalization should be performed before building a new language model. If you are working with Icelandic, have a look at `ice-asr/ice-norm`repository for some basic text normalization steps. 

## Preparing language data

### Language modeling

In the ice-kaldi implementation we use the MIT Language Modeling Toolkit for language modeling: https://github.com/mitlm/mitlm
The script `s5/local/make_ngram.sh` shows how to create an n-gram language model using mitlm.


