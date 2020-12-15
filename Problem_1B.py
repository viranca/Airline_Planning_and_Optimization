from gurobipy import *
from gurobipy import GRB
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

Aircraft  = [0,1,2,3]
Aircraft_n = [0,0,0,0]
Aircraft_leasecost  = [15000,34000, 80000, 190000]

# Aircraft = {"1": {"sp": 550, "s": 45,  "TAT": 25, "range": 1500,  "runway": 1400},
#             "2": {"sp": 820, "s": 70,  "TAT": 35, "range": 3300,  "runway": 1600},
#             "3": {"sp": 850, "s": 150, "TAT": 45, "range": 6300,  "runway": 1800},
#             "4": {"sp": 870, "s": 320, "TAT": 60, "range": 12000, "runway": 2600}}


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
with open('q_demand.csv', 'r') as f:
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
            
"""
=============================================================================
Compute a costmatrix for each aircraft type at each flight leg.
=============================================================================
"""
#aircraft 1
weekly_cost_1 = 15000
#fixed cost
C_X_1 = 300
#time-based cost
c_T_1 = 750
V_1 = 550
C_T_1 = c_T_1 * df_distance / V_1
#fuel cost
c_F_1 = 1
f = 1.42
C_F_1 = ((c_F_1 * f)/1.5) * df_distance
C_1 = C_X_1 + C_T_1 + C_F_1 

#aircraft 2
weekly_cost_2 = 34000
#fixed cost
C_X_2 = 600
#time-based cost
c_T_2 = 775
V_2 = 820
C_T_2 = c_T_2 * df_distance / V_2
#fuel cost
c_F_2 = 2
f = 1.42
C_F_2 = ((c_F_2 * f)/1.5) * df_distance
C_2 = C_X_2 + C_T_2 + C_F_2 

#aircraft 3
weekly_cost_3 = 80000
#fixed cost
C_X_3 = 1250
#time-based cost
c_T_3 = 1400
V_3 = 850
C_T_3 = c_T_3 * df_distance / V_3
#fuel cost
c_F_3 = 3.75
f = 1.42
C_F_3 = ((c_F_3 * f)/1.5) * df_distance
C_3 = C_X_3 + C_T_3 + C_F_3 

#aircraft 4
weekly_cost_4 = 190000
#fixed cost
C_X_4 = 2000
#time-based cost
c_T_4 = 2800
V_4 = 870
C_T_4 = c_T_4 * df_distance / V_4
#fuel cost
c_F_4 = 9.0
f = 1.42
C_F_4 = ((c_F_4 * f)/1.5) * df_distance
C_4 = C_X_4 + C_T_4 + C_F_4 
  
#accounting economies of scale (departing and arriving from hub)
C_1 = np.array(C_1)
for i in range(len(C_1)):
    for j in range(len(C_1)):
        if i == 1 and j != 1:
            C_1[i][j] = 0.7*C_1[i][j]
        if j == 1:
            C_1[i][j] = 0.7*C_1[i][j]
            
C_2 = np.array(C_2)
for i in range(len(C_2)):
    for j in range(len(C_2)):
        if i == 1 and j != 1:
            C_2[i][j] = 0.7*C_2[i][j]
        if j == 1:
            C_2[i][j] = 0.7*C_2[i][j]
            
C_3 = np.array(C_3)            
for i in range(len(C_3)):
    for j in range(len(C_3)):
        if i == 1 and j != 1:
            C_3[i][j] = 0.7*C_3[i][j]
        if j == 1:
            C_3[i][j] = 0.7*C_3[i][j]
            
C_4 = np.array(C_4)           
for i in range(len(C_4)):
    for j in range(len(C_4)):
        if i == 1 and j != 1:
            C_4[i][j] = 0.7*C_4[i][j]
        if j == 1:
            C_4[i][j] = 0.7*C_4[i][j]



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
C = {}
z_0 ={}
z_1 ={}
z_2 ={}
z_3 ={}

for i in airports:
    for j in airports:
        x[i,j] = m.addVar(obj = Yield[i][j]*distance[i][j],lb=0,
                           vtype=GRB.INTEGER)
        z_0[i,j] = m.addVar(obj = -CASK*distance[i][j]*s, lb=0,
                           vtype=GRB.INTEGER)
        z_1[i,j] = m.addVar(obj = -CASK*distance[i][j]*s, lb=0,
                           vtype=GRB.INTEGER)
        z_2[i,j] = m.addVar(obj = -CASK*distance[i][j]*s, lb=0,
                           vtype=GRB.INTEGER)
        z_3[i,j] = m.addVar(obj = -CASK*distance[i][j]*s, lb=0,
                           vtype=GRB.INTEGER)        


for k in Aircraft:
    C[k] = m.addVar(obj = -Aircraft_leasecost[k], lb=0,
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
        m.addConstr(x[i, j], GRB.LESS_EQUAL, (z_0[i,j]+z_1[i,j]+z_2[i,j]+z_3[i,j])*s*LF) #C2
    m.addConstr(quicksum((z_0[i,j]+z_1[i,j]+z_2[i,j]+z_3[i,j]) for j in airports), GRB.EQUAL, quicksum((z_0[j, i] + z_1[j, i] + z_2[j, i] + z_3[j, i]) for j in airports)) #C3

m.addConstr(quicksum(quicksum((distance[i][j]/sp+LTO)*(z_0[i,j]+z_1[i,j]+z_2[i,j]+z_3[i,j]) for i in airports) for j in airports),
            GRB.LESS_EQUAL, BT*AC) #C4

# for k in Aircraft:
#     m.addConstr(C[k], GRB.LESS_EQUAL, q[i][j]) #C5



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
        if z_0[i,j].X >0:
            print(Airports[i], ' to ', Airports[j], z_0[i,j].X, z_1[i,j].X, z_2[i,j].X, z_3[i,j].X)