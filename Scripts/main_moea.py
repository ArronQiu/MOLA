# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 22:56:03 2018

@author: QiuYuean
"""
import os
import time
import random
import numpy as np
import pandas as pd

import arcpy
import utils_arcpy
import utils_moea
from params import args

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

# %% Global settings
np.set_printoptions(precision=3)
IND_INIT_SIZE = 100
NBR_ITEMS = 8500 # same as the size of population
MAX_COST = 1000 # max cost of expectation
MAX_ITEM = 106 # max num of items selected, ref: http://mp.ofweek.com/medical/a145663423556
MIN_ACCS = 3.2 # average accs., ref: http://mp.ofweek.com/medical/a145663423556


weights=(1e6, -1e3, 1e-7, 1e-7)
#weights=(10000, -10000, 0.0000001, 0.01)
#weights=(10000, -10000, 0.0000001, 0.01)
#weights=(10000, -10000, 0.0000001, 0.01)

NGEN = 30 # num of generation
MU = 6 # The number of individuals to select for the next generation.
LAMBDA = 6 # The number of children to produce at each generation.
CXPB = 0.2 # sum must <= 1
MUTPB = 0.7

def main():
    # %%
    items_fs = arcpy.FeatureSet(os.path.join(args.env_workspace, "items"))
    faci_fs = arcpy.FeatureSet(os.path.join(args.env_workspace, "healthCenter"))
    
    field_name_list_faci = utils_arcpy.get_field_name_list(faci_fs)
    field_name_list_items = utils_arcpy.get_field_name_list(items_fs)
   
    items_dict = utils_arcpy.read_items_dict(
            items_file=os.path.join(args.env_workspace, "items"),
            field_list=['OBJECTID','cost','suit','idx_row','idx_col'])
    
    items_tupleSet = utils_moea.read_items_tuple(items_fs)
    
# =============================================================================
#   DEAP lib:
# =============================================================================
    # To assure reproductibility, the RNG seed is set prior to the items
    # dict initialization. It is also seeded in main().
#    random.seed(64)
    np.set_printoptions(precision=3)
    
    # Creator, a class factory that can build new classes at run-time
    # accs_avg: 0.01, accs_var: 0.0001, cost: 1-10,  suit: 0-1
    creator.create("Fitness", base.Fitness, weights=weights)
    creator.create("Individual", set, fitness=creator.Fitness)
    
    # Toolbox, a DEAP container, storing all the objects, 
    # including: an individual, the population, as well as all functions, operators, and arguments
    toolbox = base.Toolbox()
    
    # Attribute generator
    toolbox.register("attr_item", utils_moea.attr_item, items_tupleSet, NBR_ITEMS)
    
    # Structure initializers
    toolbox.register("individual", tools.initRepeat, creator.Individual, 
        toolbox.attr_item, IND_INIT_SIZE)
    
#    toolbox.register("indSet_2_Ind", tools.initRepeat, creator.Individual, toolbox.,)
    
    # Define the population to be a list of individuals
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    # Operator registration
    toolbox.register("select", tools.selNSGA2)
    toolbox.register("mate", utils_moea.cxSet, items_tupleSet=items_tupleSet, toolbox=toolbox)
    toolbox.register("mutate", utils_moea.mutSet, items_tupleSet=items_tupleSet)
    
    toolbox.register("evaluate", utils_moea.evalKnapsack, items_dict=items_dict, 
                     items_fs=items_fs, faci_fs=faci_fs, field_name_list_items=field_name_list_items,
                     flag_update=False, flag_output=False
                     )
#    toolbox.register("evaluate", utils_moea.evalKnapsack, items_dict=items_dict, 
#                     items_fs=items_fs, faci_fs=faci_fs, field_name_list_items=field_name_list_items)
    #evalKnapsack(individual, items, items_fs, faci_fs, field_name_list_faci)
    
    
    
    #
    pop = toolbox.population(n=MU)
    hof = tools.ParetoFront()
    stats = tools.Statistics(lambda ind: ind.fitness.values)
#    stats.register("avg", np.mean, axis=0)
#    stats.register("std", np.std, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)
    
    time_begin = time.time()
    population, logbook = algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats,
                              halloffame=hof)
    print "Total time used: ", time.time() - time_begin
    
    
    
#    items_hof = hof.items
#    for i, item in enumerate(items_hof):
#        print sum(item.fitness.wvalues)
        
    best_ind = hof.items[-1]
    print "****Best_ind - fitness: %.5e | wvalue: (%.2e, %.2e, %.2e, %.2e)****" \
        % tuple([sum(best_ind.fitness.wvalues)]+list(best_ind.fitness.wvalues))
    
    utils_moea.evalKnapsack(best_ind, items_dict, items_fs, faci_fs, field_name_list_items,
                 flag_update=True, flag_output=True)
    print "Finish computing with Best_ind"
    
    return pop, stats, hof, logbook


def log_to_csv(logbook):
    NGEN = len(logbook)
    
    nevals = np.zeros(NGEN)
    
    max_mu_accs = np.zeros(NGEN)
    max_va_accs = np.zeros(NGEN)
    max_cost = np.zeros(NGEN)
    max_suit = np.zeros(NGEN)
    
    min_mu_accs = np.zeros(NGEN)
    min_va_accs = np.zeros(NGEN)
    min_cost = np.zeros(NGEN)
    min_suit = np.zeros(NGEN)
    
    
    for i in range(NGEN):
        nevals[i] = logbook[i]['nevals']
        
        max_mu_accs[i] = logbook[i]['max'][0]
        max_va_accs[i] = logbook[i]['max'][1]
        max_cost[i] = logbook[i]['max'][2]
        max_suit[i] = logbook[i]['max'][3]
        
        min_mu_accs[i] = logbook[i]['min'][0]
        min_va_accs[i] = logbook[i]['min'][1]
        min_cost[i] = logbook[i]['min'][2]
        min_suit[i] = logbook[i]['min'][3]
    
    t = [nevals, max_mu_accs,max_va_accs,max_cost,max_suit,\
         min_mu_accs,min_va_accs,min_cost,min_suit]
    
    df = pd.DataFrame(t)
    df = df.transpose()
    df.columns = ['nevals', 'max_mu_accs', 'max_va_accs', 'max_cost', 'max_suit',\
                  'min_mu_accs', 'min_va_accs', 'min_cost', 'min_suit']
    
    df.to_csv('tmp_log.csv')
    return df


if __name__ == "__main__":
    pop, stats, hof, logbook = main() 
    df = log_to_csv(logbook)
    print "End of Evolution. Args: "
    print "weights\t", weights, "\nNGEN %d"% NGEN, "MU %d"% MU, \
    "LAMBDA %d"% LAMBDA, "CXPB %.2f"% CXPB, "MUTPB %.2f"% MUTPB
    
    

# =============================================================================
#   Post process
#items_hof = hof.items
#for i, item in enumerate(items_hof):
#    print sum(item.fitness.wvalues)
#    
#best_ind = list(hof.items[-1])
#best_ind = hof.items[-1]
#print "Best ind - wvalue: %.2e, %.2e, %.2e, %.2e" % best_ind.fitness.wvalues
#print  "fitness: %.5f" % sum(best_ind.fitness.wvalues)
#
#evalKnapsack(individual, items_dict, items_fs, faci_fs, field_name_list_items):

    
#a = items_hof.
#i1 = items_hof[0]
#i1.fitness

# =============================================================================
    
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
