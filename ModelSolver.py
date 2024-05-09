#!/usr/bin/env python
'''
Integrated model solver
'''
import math

from LoadData import LoadData
from BIM import BIM
from USM import USM
from BIMV import BIMV
from USMV import USMV
from GreedyHeuristic import GreedyHeuristic
from OutputSolution import save_model_result_to_excel
import os
from multiprocessing import Process


def Task(input_path, output_path, model_type):
    input_files = os.listdir(input_path)
    for input_file in input_files:
        print('----------' + input_file + '----------')
        # loading data
        N, S, H, P_max, L_max, L_min, O, P, L, P_s, L_s, plate_data, inbound_config = LoadData(
            input_path + '/' + input_file)
        # heuristic order and storage configuration
        order, storage = GreedyHeuristic(S, H, N, plate_data, inbound_config)
        # solve model
        if model_type == 'USM':
            status, result, opt_order, opt_storage, run_time = USM(N, S, H, O, P, 3600, order, storage)
        if model_type == 'BIM':
            status, result, opt_order, opt_storage, run_time = BIM(N, S, H, O, P, 3600, order, storage)
        if model_type == 'USMV':
            status, result, opt_order, opt_storage, run_time = USMV(N, S, H, O, P, 3600, order, storage)
        if model_type == 'BIMV':
            status, result, opt_order, opt_storage, run_time = BIMV(N, S, H, O, P, 3600, order, storage)
        # save result
        save_model_result_to_excel(status, result, opt_storage, plate_data, S, H, P_max, output_path + '/' + input_file,
                                   run_time)
        print('saved', output_path + '/' + input_file)


if __name__ == '__main__':
    p1 = Process(target=Task, args=('instances/group1', 'result/BI/B10', 'USM'))
    p1.start()
    p2 = Process(target=Task, args=('instances/group2', 'result/BI/B10', 'USM'))
    p2.start()
    p3 = Process(target=Task, args=('instances/group3', 'result/BI/B10', 'USM'))
    p3.start()
