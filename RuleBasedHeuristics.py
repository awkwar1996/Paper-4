#!/usr/bin/env python
'''
The compared rule based heuristics proposed in [1]. As these methods do not consider operation order, a greedy rule is
embedded to determine operation order.

[1]Boysen N, Emde S. The parallel stack loading problem to minimize blockages[J]. European Journal of Operational Research, 2016, 249(2): 618-627.
'''

from LoadData import LoadData
from copy import deepcopy
import os
import time
from LA_N import extended_LA
from OutputSolution import save_rule_algorithm_result_to_excel
def GreedyOperationOrder():
    '''
    A greedy heuristic to determine operation order. Plates with the largest group are operated first.
    If two plates are in the same group, the one whose batch has the most plates are operated first.
    If there is still a tie, choose according to the index.

    :return: List of operation order
    '''
    batch = len(inbound_config)

    if batch == 1:
        return inbound_config[0][::-1]

    operation_order = []
    while len(operation_order) < N:
        chosen_plate, chosen_batch = -1, -1
        for batch_index, batch in enumerate(inbound_config):
            if len(batch) == 0: continue
            if chosen_plate == -1:
                chosen_plate, chosen_batch = batch[-1], batch_index
            elif plate_info.loc[batch[-1], 'group'] > plate_info.loc[chosen_plate, 'group']:
                chosen_plate, chosen_batch = batch[-1], batch_index
            elif plate_info.loc[batch[-1], 'group'] == plate_info.loc[chosen_plate, 'group'] and len(batch) > len(
                    inbound_config[chosen_batch]):
                chosen_plate, chosen_batch = batch[-1], batch_index
        operation_order.append(inbound_config[chosen_batch].pop())
    return operation_order
def FewestBlockageHeuristic(operationOrder, plate_info, S, H, P):
    '''
    Fill in plate to the stack result in less blockage.
    If both stacks results in blockage or not, choose the one with the lowest stack priority.
    :param operationOrder: The inbound order
    :return: The allocation
    '''
    operationOrder1 = deepcopy(operationOrder)
    allocation = [[] for _ in range(S)]
    stack_priority = [P + 1 for _ in range(S)]

    while len(operationOrder1) > 0:
        plate = operationOrder1.pop(0)
        plate_group = plate_info.loc[plate, 'group']
        # whether plate in a stack results in no blockage
        available_flag, location_stack = False, -1
        for s in range(S):
            if len(allocation[s]) == H: continue
            if location_stack == -1:
                location_stack, available_flag = s, stack_priority[s] >= plate_group
                continue

            if available_flag == False and stack_priority[s] >= plate_group:
                location_stack, available_flag = s, True
            if available_flag == (stack_priority[s] >= plate_group):
                if stack_priority[s] < stack_priority[location_stack]:
                    location_stack, available_flag = s, stack_priority[s] >= plate_group
        allocation[location_stack].append(plate)
        stack_priority[location_stack] = min(plate_group, stack_priority[location_stack])
    return allocation
# def LeastFilledStackHeuristic(operationOrder, plate_info, S, H, P):
#     '''
#     Fill in plate to the stack result in less blockage.
#     If both stacks results in blockage or not, choose the one with minimum plates.
#     :param operationOrder: The inbound order
#     :return: The allocation
#     '''
#     operationOrder1 = deepcopy(operationOrder)
#     allocation = [[] for _ in range(S)]
#     stack_priority = [P + 1 for _ in range(S)]
#
#     while len(operationOrder1) > 0:
#         plate = operationOrder1.pop(0)
#         plate_group = plate_info.loc[plate, 'group']
#         # whether plate in a stack results in no blockage
#         available_flag, location_stack = False, -1
#         for s in range(S):
#             if len(allocation[s]) == H: continue
#             if location_stack == -1:
#                 location_stack, available_flag = s, stack_priority[s] >= plate_group
#                 continue
#
#
#             if available_flag == False and stack_priority[s] >= plate_group:
#                 location_stack, available_flag = s, True
#             if available_flag == (stack_priority[s] >= plate_group):
#                 if len(allocation[s]) < len(allocation[location_stack]):
#                     location_stack, available_flag = s, stack_priority[s] >= plate_group
#         allocation[location_stack].append(plate)
#         stack_priority[location_stack] = min(plate_group, stack_priority[location_stack])
#
#     return allocation
def MostSimilarHeuristic(operationOrder, plate_info, S, H, P):
    '''
    Fill in plate to the stack result in less blockage.
    If both stacks results in blockage or not, choose the one with the least priority differ to inbound plate.
    :param operationOrder: The inbound order
    :return: The allocation
    '''
    operationOrder1 = deepcopy(operationOrder)
    allocation = [[] for _ in range(S)]
    stack_priority = [P + 1 for _ in range(S)]

    while len(operationOrder1) > 0:
        plate = operationOrder1.pop(0)
        plate_group = plate_info.loc[plate, 'group']
        # whether plate in a stack results in no blockage
        priority_gap, location_stack = False, -1
        for s in range(S):
            if len(allocation[s]) == H: continue
            if location_stack == -1:
                location_stack, priority_gap = s, abs(stack_priority[s] - plate_group)
                continue
            if abs(stack_priority[s] - plate_group) < priority_gap:
                location_stack, priority_gap = s, abs(stack_priority[s] - plate_group)
        allocation[location_stack].append(plate)
        stack_priority[location_stack] = min(plate_group, stack_priority[location_stack])

    return allocation
