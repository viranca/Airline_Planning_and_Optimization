# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 17:48:32 2021

@author: Daan Kerstjens
"""
import pandas as pd

'''
WARNING:
CODE ONLY RUNS WITH XLRD VERSION 1.2.0
'''

path = 'AE4423_Ass2_APO.xlsx'

Airport = pd.read_excel(path,index_col=0).transpose()
FleetType = pd.read_excel(path,sheet_name='Fleet Type',index_col=0)

FleetType.to_hdf('fleetType.h5','fleetType')
Airport.to_hdf('fleetType.h5','airports')

demand = pd.read_excel(path,sheet_name='Group 26', header=None, skiprows=5,index=0,usecols='B:AG')
demand.to_csv('Demand0.csv',index=False,header=False)
