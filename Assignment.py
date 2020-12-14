import numpy as np
import math
# from scipy import special, stats
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std
import statsmodels.formula.api as smf

gen_df = pd.read_csv("Assignment1_Problem1_Datasheets_General.csv", sep=";")
group_df = pd.read_csv("Assignment1_Problem1_Datasheets_Group_26.csv", sep=";")
# print(gen_df)
# print(group_df)

'''
# Make function of haversine for calculating great circle distance between two points.
'''


def distance(o_lat, o_lon, d_lat, d_lon):
    r = 6371  # Volumetric mean radius [km]
    o_lat = np.deg2rad(o_lat)  # Convert degrees to radians
    o_lon = np.deg2rad(o_lon)
    d_lat = np.deg2rad(d_lat)
    d_lon = np.deg2rad(d_lon)
    delta_lat = (d_lat - o_lat)
    delta_lon = (d_lon - o_lon)
    a = math.sin(delta_lat / 2) * math.sin(delta_lat / 2) + math.cos(o_lat) \
        * math.cos(d_lat) * math.sin(delta_lon / 2) * math.sin(delta_lon / 2)
    c = 2 * math.atan2(np.sqrt(a), math.sqrt(1 - a))
    d = r * c
    return d  # [km]


'''
# Parameters
'''
demand = group_df.loc[:, 'EGLL':'LPMA'].values
airports = group_df.loc[:, 'ICAO Code'].values
population = gen_df.loc[:, '2015_pop':'2018_pop'].values
GDP = gen_df.loc[:, '2015_gdp':'2018_gdp'].values
latitudes = group_df.loc[:, ['Latitude (deg)']].values
longitudes = group_df.loc[:, ['Longitude (deg)']].values

'''
# Logarithms of gravity model
# ln(Dij) = ln(k) + b1*ln(pop_i*pop_j) + b2*ln(GDP_i*GDP_j) - b3*ln(f*d_ij) 
'''
Demand = np.zeros(shape=(latitudes.size, latitudes.size))
# Demand = pd.DataFrame(0, index=range(latitudes.size), columns=range(latitudes.size))
for i in range(latitudes.size):
    for j in range(latitudes.size):
        if demand[i, j] > 0:
            Demand[i, j] = np.log(demand[i, j])
Demand = Demand.flatten()
# =
# ln k?
# +
b1 = np.zeros(shape=(latitudes.size, latitudes.size))
# b1 = pd.DataFrame(0, index=range(latitudes.size), columns=range(latitudes.size))
for i in range(latitudes.size):
    for j in range(latitudes.size):
        b1[i, j] = np.log(population[i, 0] * population[j, 0])
b1 = b1.flatten()
# +
b2 = np.zeros(shape=(latitudes.size, latitudes.size))
# b2 = pd.DataFrame(0, index=range(latitudes.size), columns=range(latitudes.size))
for i in range(latitudes.size):
    for j in range(latitudes.size):
        b2[i, j] = np.log(GDP[i, 0] * GDP[j, 0])
b2 = b2.flatten()
# -
# distances = pd.DataFrame(0, index=range(latitudes.size), columns=range(latitudes.size))
distances = np.zeros(shape=(latitudes.size, latitudes.size))
for i in range(latitudes.size):
    for j in range(latitudes.size):
        distances[i, j] = distance(latitudes[i, 0], longitudes[i, 0], latitudes[j, 0], longitudes[j, 0])
distance_df = pd.DataFrame(distances)
distance_df.to_csv('distance_df')
print(distance_df)
# cost = 1.42
b3 = np.zeros(shape=(latitudes.size, latitudes.size))
# b3 = pd.DataFrame(0, index=range(latitudes.size), columns=range(latitudes.size))
for i in range(latitudes.size):
    for j in range(latitudes.size):
        if distances[i, j] > 0:
            b3[i, j] = np.log(distances[i, j])
b3 = b3.flatten()
'''
# 1.A.1: Calibrate the gravity model
'''
# OLS model
Y = Demand
X = np.column_stack((b1, b2, b3))
X = sm.add_constant(X)

model = sm.OLS(Y, X)
fit = model.fit()
print(fit.summary())
print('Parameters: ', fit.params)


'''
# 1.A.2: Forecast the population and GDP
'''

pop_2020 = np.zeros(shape=(latitudes.size, 1))
for i in range(latitudes.size):
    pop_2020[i] = population[i, 1] + (2020-2018)*((population[i, 1] - population[i, 0])/(2018-2015))

GDP_2020 = np.zeros(shape=(latitudes.size, 1))
for i in range(latitudes.size):
    GDP_2020[i] = GDP[i, 1] + (2020-2018)*((GDP[i, 1] - GDP[i, 0])/(2018-2015))


'''
# 1.A.3: Future demand with calibrated gravity model
'''
k = -13.8763
b1 = 0.5252
b2 = 0.6036
b3 = -1.3273


Demand_2020 = np.zeros(shape=(latitudes.size, latitudes.size))
for i in range(latitudes.size):
    for j in range(latitudes.size):
        if distances[i, j] > 0:
            Demand_2020[i, j] = np.exp(k) * ((((pop_2020[i]*pop_2020[j])**(b1)) * ((GDP_2020[i]*GDP_2020[j])**(b2)))/((1.42*distances[i, j])**(b3)))
print(Demand_2020)
