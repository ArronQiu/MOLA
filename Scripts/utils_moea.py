# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 22:56:03 2018

@author: QiuYuean
"""

import os
import time
import random
import numpy as np

import arcpy
import utils_fcf
import utils_accs
import utils_arcpy
from params import args


# %% Global settings
np.set_printoptions(precision=3)
IND_INIT_SIZE = 100
NBR_ITEMS = 8500 # same as the size of population
MAX_COST = 1000 # max cost of expectation
MAX_ITEM = 106 # max num of items selected, ref: http://mp.ofweek.com/medical/a145663423556
MIN_ACCS = 3.2 # average accs., ref: http://mp.ofweek.com/medical/a145663423556


#weights=(1e6, -1e3, 1e-7, 1e-7)
##weights=(10000, -10000, 0.0000001, 0.01)
##weights=(10000, -10000, 0.0000001, 0.01)
##weights=(10000, -10000, 0.0000001, 0.01)
#
#NGEN = 50 # num of generation
#MU = 10 # The number of individuals to select for the next generation.
#LAMBDA = 10 # The number of children to produce at each generation.
#CXPB = 0.45 # sum must <= 1
#MUTPB = 0.45

# %% Key functions
def mutSet(individual, items_tupleSet):
    """Mutation that pops or add an element from items_tupleSet."""
#    print "mutSet Running!"
    if random.random() < 0.2: # 【can be tuned】
        if len(individual) > 0:     # We cannot pop from an empty set
            individual.remove(random.choice(sorted(tuple(individual))))
    else:
        individual.add(list(items_tupleSet)[random.randrange(NBR_ITEMS)]) # new gene must be one of the items
    return individual,

def cxSet(ind1, ind2, items_tupleSet, toolbox):
    """
    There're three types of Cx operation, illustrated below:
    ind1: 1,2;3,4;5,6   ind2: a,b;c,d;e,f
    idx_point1 = 2      idx_point2 = 4
    Cx 1: offspring: 1,2;[c,d;e,f]
    Cx 2: offspring: 1,2;[c,d;e],6
    Cx 3: offspring: 1,2;[c],4;5,6
    """
#    ori_ind1 = ind1.copy()
#    ori_ind2 = ind2.copy()
    
    ori_ind1 = toolbox.clone(ind1)
    ori_ind2 = toolbox.clone(ind2)
    
    pro = random.random()
    if pro < 0.2:
        type_cx = 1
    elif pro < 0.6:
        type_cx = 2
    else:
        type_cx = 3
        
        
    smaller_length = len(ind1)*2 if len(ind1) < len(ind2) else len(ind2)*2
    
    list1 = set2list(ind1)
    list2 = set2list(ind2)
    
    # single-point cross-over
    if type_cx == 1:
        # index of the point, i.e., where the cross-over happens
        idx_point = random.randint(1,smaller_length-2)
        # note that, cross-over from the first point or the last one means nothing
        
        offspring1 = list1[:idx_point] + list2[idx_point:]
        offspring2 = list2[:idx_point] + list1[idx_point:]
        
        ind1 = list2set(offspring1)
        ind2 = list2set(offspring2)
        
    # double-point cross-over
    elif type_cx == 2:
        # note that, cross-over between the first point or the last one means nothing
        
        idx_point1 = random.randint(0,smaller_length-1)
        idx_point2 = random.randint(0,smaller_length-1)
        idx_point1 = min(idx_point1,idx_point2)
        idx_point2 = max(idx_point1,idx_point2)
        
        offspring1 = list1[:idx_point1] + list2[idx_point1:idx_point2] + list1[idx_point2:]
        offspring2 = list2[:idx_point1] + list1[idx_point1:idx_point2] + list2[idx_point2:]
        
        ind1 = list2set(offspring1)
        ind2 = list2set(offspring2)
        
    # single-gene cross-over  
    else: 
        idx_point = random.randint(0,smaller_length-1)
        temp = list1[idx_point]
        list1[idx_point] = list2[idx_point]
        list2[idx_point] = temp
        ind1 = list2set(list1)
        ind2 = list2set(list2)
        
        ind1 = list2set(list1)
        ind2 = list2set(list2)
    
    
    replace_nonexistent_gene(items_tupleSet, ind1, NBR_ITEMS)
    replace_nonexistent_gene(items_tupleSet, ind2, NBR_ITEMS)
    
    # 【turn ind.__class__ into deap.creator.Individual】
    # Clean ind
    for i in range(len(ori_ind1)):
        ori_ind1.pop()
    for i in range(len(ori_ind2)):
        ori_ind2.pop()
        
    # add elements of new ind
    for ele in ind1:
        ori_ind1.add(ele)
    for ele in ind2:
        ori_ind2.add(ele)
    
    return ori_ind1, ori_ind2
   
def evalKnapsack(individual, items_dict, items_fs, faci_fs, field_name_list_items, flag_update, flag_output):
    """
    Args:
        individual: a int set, each element is an item Id
        items_dict: a dict, key- an item Id, value- (id, cost, suitability) 3-tuple
        items_fs: the arcpy feature set of all items/ candidates
        faci_fs: the arcpy feature set of existing faci
    Note that both (individual and item_fs) should be pre-increasingly-sorted 
    based on Id for quicker search.
    """
    print "==================================================================="
    print "Evaluating", individual
    
    time_ind = time.time()
    
    # extract item based on individual
#    time_begin = time.time()
    ind_dict = ind_2_dict(individual, items_fs, field_name_list_items)
#    print "Time- ind_dict : %.2fs" % (time.time() - time_begin)
    
    # update feature by merging old faci_fs and new item_fs
#    time_begin = time.time()
    uptodate_feature = update_feature(individual, items_fs, faci_fs, ind_dict,flag_output)
#    print "Time- uptodate_feature : %.2fs" % (time.time() - time_begin)
    
    # run find_cloest_faci
#    time_begin = time.time()
    utils_fcf.find_cloest_faci(Inci_set = args.inIncidents, 
                               Faci_set = uptodate_feature,
                               outRoutes_name = 'routes_itr')
#    print "Time- find_cloest_faci : %.2fs" % (time.time() - time_begin)
    
    # evaluate accessibility
#    time_begin = time.time()
    service_sum = utils_accs.eval_accs(community_name='../Dataset/FileDB.gdb/community', 
             healthCenter_name=uptodate_feature, 
             routes_name='../Dataset/Output.gdb/routes_itr',
             flag_update=flag_update, flag_output=flag_output)
#    print "Time- eval_accs : %.2fs" % (time.time() - time_begin)
    
    # calculate accs_sum and accs_var
    accs_avg = np.mean(service_sum)
    accs_var = np.var(service_sum)
    
    # return result as part of fitness
    cost = 0.0
    suit = 0.0
    for item in individual:
        cost += items_dict[item][1]
        suit += items_dict[item][2]
        
    if len(individual) > MAX_ITEM:
#    or accs_avg < MIN_ACCS: # Ensure overweighted bags are dominated
        return 0.0000001, 0.0000001, 0.0000001, 0.0000001
    
    print "Time ind used: %.2fs" % (time.time() - time_ind)
#    print "Result:"
    print "accs_avg: %.10f" % accs_avg, "    cost: %.2f" % cost
    print "accs_var: %.10f" % accs_var, "    suit: %.2f" % suit
    print "==================================================================="

    return accs_avg, accs_var, cost, suit

# %%
# =============================================================================
#  test block
#items_fs_dir = os.path.join(args.env_workspace, "items")
#items_fs = arcpy.FeatureSet(items_fs_dir)
#
#faci_fs = arcpy.FeatureSet(os.path.join(args.env_workspace, "healthCenter"))
#field_name_list_faci = utils_arcpy.get_fieldNameList(faci_fs)
#num_field = len(field_name_list_faci)
                                
#individual=[(21,52),(78, 63)]

#    field_list = ['FID','accs_sum','accs_var','cost','suit']
#    field_list = ['FID','cost','suit']
# =============================================================================

def attr_item(items_tupleSet, NBR_ITEMS):
    return list(items_tupleSet)[random.randrange(NBR_ITEMS)]

def set2list(ind):
    # turn a set into sequential list for Cx operation
    seq_list = []
    for i in ind:
        seq_list.append(i[0])  
        seq_list.append(i[1])        
    return seq_list

def list2set(offspring):
    # turn offspint, a list, into a set as one individual
    offs_set = set()
    for i in range(0,len(offspring),2):
        offs_set.add((offspring[i], offspring[i+1]))
    return offs_set

def read_items_tuple(items_fs):
    field_name_list_faci = ['idx_row', 'idx_col']
#    field_name_list_faci = ['suit', 'cost']
    items_tupleSet = set()
    for record in arcpy.da.SearchCursor(items_fs, field_name_list_faci):
        tuple_temp = (record[0],record[1])
        items_tupleSet.add(tuple_temp)
    return items_tupleSet

"""
# Items can lay out as a rectangular or as the irregular shape of polygon.
# The first case seems easy to handle codes, while the second case [may] cost less time.
# For the second case, when ind. mutate or cross-over, gene should be check
# to see whether the corresponded item exist.
Args:
    items_tupleSet: a set of 2-tuple, recording the indices of row and col of each item
    ind: an ind of which nonexistente gene to be deleted
