#!/usr/bin/env python
'''
The VRP model for objective US
Created by Lebao Wu
'''

from gurobipy import *
from itertools import product

def USMV(N, S, H, O, P, running_time, order, storage):

    #Buliding model
    usmv = Model()

    #Generating variables
    y = usmv.addVars(N + 2, N + 2, vtype=GRB.BINARY, name='y')
    m = usmv.addVars(N, lb=1, ub=H, vtype=GRB.INTEGER, name='m')
    t = usmv.addVars(N, lb=1, ub=N, vtype=GRB.INTEGER, name='t')

    #Setting objective
    usmv.setObjective(quicksum(y[i, j] for i in range(N) for j in P[i]))

    # Establishing constraints
    # cons1: note, plate N+1 in paper is plate N+1 in model
    usmv.addConstrs(quicksum(y[i, j] for i in range(N)) + y[N + 1, j] == 1 for j in range(N))
    # cons2: note, plate 0 in paper is replaced by plate N in model
    usmv.addConstrs(quicksum(y[i, j] for j in range(N + 1)) == 1 for i in range(N))
    # cons3: note, plate 0 in paper is replaced by plate N in model
    usmv.addConstr(quicksum(y[i, N] for i in range(N)) <= S)
    # cons4
    usmv.addConstrs(m[j] + 1 - H * (1 - y[i, j]) - m[i] <= 0 for i in range(N) for j in range(N))
    # cons5: is set in the lb and ub of the variables m
    # cons6
    usmv.addConstrs(t[j] + 1 - N * (1 - y[i, j]) <= t[i] for i in range(N) for j in range(N))
    # cons7
    usmv.addConstrs(t[j] + 1 <= t[i] for i in range(N) for j in O[i])
    # cons8: is set in the lb and ub of the variables t



    # Initialize variables
    for n in range(N):
        t[order[n]].Start = n+1
    for stack in storage:
        former_plate = N
        for slot, plate in enumerate(stack):
            y[plate, former_plate].Start = 1
            m[plate] = slot + 1
            former_plate = plate

    # Settings
    usmv.Params.OutputFlag = 0
    usmv.Params.NoRelHeurTime = int(running_time / 60)
    usmv.Params.TimeLimit = running_time
    usmv.Params.Presolve = 2
    usmv.Params.Method = 3
    usmv.Params.Threads = 32
    usmv.optimize()

    # Output results
    optimized_order = []
    optimized_storage = [[] for s in range(S)]
    result = -1
    if usmv.SolCount >= 1:
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

        result = round(usmv.objVal)
    return usmv.status, result, optimized_order, optimized_storage, usmv.Runtime
