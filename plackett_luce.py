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

from collections import Counter
import sqlite3, argparse, time
from math import sqrt
from itertools import accumulate, combinations
from graph_lib import scc

try:
    import numpy
    HAVE_NUMPY = True
except ImportError:
    HAVE_NUMPY = False

def retrieve_sqldata(filename, sqlstring):
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    cursor.execute(sqlstring)
    return cursor.fetchall()

def plackett_luce(rankings, tolerance=1e-9, check_assumption=True, normalize=True, verbose=False):
    '''This algorithm returns the MLE of the Plackett-Luce ranking parameters
    over a given set of rankings.  It requires that the set of players is unable
    to be split into two disjoint sets where nobody from set A has beaten anyone from
    set B.  If this assumption fails, the algorithm will diverge.  If the
    assumption is checked and fails, the algorithm will short-circuit and
    return None.

    Input is a list of dictionaries, where each dictionary corresponds to an
    individual ranking and contains the player : finish for that ranking.

    Output is a dictionary containing player : plackett_luce_parameter keys
    and values.
    '''

    players = set(key for ranking in rankings for key in ranking.keys())
    rankings = [sorted(ranking.keys(),key=ranking.get) for ranking in rankings]
    if check_assumption:
        edges = [(source, dest) for ranking in rankings for source, dest in combinations(ranking, 2)]
        scc_count = len(set(scc(edges).values()))
        if verbose:
            if scc_count == 1:
                print ('No disjoint sets found.  Algorithm convergence conditions are met.')
            else:
                print('%d disjoint sets found.  Algorithm will diverge.'.format(scc_count))
        if scc_count != 1:
            return None

    ws = Counter(name for ranking in rankings for name in ranking[:-1])
    gammas = {player : 1.0 / len(players) for player in players}
    gdiff = float('inf')
    iteration = 0
    start = time.perf_counter()
    while gdiff > tolerance:
        _gammas = gammas
        gamma_sums   =  [[1 / s for s in reversed(list(accumulate(gammas[finisher] for finisher in reversed(ranking))))] for ranking in rankings]
        gammas = {player : ws[player] / sum(sum(gamma_sum[:min(ranking.index(player) + 1, len(ranking) - 1)])
                                            for ranking, gamma_sum in zip(rankings, gamma_sums)
                                                if player in ranking)
                                            for player in players}
        if normalize:
            gammas = {player : gamma / sum(gammas.values()) for player, gamma in gammas.items()}
        pgdiff = gdiff
        gdiff = sqrt(sum((gamma - _gammas[player]) ** 2 for player, gamma in gammas.items()))
        iteration += 1
        if verbose:
            now = time.perf_counter()
            print("%d %.2f seconds L2=%.2e" % (iteration, now-start, gdiff))
            if gdiff > pgdiff:
                print("Gamma difference increased, %.4e %.4e" % (gdiff, pgdiff))
            start = now
    return gammas


def pl_numpy(rankings, tolerance=1e-9, check_assumption=True, normalize=True, verbose=False):
    """ Numpy implementation of the Plackett-Luce MLE algorithm described above.
    Translated from the original Matlab code by Dr. David Hunter available at
    http://sites.stat.psu.edu/~dhunter/code/btmatlab/plackmm.m
    """
    players = list(set(key for ranking in rankings for key in ranking.keys()))
    rankings = [sorted(ranking.keys(),key=ranking.get) for ranking in rankings]
    if check_assumption:
        edges = [(source, dest) for ranking in rankings for source, dest in combinations(ranking, 2)]
        scc_count = len(set(scc(edges).values()))
        if verbose:
            if scc_count == 1:
                print ('No disjoint sets found.  Algorithm convergence conditions are met.')
            else:
                print('%d disjoint sets found.  Algorithm will diverge.'.format(scc_count))
        if scc_count != 1:
            return None

    ws = Counter(name for ranking in rankings for name in ranking[:-1])

    # matlab code is 1-based, we're using 0-based so be wary of off-by-ones
    a = numpy.array([(players.index(name) + 1, ranking_index, finish) for ranking_index, ranking in enumerate(rankings, 1) for finish, name in enumerate(ranking,1)], dtype = int)
    M, N, P = numpy.max(a, axis=0)   #finding the counts of players and contests and the max rank ... I would have used len, but following orignal code
    f = numpy.zeros((P, N), dtype=int)
    r = numpy.zeros((M, N), dtype=int)
    f[a[:,2] - 1, a[:,1] - 1] = a[:,0]
    r[a[:,0] - 1, a[:,1] - 1] = a[:,2] + P * (a[:,1] - 1)

    w = numpy.array([ws[player] for player in players], dtype=int)
    pp = sum(f > 0)  # players per contest

    gammas = numpy.ones((M)) / M
    gdiff = float('inf')
    iterations = 0
    start = time.perf_counter()
    while gdiff > tolerance:
        iterations += 1
        g = (f > 0).choose(0, gammas[f - 1].squeeze())
        g = numpy.cumsum(g[::-1,:],axis=0)[::-1,:]   #reverse vertical cumsum
        g[pp - 1, numpy.arange(numpy.shape(g)[1])] = 0
        g[g > 0] = 1 / g[g > 0]
        numpy.cumsum(g,axis=0,out=g)
        r2 = (r > 0).choose(0, g.T.flat[r - 1])  #array indexing like Matlab https://stackoverflow.com/questions/20688881/numpy-assignment-and-indexing-as-matlab
        _gammas = gammas
        gammas = w / numpy.sum(r2,axis=1)
        if normalize:
            gammas /= numpy.sum(gammas)
        pgdiff = gdiff
        gdiff = numpy.linalg.norm(gammas - _gammas)
        if verbose:
            now = time.perf_counter()
            print("%d %.2f seconds L2=%.2e" % (iterations, now-start, gdiff))
            if gdiff > pgdiff:
                print("Gamma difference increased, %.4e %.4e" % (gdiff, pgdiff))
            start = now

    return {player : gamma for player, gamma in zip(players, gammas)}


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
