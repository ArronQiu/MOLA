# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 22:56:26 2018

@author: QiuYuean
"""

import arcpy
from params import args

import os
import numpy as np
import pandas as pd

def get_field_name_list(feature_dir):
    fieldObjList = arcpy.ListFields(feature_dir)
    fieldNameList = []
    for field in fieldObjList:
        fieldNameList.append(field.name)  
    return fieldNameList

def read_feature2dict(feature_name, field_list):
    feature_numpy_inTuple = arcpy.da.FeatureClassToNumPyArray(feature_name, field_list)
    dict_0 = {}
    num_record = len(feature_numpy_inTuple)
    for i in range(num_record):
        dict_0[i] = tuple(feature_numpy_inTuple[i])
    return dict_0

def read_items_dict(items_file, field_list):
    feature_numpy_inTuple = arcpy.da.FeatureClassToNumPyArray(items_file, field_list)
    dict_0 = {}
    num_record = len(feature_numpy_inTuple)
    for i in range(num_record):
        key = (feature_numpy_inTuple[i][3], feature_numpy_inTuple[i][4])
        dict_0[key] = tuple(feature_numpy_inTuple[i])
    return dict_0


def read_feature2numpy(feature_name, field_list):
    # field_list: a list of field name, such as ['id', 'name']
    feature_numpy_inTuple = arcpy.da.FeatureClassToNumPyArray(feature_name, field_list)
    num_record = len(feature_numpy_inTuple)
    num_field = len(field_list)
    
    nparray = np.zeros((num_record,num_field))
    for i in range(num_record):
        for j in range(num_field):
            nparray[i][j] = feature_numpy_inTuple[i][j]
    return nparray

def read_feature2df(feature_name, field_list):
    # field_list: a list of field name, such as ['id', 'name']
    feature_numpy_inTuple = arcpy.da.FeatureClassToNumPyArray(feature_name, field_list)
    num_record = len(feature_numpy_inTuple)
    num_field = len(field_list)
    
    nparray = np.zeros((num_record,num_field))
    for i in range(num_record):
        for j in range(num_field):
            nparray[i][j] = feature_numpy_inTuple[i][j]
    
    dict_ = {}
    for i in range(num_field):
        field_name = field_list[i]
        dict_[field_name] = nparray[:,i]
    
    df = pd.DataFrame(dict_)
    return df

def merge_feature(in_file1, in_file2, output_file):
    """
    Args: dir or name 
    """
    
    # Create the required FieldMap and FieldMappings objects
    fm_num_Doc = arcpy.FieldMap()
    fm_suit = arcpy.FieldMap()
    fms = arcpy.FieldMappings()
    
    # Get the field names of vegetation type and suiteter for both original
    # files
    file1_num_Doc = "num_Doc"
    file2_num_Doc = "num_Doc"
    
    file1_suit = "suit"
    file2_suit = "suit"
    
    # Add fields to their corresponding FieldMap objects
    fm_num_Doc.addInputField(in_file1, file1_num_Doc)
    fm_num_Doc.addInputField(in_file2, file2_num_Doc)
    
    fm_suit.addInputField(in_file1, file1_suit)
    fm_suit.addInputField(in_file2, file2_suit)
    
    # Set the output field properties for both FieldMap objects
    num_Doc_name = fm_num_Doc.outputField
    num_Doc_name.name = 'num_Doc'
    fm_num_Doc.outputField = num_Doc_name
    
    suit_name = fm_suit.outputField
    suit_name.name = 'suit'
    fm_suit.outputField = suit_name
    
    # Add the FieldMap objects to the FieldMappings object
    fms.addFieldMap(fm_num_Doc)
    fms.addFieldMap(fm_suit)
    
    if os.path.exists(output_file):
        arcpy.Delete_management(output_file)
    
    # Merge the two feature classes
    arcpy.Merge_management([in_file1, in_file2], output_file, fms)
    
    return arcpy.FeatureSet(output_file)
