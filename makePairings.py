# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 12:57:01 2020

@author: Daan Kerstjens
"""
import pandas as pd
import ast
from tqdm import tqdm

maxDuties = 3 # Maximum of duties in 1 pair

df = pd.read_csv('dutyCosts.csv',parse_dates=['Departure','Arrival'],nrows=141,index_col=0)


def pairing(Pairs,Flnrs,Origin,Location):
    flnrs = []
    pairs = []
    for i in range(1,len(df)+1):
        if df.loc[i,'Origin'] == Location:
            loc = df.loc[i,'Destination']
            pair = Pairs + [i]
            flnr = Flnrs + ast.literal_eval(df.loc[i,'Flights'])
            # print(i,'Match',location)
            if loc == origin:
                pairs.append(pair)
                flnrs.append(flnr)
            elif len(pair) < maxDuties:
                a, b = pairing(pair,flnr,Origin,loc)
                for c in range(len(a)):
                    pairs.append(a[c])
                    flnrs.append(b[c])
    return pairs, flnrs


pairs = []
flnrs = []

for i in tqdm(range(1,len(df)+1)):
    origin = df.loc[i,'Origin']
    loc = df.loc[i,'Destination']
    flnr = ast.literal_eval(df.loc[i,'Flights'])
    pair = [i]
    a, b = pairing(pair,flnr,origin,loc)
    for c in range(len(a)):
        pairs.append(a[c])
        flnrs.append(b[c])

columnsPairs = []
columnsDuties = []
for i in range(maxDuties):
    columnsPairs.append('Pair '+str(i+1))
    columnsDuties.append('Duty '+str(i+1))
Pairs = pd.DataFrame(pairs,columns=columnsPairs)
Flnrs = pd.DataFrame(flnrs, columns=columnsDuties)
total = pd.concat([Pairs,Flnrs],axis=1)
total.to_csv('pairs.csv')

schedule = pd.read_csv('1_Timetable_Group_26.csv')
flights = schedule['Flight No.']
Flnrs = Flnrs.values
pairsperflight = []
for r in range(len(flights)):
    use = []
    for q in range(len(Flnrs)):
        if flights.iloc[r] in Flnrs[q]:
            use.append(q)
    pairsperflight.append(use)
PFP = pd.DataFrame(pairsperflight)
PFP.to_csv('Pairsperflight.csv')