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


airports = range(len(Airports))
CASK = 0.12
LF = 0.75
s = 120
sp = 870
LTO = 20/60
BT = 10
AC = 2
y = 0.18  # yield

with open('q_placeholder.csv', 'r') as f:
    df = pd.read_csv(f, sep=';', header=0)
    data = df

q = np.array(data)


#%%   
#change this
distance = np.array(data)
#distance = [[0, 2236, 3201],
#          [2236, 0, 3500],
#          [3201, 3500, 0]]


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
        x[i,j] = m.addVar(obj = y*distance[i][j],lb=0,
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