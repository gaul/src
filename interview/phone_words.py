#!/usr/bin/env python

'''
Given a phone number, find words that match a dictionary after translating the
digits to their character representation, e.g., 228 -> cat.
'''

import sys

_NUMBERS_TO_CHARS = {
    '2': 'abc',
    '3': 'def',
    '4': 'ghi',
    '5': 'jkl',
    '6': 'mno',
    '7': 'pqrs',
    '8': 'tuv',
    '9': 'wxyz',
}

def phone_words(number, words):
    for word in _phone_words_helper(list(number), words, 0):
        yield word

def _phone_words_helper(number, words, index):
    if len(number) == index:
        word = ''.join(number)
        if word in words:
            yield word
        return
    old_ch = number[index]
    for ch in _NUMBERS_TO_CHARS.get(number[index], ''):
        number[index] = ch
        for word in _phone_words_helper(number, words, index + 1):
            yield word
    number[index] = old_ch

def create_words(path):
    words = set()
    with file(path, 'r') as f:
        for line in f:
            words.add(line.strip())
    return words

def main():
    number = sys.argv[1]
    words_path = sys.argv[2]
    words = create_words(words_path)
    for word in phone_words(number, words):
        print word

if __name__ == '__main__':
    main()
