# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 15:56:11 2020

@author: Daan Kerstjens
"""
import pandas as pd
from tqdm import tqdm
import gurobipy as gp 
from gurobipy import GRB


timeLimit = 100 # Time limit on the gurobi runtime in seconds
rows = 141

dutyCosts = pd.read_csv('dutyCosts.csv',parse_dates=['Departure','Arrival'],nrows=rows,index_col=0)
timeTable = pd.read_csv('1_Timetable_Group_26.csv',index_col=0)
dutyPeriods = pd.read_csv('2_Duty_Periods_Group_26.csv',nrows=rows)
# PPF = pd.read_csv('Pairsperflight.csv')

NoOfDuties = len(dutyCosts)
NoOfFlights = len(timeTable)

m = gp.Model('Crew_pairing')
m.Params.timeLimit = timeLimit



# Make variables
x = {}
for i in range(NoOfDuties): 
    x[i] = m.addVar(vtype = GRB.BINARY, name='x'+str(i))
m.update() 

# Make constraints
# Make sure each flight is in only one used pairing
flights = timeTable.index
Flnrs = dutyPeriods['Flights']
pairsperflight = []
for r in tqdm(flights):
    use = []
    for q in range(len(Flnrs)):
        if r in Flnrs.iloc[q]:
            use.append(q)
    pairsperflight.append(use)
for i in range(NoOfFlights):
    m.addConstr(gp.quicksum(x[k] for k in pairsperflight[i]) == 1 )

# Make objective

m.setObjective(gp.quicksum(x[i] * dutyCosts['Cost'].iloc[i] for i in range(NoOfDuties)),GRB.MINIMIZE)
m.update()

m.optimize()