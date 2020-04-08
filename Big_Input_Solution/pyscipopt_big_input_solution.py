import pandas as pd
from pyvpsolver import *

# Preprocess
df_orders = pd.read_csv('demand_big.csv', delimiter='\t')
df_orders.columns = ['bin_length', 'quantity', 'subtotal']
orders_length = df_orders['bin_length'].values
orders_q = df_orders['quantity'].values

df_available = pd.read_csv('actual_big.csv', delimiter='\t')
available_length = df_available['wire_length'].values
available_q = df_available['quantity'].values

def BinPacking(w, q):
    s=[]
    for j in range(len(w)):
        for i in range(q[j]):
            s.append(w[j])
    return s

actual_length = BinPacking(available_length, available_q)
actual_length = [[i]for i in actual_length]
Ws = actual_length
Cs = [1]*len(actual_length)
Qs = [1]*len(actual_length)
ws = [[[x]] for x in orders_length]
b = orders_q.tolist()

# Creating instance
instance = MVP(Ws, Cs, Qs, ws, b)
afg = AFG(instance)

# Solving using Gurobi optimizer
output, solution = VPSolver.script("vpsolver_scip.sh", instance)

# Postprocessing
df_1 = pd.DataFrame(solution[1])
df_1.columns = ['raw_solution']
bin_len = [44, 53, 60, 105, 120, 157]

def get_scrap(x):
    if x < min(bin_len):
        return x
    else:
        return 0

def get_bin_size(x):
    if x != None:
        x = x[1]
        result = []
        for i in x:
            result.append(bin_len[i[0]])
        return result
    else:
        return 0

def get_leftover(x):
    if x[1] == 0:
        return 0
    else:
        return x[0] - sum(x[1])
    
df_1['wire_len'] = actual_length
df_1['bins'] = df_1.apply(lambda x: get_bin_size(x[0]), axis = 1)
df_1['wire_len'] = df_1.apply(lambda x: (x[1][0]), axis = 1)
df_1 = df_1.drop(columns='raw_solution')
df_1['leftover'] = df_1.apply(lambda x: get_leftover(x) ,axis = 1)
df_1['scrap'] = df_1.apply(lambda x: get_scrap(x[2]), axis=1)

bins_count = df_1['bins'].values.tolist()
bins_count = [i for i in bins_count if i != 0]

bin_times = sum(bins_count, [])
bin_dict = {}
for i in bin_times:
    if i not in bin_dict:
        bin_dict[i] = 1
    else:
        bin_dict[i] += 1

print(bin_dict)
print('Scrap equals to: ',df_1['scrap'].sum())

df_1.to_excel('PySCIPOPT_Big_input_results.xlsx')