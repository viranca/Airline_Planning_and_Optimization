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

# Loading flighttimes
flighttime_ac0 = pd.read_csv('flighttime_ac0.csv',index_col=0)
flighttime_ac0.columns = [0]
flighttime_ac1 = pd.read_csv('flighttime_ac1.csv',index_col=0)
flighttime_ac1.columns = [1]
flighttime_ac2 = pd.read_csv('flighttime_ac2.csv',index_col=0)
flighttime_ac2.columns = [2]
flighttime = pd.concat([flighttime_ac0,flighttime_ac1, flighttime_ac2],axis=1)
flighttime.index = rows
flighttime = np.ceil(10*flighttime)
flighttime += 5 # adding half an hour for start & landing time

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
    # for i in tqdm(range(100)):
        for airport in rows:
            if i < 1200:
                if profits.at[airport,1200-i-1] < profits.at[airport,1200-i]:
                    profits.at[airport,1200-i-1] = profits.at[airport,1200-i]
            if airport != base:
                time = 1200-i-int(flighttime.at[airport,j])
                if time > 0:
                    timeblock = int(np.floor(time/40))+2
                    distance = distances.at[airport,'1']
                    cost = costs.at[airport,j]
                    if timeblock > 3:
                        flowBack = demand.loc[(base,airport),timeblock] + 0.2*demand.loc[(base,airport),timeblock-1] + 0.2*demand.loc[(base,airport),timeblock-2]
                        flow = demand.loc[(airport,base),timeblock]+0.2*demand.loc[(airport,base),timeblock-1]+0.2*demand.loc[(airport,base),timeblock-2]
                    elif timeblock > 2:
                        flowBack = demand.loc[(base,airport),timeblock] + 0.2*demand.loc[(base,airport),timeblock-1]
                        flow = demand.loc[(airport,base),timeblock]+0.2*demand.loc[(airport,base),timeblock-1]
                    else:
                        flowBack = demand.loc[(base,airport),timeblock]
                        flow = demand.loc[(airport,base),timeblock]
                    if flow > capacity[j]:
                        flow = capacity[j]
                    revenue = distance * 0.26 * flow
                    profit = profits.at[base,1200-i] + revenue - cost
                    if profit > profits.at[airport,time] or np.isnan(profits.at[airport,time]):
                        profits.at[airport,time] = profit
        
                    if flowBack > capacity[j]:
                        flowBack = capacity[j]
                    revenueBack = distance*0.26*flowBack
                    profitBack = profits.at[airport,1200-i] + revenueBack - cost
                    if profitBack > profits.at[base,time]:
                        profits.loc[base,:time] = profitBack
                        control[time] = airport
    obj = profits.at[base,0]
    control_df = pd.DataFrame([control],index=['control'],columns=columns)
    df = profits.append(control_df)
    df.to_csv('profits'+str(j)+'.csv')
    print('Done with profit table for aicraft type ',j,'\nOptimal:',obj,'\n',flush=True)
    return [profits,control,obj]


[profits0,control0,obj0] = profitTable(0)
[profits1,control1,obj1] = profitTable(1)
[profits2,control2,obj2] = profitTable(2)
'''
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
        control = control2'''
best = [obj0,obj1,obj2].index(max([obj0,1,2]))
profits = [profits0,profits1,profits2][best]
control = [control0,control1,control2][best]
obj = [obj0,obj1,obj2][best]
print('Aircraft type',best,'selected\n')

control_df = pd.DataFrame([control],index=['control'],columns=columns)
df = profits.append(control_df)
df.to_csv('profits.csv')

time = 0
loc = [base]
dep = []
prof = [0]
# prof2 = []
while time < 1200:
    if profits.at[loc[-1],time] != profits.at[loc[-1],time+1]:
        dep.append(time)
        timeblock = int(np.floor(time/40))+2
        if loc[-1] == base:
            b = control[time]
            loc.append(control[time])
            cost = costs.at[loc[-1],best]
            distance = distances.at[loc[-1],'1']
            time += int(flighttime.at[control[time],best])
        else:
            distance = distances.at[loc[-1],'1']
            cost = costs.at[loc[-1],best]
            b = base
            time += int(flighttime.at[loc[-1],best])
            loc.append(base)
        
        a = loc[-2]
        if timeblock > 3:
            flow = demand.loc[(a,b),timeblock] + 0.2*demand.loc[(a,b),timeblock-1] + 0.2*demand.loc[(a,b),timeblock-2]
        elif timeblock > 2:
            flow = demand.loc[(a,b),timeblock] + 0.2*demand.loc[(a,b),timeblock-1]
        else:
            flow = demand.loc[(a,b),timeblock]
            
        if flow > capacity[best]:
            flow = capacity[best]
        revenue = distance * 0.26 * flow
        profit = prof[-1] + revenue - cost
        prof.append(profit)
        # prof2.append(revenue-cost)
        if timeblock > 3:
            if flow < 0.2 *demand.loc[(a,b),timeblock-2]:
                demand.loc[(a,b),timeblock-2] -= flow
                flow = 0
            else:
                flow -= demand.loc[(a,b),timeblock-2]
                demand.loc[(a,b),timeblock-2] = 0
        if timeblock > 2:
            if flow < 0.2 *demand.loc[(a,b),timeblock-1]:
                demand.loc[(a,b),timeblock-1] -= flow
                flow = 0
            else:
                flow -= demand.loc[(a,b),timeblock-1]
                demand.loc[(a,b),timeblock-1] = 0
        
        if flow < demand.loc[(a,b),timeblock]:
            demand.loc[(a,b),timeblock] -= flow
            flow = 0
        else:
            flow -= demand.loc[(a,b),timeblock]
            demand.loc[(a,b),timeblock] = 0
        if flow != 0:
            print('\nEr gaat iets fout\n',flush=True)
    else:
        time += 1
# obj = round([obj0,obj1,obj2][best])
red = round(obj-profit)
redRel = round(red/obj*100,1)
print('The objective value of',obj,'was reduced by:',red,'(',redRel,'%) due to demand which had been used double')
