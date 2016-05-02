#!/usr/bin/env python

import itertools

'''Solve __ - 2_ = __ * _ = __.  From Escape from the Time Travel Lab on
1 May 2016.'''
for perm in itertools.permutations(range(1, 10)):
    x = (perm[0] * 10 + perm[1]) - (perm[2] * 10 + perm[3])
    y = (perm[4] * 10 + perm[5]) * perm[6]
    z = perm[7] * 10 + perm[8]
    if perm[2] == 2 and x == y and y == z:
        print('%d%d - %d%d = %d%d * %d = %d%d' % perm)
