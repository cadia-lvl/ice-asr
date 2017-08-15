#Kaldi error analysis of Icelandic ASR

Kaldi error analysis contains scripts for the analysis of errors made by the Kaldi ASR system when decoding Icelandic speech.

The subjects of analysis are partly in line with research in ASR error analysis - here we have tools to test
different hypotheses four our data.
Research has e.g. shown the following:

* Errors are likely to be followed by errors
* More frequent words are more likely to be correct decoded than less frequent words
* Female speakers generally have better decoding results than male speakers
* Shorter words are generally more erroneous than longer words

Additionally, to see how severe errors are and improvement of which parts of the ASR system would most likely lead to better
results (e.g. improvement of the language model), the following aspects can be examined:

* Do substitution errors occur within the same inflection paradigm or not?
* How is the distribution of errors between word classes?
* Is the correct hypothesis contained within n-best hypotheses of the decoding lattice?
* How severe are the errors in terms of edit distance, both character- and word-wise?
* Do we have many errors that are caused by compounds not being correctly written out (compound in two words or
two words as a compound)?

Input files to analyse are always taken from the `wer_details` directory created by the scoring script in Kaldi. 
Several analysis scripts need additional files which are documented for each script as **additional required files**.

Substitutions part of same inflection paradigm or not: `bin_checker.py`
------------------------------------------------------------------------

