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
from tqdm import tqdm
import gurobipy as gp 
from gurobipy import GRB


timeLimit = 100 # Time limit on the gurobi runtime in seconds
rows = 141

dutyCostsTotal = pd.read_csv('dutyCosts.csv',parse_dates=['Departure','Arrival'],index_col=0)
timeTable = pd.read_csv('1_Timetable_Group_26.csv')
dutyPeriodsTotal = pd.read_csv('2_Duty_Periods_Group_26.csv')
dutyCosts = dutyCostsTotal.iloc[:rows]
dutyPeriods = dutyPeriodsTotal.iloc[:rows]
# PPF = pd.read_csv('Pairsperflight.csv')

NoOfDuties = len(dutyCosts)
NoOfFlights = len(timeTable)


m = gp.Model('Crew_pairing')
m.Params.timeLimit = timeLimit



# Make variables
x = m.addMVar(NoOfDuties)

# Make constraints
# Make sure each flight is in only one used pairing
# Create a matrix of pairs per flight
delta_fp = np.zeros([len(timeTable),len(dutyPeriods)])
flights = timeTable['Flight No.'].values
Flnrs = dutyPeriods['Flights']
pairsperflight = []

for i in tqdm(range(len(Flnrs))):
    q = ast.literal_eval(Flnrs[i])
    for r in q:
        # print(r)
        flnr = np.where(flights == r)[0][0]
        delta_fp[flnr,i] = 1
b = np.ones(NoOfFlights)
m.addConstr(delta_fp@x == b)


# Make objective
cp = dutyCosts['Cost'].values
cp = cp.transpose()
m.setObjective(cp @ x)
m.update()

m.optimize()

Pi = m.getAttr(GRB.Attr.Pi, m.getVars())

# Dual problem
n = gp.Model('PricingProblem')
n.Params.timeLimit = timeLimit

# Make variables
y = n.addMVar(NoOfFlights)
n.update()

# Make Constraints
delta_pf = delta_fp.transpose()
cp = cp.transpose()
n.addConstr(delta_pf @y <= cp)
n.update()

# Make objective
one = np.ones([1,NoOfFlights])
n.setObjective(one @ y,GRB.MAXIMIZE)
n.update()

n.optimize()

Pi2 = n.getAttr(GRB.Attr.Pi, n.getVars())