# def FirstFitHeuristic(operationOrder, plate_info, S, H, P):
#     '''
#     Fill in plate to the stack result in less blockage.
#     If both stacks results in blockage or not, choose the first one.
#     :param operationOrder: The inbound order
#     :return: The allocation
#     '''
#     operationOrder1 = deepcopy(operationOrder)
#     allocation = [[] for _ in range(S)]
#     stack_priority = [P + 1 for _ in range(S)]
#
#     while len(operationOrder1) > 0:
#         plate = operationOrder1.pop(0)
#         plate_group = plate_info.loc[plate, 'group']
#         # whether plate in a stack results in no blockage
#         available_flag, location_stack = False, -1
#         for s in range(S):
#             if len(allocation[s]) == H: continue
#             if location_stack == -1:
#                 location_stack, available_flag = s, stack_priority[s] >= plate_group
#                 continue
#
#             if available_flag == False and stack_priority[s] >= plate_group:
#                 location_stack, available_flag = s, True
#         allocation[location_stack].append(plate)
#         stack_priority[location_stack] = min(plate_group, stack_priority[location_stack])
#
#     return allocation
def BestFitHeuristic(operationOrder, plate_info, S, H, P):
    '''
    Fill in plate to the stack result in less blockage.
    If both stacks results in blockage or not, choose the one with the least priority differ to inbound plate.
    :param operationOrder: The inbound order
    :return: The allocation
    '''
    operationOrder1 = deepcopy(operationOrder)
    allocation = [[] for _ in range(S)]
    stack_priority = [P for _ in range(S)]
    remain_lower_plate = [0] * P
    for plate in operationOrder1:
        plate_group = plate_info.loc[plate, 'group']
        if plate_group == P: continue
        for group_index in range(plate_group, P):
            remain_lower_plate[group_index] += 1

    while len(operationOrder1) > 0:
        plate = operationOrder1.pop(0)
        plate_group = plate_info.loc[plate, 'group']
        # whether plate in a stack results in no blockage
        available_flag, location_stack, aHats = False, -1, -1
        for s in range(S):
            if len(allocation[s]) == H: continue
            stack_aHats = remain_lower_plate[stack_priority[s] - 1]
            if location_stack == -1:
                location_stack, available_flag, aHats = s, stack_priority[s] >= plate_group, stack_aHats
                continue
            if available_flag == False and stack_priority[s] >= plate_group:
                location_stack, available_flag, aHats = s, True, stack_aHats
            if available_flag == (stack_priority[s] >= plate_group):
                if stack_aHats < aHats:
                    location_stack, available_flag, aHats = s, stack_priority[s] >= plate_group, stack_aHats
                elif stack_aHats == aHats and len(allocation[s]) < len(allocation[location_stack]):
                    location_stack, available_flag, aHats = s, stack_priority[s] >= plate_group, stack_aHats
        allocation[location_stack].append(plate)
        stack_priority[location_stack] = min(plate_group, stack_priority[location_stack])
        if plate_group != P:
            for group_index in range(plate_group, P):
                remain_lower_plate[group_index] -= 1

    return allocation
