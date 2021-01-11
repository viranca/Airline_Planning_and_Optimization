# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 12:10:14 2020

@author: Daan Kerstjens
"""
import numpy as np
import pandas as pd
from tqdm import tqdm
from datetime import timedelta

base = 'CDG'
tf = 6 # minutes in a timeframe
SLT = 5 # Additional time for start and landing
timesteps = 1200 # Timesteps of 6 minutes, totalling 120 hrs = 5 days
blocktime = 40 # Demand is splitted in timeblocks of 4 hours each
RTK = 0.26/1000 # revenue per kg per kilometer

""" Loading input data """
# List all airports
airports = pd.read_hdf('FleetType.h5','airports')
rows = tuple(airports['IATA code'].values) # IATA code of all airports
rwy = airports['Runway (m)'] # Runway lengths
rwy.index = rows

# First load information regarding a/c types
FleetType = pd.read_hdf('FleetType.h5','fleetType')
capacity = tuple(FleetType.loc['Cargo capacity [kg]'].values)
TAT = tuple(FleetType.loc['Average TAT [min]'].values/tf) # Turn Around Time (in timesteps of 6 minutes)
maxRange = tuple(FleetType.loc['Maximum Range [km]'].values) # max Range per a/c type
# leaseCost = tuple(FleetType.loc['Lease Cost [€]'].values)
fleet = FleetType.loc['Fleet'].values
minRwy = tuple(FleetType.loc['Runway Required [m]'].values)

# Loading flighttimes, per aircraft type
def loadFlighttimes():
    flighttime_ac0 = pd.read_csv('flighttime_ac0.csv',index_col=0,header=None)
    flighttime_ac0.columns = [0]
    flighttime_ac1 = pd.read_csv('flighttime_ac1.csv',index_col=0,header=None)
    flighttime_ac1.columns = [1]
    flighttime_ac2 = pd.read_csv('flighttime_ac2.csv',index_col=0,header=None)
    flighttime_ac2.columns = [2]
    flighttime = pd.concat([flighttime_ac0,flighttime_ac1, flighttime_ac2],axis=1)
    flighttime.index = rows
    flighttime = np.ceil(10*flighttime)
    flighttime += SLT # adding half an hour for start & landing time
    flighttime += TAT # Adding the turn-around-time to the end of each flight
    return flighttime
flighttime = loadFlighttimes()

# Loading initial demand
demand1 = pd.read_csv('Demand0.csv',index_col=[0,1],header=None)
# Loading distance matrix
distances = pd.read_csv('distancematrix.csv',index_col=0,header=None)
distances.index = rows #giving airport names as index

# Loading costs of every flight, per aircraft type
def loadCosts():
    costs_ac0 = pd.read_csv('costmatrix_ac0.csv',index_col=0,header=None)
    costs_ac0.columns=[0]
    costs_ac1 = pd.read_csv('costmatrix_ac1.csv',index_col=0,header=None)
    costs_ac1.columns=[1]
    costs_ac2 = pd.read_csv('costmatrix_ac2.csv',index_col=0,header=None)
    costs_ac2.columns=[2]
    costs = pd.concat([costs_ac0,costs_ac1,costs_ac2],1)
    costs.index = rows
    return costs
costs = loadCosts()

del FleetType,airports,loadFlighttimes,loadCosts # Removing from memory, since these are not used anymore

# Making column names for profit table
columns = np.linspace(0,timesteps,timesteps+1)
columns = columns.astype(int)

# Making column names for schedule
columNames = ('Departure Day','Departure Time','Arrival Day','Arrival Time','Origin','Destination','Cargo','Profit')

""" Function making profit table """
def profitTable (j,demand,run):
    profits = pd.DataFrame(index=rows,columns=columns) # DataFrame (table) containing profits for best route as in slide 31, lecture 7
    control = ['']*(timesteps+1) # Array containing destination to fly to from base to obtain the indicated profit
    profits.at[base] = 0 # Keeping the aircraft grounded at all times has no cost or profit, hence the hub row must be non-negative
    
    # Looping through all timesteps, from end to start
    # For each column 'i', for each airport, if it results in a higher profit:
        # (1) the profit is copied 1 timestep back at the same airport (grounding costs and yields 0)
        # (2) the yield minus cost for a flight from the hub to this airport, at the required time of departure ('time'), is added to the hub row at the 'time', to which the profit of the current time 'i' at current airport is added as well
        # (3) the yield minus cost for a flight from this airport to the hub, at the required 'time', is added to the specific airport row at the 'time', to which the profit of current time 'i' at the hub is added
    for i in tqdm(columns):
    # for i in tqdm(range(100)):
        for airport in rows:
            # (1) Adding, if profitable, the profit one timestep back
            if i < timesteps:
                if profits.at[airport,timesteps-i-1] < profits.at[airport,timesteps-i]:
                    profits.at[airport,timesteps-i-1] = profits.at[airport,timesteps-i]
            if airport != base: # flight from CDG to CDG are nonsense
                time = timesteps-i-int(flighttime.at[airport,j]) 
                # Since flighttimes are assumed to be independable on direction, this is the departure time to either fly from hub to current airport and to fly from 
                # current airport to hub, arriving at current timestep i. Only flight departing within the time horizon are considered. (Valid since only schedules 
                # starting the five day period at CDG are considered in the end)
                if time > 0:
                    # timeblock (departing time), distance and cost are independent on direction of flight:
                    timeblock = int(np.floor(time/blocktime))+2 # The total period is devided into 30 timeblocks, for which the demand is known. The value is incremented by 2, due to the way it is saved (hence timeblock 0 contains the first 4 hours of the first day)
                    distance = distances.at[airport,1]
                    cost = costs.at[airport,j]
                    
                    if distance > maxRange[j]:
                        cost *= 10**6 # Adding a big penalty preventing the scheduling of out of range airports
                    if rwy[airport] < minRwy[j]:
                        cost *= 10**6 # Adding a big penalty preventing the scheudling to/from airport with a too short runway (NB. Superfluous check with our dataset, all rwys are long enough)
                    
                    # The flow (cargo weight) that could be transported consist of all demand at departure time timeblock, and 20% of the 2 timeblocks before. To prevent index errors, 
                    # the first 2 timeblocks are hardcoded to zero, since the last few and first few timeblocks have 0 demand anyway
                    # 'flow' is cargo weight to be transported from hub to current airport
                    # 'flowBack' is cargo weight to be transported from current airport to hub
                    if timeblock > 3:
                        flowBack = demand.loc[(base,airport),timeblock] + 0.2*demand.loc[(base,airport),timeblock-1] + 0.2*demand.loc[(base,airport),timeblock-2]
                        flow = demand.loc[(airport,base),timeblock]+0.2*demand.loc[(airport,base),timeblock-1]+0.2*demand.loc[(airport,base),timeblock-2]
                    else:
                        flow = 0
                        flowBack = 0
                    '''
                    elif timeblock > 2:
                        flowBack = demand.loc[(base,airport),timeblock] + 0.2*demand.loc[(base,airport),timeblock-1]
                        flow = demand.loc[(airport,base),timeblock]+0.2*demand.loc[(airport,base),timeblock-1]
                    else:
                        flowBack = demand.loc[(base,airport),timeblock]
                        flow = demand.loc[(airport,base),timeblock]
                    '''
                    
                    # if the demand is higher than the capacity of the a/c type, the flow is limited to the capacity
                    if flow > capacity[j]:
                        flow = capacity[j]
                    if flowBack > capacity[j]:
                        flowBack = capacity[j]
                    revenue = distance * RTK * flow
                    revenueBack = distance*RTK*flowBack
                    
                    # Profit at time of departure at hub, is profit at current time at current airport plus revenue made minus flying costs
                    profit = profits.at[base,timesteps-i] + revenue - cost
                    # Profit at time of departure at current airport, is profit at current time at hub plus revenue made minus flying costs
                    profitBack = profits.at[airport,timesteps-i] + revenueBack - cost
                    
                    # If this is more profitable than previous examined options, replace it in the profit table!
                    if profit > profits.at[airport,time] or np.isnan(profits.at[airport,time]):
                        profits.at[airport,time] = profit
        
                    if profitBack > profits.at[base,time]:
                        profits.loc[base,:time] = profitBack
                        control[time] = airport # add name of airport to control sequence
    obj = profits.at[base,0] # The objective (maximum profit at time 0 at CDG)
    # obj -= leaseCost[j] # Lease Costs have to be deducted from total objective
    
    # Write a csv of profit table, including control sequence
    control_df = pd.DataFrame([control],index=['control'],columns=columns)
    df = profits.append(control_df)
    df.to_csv('profits'+str(run)+'_'+str(j)+'.csv')
    
    print('Done with profit table for aicraft type ',j,'\nOptimal:',obj,'\n',flush=True)
    return profits,control,obj

""" Function making flight schedule, based on profits """
def schedule(run,best,profits,demand):
    # Set initial values for the schedule
    time = 0 # current time
    loc = [base] # list of airports visited, in order
    depDay = [] # List of departure days
    depTime = [] # List of departure times
    arrDay = [] # List of arrival days
    arrTime = [] # List of arrival times
    prof = [] # List of profit up to current time
    flows = [] # List of cargo weight transported on each leg
    prof2 = [] # List of profit of individual legs
    
    # Loop through the entire schedule horizon
    while time < timesteps:
        # Only fly if the profit changes between current and next timestep at current location, otherwise keep incrementing time until this is the case
        if profits.at[loc[-1],time] != profits.at[loc[-1],time+1]:
            dep = timedelta(hours=time/10) # Departure time is current time
            depDay.append(dep.days) 
            depTime.append(timedelta(seconds=dep.seconds))
            # deptest.append(pd.Timedelta(time))
            timeblock = int(np.floor(time/blocktime))+2
            if loc[-1] == base: # In this case, the flight goes from CDG to other airport
                loc.append(control[time]) # destination is given by control array
                # Cost, distance and flighttime depend on destination (these matrices only give hub-spoke values)
                cost = costs.at[loc[-1],best]
                distance = distances.at[loc[-1],1]
                time += int(flighttime.at[control[time],best])
            else:
                # Cost, distance and flighttime depend on origin (these matrices only give hub-spoke values)
                distance = distances.at[loc[-1],1]
                cost = costs.at[loc[-1],best]
                time += int(flighttime.at[loc[-1],best])
                loc.append(base)
            
            a = loc[-2] # origin
            b = loc[-1] # destination
            # To prevent index errors, flow in first 2 timeblocks are hardcoded 0 (index start at 2, valid since first and last few timeblocks have 0 demand)
            if timeblock > 3:
                flow = demand.loc[(a,b),timeblock] + 0.2*demand.loc[(a,b),timeblock-1] + 0.2*demand.loc[(a,b),timeblock-2]
            else:
                flow = 0
            '''
            elif timeblock > 2:
                flow = demand.loc[(a,b),timeblock] + 0.2*demand.loc[(a,b),timeblock-1]
            else:
                flow = demand.loc[(a,b),timeblock]
                '''
            if flow > capacity[best]:
                flow = capacity[best]
            revenue = distance * RTK * flow
            profit = prof[-1] + revenue - cost
            prof.append(profit)
            flows.append(flow)
            prof2.append(revenue-cost)
            # print()
            arr = timedelta(hours=(time-TAT[best])/10) # Arrival time, since the TAT has been added to the flighttimes, this is deducted here for display in schedule
            arrDay.append(arr.days)
            arrTime.append(timedelta(seconds=arr.seconds))
            
            # The transported weight has to be deducted from the demand. Since in the initial profit table, the route is unknown, this could result in a lower profit, alas.
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
    red = round(obj-profit) # Absolute reduction due to cargo rostered more than once
    redRel = round(red/obj*100,1) # Relative reduction
    print('The objective value of',round(obj),'was reduced by:',red,'(',redRel,'%) due to demand which had been used double\n\n')
    demand.to_csv('Demand'+str(run)+'.csv')
    
    
    schedule = pd.DataFrame([depDay,depTime,arrDay,arrTime,loc[:-1],loc[1:],flows,prof2],index=columNames).transpose()
    schedule[[columNames[0],columNames[2]]] += 1 # Start at day 1 instead of day 0
    schedule.to_csv('schedule'+str(run)+'_ac'+str(best)+'.csv')
    return demand,flows,loc


""" Main script, iterating over the fleet using above functions to calculate profits and make flight schedule """
# Creating some variables
run = 1
demand2 =[]
flows2 = []
loc2 = []
dep2 = []
# demand1 = demand.copy()

# Calculating all profit tables and flight schedule as long as there're unused aircraft left
while sum(fleet) > 0:
    for i in range(3):
        print('Aircraft type',i,'left:',fleet[i],flush=True)
    profits=[] # (empty) List of profit tables
    control=[] # (empty) list of control arrays
    obj=[] # (empty) list of objective found
    actype = [] # (empty) list of a/c types considered
    
    # Only make calculations for a/c types that are actually available
    if fleet[0] > 0:
        profits0,control0,obj0 = profitTable(0,demand1,run)
        profits.append(profits0)
        control.append(control0)
        obj.append(obj0)
        actype.append(0)
    if fleet[1] > 0:
        profits1,control1,obj1 = profitTable(1,demand1,run)
        profits.append(profits1)
        control.append(control1)
        obj.append(obj1)
        actype.append(1)
    if fleet[2] > 0:
        profits2,control2,obj2 = profitTable(2,demand1,run)
        profits.append(profits2)
        control.append(control2)
        obj.append(obj2)
        actype.append(2)
        
    # Selecting the a/c type with the highest profit (greedy model), and throwing out the other variables
    best = obj.index(max(obj))
    profits = profits[best]
    control = control[best]
    obj = obj[best]
    actype = actype[best]
    
    if obj < 0:
        print('There is no profitable option left')
        break
    
    # If there's a profitable option, write it down, and deduct a/c from fleet
    fleet[actype] -= 1
    print('Aircraft type',actype,'selected\n')
    
    demand1,flows1,loc1 = schedule(run,actype,profits,demand1)
    # schedule(run,actype,profits,demand)
    # demand2.append(demand1)
    # flows2.append(flows1)
    # loc2.append(loc1)
    # dep2.append(dep1)
    run += 1 # Variable to keep track of order of flight schedules

