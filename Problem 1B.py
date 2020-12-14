from gurobipy import *
import pandas as pd
import numpy as np


"""
=============================================================================
Setup parameters and demand/distance matrix:
=============================================================================
"""

Airports = ['London', 'Paris', 'Amsterdam',	'Frankfurt', 'Madrid',	'Barcelona', 'Munich', 
            'Rome', 'Dublin', 'Stockholm', 'Lisbon', 'Berlin', 'Helsinki', 'Warsaw', 'Edinburgh', 'Bucharest', 
            'Heraklion', 'Reykjavik',	'Palermo', 'Madeira']

Aircraft = {"1": {"sp": 550, "s": 45,  "TAT": 25, "range": 1500,  "runway": 1400},
            "2": {"sp": 820, "s": 70,  "TAT": 35, "range": 3300,  "runway": 1600},
            "3": {"sp": 850, "s": 150, "TAT": 45, "range": 6300,  "runway": 1800},
            "4": {"sp": 870, "s": 320, "TAT": 60, "range": 12000, "runway": 2600}}


airports = range(len(Airports))
CASK = 0.12       #unit operation cost per ASK flown
LF = 0.8          #average load factor
s = 120           #number of seats per aicraft
sp = 870          #speed of aicraft
LTO = 20/60       #same as turn around time
BT = 10*7         #times 7 for weekly times the number of aircraft
AC = 4            #number of aircraft types
y = 0.18          #yield

"""
=============================================================================
demand, distance and yield for every flight leg:
=============================================================================
"""
with open('q_placeholder.csv', 'r') as f:
    df_demand = pd.read_csv(f, sep=';', header=0)
q = np.array(df_demand)

with open('distance_df.csv', 'r') as f:
    df_distance = pd.read_csv(f, sep=',', header=0)
distance = np.array(df_distance)


Yield = 5.9 * (df_distance ** -0.76) + 0.043
Yield = np.array(Yield)
for i in range(len(Yield)):
    for j in range(len(Yield)):
        if i == j:
            Yield[i][j] = 0
            

    
#%%
"""
=============================================================================
Objective function: max revenue
=============================================================================
"""
# Start modelling optimization problem
m = Model('APO1B')
x = {}
z = {}
for i in airports:
    for j in airports:
        x[i,j] = m.addVar(obj = Yield[i][j]*distance[i][j],lb=0,
                           vtype=GRB.INTEGER)
        z[i,j] = m.addVar(obj = -CASK*distance[i][j]*s, lb=0,
                           vtype=GRB.INTEGER)

m.update()
m.setObjective(m.getObjective(), GRB.MAXIMIZE)  # The objective is to maximize revenue

"""
=============================================================================
Constraints:
=============================================================================
"""
for i in airports:
    for j in airports:
        m.addConstr(x[i,j], GRB.LESS_EQUAL, q[i][j]) #C1
        m.addConstr(x[i, j], GRB.LESS_EQUAL, z[i,j]*s*LF) #C2
    m.addConstr(quicksum(z[i,j] for j in airports), GRB.EQUAL, quicksum(z[j, i] for j in airports)) #C3

m.addConstr(quicksum(quicksum((distance[i][j]/sp+LTO)*z[i,j] for i in airports) for j in airports),
            GRB.LESS_EQUAL, BT*AC) #C4





m.update()
m.write('test.lp')
# Set time constraint for optimization (5minutes)
# m.setParam('TimeLimit', 1 * 60)
# m.setParam('MIPgap', 0.009)
m.optimize()
# m.write("testout.sol")
status = m.status

if status == GRB.Status.UNBOUNDED:
    print('The model cannot be solved because it is unbounded')

elif status == GRB.Status.OPTIMAL or True:
    f_objective = m.objVal
    print('***** RESULTS ******')
    print('\nObjective Function Value: \t %g' % f_objective)

elif status != GRB.Status.INF_OR_UNBD and status != GRB.Status.INFEASIBLE:
    print('Optimization was stopped with status %d' % status)


# Print out Solutions
print()
print("Frequencies:----------------------------------")
print()
for i in airports:
    for j in airports:
        if z[i,j].X >0:
            print(Airports[i], ' to ', Airports[j], z[i,j].X)