def LeastStorageChanceHeuristic(operationOrder, plate_info, S, H, P):
    '''
    Fill in plate to the stack result in less blockage.
    If both stacks results in blockage or not, choose the one with the least priority differ to inbound plate.
    :param operationOrder: The inbound order
    :return: The allocation
    '''
    operationOrder1 = deepcopy(operationOrder)
    allocation = [[] for _ in range(S)]
    stack_priority = [P for _ in range(S)]
    remain_lower_plate = [0] * P
    remain_group_slot = [H * S] * P
    for plate in operationOrder1:
        plate_group = plate_info.loc[plate, 'group']
        for group_index in range(plate_group - 1, P):
            remain_lower_plate[group_index] += 1

    while len(operationOrder1) > 0:
        plate = operationOrder1.pop(0)
        plate_group = plate_info.loc[plate, 'group']
        # whether plate in a stack results in no blockage
        available_flag, location_stack, lsl = False, -1, -1
        for s in range(S):
            if len(allocation[s]) == H: continue
            stack_lsl = remain_lower_plate[stack_priority[s] - 1] / remain_group_slot[stack_priority[s] - 1] * (H - len(allocation[s]))
            if location_stack == -1:
                location_stack, available_flag, lsl = s, stack_priority[s] >= plate_group, stack_lsl
                continue
            if available_flag == False and stack_priority[s] >= plate_group:
                location_stack, available_flag, lsl = s, True, stack_lsl
            if available_flag == (stack_priority[s] >= plate_group):
                if stack_lsl < lsl:
                    location_stack, available_flag, lsl = s, stack_priority[s] >= plate_group, stack_lsl
                elif stack_lsl == lsl and len(allocation[s]) < len(allocation[location_stack]):
                    location_stack, available_flag, lsl = s, stack_priority[s] >= plate_group, stack_lsl
        for group_index in range(min(stack_priority[location_stack], plate_group)):
            remain_group_slot[group_index] -= 1
        for group_index in range(plate_group, stack_priority[location_stack]):
            remain_group_slot[group_index] -= H - len(allocation[location_stack])
        allocation[location_stack].append(plate)
        stack_priority[location_stack] = min(plate_group, stack_priority[location_stack])
        for group_index in range(plate_group - 1, P):
            remain_lower_plate[group_index] -= 1
    return allocation
def WeightedSimilarHeuristic(operationOrder, plate_info, S, H, P):
    '''
    Fill in plate to the stack result in less blockage.
    If both stacks results in blockage or not, choose the one with the least priority differ to inbound plate.
    :param operationOrder: The inbound order
    :return: The allocation
    '''
    operationOrder1 = deepcopy(operationOrder)
    allocation = [[] for _ in range(S)]
    weighted_stack_group = [P for _ in range(S)]

    while len(operationOrder1) > 0:
        plate = operationOrder1.pop(0)
        plate_group = plate_info.loc[plate, 'group']
        # whether plate in a stack results in no blockage
        weighted_group_gap, location_stack = False, -1
        for s in range(S):
            if len(allocation[s]) == H: continue
            if location_stack == -1:
                location_stack, weighted_group_gap = s, abs(weighted_stack_group[s] - plate_group)
                continue
            if abs(weighted_stack_group[s] - plate_group) < weighted_group_gap:
                location_stack, weighted_group_gap = s, abs(weighted_stack_group[s] - plate_group)

        if len(allocation[location_stack]) == 0:
            weighted_stack_group[location_stack] = plate_group
        else:
            weighted_stack_group[location_stack] = \
                ((weighted_stack_group[location_stack] * len(allocation[location_stack]) + plate_group) /
                 (len(allocation[location_stack]) + 1))
        allocation[location_stack].append(plate)

    return allocation
def rule_based_combined(operationOrder, plate_info, N, S, H, P):
    best_allocation = WeightedSimilarHeuristic(operationOrder, plate_info, S, H, P)
    best_relocation = extended_LA(plate_info, best_allocation, N, S, H + 2)
    function = 'WS'

    allocation = LeastStorageChanceHeuristic(operationOrder, plate_info, S, H, P)
    relocation = extended_LA(plate_info, allocation, N, S, H + 2)
    if relocation < best_relocation:
        best_relocation, best_allocation, function = relocation, allocation, 'LSC'

    # allocation = LeastFilledStackHeuristic(operationOrder, plate_info, S, H, P)
    # relocation = extended_LA(plate_info, allocation, N, S, H + 2)
    # if relocation < best_relocation:
    #     best_relocation, best_allocation = relocation, allocation

    allocation = FewestBlockageHeuristic(operationOrder, plate_info, S, H, P)
    relocation = extended_LA(plate_info, allocation, N, S, H + 2)
    if relocation < best_relocation:
        best_relocation, best_allocation, function = relocation, allocation, 'FB'

    allocation = MostSimilarHeuristic(operationOrder, plate_info, S, H, P)
    relocation = extended_LA(plate_info, allocation, N, S, H + 2)
    if relocation < best_relocation:
        best_relocation, best_allocation, function = relocation, allocation, 'MS'

    # allocation = FirstFitHeuristic(operationOrder, plate_info, S, H, P)
    # relocation = extended_LA(plate_info, allocation, N, S, H + 2)
    # if relocation < best_relocation:
    #     best_relocation, best_allocation = relocation, allocation

    allocation = BestFitHeuristic(operationOrder, plate_info, S, H, P)
    relocation = extended_LA(plate_info, allocation, N, S, H + 2)
    if relocation < best_relocation:
        best_relocation, best_allocation, function = relocation, allocation, 'BF'

    return best_allocation, best_relocation, function
