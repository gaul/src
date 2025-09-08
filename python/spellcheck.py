#!/usr/bin/env python

'''spellcheck.py - parse source code and spell check comments, strings, or all
tokens.

Usage: find $SRCDIR -name \*.java | spellcheck.py --dict /usr/share/dict/words

Most users will need a large custom dictionary of technical terms, e.g.,
HTTP, malloc, etc.  Users may want to pipe output through
"sort | uniq -c | sort -n" to find unusual and often incorrect spellings.
'''

__VERSION__ = 20250907

# TODO: allow compoundwords?
# TODO: bundle standard programming dictionary
# TODO: calculate edit distance from misspellings to likely spellings
# TODO: control word-splitting: camelCase, contractions, hyphenation
# TODO: diff mode for pre-push hooks
# TODO: emit file names and line numbers
# TODO: ignore comments, /* */, //, #
# TODO: ignore hex hashes
# TODO: ignore URLs
# TODO: incremental mode: show new misspellings since last run
# TODO: port to python 3
# TODO: show unusual spellings first (configurable limit?)
# TODO: single- and double-quote strings
# TODO: upper-case letters

# compare with: http://pypi.python.org/pypi/scspell

import argparse
import re
import string
import sys

STRING_CHAR = '"'

def parse_stream(stream, tokenize_all):
    '''Parse strings from stream of source code and emit tokenized words, e.g.,
    string = "foo bar" -> [foo, bar]
    "myString" -> [my, string]
    '''
    for line in stream:
        string = ''
        in_string = False
        in_backslash = False
        last_char = None
        for char in line:
            if tokenize_all or in_string:
                if in_backslash:
                    in_backslash = False
                    yield string
                    string = ''
                elif char == '\\':
                    in_backslash = True
                # parse camelCase
                # XXX better to do this outside parse_stream?
                elif (char.isupper() and last_char is not None and
                      last_char.isalpha() and not last_char.isupper()):
                    yield string
                    string = char
                elif char == STRING_CHAR:
                    in_string = False
                    yield string
                    string = ''
                else:
                    string += char
            else:
                if char == STRING_CHAR:
                    in_string = True
            last_char = char
        if len(string) > 0:
            yield string
        string = ''

translations = str.maketrans(string.ascii_uppercase, string.ascii_lowercase, string.digits + string.punctuation + string.whitespace)

def populate_dictionary(filename, dictionary):
    with open(filename, 'r') as f:
        for word in f:
            dictionary.add(word.translate(translations))

def main():
    parser = argparse.ArgumentParser(
            description='spell check strings in source code')
    parser.add_argument('--dict', dest='dictionaries',
            action='append', required=True)
    parser.add_argument('--tokenize-all', dest='tokenize_all',
            action='store_true', default=False)
    args = parser.parse_args(sys.argv[1:])

    all_dictionaries = set()
    for wordlist in args.dictionaries:
        populate_dictionary(wordlist, all_dictionaries)

    exit_code = 0
    for filename in sys.stdin:
        filename = filename[:-1]
        with open(filename, 'r') as f:
            for my_string in parse_stream(f, args.tokenize_all):
                # TODO: second parser!
                for word in re.split("[^A-Za-z]", my_string):
                    cword = word.translate(translations)
                    if cword == '':
                        continue
                    if cword not in all_dictionaries:
                        exit_code = 1
                        print(word)

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
