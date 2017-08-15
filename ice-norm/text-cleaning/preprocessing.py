# -*- coding: utf-8 -*-

"""

    Preprocessing text for normalization.
    * Remove all kinds of symbols not relevant for syntax or pronunciation (see char_constants.NON_VALID_CHARS)
    * Remove dashes and correct spaces
    * Remove e-mail addresses
    * Clean urls so that they don't contain 'www.' or '.is/.com/.net'
    * Removes one kind of special string 'Þú ert hér:' followed by webpage links like 'Forsíða'
    * Tokenizes the preprocessed text, thus separating puncutation from words

    Otherwise leaves more complicated formatting issues for later steps.

    Format of the input corpus (Leipzig Wortschatz): One sentence per line, ending with a full stop.

"""

import re
import nltk

import char_constants
#from normalization import char_constants


LETTERS = '[' + char_constants.LETTERS + ']+'
WEBPAGE_LOC = 'Þú ert hér:'

def delete_non_conform_symbols(line):
    non_valid = re.compile(char_constants.NON_VALID_CHARS)
    clean_line = re.sub(non_valid, '', line)
    return clean_line


def remove_dashes(line):
    """
    Remove dashes preceded or followed by letters: 'Norður-Ameríka' becomes 'Norður Ameríka',
    'félags- og tryggingamálaráðuneytinu' becomes 'félags og tryggingamálaráðuneytinu',
    but 91-97 stays as it is. Dashes between numbers can be pronunciated and thus should be
    processed in a later step if it should be dealt with. Dashes surrounded by spaces are also
    left as is, as they often function as a kind of sentence boundary: 'tröll til sölu - Stóðhestsefni ...'

    :param line:
    :return:
    """
    replaced = line
    pattern = re.compile(LETTERS + '-\s*' + LETTERS)

    for m in re.finditer(pattern, line):
        substr = m.group()
        repl = substr.replace('-', ' ')
        replaced = replaced.replace(substr, repl)

    return replaced


def replace_e_mail(line):
    """
    Delete e-mail address if found in line
    :param line:
    :return: line without e-mail if found, otherwise return line
    """
    match = re.search('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{2,4}', line)
    if match:
        e_mail = match.group()
        return line.replace(e_mail, '')

    return line


def replace_pattern(regex, text):
    pattern = re.compile(regex, re.IGNORECASE)

    m = pattern.match(text)
    res = text
    if m:
        for g in m.groups():
            if g:
                res = res.replace(g, '')

    return res.strip()


def clean_web_page_labels(line):
    """
    Cleans out some special web page vocabulary:
    "11 Nýársmessa í Holtskirkju Þú ert hér: bb.is  Forsíða  Grein án commenta Alþjóða gjaldeyrissjóðurinn segir að
    tæknilega sé kreppan sé að baki." Becomes: "Alþjóða gjaldeyrissjóðurinn segir að tæknilega sé kreppan sé að baki ."

    :param line:
    :return: line cleaned from web page specific labels (Þú ert hér:, Forsíða, ...), might even return an empty line
    if it starts with a 'suspicious' label
    """

    if re.search(WEBPAGE_LOC, line):
        if re.search('(Gestabók)|(Viðburðir)', line):
            return ''
        tokens = nltk.word_tokenize(line)
        anchor_ind = tokens.index(':')
        text = ' '.join(tokens[anchor_ind + 4:])
        text = text.replace('án commenta', '')
        return text

    res = replace_pattern('(^innlent)?.+(meira forsíða\.\.$)', line)
    res = replace_pattern('(^innlent)?.+(forsíða\.\.$)', res)
    return res.strip()


def process(line):
    """
    Perform some cleaning procedures: remove all symbols irrelevant for syntax and pronunciation;
    remove e-mail addresses; remove some web-page specific labels (to avoid bias in word frequency).

    :param line:
    :return: a cleaned version of the input, where also punctuation is separated by spaces
    """
    processed_line = delete_non_conform_symbols(line)
    processed_line = remove_dashes(processed_line)
    processed_line = replace_e_mail(processed_line)
    processed_line = clean_web_page_labels(processed_line)
    tokens = nltk.word_tokenize(processed_line)
    result = ' '.join(tokens)
    return result[:-1]
