#!/usr/bin/env python
'''
Determing the operation order by ALNS
'''

import math
import random
import time
from copy import deepcopy
import numpy as np
from RuleBasedHeuristics import rule_based_combined
import os
from LoadData import LoadData
from OutputSolution import save_algorithm_result_to_excel




class ALNS():
    #information of the problem and question
    plate_info = dict()
    inbound_config = []
    N, S, H, P = 0, 0, 0, 0
    precedssor, successor = {}, {}
    plate_order = []

    #result information
    global_order, current_order, new_order = [], [], []
    global_result, current_result, new_result = math.inf, math.inf, math.inf
    global_allocation, current_allocation, new_allocation = [], [], []
    global_allocation_function, new_allocation_function = '', ''

    #algorithm parameters
    #1. operators
    chosen_removal, chosen_insertation = -1, -1
    number_of_removal, number_of_insertion = 5, 4
    removal_score = [10 for i in range(number_of_removal)]
    insertion_score = [10 for i in range(number_of_insertion)]
    removal_number = 0
    w_1, w_2, w_3, w_4 = 1.5, 1.0, 0.8, 0.6
        # w_1: score reward that improve the global solution
        # w_2: score reward that improve the current solution
        # w_3: score reward that doesn't improve the solution but accepted
        # w_4: score reward that is unaccepted
    #2. main loop
    #max_iteration = 2000
    #3. acceptance
    alpha = 0.95# rate of cooling
    temperature = 100# initial temperature
    run_time = 0

    def __init__(self, plate_info, inbound_config, N, S, H, P, O, run_time):
        print('----------ALNS started----------')
        self.N, self.S, self.H, self.P, self.plate_info, self.precedssor,self.inbound_config, = \
            N, S, H, P, plate_info, O, inbound_config
        #后续作业
        batch = len(inbound_config)
        batch_max = max([len(inbound_config[b]) for b in range(batch)])
        for b in range(batch):
            sets = []
            for plate in inbound_config[b]:
                self.successor[plate] = sets[:]
                sets.append(plate)
        #对plate进行排序，确定每个plate正常情况下应该放的位置
        for p in range(self.P)[::-1]:
            for height in range(batch_max)[::-1]:
                for b in range(batch):
                    if len(inbound_config[b]) >= height + 1 and self.plate_info.loc[inbound_config[b][height],'group'] == p+1:
                            self.plate_order.append(inbound_config[b][height])
        # 计算每次移除的数量
        self.removal_number = math.ceil(self.N * 0.3)
        self.temperature = self.N
        self.run_time = run_time
    def initial_heuristic(self, type=2):
        temp_inbound_config = deepcopy(self.inbound_config)
        if type == 1:#random
            batch = [i for i in range(len(self.inbound_config))]
            while len(self.new_order) < self.N:
                selected_batch = random.choice(batch)
                self.new_order.append(temp_inbound_config[selected_batch].pop())
                if len(temp_inbound_config[selected_batch]) == 0: batch.remove(selected_batch)
        if type == 2:#greedy
            while len(self.new_order) < self.N:
                largest_group, selected_batch = 0, -1
                for b in range(len(self.inbound_config)):
                    # batch have no item
                    if len(temp_inbound_config[b]) == 0: continue
                    # no item have been selected
                    if selected_batch == -1:
                        largest_group, selected_batch = self.plate_info.loc[temp_inbound_config[b][-1], 'group'], b
                        continue
                    if self.plate_info.loc[temp_inbound_config[b][-1], 'group'] > largest_group:
                        largest_group, selected_batch = self.plate_info.loc[temp_inbound_config[b][-1], 'group'], b
                    elif self.plate_info.loc[temp_inbound_config[b][-1], 'group'] == largest_group and \
                            len(temp_inbound_config[b]) > len(temp_inbound_config[selected_batch]):
                        largest_group, selected_batch = self.plate_info.loc[temp_inbound_config[b][-1], 'group'], b
                self.new_order.append(temp_inbound_config[selected_batch].pop())

        self.allocation_and_relocation()
        self.global_order, self.current_order = self.new_order, self.new_order
        self.global_result, self.current_result = self.new_result, self.new_result
        self.global_allocation, self.current_allocation = self.new_allocation, self.new_allocation
        self.global_allocation_function = self.new_allocation_function
        print(f'initialize relocation {self.global_result}')
    def allocation_and_relocation(self):
        self.new_allocation, self.new_result, self.new_allocation_function = \
            rule_based_combined(self.new_order, self.plate_info, self.N, self.S, self.H, self.P)
    def acceptance(self):
        if self.new_result < self.global_result:#improve global result
            self.global_result, self.global_order, self. global_allocation = self.new_result, self.new_order, self.new_allocation
            self.current_result, self.current_order, self.current_allocation = self.new_result, self.new_order, self.new_allocation
            self.global_allocation_function = self.new_allocation_function
            self.removal_score[self.chosen_removal] += self.w_1
            self.insertion_score[self.chosen_insertation] += self.w_1
        elif self.new_result < self.current_result:#improve current result
            self.current_result, self.current_order, self.current_allocation = self.new_result, self.new_order, self.new_allocation
            self.removal_score[self.chosen_removal] += self.w_2
            self.insertion_score[self.chosen_insertation] += self.w_2
        elif random.random() <= math.exp((self.global_result - self.new_result)/self.temperature):#accepted by SA
            self.current_result, self.current_order, self.current_allocation = self.new_result, self.new_order, self.new_allocation
            self.removal_score[self.chosen_removal] += self.w_3
            self.insertion_score[self.chosen_insertation] += self.w_3
        else:#unaccepted
            self.removal_score[self.chosen_removal] += self.w_4
            self.insertion_score[self.chosen_insertation] += self.w_4
    def neighborhood_search(self):
        # random removal
        def removal_0():
            for i in range(self.removal_number):
                ejected_list.append(self.new_order.pop(random.randint(0, len(self.new_order) - 1)))
        # segment removal
        def removal_1():
            removal_start = random.randint(0, len(self.new_order) - 1 - self.removal_number)
            for i in range(self.removal_number):
                ejected_list.append(self.new_order.pop(removal_start))
        # group removal
        def removal_2():
            pop_group = random.randint(1, self.P)
            for plate in self.new_order:
                if self.plate_info.loc[plate, 'group'] == pop_group:
                    self.new_order.remove(plate)
                    ejected_list.append(plate)
        # unordered removal
        def removal_3():
            unordered_value = []
            for n in range(self.N):
                order_gap = abs(n - self.plate_order.index(self.new_order[n]))
                if len(ejected_list) < self.removal_number:
                    ejected_list.append(self.new_order[n])
                    unordered_value.append(order_gap)
                elif order_gap > min(unordered_value):
                    deleted_index = unordered_value.index(min(unordered_value))
                    unordered_value.pop(deleted_index)
                    ejected_list.pop(deleted_index)
                    ejected_list.append(self.new_order[n])
                    unordered_value.append(order_gap)
            for plate in ejected_list:
                self.new_order.pop(self.new_order.index(plate))
        # batch removal
        def removal_4():
            pop_batch = random.randint(1, int(self.plate_info.max()['batch']))
            for plate in self.new_order:
                if self.plate_info.loc[plate, 'batch'] == pop_batch:
                    self.new_order.remove(plate)
                    ejected_list.append(plate)
        # random insertion
        def insertion_0():
            for plate in ejected_list:
                former_index = -1
                later_index = self.N - 1
                for former_plate in self.precedssor[plate]:
                    if former_plate in self.new_order :
                        former_index = max(former_index, self.new_order.index(former_plate))
                for later_plate in self.successor[plate]:
                    if later_plate in self.new_order:
                        later_index = min(later_index, self.new_order.index(later_plate))
                if former_index + 1 >= later_index:
                    self.new_order.insert(former_index, plate)
                else:
                    self.new_order.insert(random.randint(former_index + 1, later_index),plate)
        # advance insertion
        def insertion_1():
            for plate in ejected_list:
                former_index = -1
                for former_plate in self.precedssor[plate]:
                    if former_plate in self.new_order:
                        former_index = max(former_index, self.new_order.index(former_plate))

                self.new_order.insert(former_index + 1, plate)
        # ordered insertion
        def insertion_2():
            for plate in ejected_list:
                former_index = -1
                later_index = self.N - 1
                for former_plate in self.precedssor[plate]:
                    if former_plate in self.new_order:
                        former_index = max(former_index, self.new_order.index(former_plate))
                for later_plate in self.successor[plate]:
                    if later_plate in self.new_order:
                        later_index = min(later_index, self.new_order.index(later_plate))

                order_of_plate = self.plate_order.index(plate)
                if order_of_plate <= former_index:
                    self.new_order.insert(former_index+1, plate)
                elif order_of_plate >= former_index:
                    self.new_order.insert(later_index, plate)
                else: self.new_order.insert(order_of_plate, plate)
        # backward insertion
        def insertion_3():
            for plate in ejected_list:
                latter_index = self.N - 1
                for latter_plate in self.successor[plate]:
                    if latter_plate in self.new_order:
                        latter_index = min(latter_index, self.new_order.index(latter_plate))

                self.new_order.insert(latter_index, plate)
        # choose operator by roulette
        def choose_operator(type):
            if type == 'remove':
                temp = [sum(self.removal_score[:i + 1]) for i in range(self.number_of_removal)]
                temp = [temp[i] / temp[-1] for i in range(self.number_of_removal)]
                random_value = random.random()

                i = 0
                while (i <= self.number_of_removal - 1):
                    if random_value < temp[i]:
                        return i
                    i += 1
                return self.number_of_insertion - 1
            if type == 'insert':
                temp = [sum(self.insertion_score[:i + 1]) for i in range(self.number_of_insertion)]
                temp = [temp[i] / temp[-1] for i in range(self.number_of_insertion)]
                random_value = random.random()

                i = 0
                while (i <= self.number_of_insertion - 1):
                    if random_value < temp[i]:
                        return i
                    i += 1
                return self.number_of_insertion - 1

        removal_operator_dict = {
            0: removal_0,
            1: removal_1,
            2: removal_2,
            3: removal_3,
            4: removal_4,
        }
        insertion_operator_dict = {
            0: insertion_0,
            1: insertion_1,
            2: insertion_2,
            3: insertion_3,
        }
        ejected_list = []
        self.new_order = deepcopy(self.current_order)
        # conduct removal
        self.chosen_removal = choose_operator('remove')
        removal_operator_dict[self.chosen_removal]()
        # sort ejected_list
        ejected_order = [self.plate_order[i] for i in ejected_list]
        ejected_list, _ = zip(*sorted(zip(ejected_list,ejected_order),key=lambda x:x[1]))
        # conduct insertion
        self.chosen_insertation = choose_operator('insert')
        insertion_operator_dict[self.chosen_insertation]()
    def main_procedure(self):
        start_time = time.time()
        self.initial_heuristic()
        iteration = 0
        while time.time() - start_time <= self.run_time:
            print(f'Iteration {iteration}, Time: {time.time()}')
            self.neighborhood_search()
            self.allocation_and_relocation()
            self.acceptance()
            self.temperature *= self.alpha
            iteration += 1
        return self.global_order, self.global_allocation, self.global_result, self.new_allocation_function
    def temp_main_procedure(self):
        self.initial_heuristic()
        return self.global_order, self.global_allocation, self.global_result, self.new_allocation_function
if __name__ == '__main__':
    # N, S, H, P, _, _, O, _, _, _, _, plate_info, inbound_config = LoadData('DataFormat30.xlsx')
    # run_time = 30*60
    # alns = ALNS(plate_info, inbound_config, N, S, H, P, O, run_time)
    # order, allocation, relocation, allo_function = alns.main_procedure()
    # print(relocation)
    data_path = 'instances/temp'
    output_path = 'result'
    run_time = 30 * 60

    input_files = os.listdir(data_path)
    for input_file in input_files:
        print('----------' + input_file + '----------')
        # loading data
        N, S, H, P, _, _, O, _, _, _, _, plate_info, inbound_config = LoadData(data_path + '/' + input_file)
        alns = ALNS(plate_info, inbound_config, N, S, H, P, O, run_time)
        order, allocation, relocation, function = alns.main_procedure()
        print(relocation)
        save_algorithm_result_to_excel(input_file, relocation, function, output_path + '/ALNS result.xlsx')