if __name__ == "__main__":
    N, S, H, P, _, _, O, _, _, _, _, plate_info, inbound_config = LoadData('N500S125H4B6_17.xlsx')
    order = GreedyOperationOrder()
    print(time.time())
    print(WeightedSimilarHeuristic(order, plate_info, S, H, P))
    print(BestFitHeuristic(order, plate_info, S, H, P))
    print(LeastStorageChanceHeuristic(order, plate_info, S, H, P))
    print(time.time())
    # data_path = 'instances/batch 1'
    # output_path = 'result/Rule Based Heuristic/'
    # batch = 1
    #
    # instances = os.listdir(data_path)
    # for instance in instances:
    #     print(instance)
    #     N, S, H, P, _, _, O, _, _, _, _, plate_info, inbound_config = LoadData(data_path + '/' + instance)
    #     alg_result = {
    #         'FewestBlockageHeuristic': [],
    #         'LeastFilledStackHeuristic': [],
    #         'MostSimilarHeuristic': [],
    #         'FirstFitHeuristic': [],
    #         'BestFitHeuristic': [],
    #     }
    #     start_time = time.time()
    #     Order = GreedyOperationOrder()
    #     operation_order_time = time.time() - start_time
    #
    #     print('FewestBlockageHeuristic')
    #     alg_list = [FewestBlockageHeuristic, LeastFilledStackHeuristic, MostSimilarHeuristic, FirstFitHeuristic, BestFitHeuristic]
    #     start_time = time.time()
    #     Allocation = FewestBlockageHeuristic(Order)
    #     allocation_time = time.time() - start_time
    #     Relocation = extended_LA(plate_info, Allocation, N, S, H + 2)
    #     alg_result['FewestBlockageHeuristic'].append(Relocation)
    #     alg_result['FewestBlockageHeuristic'].append(allocation_time + operation_order_time)
    #
    #     print('LeastFilledStackHeuristic')
    #     start_time = time.time()
    #     Allocation = LeastFilledStackHeuristic(Order)
    #     allocation_time = time.time() - start_time
    #     Relocation = extended_LA(plate_info, Allocation, N, S, H + 2)
    #     alg_result['LeastFilledStackHeuristic'].append(Relocation)
    #     alg_result['LeastFilledStackHeuristic'].append(allocation_time + operation_order_time)
    #
    #     print('MostSimilarHeuristic')
    #     start_time = time.time()
    #     Allocation = MostSimilarHeuristic(Order)
    #     allocation_time = time.time() - start_time
    #     Relocation = extended_LA(plate_info, Allocation, N, S, H + 2)
    #     alg_result['MostSimilarHeuristic'].append(Relocation)
    #     alg_result['MostSimilarHeuristic'].append(allocation_time + operation_order_time)
    #
    #     print('FirstFitHeuristic')
    #     start_time = time.time()
    #     Allocation = FirstFitHeuristic(Order)
    #     allocation_time = time.time() - start_time
    #     Relocation = extended_LA(plate_info, Allocation, N, S, H + 2)
    #     alg_result['FirstFitHeuristic'].append(Relocation)
    #     alg_result['FirstFitHeuristic'].append(allocation_time + operation_order_time)
    #
    #     print('BestFitHeuristic')
    #     start_time = time.time()
    #     Allocation = BestFitHeuristic(Order)
    #     allocation_time = time.time() - start_time
    #     Relocation = extended_LA(plate_info, Allocation, N, S, H + 2)
    #     alg_result['BestFitHeuristic'].append(Relocation)
    #     alg_result['BestFitHeuristic'].append(allocation_time + operation_order_time)
    #
    #     save_rule_algorithm_result_to_excel(instance, alg_result, output_path + 'batch' + str(batch) + '.xlsx')
    #     del N, S, H, P, O, plate_info, inbound_config, Order, Allocation, Relocation
