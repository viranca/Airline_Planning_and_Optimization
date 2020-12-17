# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 15:02:49 2020

@author: Daan Kerstjens
"""
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 15:56:11 2020

@author: Daan Kerstjens
"""
import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
from tqdm import tqdm
import gurobipy as gp 
from gurobipy import GRB

# Input variables
timeLimit = 100 # Time limit on the gurobi runtime in seconds, just to prevent an endless loop
rows = 141 # the first 141 rows of the duty periods contain the single flights

# Reading data from files
dutyCostsTotal = pd.read_csv('2_dutyCosts.csv',parse_dates=['Departure','Arrival'],index_col=0)
timeTable = pd.read_csv('1_Timetable_Group_26.csv')
dutyPeriodsTotal = pd.read_csv('2_Duty_Periods_Group_26.csv')

# Creating variables needed initially
dutyCosts = dutyCostsTotal.iloc[:rows]
dutyPeriods = dutyPeriodsTotal.iloc[:rows]
NoOfDuties = len(dutyCosts)
NoOfFlights = len(timeTable)
cp = dutyCosts['Cost'].values

# Creating delta_f^p: matrix containing all flights and all duty 
# periods, with delta_fpTotal[i,j] = 1 if flight i is serviced in duty j
delta_fpTotal = np.zeros([len(timeTable),len(dutyPeriodsTotal)])
flights = timeTable['Flight No.'].values
Flnrs = dutyPeriodsTotal['Flights']
pairsperflight = []

for i in tqdm(range(len(Flnrs))):
    q = ast.literal_eval(Flnrs[i])
    for r in q:
        # print(r)
        flnr = np.where(flights == r)[0][0]
        delta_fpTotal[flnr,i] = 1


# Dual problem
n = gp.Model('PricingProblem')
n.Params.timeLimit = timeLimit

# Make variables
y = n.addMVar(NoOfFlights)
n.update()

# Make Constraints
delta_fp = delta_fpTotal[:,:NoOfDuties] # only single leg duties are used
delta_pf = delta_fp.transpose()
n.addConstr(delta_pf @y <= cp)
n.update()

# Make objective
one = np.ones([1,NoOfFlights])
n.setObjective(one @ y,GRB.MAXIMIZE)
n.update()

n.optimize()

Pi2 = n.getAttr(GRB.Attr.Pi, n.getVars())



cpTot = dutyCostsTotal['Cost'].values
slackness = [-100]
k = 0
objectives = [n.objVal]
oud = 1e6
diff = 20
columns = list(range(NoOfDuties))
while diff > 0.001:
    Pif = np.array(n.getAttr(GRB.Attr.X,n.getVars()))
    slackness = cpTot - (delta_fpTotal.transpose() @ Pif)
    newColumns = list(slackness.argsort()[:50])
    columns += newColumns
    # newColumns = list(range(rows)) + newColumns
    
    # dutyCosts = dutyCostsTotal.iloc[newColumns]
    cp = dutyCostsTotal['Cost'].iloc[newColumns].values
    delta_fp = delta_fpTotal[:,newColumns]
    delta_pf = delta_fp.transpose()
    n.addConstr(delta_pf @y <= cp)
    n.update()
    n.optimize()
    k += 1
    # print(oud-n.objVal)
    objectives.append(n.objVal)
    diff = oud-n.objVal
    oud = n.objVal
    if k > 50:
        break

x = range(len(objectives))
plt.figure()
plt.plot(x,objectives,'x')
plt.xlabel('Iteration')
# plt.xticks(x)
plt.xticks(np.arange(min(x), max(x)+2, 2))
plt.ylabel('Objective value')
plt.savefig('2_Problem2_objectiveIteration.png')
plt.show()

chosenPairings = n.getAttr(GRB.Attr.Pi)
print('The (relaxed) pricing problem has the following pairings scheduled:')
for i in range(len(chosenPairings)):
    if chosenPairings[i] > 0:
        print('Duty',i,':',chosenPairings[i])

NoOfDuties = len(columns)
dutyCosts = dutyCostsTotal.iloc[columns]
m = gp.Model('Crew_pairing')
m.Params.timeLimit = timeLimit



# Make variables
x = m.addMVar(NoOfDuties,vtype=GRB.BINARY)

# Make constraints
# Make sure each flight is in only one used pairing
# Create a matrix of pairs per flight
delta_fp = delta_fpTotal[:,columns]
b = np.ones(NoOfFlights)
m.addConstr(delta_fp@x == b)


# Make objective
cp = dutyCosts['Cost'].values
cpT = cp.transpose()
m.setObjective(cpT @ x)
m.update()

m.optimize()

chosenPairings = m.getAttr(GRB.Attr.X)
print('The (binary) crew pairing problem has the following pairings scheduled:')
for i in range(len(chosenPairings)):
    if chosenPairings[i] > 0:
        print('Duty',i)