#Ice-Kaldi - Open ASR for Icelandic
###v 0.1

Ice-Kaldi (could be freely translated as "ice cold" in Icelandic) is an open automatic speech recognition environment for Icelandic. 
The system is being developed at the Reykjavik University for the purpose of having freely accessible resources for the development and customization of Icelandic speech recognition systems.

###Resources

The system is being trained on the _Málrómur_ speech data set, developed during the _Almannarómur_ project in the years 2010-2011. _Málrómur_ consists of about 127,000 recorded utterances from 556 Icelandic speakers. A part of the data set is accessible for download at http://malfong.is/, for a description of the data collection project see _Guðnason et al. (2012): Almannarómur: An open Icelandic speech corpus_ (http://www.mica.edu.vn/sltu2012/files/proceedings/15.pdf).

The pronunciation dictionary is based on the Icelandic pronunciation dictionary _Framburðarorðabók_ accessible on http://malfong.is. However, Rómur's pronunciation dictionary is more than double the size of the original pronunciation dictionary, and some inconsistencies in the original transcripts have been attacked. The pronunciation dictionary can be found in the `malromur` directory.

For the language models data from the Leipzig Wortschatz project were used. Part of this data can be accessed without a special agreement from http://corpora2.informatik.uni-leipzig.de/download.html

Rómur uses the Kaldi speech recognition toolkit (http://kaldi-asr.org/, https://github.com/kaldi-asr/kaldi) which is distributed under the Apache License, Version 2.0.

###Current status

The current setup uses a TDNN-LSTM implemented in the Kaldi framework. The recipe followed is from the Switchboard experiment: kaldi/egs/swbd/s5c/local/chain/run_tdnn_lstm.sh, the main training script being kaldi/egs/wsj/s5/steps/nnet3/chain/train.py. NOTE: since we are using a version of Kaldi from February 2017, some updated Python scripts have been stored locally within our project. 
The network was trained using about 100 hours of speech from _Málrómur_. <EXPLAIN MORE TECHNICAL THINGS ABOUT THE TDNN-LSTM> 
The language model is a trigram model with modified Kneser-Ney smoothing, built from 1 million sentences (17.6 million words) from the Leipzig Wortschatz project and training data from the _Málrómur_ prompts. The size of the pronunciation dictionary is about 136,000 words.

This setup reaches a word error rate (WER) of 16.43% on a test set of 6,000 open vocabulary utterances and 8.69% on a subset of 4,700 closed vocabulary utterances. In the course of the project the aim is to improve the models and the training setup to further reduce WER.

###Use the resources
See the Readme file in the _s5_ directory.

###Contact
The resources are being developed at the Language and Voice Lab at the Reykjavik University (http://www.ru.is/, http://lvl.ru.is).
Contact: Anna Björk Nikulásdóttir, annabn@ru.is 

###License and Copyright
???





