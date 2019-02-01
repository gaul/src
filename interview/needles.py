#!/usr/bin/env python

'''\
Given two strings, remove all characters contained in the latter from
the former.  Note that order is preserved.  For example:

    "ab",       "b"    -> "a"
    "abcdabcd", "acec" -> "bdbd"

What is the run-time of your algorithm?  How much memory does it use?  Is it
optimal?

linear search with memcpy:    O(nh**2)
linear search without memcpy: O(nh)
sort then binary search:      O(n log n + h log n)
table lookup:                 O(n + h)
'''

def remove_needles(haystack, needles):
    needles_set = frozenset(needles)
    return ''.join(c for c in haystack if c not in needles_set)

def remove_needles_test(haystack, needles, expected):
    actual = remove_needles(haystack, needles)
    assert actual == expected

def main():
    remove_needles_test('', '', '');
    remove_needles_test('a', '', 'a');
    remove_needles_test('', 'a', '');
    remove_needles_test('ab', 'b', 'a');
    remove_needles_test('bab', 'b', 'a');
    remove_needles_test('bab', 'a', 'bb');
    remove_needles_test('abcdabcd', 'acec', 'bdbd');

if __name__ == '__main__':
    main()
