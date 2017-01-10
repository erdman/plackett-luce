#!/usr/bin/env python3

from plackett_luce import plackett_luce
from itertools import groupby

with open('nascar2002.txt','r') as infile:
    rankings = [tuple(map(int,line.split())) for line in infile.readlines()[1:]]    #drop header

rankings = [{driver:place for driver, race, place in group} for _, group in groupby(rankings,key=lambda x: x[1])]
gammas = plackett_luce(rankings)
normalizing_constant = sum(gammas.values())
gammas = {driver : value / normalizing_constant for driver, value in gammas.items()}

for gamma, player in sorted([(v,k) for k,v in gammas.items()], reverse=True):
    print("{:<5}{:5.3f}".format(player, gamma))



    
