#!/usr/bin/env python
'''
A greedy heuristic used to get an initial solution for the Models
'''
import copy
from itertools import product
import math
import numpy as np
import openpyxl
import pandas as pd


def GreedyHeuristic(S, H, N, plate_data, inbound_config):

    inbound_order = []
    storage_config = [[] for s in range(S)]
    min_group_of_each_stack = [math.inf for i in range(S)]
    min_long_of_each_stack = [math.inf for i in range(S)]

    for i in range(N):
        # 确定入库钢板
        inbound_stack_index = -1
        group = 0
        long = 0
        for s in range(len(inbound_config)):
            if len(inbound_config[s]) == 0: continue
            if inbound_stack_index == -1 or plate_data.loc[inbound_config[s][-1], 'group'] > group:
                inbound_stack_index = s
                group = plate_data.loc[inbound_config[inbound_stack_index][-1], 'group']
                long = plate_data.loc[inbound_config[inbound_stack_index][-1], 'long']
                continue
            if plate_data.loc[inbound_config[s][-1], 'group'] == group and plate_data.loc[
                inbound_config[s][-1], 'long'] > long:
                inbound_stack_index = s
                group = plate_data.loc[inbound_config[inbound_stack_index][-1], 'group']
                long = plate_data.loc[inbound_config[inbound_stack_index][-1], 'long']

        inbound_plate = inbound_config[inbound_stack_index].pop()
        inbound_plate_group = plate_data.loc[inbound_plate, 'group']
        inbound_plate_long = plate_data.loc[inbound_plate, 'long']
        inbound_order.append(inbound_plate)

        # 确定存储堆位
        is_block = True
        location_stack = -1
        for s in range(S):
            if len(storage_config[s]) == H: continue

            # if len(storage_config[s]) == 0:
            #     location_stack = s
            #     is_block = False
            #     continue
            if location_stack == -1:
                location_stack = s
                is_block = plate_data.loc[inbound_plate, 'group'] > min_group_of_each_stack[s]
                continue
            if plate_data.loc[inbound_plate, 'group'] <= min_group_of_each_stack[s]:#is_block = False
                if is_block == False:
                    if min_group_of_each_stack[location_stack] < min_group_of_each_stack[s]:
                        continue
                    elif min_group_of_each_stack[location_stack] == min_group_of_each_stack[s]:
                        if min_long_of_each_stack[location_stack] - plate_data.loc[inbound_plate, 'group'] >= 0 and \
                                min_long_of_each_stack[s] - plate_data.loc[inbound_plate, 'group'] <= 0:
                            continue
                        elif min_long_of_each_stack[location_stack] - plate_data.loc[inbound_plate, 'group'] >= 0 and \
                                min_long_of_each_stack[s] - plate_data.loc[inbound_plate, 'group'] >= 0 \
                                and min_long_of_each_stack[location_stack] <= min_long_of_each_stack[s]:
                            continue
                is_block = False
                location_stack = s
            elif is_block == True:
                if min_long_of_each_stack[location_stack] - plate_data.loc[inbound_plate, 'group'] <= 0 and \
                        min_long_of_each_stack[s] - plate_data.loc[inbound_plate, 'group'] >= 0:
                    location_stack = s
                if min_long_of_each_stack[location_stack] - plate_data.loc[inbound_plate, 'group'] >= 0 and \
                        min_long_of_each_stack[s] - plate_data.loc[inbound_plate, 'group'] >= 0 and \
                        min_long_of_each_stack[location_stack] > min_long_of_each_stack[s]:
                    location_stack = s
        #
        storage_config[location_stack].append(inbound_plate)
        min_long_of_each_stack[location_stack] = min(min_long_of_each_stack[location_stack],
                                                     plate_data.loc[inbound_plate, 'long'])
        min_group_of_each_stack[location_stack] = min(min_group_of_each_stack[location_stack],
                                                      plate_data.loc[inbound_plate, 'group'])
    return inbound_order, storage_config
