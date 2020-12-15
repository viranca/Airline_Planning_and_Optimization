# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 15:56:11 2020

@author: Daan Kerstjens
"""
import pandas as pd
import ast
from tqdm import tqdm
import gurobipy as gp 
from gurobipy import GRB

pilots = 150
timeLimit = 100 # Time limit on the gurobi runtime in seconds
days = 5

dutyCosts = pd.read_csv('dutyCosts.csv',parse_dates=['Departure','Arrival'],nrows=141,index_col=0)
pairings = pd.read_csv('pairs.csv')

maximum = len(dutyCosts)


m = gp.Model('Crew_pairing')
m.Params.timeLimit = timeLimit

x = {}
for i in tqdm(range(len(pairings))): 
    for j in range(days): 
        x[i,j] = m.addVar(vtype = GRB.BINARY, name='x'+str(i)+'_'+str(j))
m.update() 

