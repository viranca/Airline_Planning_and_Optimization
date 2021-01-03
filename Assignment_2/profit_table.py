# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 12:10:14 2020

@author: Daan Kerstjens
"""
import numpy as np
import pandas as pd
from tqdm import tqdm

rows = ['LHR','CDG','AMS','FRA','MAD','BCN','MUC','FCO','DUB','ARN','LIS','TXL','HEL','WAW','EDI','OTP','HER','KEF','PMO','FNC']
base = 'CDG'
capacity = [23000,35000,120000]

flighttime_ac0 = pd.read_csv('flighttime_ac0.csv',index_col=0)
flighttime_ac0.columns = [0]
flighttime_ac1 = pd.read_csv('flighttime_ac1.csv',index_col=0)
flighttime_ac1.columns = [1]
flighttime_ac2 = pd.read_csv('flighttime_ac2.csv',index_col=0)
flighttime_ac2.columns = [2]
flighttime = pd.concat([flighttime_ac0,flighttime_ac1, flighttime_ac2],axis=1)
flighttime.index = rows
flighttime = round(10*flighttime)

demand = pd.read_csv('Demand26_2.csv',index_col=[0,1],header=None)
distances = pd.read_csv('distancematrix.csv',index_col=0)
distances.index = rows
costs_ac0 = pd.read_csv('costmatrix_ac0.csv',index_col=0)
costs_ac0.columns=[0]
costs_ac1 = pd.read_csv('costmatrix_ac1.csv',index_col=0)
costs_ac1.columns=[1]
costs_ac2 = pd.read_csv('costmatrix_ac2.csv',index_col=0)
costs_ac2.columns=[2]
costs = pd.concat([costs_ac0,costs_ac1,costs_ac2],1)
costs.index = rows

columns = np.linspace(0,1200,1201)
columns = columns.astype(int)


def profitTable (j):
    profits = pd.DataFrame(index=rows,columns=columns)
    control = ['']*1201
    profits.at[base] = 0 # last column
    for i in tqdm(columns):
        for airport in rows:
            if airport != base:
                time = 1200-i-int(flighttime.at[airport,j])
                if time > 0:
                    timeblock = int(np.floor(time/40))+2
                    distance = distances.at[airport,'1']
                    cost = costs.at[airport,j]
                    if timeblock == 32:
                        print('\nWARNING:',i,time,airport)
                    flow = demand.loc[base].loc[airport,timeblock]
                    if flow > capacity[0]:
                        flow = capacity[0]
                    revenue = distance * 0.26 * flow
                    profit = profits.at[base,1200-i] + revenue - cost
                    if profit > profits.at[airport,time] or np.isnan(profits.at[airport,time]):
                        profits.loc[airport,:time] = profit
        
                    flowBack = demand.loc[airport].loc[base,timeblock]
                    if flowBack > capacity[0]:
                        flowBack = capacity[0]
                    revenueBack = distance*0.26*flowBack
                    profitBack = profits.at[airport,1200-i] + revenueBack - cost
                    if profitBack > profits.at[base,time]:
                        profits.loc[base,:time] = profitBack
                        control[time] = airport
    obj = profits.at[base,0]
    control_df = pd.DataFrame([control],index=['control'],columns=columns)
    df = profits.append(control_df)
    df.to_csv('profits'+str(j)+'.csv')
    print('Done with profit table for aicraft type ',j,'\n',flush=True)
    return [profits,control,obj]

[profits0,control0,obj0] = profitTable(0)
[profits1,control1,obj1] = profitTable(1)
[profits2,control2,obj2] = profitTable(2)
if obj0 > obj1:
    if obj0 > obj2:
        best = 0
        profits = profits0
        control = control0
    else:
        best = 2
        profits = profits2
        control = control2
else:
    if obj1 > obj2:
        best = 1
        profits = profits1
        control = control1
    else:
        best = 2
        profits = profits2
        control = control2

control_df = pd.DataFrame([control],index=['control'],columns=columns)
df = profits.append(control_df)
df.to_csv('profits.csv')

time = 0
loc = [base]
dep = []
# prof = []
while time < 1200:
    if profits.at[loc[-1],time] != profits.at[loc[-1],time+1]:
        dep.append(time)
        # prof.append(profits.at[loc[-1],time])
        if loc[-1] == base:
            loc.append(control[time])
            time += int(flighttime.at[control[time],best])
        else:
            time += int(flighttime.at[loc[-1],best])
            loc.append(base)
    else:
        time += 1
