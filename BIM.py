#!/usr/bin/env python
'''
The ordinary model for objective BI
Created by Lebao Wu
'''

from gurobipy import *
from itertools import product

def BIM(N, S, H, O, P, running_time, order, storage):
    Coefficient = [1] * N

    #Buliding model
    bim = Model()

    # Generating variables
    x = bim.addVars(N, N, vtype=GRB.BINARY, name='x')
    z = bim.addVars(N, S, vtype=GRB.BINARY, name='z')
    beta = bim.addVars(N, vtype=GRB.BINARY, name='beta', obj=Coefficient)

    # Establishing constraints
    # cons1
    bim.addConstrs(x.sum(i, '*') == 1 for i in range(N))
    # cons2
    bim.addConstrs(x.sum('*', n) == 1 for n in range(N))
    # cons3
    bim.addConstrs(quicksum(n * x[i, n] - n * x[j, n] for n in range(N)) >= 0 for i in range(N) for j in O[i])
    # cons4
    bim.addConstrs(z.sum(i, '*') == 1 for i in range(N))
    # cons5
    bim.addConstrs(z.sum('*', s) <= H for s in range(S))
    # cons6
    bim.addConstrs(
        N * beta[i] >= quicksum(n * x[i, n] - n * x[j, n] for n in range(N)) - 2 * N * (2 - z[i, s] - z[j, s]) \
        for i in range(N) for j in P[i] for s in range(S))

    # Initialize variables
    for i, n in product(range(N), range(N)):
        x[i, n].Start = 1 if order[n] == i else 0
    for s, i in product(range(S), range(N)):
        z[i, s].Start = 1 if i in storage[s] else 0

    #Settings
    bim.Params.OutputFlag = 0  # no show = 0
    bim.Params.NoRelHeurTime = int(running_time / 60)
    bim.Params.TimeLimit = running_time
    bim.Params.Presolve = 2
    bim.Params.Method = 3
    bim.Params.Threads = 32
    bim.optimize()

    #Output result
    optimized_order = []
    optimized_storage = [[] for s in range(S)]
    result = -1
    if bim.SolCount >= 1:
        for n in range(N):
            for i in range(N):
                if round(x[i, n].x) >= 0.999:
                    optimized_order.append(i)
                    break
        for n in range(N):
            for s in range(S):
                if round(z[optimized_order[n], s].x) >= 0.999:
                    optimized_storage[s].append(optimized_order[n])
                    break
        result = round(bim.objVal)
    return bim.status, result, optimized_order, optimized_storage, bim.Runtime
