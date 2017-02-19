#!/usr/bin/env python3

from plackett_luce import plackett_luce
from itertools import groupby

with open('nascar2002.txt','r') as infile:
    rankings = [tuple(map(int,line.split())) for line in infile.readlines()[1:]]    #drop header

rankings = [{driver:place for driver, race, place in group} for _, group in groupby(rankings,key=lambda x: x[1])]
gammas = plackett_luce(rankings, verbose=True)
for gamma, player in sorted([(v,k) for k,v in gammas.items()], reverse=True):
    print("{:<5}{:6.4f}".format(player, gamma))

from plackett_luce import pl_numpy as plackett_luce
gammas = plackett_luce(rankings, verbose=True)
for gamma, player in sorted([(v,k) for k,v in gammas.items()], reverse=True):
    print("{:<5}{:6.4f}".format(player, gamma))

#~ travis@F555L ~/Documents/halite/plackett-luce $ ./test_pl_nascar.py
#~ 58   0.1864
#~ 68   0.1096
#~ 54   0.0274
#~ 51   0.0235
#~ 66   0.0230
#~ 37   0.0205
#~ 82   0.0184
#~ 32   0.0168
#~ 72   0.0167
#~ 61   0.0161
#~ 31   0.0154
#~ 48   0.0153
#~ 52   0.0148
#~ 13   0.0146
#~ 63   0.0146
#~ 80   0.0142
#~ 12   0.0138
#~ 2    0.0135
#~ 67   0.0133
#~ 14   0.0127
#~ 60   0.0126
#~ 64   0.0126
#~ 53   0.0123
#~ 33   0.0118
#~ 62   0.0115
#~ 4    0.0115
#~ 76   0.0112
#~ 49   0.0109
#~ 77   0.0102
#~ 27   0.0099
#~ 42   0.0099
#~ 38   0.0097
#~ 45   0.0094
#~ 44   0.0093
#~ 34   0.0092
#~ 3    0.0090
#~ 21   0.0084
#~ 18   0.0082
#~ 36   0.0081
#~ 50   0.0080
#~ 41   0.0076
#~ 74   0.0073
#~ 55   0.0073
#~ 43   0.0072
#~ 35   0.0070
#~ 25   0.0070
#~ 22   0.0068
#~ 10   0.0065
#~ 7    0.0065
#~ 5    0.0063
#~ 26   0.0062
#~ 28   0.0062
#~ 6    0.0062
#~ 73   0.0061
#~ 9    0.0061
#~ 83   0.0059
#~ 79   0.0058
#~ 59   0.0057
#~ 39   0.0057
#~ 78   0.0055
#~ 23   0.0053
#~ 71   0.0053
#~ 65   0.0052
#~ 20   0.0052
#~ 56   0.0049
#~ 16   0.0039
#~ 15   0.0030
#~ 1    0.0029
#~ 70   0.0029
#~ 69   0.0028
#~ 40   0.0025
#~ 19   0.0022
#~ 81   0.0022
#~ 17   0.0022
#~ 8    0.0021
#~ 47   0.0021
#~ 11   0.0019
#~ 57   0.0019
#~ 46   0.0019
#~ 30   0.0017
#~ 29   0.0017
#~ 75   0.0015
#~ 24   0.0014