"""
def del_nonexistent_gene(items_tupleSet, ind):
    ind_temp = ind.copy()
    for gene in ind_temp:
        if(gene not in items_tupleSet):
            ind.remove(gene)
    
def replace_nonexistent_gene(items_tupleSet, ind, NBR_ITEMS):
    ind_temp = ind.copy()
    for gene in ind_temp:
        if(gene not in items_tupleSet):
            ind.remove(gene)
            ind.add(list(items_tupleSet)[random.randrange(NBR_ITEMS)])

# UPDATE: the way of encoding changes: each gene is (idx_row, idx_col)
# Designed for geographic problem. Ref: DOI:10.13284/j.cnki.rddl.001418
def ind_2_dict(individual, items_fs, field_name_list_items):
    ''' extract item according to individual
    create a dict to store field value of items'''
    field_value = {}
    for i in range(len(field_name_list_items)):
        field_value[field_name_list_items[i]] = []
    
    # extract ind's idx_row and idx_col respectively
    list_idx_row = []
    list_idx_col = []
    for gene in individual:
        list_idx_row.append(gene[0])
        list_idx_col.append(gene[1])
    
    # search items based on idx_row and idx_col
    for record in arcpy.da.SearchCursor(items_fs, field_name_list_items):
        r_idx_row = record[6] # 【!!!! WARNING !!!! IDX Should Be Confirmed!!!】
        r_idx_col = record[7] # 【!!!! WARNING !!!! IDX Should Be Confirmed!!!】
        if r_idx_row not in list_idx_row:
            continue
        elif r_idx_col not in list_idx_col:
            continue
        else:
            for i in range(len(record)): # append each field value of each gene
                field_value[field_name_list_items[i]].append(record[i])
    
    return field_value

def update_feature(individual, items_fs, faci_fs, ind_dict, flag_best):
    ''' create a new feature class and merge 2 parts of healthCenter for later calculation'''
    tmp_fc_path = os.path.join(args.output_folder_fc, "tmp_fc.shp")
    
    # delete existing one
    if os.path.exists(tmp_fc_path):
        arcpy.Delete_management(tmp_fc_path)
    # create a new one using items_fs as template (to avoid filed_name mismatch)
    spatial_reference = args.env_workspace + '/items'
    tmp_fc = arcpy.CreateFeatureclass_management(
            args.output_folder_fc, "tmp_fc", "POINT", 
            template=items_fs, spatial_reference=spatial_reference)[0]
    
    # the Id name may vary among 'OBJECTID', 'FID', 'Id' (not sure if it's common),
    # so use field_name_list_items later
    field_name_list_items = utils_arcpy.get_field_name_list(items_fs)  
    # why using items_fs can't produce same field_name_list?
    field_name_list_items = [u'FID'] + field_name_list_items[1:]
    
    # Open an insert cursor to insert data
    with arcpy.da.InsertCursor(tmp_fc, field_name_list_items) as cursor:
        for i in range(len(individual)):
            row_list = []
            for field in field_name_list_items:
                if field == 'FID':
                    field = 'OBJECTID'
                row_list.append(ind_dict[field][i])
            cursor.insertRow(row_list)
    
    if flag_best:
        output_file = os.path.join(args.output_folder_fc, 'healthCenter_best_ind.shp')
    else:
        output_file = os.path.join(args.output_folder_fc, 'temp_merged_fc.shp')

    # merge them into a new feature
    temp_merged_fc = utils_arcpy.merge_feature(
            faci_fs, tmp_fc, output_file)
    
    return temp_merged_fc