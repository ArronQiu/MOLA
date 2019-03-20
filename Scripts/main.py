# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 22:55:58 2018

@author: QiuYuean
"""

# The objectives of this project include:
# 1. Calculate the accessibitily (short as acc) of health centers for citizens.
# 2. Locate a number of new centers for urban planning, to optimizing a list of 
# objective functions including: 1) total acc, 2) variation of acc, 3) suitability,
# 4) constructing and operating cost.
# If it helps, please cite our paper and star the project.
# Ref: ___ .

# The workflow can be described as follow:
# 1. Prepare data, including healthCenter.shp, community.shp, roads.shp, population.shp.
# The first three data is for the first obj., the last one is for the second 
# (when multi-optimizing using MOEA, users shall provide the so-called 'population' data,
# which can be regarded as candidates for choosing locations for new centers. )
# Note that this data should use a projected system rather than a geographic one.

# 2. The module then choose several new healthCenters based on MOEA, multi-objective evolutionary algorithm.
# There're lots of libs for doing this and we chose DEAP,
# ref: 
# The MOEA can be described as follow:
# 1). 


import arcpy
import utils_accs
import utils_fcf
from params import args

import utils_moea
from deap import algorithms
from deap import base
from deap import creator
from deap import tools

import random
import numpy


def stage_1():
    if(utils_fcf.find_cloest_faci()):
        print "find_cloest_faci: succeed!"
        service_sum = utils_accs.eval_accs()
        if(utils_accs.assign_accs(service_sum)):
            print "============================================================"
            print "Stage 1 completed. Accs has been computed \nand assigned to the community polygon in 'File.gdb'."
            print "============================================================"
            print "Settings are shown as follows: (see params.py in detail)"
            print "============================================================"
            print "args.env_workspace: \t\t\t", args.env_workspace
            print "args.outGeodatabase: \t\t\t", args.outGeodatabase
            print "args.Number_of_Facilities_to_Find: \t", args.Number_of_Facilities_to_Find
            print "args.Default_Cutoff: \t\t\t", args.Default_Cutoff
            print "args.measurement_units: \t\t", args.measurement_units
            print "args.Maximum_Snap_Tolerance: \t\t", args.Maximum_Snap_Tolerance
            print "args.Travel_Direction: \t\t\t", args.Travel_Direction
        else:
            print "assign_accs: fail!"
    else:
        print "find_cloest_faci: fail!"

service_sum = utils_accs.eval_accs(
            community_name='../Dataset/FileDB.gdb/community',
            healthCenter_name='../Dataset/FileDB.gdb/healthCenter_hofLast_merged',
            if_update=True)

def stage_3():
    # update accs of community_ply_accsUpdated to illustrate its variation from optimization
    utils_fcf.find_cloest_faci(Inci_set = args.inIncidents,
                     Faci_set = '../Dataset/FileDB.gdb/healthCenter_hofLast_merged'
                     )
    
    service_sum = utils_accs.eval_accs(
            community_name='../Dataset/FileDB.gdb/community',
            healthCenter_name='../Dataset/FileDB.gdb/healthCenter_hofLast_merged',
            if_update=True)
    

def main_v0():
    
    pop = toolbox.population(n=MU)
    hof = tools.ParetoFront()
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)
    
    algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats,
                              halloffame=hof)
    
    return pop, stats, hof

def stage_2():
    # initial moea
    IND_INIT_SIZE = 5
    NBR_ITEMS = 197642 # same as the number of population ?
    MAX_ITEM = 20 # at most, how many new healthCenters we want?
    
    random.seed(64)
    
    NGEN = 50
    MU = 50
    LAMBDA = 100
    CXPB = 0.7
    MUTPB = 0.2
    
    # To assure reproductibility, the RNG seed is set prior to the items
    # dict initialization. It is also seeded in main().
    random.seed(64)
    
    # Create the item dictionary: item name is an integer (for Id)
    # and value is a (cost, suitability) 2-tuple.
    items = {}
    # Create random items and store them in the items' dictionary.
    for i in range(NBR_ITEMS):
        items[i] = (random.randint(1, 10), random.uniform(0, 100))
    
    # acc_sum, acc_var, cost, suit
    creator.create("Fitness", base.Fitness, weights=(1.0, -1.0, -1.0, 1.0))
    creator.create("Individual", set, fitness=creator.Fitness)
    
    pop = toolbox.population(n=MU)
    
    
    # load Item into feature class, Faci into feature class
    
    # based on Id, select items in Items
    
    # form a feature set
    
    # pass to the na function and evaluate
    
    # return to moea to evaluate and iterate

def main():
    exp_1()
    exp_2()
    
if __name__=="__main__":
    main()

