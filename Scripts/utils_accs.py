# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 22:56:12 2018

@author: QiuYuean
"""

import arcpy
from params import args
import pandas as pd
import numpy as np

# %% Read variable for evaluation
def read_demand(community_name, field_demand = 'Sum_常住'):
    """
    community_demand = arcpy.da.FeatureClassToNumPyArray(community_name, 
                                                         ['FID','Demand0','Demand1','Demand2'])
    to_np = np.zeros((routes.shape[0],4))
    for i in range(routes.shape[0]):
        to_np[i][0] = routes[i][0]
        to_np[i][1] = routes[i][1]
        to_np[i][2] = routes[i][2]
        to_np[i][3] = routes[i][3]
    
    df = pd.DataFrame({'FacilityID':to_np[:,0],'Demand0':to_np[:,1],'Demand1':to_np[:,2],'Demand2':to_np[:,3]})
    """
    community_demand = arcpy.da.FeatureClassToNumPyArray(community_name, ['OBJECTID'] + [field_demand])
    to_np_int = np.zeros((community_demand.shape[0]),dtype=np.int)
    to_np_float = np.zeros((community_demand.shape[0]))
    
    for i in range(community_demand.shape[0]):
        to_np_int[i] = community_demand[i][0]
        to_np_float[i] = community_demand[i][1]
    
    if min(to_np_int) == 1: # make every id start from 0
        to_np_int = to_np_int - 1
        
    demand_df = pd.DataFrame({'demand_InciID':to_np_int,'demand':to_np_float})
    return demand_df

def read_service(healthCenter_name, field_demand = 'num_Doc'):
    """
    hcenter_service = arcpy.da.FeatureClassToNumPyArray(hcenter_name, 
                                                         ['FID','service0','service1','service2'])
    to_np = np.zeros((routes.shape[0],4))
    for i in range(routes.shape[0]):
        to_np[i][0] = routes[i][0]
        to_np[i][1] = routes[i][1]
        to_np[i][2] = routes[i][2]
        to_np[i][3] = routes[i][3]
    
    df = pd.DataFrame({'FacilityID':to_np[:,0],'service0':to_np[:,1],'service1':to_np[:,2],'service2':to_np[:,3]})
    """
    try:
        hcenter_service = arcpy.da.FeatureClassToNumPyArray(healthCenter_name, ['OBJECTID'] + [field_demand])
    except:
        hcenter_service = arcpy.da.FeatureClassToNumPyArray(healthCenter_name, ['FID'] + [field_demand])
        
    to_np_int = np.zeros((hcenter_service.shape[0]), dtype=np.int)
    to_np_float  = np.zeros((hcenter_service.shape[0]))
    
    for i in range(hcenter_service.shape[0]):
        to_np_int[i] = hcenter_service[i][0]
        to_np_float[i] = hcenter_service[i][1]
    
    if min(to_np_int) == 1:
        to_np_int = to_np_int - 1
        
    service_df = pd.DataFrame({'service_FaciID':to_np_int,'service':to_np_float})
    return service_df

def read_routes(routes_name):
    routes = arcpy.da.FeatureClassToNumPyArray(routes_name, ['FacilityOID','IncidentOID'])
    to_np = np.zeros((routes.shape[0],2),dtype=np.int)
    for i in range(routes.shape[0]):
        to_np[i][0] = routes[i][0]
        to_np[i][1] = routes[i][1]
    
    if min(to_np[:,0]) == 1:
        to_np[:,0] = to_np[:,0]-1
    if min(to_np[:,1]) == 1:
        to_np[:,1] = to_np[:,1]-1
    
    routes_df = pd.DataFrame({'routes_FaciID':to_np[:,0],'routes_InciID':to_np[:,1]})
    return routes_df
   
#%% Evalute, assign, or update
def eval_accs(community_name = '../Dataset/FileDB.gdb/community',
                      healthCenter_name ='../Dataset/FileDB.gdb/healthCenter', 
                      routes_name = '../Dataset/Output.gdb/Routes',
                      flag_update=False, flag_output=False):
    """
    Args:
        routes_df: a df, read and passed after solving the na. Note that it varies across interations.
        demand_df: a df,  read from the community feature.
        service_df a df,  read from the healthCenter feature.
    """
    # read data
    demand_df = read_demand(community_name)
    service_df = read_service(healthCenter_name)
    routes_df = read_routes(routes_name)
    
    # calculate
    routes_df.sort_values('routes_FaciID',inplace=True)
    routes_df.reset_index(drop=True , inplace=True)
    
    demand_df.sort_values('demand_InciID',inplace=True)
    demand_df.reset_index(drop=True , inplace=True)
    
    service_df.sort_values('service_FaciID',inplace=True)
    service_df.reset_index(drop=True , inplace=True)
    
    routes_FaciID = routes_df['routes_FaciID'] # increasing, but may jump from one to one
    routes_InciID = routes_df['routes_InciID'] # random
    # every ID in routes must be contained by the following:
    demand_InciID = demand_df['demand_InciID'] # increasing one by one
    service_FaciID = service_df['service_FaciID'] # increasing one by one
    
    demand = demand_df['demand']
    service = service_df['service']
    
    num_routes = routes_FaciID.shape[0]
    num_Faci = service_FaciID.shape[0]
    num_Inci = demand_InciID.shape[0]
    
    # create two arrays
    demand_sum = np.zeros((num_Faci,1)) # how much demand is assigned to each faci
    service_div = np.zeros((num_Faci, 1)) # how a Faci is divided by its demand
    service_sum = np.zeros((num_Inci,1)) # how much service is assigned to each inci, i.e., accessibility of each.

    for i in range(num_routes):
        id_inci = routes_InciID[i]
        id_faci = routes_FaciID[i]
        demand_ = demand[id_inci]
        demand_sum[id_faci] = demand_sum[id_faci] + demand_
    
    for i in range(num_Faci):
        if demand_sum[i] != 0:
            service_div[i] = service[i] / demand_sum[i] 
    
    for i in range(num_routes):
        id_inci = routes_InciID[i]
        id_faci = routes_FaciID[i]
        service_sum[id_inci] = service_sum[id_inci] + service_div[id_faci]
    
    # update accs of community_ply
    if flag_update:
        community_ply_name = args.env_workspace + '/community_ply_simu_accs'
        update_simu_accs(community_ply_name, service_sum)

    if flag_output:
        df = pd.DataFrame(service_sum)
        df.to_csv(args.output_folder + '/accs.csv')
        
    return service_sum

def assign_accs(service_sum, community_ply_name='community_ply'):
    '''Assign accs value to commnity_ply FOR ACTUAL EVALUATION'''
    arcpy.env.workspace = args.env_workspace
    
    # Create a cursor on a feature class
    rows = arcpy.UpdateCursor(community_ply_name)
    
    try:
        # Loop through the rows in the attribute table
        for row in rows:
            row.setValue('accs',  service_sum[row.getValue('OBJECTID')-1][0])
            rows.updateRow(row)
        return True
    except Exception as e:
        print e
        return False
 
def update_simu_accs(community_ply_name, service_sum):
    '''Update accs value to commnity_ply FOR SIMULATION EVALUATION'''
    # Create update cursor for feature class
    rows = arcpy.UpdateCursor(community_ply_name)
    # Update the field used in buffer so the distance is based on the
    # road type. Road type is either 1, 2, 3, or 4. Distance is in meters.
    i = 0
    for row in rows:
        # Fields from the table can be dynamically accessed from the
        # row object. Here fields named BUFFER_DISTANCE and ROAD_TYPE
        # are used
        row.setValue("accs", float(service_sum[i]))
        i = i+1
        rows.updateRow(row)
    # Delete cursor and row objects to remove locks on the data.
    del row
    del rows
    
#eval_accs(community_name = '../Dataset/FileDB.gdb/community',
#                  healthCenter_name ='../Dataset/FileDB.gdb/healthCenter_hofLast_merged', 
#                  routes_name = args.outGeodatabase + '/Routes',
#                  flag_update=False, flag_output=False)