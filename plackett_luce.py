#!/usr/bin/env python3

'''
Calculates the Bradley Terry factors for bots from Halite using Plackett-Luce model,
which is the generalization of BT for multiplayer rankings.  This model is more
appropriate for static competitiors (like programmed bots) than TrueSkill rankings,
because it gives equal weight to the whole history at once and is not order-dependent.
As result, proper orderings can be determined with less data.

Source:  Sections 5 and 6 starting on p.395 (p.12 in pdf) of
         Hunter, David R. MM algorithms for generalized Bradley-Terry models.
            Ann. Statist. 32 (2004), no. 1, 384--406. doi:10.1214/aos/1079120141.
            http://projecteuclid.org/euclid.aos/1079120141.

The algorithm here generates the BT factors using MLE.  A Bayesian approach has
also recently been developed, which has some advantages.  See "Bayesian inference for
Plackett-Luce ranking models"  (Guiver, Snelson; 2009).
            
'''

import sqlite3
from collections import Counter
import argparse


def retrieve_sqldata(filename, sqlstring):
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    cursor.execute(sqlstring)
    return cursor.fetchall()    

def plackett_luce(rankings):
    ''' Returns dictionary containing player : plackett_luce_parameter keys
    and values. This algorithm requires that every player avoids coming in
    last place at least once and that every player fails to win at least once.
    If this assumption fails (not checked), the algorithm will diverge.

    Input is a list of dictionaries, where each dictionary corresponds to an
    individual ranking and contains the player : finish for that ranking.

    The plackett_luce parameters returned are un-normalized and can be
    normalized by the calling function if desired.'''
    players = set(key for ranking in rankings for key in ranking.keys())
    ws = Counter(name for ranking in rankings for name, finish in ranking.items() if finish < len(ranking))
    gammas = {player : 1.0 / len(players) for player in players}
    _gammas = {player : 0 for player in players}
    while sum((gamma - _gammas[player]) ** 2 for player, gamma in gammas.items()) > 1e-9:
        denoms = {player : sum(sum(0 if player not in ranking or ranking[player] < place else 1 / sum(gammas[finisher] for finisher in ranking if ranking[finisher] >= place) for place in range(1,len(ranking))) for ranking in rankings) for player in players}
        _gammas = gammas
        gammas = {player : ws[player] / denoms[player] for player in players}
    return gammas


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, default='db.sqlite3', help='Name of the games database.')
    parser.add_argument("-E", "--exclude-inactive", dest="excludeInactive", action = "store_true", default = False, help = "Exclude inactive bots from printed results.  All bots are always included for calculation purposes.")
    args = parser.parse_args()
    _rankings = retrieve_sqldata(args.filename, 'select game_id, name, finish, field_size from games')
    rankings = list()
    while _rankings:
        field_size = _rankings[0][3]
        rankings.append({player:finish for _, player, finish, _ in _rankings[:field_size]})
        _rankings = _rankings[field_size:]

    gammas = plackett_luce(rankings)
    player_data = retrieve_sqldata(args.filename, 'select name, path, active from players')
    active_status = {player:active for player, _, active in player_data}
    paths = {player:path for player, path, _ in player_data}
    normalizing_constant = sum(value for player, value in gammas.items() if (not args.excludeInactive) or active_status[player])

    gammas = {player : value / normalizing_constant for player, value in gammas.items() if (not args.excludeInactive) or active_status[player]}   #normalize

    for gamma, player in sorted([(v,k) for k,v in gammas.items()], reverse=True):
        print("{:<25}{:5.3f}   {:^1}  {:<25}".format(player, gamma, active_status[player], paths[player]))
