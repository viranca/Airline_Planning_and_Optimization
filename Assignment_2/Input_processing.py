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

Aircraft  = [0,1,2]
Aircraft_speed = [800, 850, 920]
Aircraft_cargo_capacity  = [23000, 35000, 120000]
Aircraft_TAT = [90/60, 120/60, 150/60]
Aircraft_range = [1500, 3300, 6300]
Aircraft_runway_required = [1400, 1600, 1800]
Aircraft_leasecost  = [2143, 4857, 11429]
Aircraft_fixed_cost = [750, 1500, 3125]
Aircraft_hourly_cost = [1875, 1938, 3500]
Aircraft_fuel_parameter = [2.5, 5, 9.5]


"""
=============================================================================
demand and distance for every flight leg:
=============================================================================
"""
path = 'AE4423_Ass2_APO.xlsx'

Airport = pd.read_excel(path)
airports = pd.Series(Airport.iloc[0])

FleetType = pd.read_excel(path,sheet_name='Fleet Type',index_col=0)
FleetType.to_hdf('fleetType.h5','fleetType')
airports.to_hdf('fleetType.h5','airports')

demand = pd.read_excel(path,sheet_name='Group 26', header=None, skiprows=5,index=0,usecols='B:AG')
demand.to_csv('Demand0.csv',index=False,header=False)

with open('1_distance_df.csv', 'r') as f:
    df_distance = pd.read_csv(f, sep=',', header=0)
df_distance = df_distance['1']
df_distance.to_csv('distancematrix.csv')
distance = np.array(df_distance)


            

"""
=============================================================================
Compute a costmatrix for each aircraft type at each flight leg.
=============================================================================
"""
#Appendix D
#aircraft 0
#fixed cost
C_X_0 = Aircraft_fixed_cost[0]
#time-based cost in hours
c_T_0 = Aircraft_hourly_cost[0]
V_0 = Aircraft_speed[0]
C_T_0 = c_T_0 * (df_distance / V_0)
#fuel cost
c_F_0 = Aircraft_fuel_parameter[0]
f = 1.42
C_F_0 = ((c_F_0 * f)/1.5) * df_distance
C_0 = C_X_0 + C_T_0 + C_F_0 

#aircraft 1
#fixed cost
C_X_1 = Aircraft_fixed_cost[1]
#time-based cost
c_T_1 = Aircraft_hourly_cost[1]
V_1 = Aircraft_speed[1]
C_T_1 = c_T_1 * (df_distance / V_1)
#fuel cost
c_F_1 = Aircraft_fuel_parameter[1]
f = 1.42
C_F_1 = ((c_F_1 * f)/1.5) * df_distance
C_1 = C_X_1 + C_T_1 + C_F_1 

#aircraft 2
#fixed cost
C_X_2 = Aircraft_fixed_cost[2]
#time-based cost
c_T_2 = Aircraft_hourly_cost[2]
V_2 = Aircraft_speed[2]
C_T_2 = c_T_2 * (df_distance / V_2)
#fuel cost
c_F_2 = Aircraft_fuel_parameter[2]
f = 1.42
C_F_2 = ((c_F_2 * f)/1.5) * df_distance
C_2 = C_X_2 + C_T_2 + C_F_2 

           
costmatrix_ac0 = pd.DataFrame(C_0)
costmatrix_ac0 = costmatrix_ac0['1']
costmatrix_ac0.to_csv('costmatrix_ac0.csv')
#print(costmatrix_ac0)

costmatrix_ac1 = pd.DataFrame(C_1)
costmatrix_ac1 = costmatrix_ac1['1']
costmatrix_ac1.to_csv('costmatrix_ac1.csv')
#print(costmatrix_ac1)   

costmatrix_ac2 = pd.DataFrame(C_2)
costmatrix_ac2 = costmatrix_ac2['1']
costmatrix_ac2.to_csv('costmatrix_ac2.csv')
#print(costmatrix_ac2)            


#%%

"""
=============================================================================
Compute a flighttime matrix for each aircraft type at each flight leg.
=============================================================================
"""


flighttime_ac0 = df_distance/Aircraft_speed[0]
flighttime_ac0.to_csv('flighttime_ac0.csv')

flighttime_ac1 = df_distance/Aircraft_speed[1]
flighttime_ac1.to_csv('flighttime_ac1.csv')

flighttime_ac2 = df_distance/Aircraft_speed[2]
flighttime_ac2.to_csv('flighttime_ac2.csv')


























           