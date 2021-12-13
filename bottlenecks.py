# -*- coding: utf-8 -*-
# Copyright (C) 2020-2022 Sarang Bhagwat <sarangb2@illinois.edu>
# 
# This module is under the UIUC open-source license. See 
# github.com/BioSTEAMDevelopmentGroup/biosteam/blob/master/LICENSE.txt
# for license details.
"""
Created on Fri Sep 10 22:20:55 2021

@author: sarangbhagwat
"""

import cProfile
import pstats
import pandas

def get_bottlenecks_full_list(funct):
    profile=cProfile.Profile()
    profile.runcall(funct)
    # stats = cProfile.runctx("funct()", locals(), globals(), filename)
    # stats = pstats.Stats(profile)
    # stats.sort_stats('cumulative')
    # stats.reverse_order()
    # stats.print_stats()
    stats = profile.getstats()
    statslist = [(i[0], i[1], i[3], i[4]) for i in stats]
    statslist.sort(key=lambda i: i[2], reverse=True)
    return statslist

def get_bottlenecks(funct, filename=None, length=80, max_timefrac_for_singlecallers=0.95, remove_from_path=None):
    statslist = get_bottlenecks_full_list(funct=funct)
    total_time = statslist[0][2]
    indices_to_remove = (statslist.index(i) for i in statslist 
                         if i[1]==1 and i[2]>max_timefrac_for_singlecallers*total_time and not i[2]==total_time)
    for index in indices_to_remove:
        statslist.remove(statslist[index])
    statslist=statslist[0:length]
    statsdict = {get_keys(i[0])[0]: {'Path': get_keys(i[0], remove_from_path=remove_from_path)[1],
                                     'N_calls': i[1], 'Mean_time_per_call [s]': i[2]/i[1],
                                     'Cumulative_time [s]': i[2]} for i in statslist}
    df = pandas.DataFrame(statsdict).transpose()
    df.to_csv(filename+'.csv')
    return df

def get_keys(codeobject, function_name_start_index=13, path_start_identifier='"', remove_from_path=None):
    orig_str = str(codeobject)
    if 'code object' in orig_str:
        trunc_str = orig_str[function_name_start_index:-1]
        function_name_str = ''
        for i in trunc_str:
            if not i== ' ':
                function_name_str+=i
            else:
                break
        path_start_index = trunc_str.index(path_start_identifier)
        path_str = trunc_str[path_start_index:]
        if not remove_from_path:
            return function_name_str, path_str
        else:
            if type(remove_from_path)==str:
                remove_from_path=[remove_from_path]
            for substr in remove_from_path:
                path_str = get_str_with_substr_removed(path_str, substr)
            return function_name_str, path_str
    # elif 'built-in' in orig_str:
    #     return 'built-in method', orig_str.rsplit('built-in method')[1][1:]
    else:
        return orig_str, None
    
def get_str_with_substr_removed(orig_str, substr):
    if substr in orig_str:
        splitstr = orig_str.rsplit(substr)
        return splitstr[0] + splitstr[1]
    else:
        return orig_str