**Additional required files:** .csv version of the BÍN database (http://bin.arnastofnun.is/forsida/). The BÍN 
database is case sensitive, create a lowercased version if your `ops` file only contains lowercased words.

**Usage:** `python bin_checker.py path/to/wer_details/ops path/to/SHsnid.csv <-o output_dir (default=kaldi_ops_by_lemma)>`

**Output:** `output_dir/different_lemma.txt output_dir/same_lemma.txt output_dir/wordform_not_in_bin.txt`
Summary is printed to stdout.

**Example:**

    ========= REPORT: substitutions same inflection paradigm or not ============

    Total number of substitutions: 1150
    Total number of distinctive same lemma substitutions: 400
    Total number of same lemma substitutions: 444 (38.61%)
    Total number of distinctive different lemma substitutions: 514
    Total number of different lemma substitutions: 569 (49.48%)

    Distinctive words not found in BÍN: 52
    Total number of substitutions of words not found in BÍN: 137 (11.91%)
    
different_lemma.txt:

    enn	en	12
    vegar	hinsvegar	8
    á	og	5
    á	af	4

same_lemma.txt:

    kemur	kæmi	8
    eru	er	6
    er	eru	4
    loka	lokað	4
    kyrrstæðum	kyrrstæðan	3

General error analysis: edit distance, compounds `categories.py`
-----------------------------------------------------------------

This scripts categorizes errors mainly by edit distance: 

* word wise edit distance one, caused by one deletion or insertion
* word wise edit distance one, caused by one substitution AND the edit distance between the reference word and 
the hypothesis is equal to one
* same as above, but the edit distance between the reference and hypothesis is greater than one
* other errors - utterances that do not match one of the other categories, i.e. more than one error per utterance
* compounds: reference - hypothesis pairs where ref uses a compound and the hypothesis two seperated words, or vice versa. This
analysis is done to extract potential compounds, to estimate the influence of these errors on the overall WER (each 
error of this kind causes two errors: either one insertion or deletion, and one substitution) and to collect material
for how to deal with the compound issue in the ASR system. Example: 'hinsvegar' - 'hins vegar' (note: 
all other categories are mutually exclusive, utterances in this category also belong to the last category 'other errors')

**Usage:** `python categories.py path/to/wer_details/per_utt <-o output_dir (default=kaldi_error_cats)>`

**Output:** `output_dir/compounds, correct, levenshtein_gt_one, levenshtein_one, one_inserted_or_deleted, other_errors`

**Example:**

stdout:

    ========== Analyzing per_utt file from Kaldi decoding ==============

    Correct decoded utterances: 3716

    Utterances with compounds: 51
    Total occurrences of compounds : 102
    Utterances with levenshtein_gt_one: 315
    Total occurrences of levenshtein_gt_one : 315
    Utterances with levenshtein_one: 342
    Total occurrences of levenshtein_one : 342
    Utterances with one_inserted_or_deleted: 93
    Total occurrences of one_inserted_or_deleted : 93
    Utterances with other_errors: 344
    Total occurrences of other_errors : 844

compounds:

    <id1>	mótinu verður fram haldið í dag	mótinu verður *** framhaldið í dag	 : 	framhaldið
    <id2>	magma hefur greitt fyrir hluta bréfanna	magma hefur greitt fyrir *** hlutabréfanna	 : 	hlutabréfanna
    <id3>	ók ölvaður út af í skutulsfirði	ók ölvaður *** útaf í skutulsfirði	 : 	útaf

levenshtein_one:

    <id1>	búin að reka umboðsmanninn	búinn að reka umboðsmanninn	búin	búinn
    <id2>   gili	kili	gili	kili
    <id3>	vakta hurðarbak eftir eldsvoða	vakta hurðarbaki eftir eldsvoða	hurðarbak	hurðarbaki
    <id4>	eins sé mikill metnaður í hópnum	ein sé mikill metnaður í hópnum	eins	ein



Errors by context: `errors_by_context.py`
-----------------------------------------

Reports on errors following an error, errors following correct decoding and vice versa. Analyses operation sequences
like `[C, I, S, C, C]`.

**Usage:** `python errors_by_context.py path/to/wer_details/per_utt <-o output_dir (default=kaldi_per_utt_by_context)>`

**Output:** `output_dir/errors_after_C.txt, errors_after_D.txt, errors_after_I.txt, errors_after_S.txt, errors_beginning.txt`

Statistics are printed to stdout

**Example:**

    ========== Analyzing context of errors from per_utt file from Kaldi decoding ==============
    Errors in the beginning of an utterance: 489
    Errors after correct decoding: 682
    Errors after Deletions: 201
    Errors after Insertions: 96
    Errors after Substitutions: 126
    SUM ERRORS: 1594

    Correct in the beginning of an utterance: 4321
    Correct after correct decoding: 10431
    Correct after Deletions: 58
    Correct after Insertions: 64
    Correct after Substitutions: 695

    Sum of operations: 17163
    Correct: 15569
    Insertions: 161
    Deletions: 283
    Substitutions: 1150
    Sum utterances: 4810

    Probabilities:
    P(E) = 0.09
    P(C) = 0.91
    P(E|E) = 0.34
    P(E|C) = 0.06
    P(C|E) = 0.66
    P(C|C) = 0.94

errors_after_S.txt:

    nú brosi ég út í bæði	nú brosi *** og til bæði	['C', 'C', 'D', 'S', 'S', 'C']	3
    sveitarfélögin gripu fyrr til aðgerða	*** stéttarfélögin gripið til aðgerða	['D', 'S', 'S', 'C', 'C']	3
    stal veski og notaði greiðslukort	*** *** starfið skjálfanda greiðslukort	['D', 'D', 'S', 'S', 'C']	4
    samgöngumálin rædd við lífeyrissjóði	samgöngumálin *** ræddi lífeyrissjóð	['C', 'D', 'S', 'S']	3


Errors by corpus frequencies: `errors_by_frequency.py`
-------------------------------------------------------

Given a frequency list of the words of the corpus used for the language model, analyse if higher frequency words from
the corpus are used as substitutions for lower frequency words.

**Additional required files:** A file with frequency information, format: `word frequency`

**Usage:** `python errors_by_frequency.py path/to/wer_details/ops frequency_file <-o output_dir 
(default=kaldi_ops_by_corpus_freq)> <-n number of most frequent words to include in accuracy analysis (default=use all words)>`

**Output:** `output_dir/hypothesis_by_correct, hypothesis_by_occurrence, references_by_correct, references_by_occurrence,
subst_less_freq_with_more_freq, subst_more_freq_with_less_freq`

The output files named references_by* and hypothesis_by* show accuracy of each reference and hypothesis word, either ordered
by occurrences in the test set or by accuracy. The last column in these files shows corpus frequency. Two additional files
show which lower frequency words are replaced by higher frequency words and vice versa.

**Example:**

stdout:

    Substitutions of a less freq word with more freq word: 610
    Substitutions of a more freq word with a les freq word: 540

references_by_occurrence:

    WORD       OCC  C    D   I  S   %Correct  FREQ  
    í          698  656  20  0  22  93.98%    701835
    á          565  532  9   0  24  94.16%    476398
    að         281  257  12  0  12  91.46%    738528
    er         245  220  12  0  13  89.80%    278596
    ekki       198  193  1   0  4   97.47%    137895
    um         191  179  1   0  11  93.72%    204591
    við        167  152  5   0  10  91.02%    175791

subst_less_freq_with_more_freq:

    enn (14904) replaced by en (169531) 12 times
    eru (69421) replaced by er (278596) 6 times
    á (476398) replaced by og (570318) 5 times
    vestantil (5) replaced by til (198852) 4 times
    á (476398) replaced by að (738528) 3 times
    af (101103) replaced by á (476398) 3 times
    gili (3) replaced by kili (18) 3 times

Errors by speaker features, e.g. gender: `errors_by_speaker_class.py`
---------------------------------------------------------------------

This script sorts results from `wer_details/per_spk` by some feature given by a file mapping from speaker ids to feature.
Typically this would be gender, but also other features like age or origin could be used. The script classifies the 
speaker results by whichever features are given in the mapping file.

**Additional required files:** A file containing mappings between speaker ids as in the `per_spk` file, and some
 feature like gender. Format: `speaker_id\tspeaker_feature`

**Usage:** `python errors_by_speaker_class.py path/to/wer_details/per_spk speaker-ids2feature <-o output_dir 
(default=kaldi_per_spk_by_feature)>`

**Output:** `output_dir/speaker_statistics`

**Example:**
    
    Comparison of speaker results by speaker features:
    ===================================================
    male spoke 8603 words in 2415 sentences.
    Total number of word errors were: 778 and sentence errors were: 548
    Max WER: 23.02
    Min WER: 4.26
    Average WER: 9.09%
    General WER of male speakers: 9.04%
    -------------------
    female spoke 8399 words in 2395 sentences.
    Total number of word errors were: 816 and sentence errors were: 546
    Max WER: 28.4
    Min WER: 4.43
    Average WER: 9.69%
    General WER of female speakers: 9.72%
    -------------------
    Total spoken words: 17002 in 4810 sentences
    Total number of word errors were: 1594 and sentence errors were 1094
    Overall WER: 9.38

Errors by word length: `errors_by_word_length.py`
--------------------------------------------------

**Usage:** `python errors_by_word_length.py path/to/wer_details/ops <-o output_dir (default=kaldi_ops_by_length)>
<-n numberof most frequent words to include in the analysis (default=all)>`

**Output:** `output_dir/hypothesis_accumulated, hypothesis_sorted_by_accuracy, hyptothesis_sorted_by_length, 
hypothesis_sorted_by_occurrence_count` and the same for `references`

**Example:**

references_accumulated ('WORD' here meaning 'word-length', i.e. statistics accumulated over all words of the same length): 

    WORD  OCC   C     D   I  S    %Correct
    1     1280  1194  29  0  57   93.28%  
    2     1305  1177  41  0  87   90.19%  
    3     1570  1440  33  0  97   91.72%  
    4     2024  1830  56  0  138  90.42%  
    5     2978  2740  45  0  193  92.01%  
    6     1922  1766  19  0  137  91.88% 
     ...

references_sorted_by_accuracy:

    WORD                     OCC  C    D   I    S   %Correct
    dag                      36   36   0   0    0   100.00% 
    hjá                      36   36   0   0    0   100.00% 
    vilja                    34   34   0   0    0   100.00% 
    mjög                     33   33   0   0    0   100.00% 
    vel                      29   29   0   0    0   100.00% 

Errors by word class: `errors_by_wordclass.py`
----------------------------------------------

**Additional required file:** A POS-tag version of the utterances in the test set. Depending on the tagger you are using,
you might want to limit the statistics to multi-word utterances. The script can handle two types of format of the 
POS-tagged files:

IceTagger format:

    Enska nven
    bönnuð sþgven
    í aþ
    kínverskum lkfþsf
    miðlum lkfþsf <UNKNOWN>
    . .
    Allir fokfn
    fórust sfm3fþ
    í aþ
    flugslysinu nheþg <UNKNOWN>
    . .

JSON-format (Greynir):

    {
    "result": [
        [
        [
            "Telur",
            "sfg3en"
        ],
        [
            "að",
            "c"
        ],
        ...
        ],
        [
        ...
        ]
      ]
    }

For other formats, please adapt the script.

NOTE: the script uses the first character of each pos-tag string to define a word class, `sfg3en` thus becomes `s`

**Usage:** `python errors_by_wordclass.py path/to/wer_details/per_utt path/to/pos_tagged_utterances 
<-o output_dir (default=kaldi_per_wordclass)> <-f json (default=IceTagger format)>`

**Output:** To stdout: statistics per word class; `output_dir/<wordclass>_errors`

**Examples:** 

stdout:

    l
    Total occurrences: 1377
    Error ratio: 0.07
    ---- Substitution ratio: 0.06
    ---- Deletion ratio: 0.01
    ========================
    e
    Total occurrences: 1
    Error ratio: 1.00
    ---- Substitution ratio: 1.00
    ---- Deletion ratio: 0.00
    ========================    
    n
    Total occurrences: 5899
    Error ratio: 0.08
    ---- Substitution ratio: 0.07
    ---- Deletion ratio: 0.01
    ...

n_errors:

    afghanistan	afganistan
    aflamark	aflamarks
    afurða	afurðanna
    aga	eiga
    akreina	***
    akstursleiðum	akstursleiðir
    ...



Search for correct hypothesis in n-best hypotheses: `hypothesis_in_nbest.py`
----------------------------------------------------------------------------

**Additional required files:** The n-best hypotheses from Kaldi in text format, probably in a directory structure
like `nbest/archives.1/words_text.txt, nbest/archives.2/words_text.txt ...` etc. The script expects either a directory
of directories, each containing a file `words_text.txt` (you can easily change this constant in the script) or 
just a directory directly containing this file (if you only have one)

**Usage:** `python hypothesis_in_nbest.py path/to/wer_details/per_utt path/to/nbest_dir <-o output_dir 
(default=kaldi_per_utt_nbest)`

**Output:** `output_dir/all_wrong, in_nbest` where the `all_wrong` file contains utterance ids with nbest hypotheses
whereof none matches the correct reference.

**Example:**

to stdout:

    Correct hypotheses: 3669
    In nbest: 775
    Not in nbest: 366

all_wrong:

    is_is-tm11_02-2011-11-21T23:08:40.007719	samgöngumálin ræddi lífeyrissjóð
    is_is-tm11_02-2011-11-21T23:08:40.007719	samgöngumálin ræddi í lífeyrissjóð
    is_is-tm11_02-2011-11-21T23:08:40.007719	samgöngumálin ræddu í lífeyrissjóð
    is_is-tm11_02-2011-11-21T23:08:40.007719	samgöngumálin rædd í lífeyrissjóð
    is_is-tm11_02-2011-11-21T23:08:40.007719	samgöngumálin ræddu lífeyrissjóð
    is_is-tm11_02-2011-11-21T23:08:40.007719	samgöngumálin ræddi lífeyrissjóði
    is_is-tm11_02-2011-11-21T23:08:40.007719	samgöngumálin ræddi lífeyrissjóðnum
    is_is-tm11_02-2011-11-21T23:08:40.007719	samgöngumálin ræddi nýverið sól
    is_is-tm11_02-2011-11-21T23:08:40.007719	samgöngumálin rædd við lífeyrissjóðina
    is_is-tm11_02-2011-11-21T23:08:40.007719	samgöngumálin ræddi lífi sól
    is_is-tm11_02-2011-11-21T23:08:40.007719	REF=samgöngumálin rædd við lífeyrissjóði

in_nbest (ordered by hypothesis rank from n-best, last column showing the actual chosen best path):

    NBEST-ID                                              CORRECT-HYP                                                  NBEST-RANK-1                                             
    is_is-jais_2_03-2011-11-27T20:25:44.520412-2          laugalandi                                                   laugarlandi                                              
    is_is-jais_04_04-2011-11-27T19:48:44.982107-2         lögreglan vinnur að rannsókn málsins                         lögregla vinnur að rannsókn málsins                      
    is_is-ok21-2011-09-21T16:55:49.456796-2               þetta veltur allt á siglingastofnun                          þetta veltur allt að siglingastofnun                     
    is_is-althingi3_07-2011-12-03T01:33:03.284525-2       lokuðu vef sænsku ríkisstjórnarinnar                         þeir lokuðu vef sænsku ríkisstjórnarinnar                
    is_is-althingi3_05-2011-12-03T01:23:06.737348-2       mjósundi                                                     mjósyndi                                                 
    is_is-ok72-2011-09-26T20:32:44.808690-2               varað við stormi suðvestanlands                              varað við stormi suðaustanlands  
    