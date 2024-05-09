#!/usr/bin/env python
'''
The VRP model for objective BI
Created by Lebao Wu
'''

from gurobipy import *
from itertools import product

def BIMV(N, S, H, O, P, running_time, order, storage):
    Coefficient = [1] * N

    #Buliding model
    bimv = Model()

    # Generating variables
    v = bimv.addVars(S, N, H, vtype=GRB.BINARY, name='v')
    beta = bimv.addVars(N, vtype=GRB.BINARY, name='beta', obj=Coefficient)
    t = bimv.addVars(N, lb=1, ub=N, vtype=GRB.INTEGER, name='t')

    # Establishing constraints
    # cons1
    bimv.addConstrs(v.sum('*', i, '*') == 1 for i in range(N))
    # cons2
    bimv.addConstrs(v.sum(s, '*', h) <= 1 for s in range(S) for h in range(H))
    # cons3
    bimv.addConstrs(v.sum(s, '*', h + 1) <= v.sum(s, '*', h) for s in range(S) for h in range(H - 1))
    # cons4
    bimv.addConstrs(t[j] + 1 <= t[i] for i in range(N) for j in O[i])
    # cons5: is set on the lb and ub of variable t

    # cons6
    bimv.addConstrs(t[i] + 1 - N * (2 - v[s, i, h] - v[s, j, h + 1]) <= t[j]
                    for i in range(N) for j in range(N) for s in range(S) for h in range(H - 1))
    #cons7
    bimv.addConstrs(beta[i] >= v[s, i, h] + quicksum(v[s, j, h1] for h1 in range(h)) - 1
                    for i in range(N) for j in P[i] for s in range(S) for h in range(1, H))

    # Initialize variables
    for n in range(N):
        t[order[n]].Start = n + 1
    for s in range(S):
        for h, plate in enumerate(storage[s]):
            v[s, plate, h].Start = 1

    #Settings
    bimv.Params.OutputFlag = 0  # no show = 0
    bimv.Params.NoRelHeurTime = int(running_time / 60)
    bimv.Params.TimeLimit = running_time
    bimv.Params.Presolve = 2
    bimv.Params.Method = 3
    bimv.Params.Threads = 32
    bimv.optimize()

    #Output result
    optimized_order = []
    optimized_storage = [[] for s in range(S)]
    result = -1
    if bimv.SolCount >= 1:
        for i in range(N):
            if len(optimized_order) == 0:
                optimized_order.append(i)
                continue
            if round(t[i].x) > max([round(t[plate].x) for plate in optimized_order]):
                optimized_order.insert(-1, i)
            for index, plate in enumerate(optimized_order):
                if round(t[i].x) <= round(t[plate].x):
                    optimized_order.insert(index, i)
                    break

            for s in range(S):
                for h in range(H):
                    if sum(round(v[s, i, h].x) for i in range(N)) >= 1:
                        optimized_storage[s].append(sum([i * round(v[s, i, h].x) for i in range(N)]))
                    else:
                        break

        result = round(bimv.objVal)
    return bimv.status, result, optimized_order, optimized_storage, bimv.Runtime
