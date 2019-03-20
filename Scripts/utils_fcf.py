# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 20:11:05 2018

@author: QiuYuean
"""

# http://desktop.arcgis.com/zh-cn/arcmap/latest/tools/network-analyst-toolbox/find-closest-facilities.htm

# Name: FindClosestFacilities_Workflow.py
# Description: For each store, find the closest warehouse. The output will show
#              the routes between stores and warehouses, driving directions,
#              and the subset of warehouses that were closest to stores.
#
#              Added: after solving and saving, convert the 'routes' in the 
#              out_gdb into numpy and parse

# Requirements: Network Analyst Extension

#Import system modules
import arcpy
from arcpy import env
from params import args

import os

def new_fcf_layer():
    """
        Take basic data and create a 'Cloest Facility' analysis layer
        Args:
            nothing but please import data into a File.gdb and create a network_dataset(nds) beforehand
        Return:
            nothing but output an analysis layer
        Note:
            ONLY incidents and facilities will be imported
            basic layer setting can be modified
    """
    #Set environment settings
    env.workspace = args.env_workspace
    env.output_folder = args.output_folder
    env.overwriteOutput = args.env_overwriteOutput
    
    #Set other basic settings
    nds = os.path.join(args.env_workspace, "Transportation", "Transportation_ND")
    incidents = os.path.join(args.env_workspace, "community")
    facilities = os.path.join(args.env_workspace, "healthCenter")
    analysis_layer_name = "ClosestFacility"
    
    #Check out the Network Analyst extension license
    arcpy.CheckOutExtension("Network")
    
    make_layer_result = arcpy.na.MakeClosestFacilityLayer(
            in_network_dataset=nds, 
            out_network_analysis_layer=analysis_layer_name, 
            impedance_attribute="Minutes", 
            travel_from_to=args.Travel_Direction, 
            default_cutoff=args.Default_Cutoff, 
            default_number_facilities_to_find=args.Number_of_Facilities_to_Find, 
            accumulate_attribute_name=["Meters", "Minutes"], # same as attributes of nds 
            UTurn_policy=args.UTurn_Policy, 
            restriction_attribute_name=None,
            hierarchy=None, 
            hierarchy_settings=None, 
            output_path_shape="TRUE_LINES_WITH_MEASURES", 
            time_of_day=None, 
            time_of_day_usage=None)
    
    
    layer_object = make_layer_result.getOutput(0)
    
    #Add facilities and incidents to the analysis layer using default field mappings         
    sub_layer_names = arcpy.na.GetNAClassNames(layer_object)
    facility_layer_name = sub_layer_names["Facilities"]
    incident_layer_name = sub_layer_names["Incidents"]
    routesLayerName = sub_layer_names["CFRoutes"]
    
    arcpy.na.AddLocations(layer_object, facility_layer_name, facilities,
                          search_tolerance=args.Maximum_Snap_Tolerance,)
#                          snap_to_position_along_network=True, 
#                          snap_offset=args.Maximum_Snap_Tolerance)
    
    arcpy.na.AddLocations(layer_object, incident_layer_name, incidents,
                          search_tolerance=args.Maximum_Snap_Tolerance,)
#                          snap_to_position_along_network=True, 
#                          snap_offset=args.Maximum_Snap_Tolerance)
    
    #Save the basic layer
    output_layer_file = os.path.join(env.output_folder, analysis_layer_name + ".lyr")
    arcpy.management.SaveToLayerFile(layer_object, output_layer_file, "RELATIVE")
    
    #Solve the closest facility layer
    arcpy.na.Solve(layer_object)
    
    #Save the solved closest facility layer as a layer file on disk
    output_layer_file = os.path.join(env.output_folder, analysis_layer_name + "_solved.lyr")
    layer_object.saveACopy(output_layer_file)
    
    # Get the output Routes sublayer and save it to a feature class
    if_save_routes = False
    if if_save_routes:
        RoutesSubLayer = arcpy.mapping.ListLayers(layer_object, routesLayerName)[0]
        arcpy.management.CopyFeatures(RoutesSubLayer, args.outGeodatabase + "/outRoutes")
    

def find_cloest_faci(Inci_set = args.inIncidents,
                     Faci_set = args.inFacilities,
                     outRoutes_name = args.outRoutes):
        """
        Take basic data and settings, solve the problem and output 'routes' into Output.gdb
        Args:
            inIncidents: Feature Set or File_name in File.DB
            inFacilities: Feature Set or File_name in File.DB
        Return:
            nothing but output 'routes' into Output.gdb
        """
        try:
        
            #Set environment settings
            env.workspace = args.env_workspace
            env.overwriteOutput = args.env_overwriteOutput
            #Check out the Network Analyst extension license
            arcpy.CheckOutExtension("Network")
        
            #Set local variables
#            inIncidents = os.path.join(args.env_workspace, args.inIncidents)
#            Inci_set = arcpy.FeatureSet(inIncidents)
#            
#            inFacilities = os.path.join(args.env_workspace, args.inFacilities)
#            Faci_set = arcpy.FeatureSet(inFacilities)
            
            inNetworkDataset = args.inNetworkDataset
            outGeodatabase = args.outGeodatabase
            outDirections = args.outDirections
            outClosestFacilities = args.outClosestFacilities
            # different name from default in stage 2, since routes.shp differs in each iteration
#            outRoutes = outRoutes_name
            
            #optional
            Default_Cutoff = args.Default_Cutoff
            measurement_units = args.measurement_units
            Number_of_Facilities_to_Find = args.Number_of_Facilities_to_Find
#            Maximum_Snap_Tolerance = args.Maximum_Snap_Tolerance
#        
#            Travel_Direction = args.Travel_Direction
#            UTurn_Policy = args.UTurn_Policy
#            
#            Save_Output_Network_Analysis_Layer = args.Save_Output_Network_Analysis_Layer 
#            Save_Route_Data = args.Save_Route_Data
        
#        FindClosestFacilities(Incidents=None, Facilities=None, Measurement_Units=None, 
#                                  Network_Dataset=None, Output_Geodatabase=None, Output_Routes_Name=None, 
#                                  Output_Directions_Name=None, Output_Closest_Facilities_Name=None, 
#                                  Number_of_Facilities_to_Find=None, Default_Cutoff=None, 
#                                  Travel_Direction=None, Time_of_Day=None, Time_of_Day_Usage=None, 
#                                  Time_Zone_for_Time_of_Day=None, UTurn_Policy=None, Point_Barriers=None, 
#                                  Line_Barriers=None, Polygon_Barriers=None, Time_Attribute=None, 
#                                  Time_Attribute_Units=None, Distance_Attribute=None, 
#                                  Distance_Attribute_Units=None, Use_Hierarchy_in_Analysis=None, 
#                                  Restrictions=None, Attribute_Parameter_Values=None, 
#                                  
#                                  Accumulate_Attributes=None, Maximum_Snap_Tolerance=None, 
#                                  Feature_Locator_WHERE_Clause=None, Route_Shape=None, 
#                                  Route_Line_Simplification_Tolerance=None, Populate_Directions=None, 
#                                  Directions_Language=None, Directions_Distance_Units=None, 
#                                  Directions_Style_Name=None,
#                                  Maximum_Features_Affected_by_Point_Barriers=None,
#                                  Maximum_Features_Affected_by_Line_Barriers=None, 
#                                  Maximum_Features_Affected_by_Polygon_Barriers=None, 
#                                  Maximum_Facilities=None, Maximum_Facilities_to_Find=None, 
#                                  Maximum_Incidents=None,
#                                  Force_Hierarchy_Beyond_Distance=None, 
#                                  Save_Output_Network_Analysis_Layer=None, Travel_Mode=None)
        
            # Run FindClosestFacilities. Choose to find only the closest facility.
            arcpy.na.FindClosestFacilities(Inci_set, 
                                           Faci_set, 
                                           measurement_units,
                                           inNetworkDataset, 
                                           outGeodatabase, 
                                           outRoutes_name, 
                                           outDirections, 
                                           outClosestFacilities,
                                           Number_of_Facilities_to_Find = Number_of_Facilities_to_Find,
                                           Default_Cutoff = Default_Cutoff,
        #                                   Save_Output_Network_Analysis_Layer = Save_Output_Network_Analysis_Layer
        #                                   Save_Route_Data = True,
                                            )
        
#            print "Networ Analysis run successfully."
#            print "Routes saved as: ", outGeodatabase + '/' + outRoutes
            return True
        
        except Exception as e:
            # If an error occurred, print line number and error message
            import sys
            tb = sys.exc_info()[2]
            print "An error occured on line %i" % tb.tb_lineno
            print str(e)
            return False