import pandas as pd
from pyvpsolver import *
import numpy as np
import os
import sys
import timeout_decorator

if __name__ == "__main__":

    def read_input(input_bin_requirement, input_inventory):
        # Input Demand
        df_order = pd.read_excel(input_bin_requirement, header=None)
        df_order = df_order.dropna(axis=1, how='all')
        df_order = df_order.iloc[2:,:]
        order_q = df_order.loc[3, 1:].values.astype('int')
        order_b = df_order.loc[4, 1:].values.astype('int')

        # Input Inventory
        df_inventory = pd.read_excel(input_inventory, header=None)
        inventory_header = df_inventory.iloc[3, :]
        df_inventory.columns = inventory_header
        df_inventory = df_inventory.iloc[4:, :]
        inventory = sorted(df_inventory['Length (m)'].values.astype('int'))
        
        return order_q, order_b, inventory
    
    @timeout_decorator.timeout(50)
    def solve(order_q, order_b, inventory, cost, solver):
        cost_dict = {'linear': inventory, 'quadratic':np.array(inventory)*inventory}
        solver_dict = {'scip':"vpsolver_scip.sh", 'gurobi':'vpsolver_gurobi.sh', 'glpk':'vpsolver_glpk.sh'}
        Ws = [[i] for i in inventory]
        Cs = cost_dict[cost]
        Qs = [1]*len(inventory)
        ws = [[[x]] for x in order_b]
        b = order_q
        
        instance = MVP(Ws, Cs, Qs, ws, b)
        afg = AFG(instance)

        output, solution = VPSolver.script(solver_dict[solver], instance)
        
        return solution

    def format_solution_and_save(solution, cost, solver):
    
        # Formatting Solution
        df_solution = pd.DataFrame(solution[1])
        df_solution.columns = ['raw_solution']

        def get_scrap(x):
            if x < min(order_b):
                return x
            else:
                return 0

        def get_bin_size(x):
            if x != None:
                x = x[1]
                result = []
                for i in x:
                    result.append(order_b[i[0]])
                return result
            else:
                return 0

        def get_leftover(x):
            if x[1] == 0:
                return 0
            else:
                return x[0] - sum(x[1])

        df_solution['wire_len'] = inventory
        df_solution['bins'] = df_solution.apply(lambda x: get_bin_size(x[0]), axis = 1)
        df_solution = df_solution.drop(columns='raw_solution')
        df_solution['leftover'] = df_solution.apply(lambda x: get_leftover(x) ,axis = 1)
        df_solution['scrap'] = df_solution.apply(lambda x: get_scrap(x[2]), axis=1)

        bin_dict = {}
        for i in range(1, len(order_b)+1):
            df_solution['bin_'+str(i)] = 0
            bin_dict[order_b[i-1]] = 'bin_'+str(i)

        for index, row in enumerate(df_solution.values):
            allocated_bins = row[1]
            if type(allocated_bins) == list:
                for i in allocated_bins:
                    bin_id = bin_dict[i]
                    df_solution[bin_id][index]+=1
                    
        print('Cost: ', cost)            
        print('Solver: ', solver)
        print('Saved formatted solution as .xlsx in: ', os.getcwd())
        df_solution.to_excel(solver + '_solution_' + cost +'.xlsx')

    try:
        order_q, order_b, inventory = read_input(sys.argv[1], sys.argv[2])
    except:
        print('Please give appropriate input format')
        print('Please refer to documentation')
    
    solvers = ['scip', 'gurobi', 'glpk']
    costs = ['linear', 'quadratic']
    for solver in solvers:
        for cost in costs:
            try:
                raw_solution = solve(order_q, order_b, inventory, cost, solver)
                format_solution_and_save(raw_solution, cost, solver)
                try:
                    print('Finished Solving with:', solver)
                    print('---------------------')
                    print('---------------------')
                    print('---------------------')
                except TimeoutError:
                    print(solver, 'could not converge in given timer,reached timeout error, please increase timeout time')
                    continue
            except:
                print('Error, could not import:', solver)
                print('Please install',solver, 'properly')
