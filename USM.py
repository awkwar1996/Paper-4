#!/usr/bin/env python
'''
The ordinary model for objective US
Created by Lebao Wu
'''

from gurobipy import *
from itertools import product


def USM(N, S, H, O, P, running_time, order, storage):

    #Buliding model
    usm = Model()

    #Generating variables
    x = usm.addVars(N, N, vtype=GRB.BINARY, name='x')
    y = usm.addVars(N + 2, N + 2, vtype=GRB.BINARY, name='y')
    m = usm.addVars(N, lb=1, ub=H, vtype=GRB.INTEGER, name='m')
    #Setting objective
    usm.setObjective(quicksum(y[i, j] for i in range(N) for j in P[i]))

    #Establishing constraints
    # cons1
    usm.addConstrs(x.sum(i, '*') == 1 for i in range(N))
    # cons2
    usm.addConstrs(x.sum('*', n) == 1 for n in range(N))
    # cons3
    usm.addConstrs(quicksum(n * x[i, n] - n * x[j, n] for n in range(N)) >= 0 for i in range(N) for j in O[i])
    # cons4
    usm.addConstrs(N * (1 - y[i, j]) >= quicksum(n * x[j, n] - n * x[i, n] for n in range(N)) \
                   for i in range(N) for j in range(N))
    # cons5: note, plate N+1 in paper is plate N+1 in model
    usm.addConstrs(quicksum(y[i, j] for i in range (N)) + y[N + 1, j] == 1 for j in range(N))
    # cons6: note, plate 0 in paper is replaced by plate N in model
    usm.addConstrs(quicksum(y[i, j] for j in range(N+1)) == 1 for i in range(N))
    # cons7: note, plate 0 in paper is replaced by plate N in model
    usm.addConstr(quicksum(y[i, N] for i in range(N)) <= S)
    # cons8
    usm.addConstrs(m[j] + 1 - H * (1 - y[i, j]) - m[i] <= 0 for i in range(N) for j in range(N))
    # cons9: is set in the lb and ub of the variables

    #Initialize variables
    for i, n in product(range(N), range(N)):
        x[i, n].Start = 1 if order[n] == i else 0
    for stack in storage:
        former_plate = N
        for slot, plate in enumerate(stack):
            y[plate, former_plate].Start = 1
            m[plate] = slot + 1
            former_plate = plate

    #Settings
    usm.Params.OutputFlag = 0
    usm.Params.NoRelHeurTime = int(running_time / 60)
    usm.Params.TimeLimit = running_time
    usm.Params.Presolve = 2
    usm.Params.Method = 3
    usm.Params.Threads = 32
    usm.optimize()

    #Output results
    optimized_order = []
    optimized_storage = [[] for s in range(S)]
    result = -1
    if usm.SolCount >= 1:
        for n in range(N):
            for i in range(N):
                if round(x[i, n].x) >= 0.999:
                    optimized_order.append(i)
                    break

        for i in range(N):
            if round(y[i, N].x) >= 0.999:
                for s in range(S):
                    if len(optimized_storage[s]) == 0:
                        optimized_storage[s].append(i)
                        break
        for s in range(S):
            plate = optimized_storage[s][-1]
            run_flag = True
            while run_flag:
                run_flag = True if sum(round(y[i, plate].x) for i in range(N)) >= 1 else False
                if run_flag:
                    next_plate = sum([i * round(y[i, plate].x) for i in range(N)])
                    optimized_storage[s].append(next_plate)
                    plate = next_plate

        result = round(usm.objVal)
    return usm.status, result, optimized_order, optimized_storage, usm.Runtime
