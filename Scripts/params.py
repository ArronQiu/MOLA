# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 12:30:25 2018

@author: QiuYuean
"""

import argparse

parser = argparse.ArgumentParser(description='some argv for na.')
parser.add_argument('--env_workspace', type=str, default='../Dataset/FileDB.gdb',
                   help='the workspace for environment.')

parser.add_argument('--output_folder', type=str, default='../Dataset/output_folder',
                   help='the output folder.')

parser.add_argument('--output_folder_fc', type=str, default='../Dataset/output_folder',
                   help='the output folder for feature class created in each iteration.')

parser.add_argument('--env_overwriteOutput', type=bool, default=True,
                   help='whether can overwrite output.')

parser.add_argument('--inNetworkDataset', type=str, default='Transportation/Transportation_ND',
                   help='inNetworkDataset.')

parser.add_argument('--inIncidents', type=str, default='community',
                   help='the name of incidents in the ND.')

parser.add_argument('--inFacilities', type=str, default='healthCenter',
                   help='the name of facilities in the ND.')

parser.add_argument('--outGeodatabase', type=str, default='../Dataset/Output.gdb',
                   help='the output gdb.')

parser.add_argument('--outRoutes', type=str, default='Routes',
                   help='the name of output routes.')

parser.add_argument('--outDirections', type=str, default='Directions',
                   help='the name of output directions.')

parser.add_argument('--outClosestFacilities', type=str, default='ClosestFacilities',
                   help='the name of output cloest facilities.')

parser.add_argument('--measurement_units', type=str, default='Minutes')

parser.add_argument('--Default_Cutoff', type=int, default=40)
parser.add_argument('--Maximum_Snap_Tolerance', type=int, default=2000)
parser.add_argument('--Number_of_Facilities_to_Find', type=int, default=20)

parser.add_argument('--Travel_Direction', type=str, default='TRAVEL_TO')
parser.add_argument('--UTurn_Policy', type=str, default='ALLOW_UTURNS')

parser.add_argument('--Save_Output_Network_Analysis_Layer', type=bool, default=True)
parser.add_argument('--Save_Route_Data', type=bool, default=True)

args = parser.parse_args()
