# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 22:44:15 2020

@author: Daan Kerstjens
"""
import pandas as pd
import ast
from tqdm import tqdm

maxDuties = 5 # Maximum of duties in 1 pair

df = pd.read_csv('dutyCosts.csv',parse_dates=['Departure','Arrival'],nrows=141,index_col=0)

def pair(org,loc,flights,level,b):
    pairs = []
    c = 0
    d = 0
    for i in range(1,len(df)+1):
        if df.loc[i,'Origin'] == loc:
            print(i,df.loc[i,'Origin'],df.loc[i,'Destination'],level)
            d += 1
            loc = df.loc[i,'Destination']
            # flight = df.loc[i,'Flights']
            # flights += ast.literal_eval(flight)
            flight = flights + ast.literal_eval(df.loc[i,'Flights'])
            if loc == org:
                pairs.append(flight)
            elif len(flight) < maxDuties:
                # print(org,loc)
                a = pair(org,loc,flight,level+1,i)
                if len(a) > 0:
                    c += 1
                for b in a:
                    pairs.append([flight]+[b])
            else:
                c += 0
                print('Over maxDuties:',flight,'Totalling: ',len(flight))
    # if len(pairs) == 0:
    #     print('Er is een probleem',org,loc,'Op level:',level,'Iteratie:',i,'c: ',c,d)
    return pairs

Pairs = []
org = df.loc[4,'Origin']
loc = df.loc[4,'Destination']
flights = df.loc[4,'Flights']
flights = ast.literal_eval(flights)
Pairs = pair(org,loc,flights,0,0)
'''
for a in tqdm(range(1,len(df)+1)):
    org = df.loc[a,'Origin']
    loc = df.loc[a,'Destination']
    flights = df.loc[a,'Flights']
    flights = ast.literal_eval(flights)
    Pairs.append(pair(org,loc,flights,0,a))
'''