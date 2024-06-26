import subprocess
import multiprocessing as mp

import numpy as np
import os


def gen_dakota_input(var_names, nominals, lbs, ubs, num_eval=2400):
    
    dkt_in='''
        # Dakota Input File: sample.in
        # Usage:
        #    dakota -i sample.in -o sample.out > sample.stdout
        # or if run in multi-level parallelism:
        #    mpirun dakota -i sample.in -o sample.out > sample.stdout
        #    or
        #	 mpexec dakota -i sample.in -o sample.out > sample.stdout

		environment
			tabular_data
			tabular_data_file = "sample.dat"

		model
			single

		interface
			fork
			analysis_drivers = "interface_bb.py"
			parameters_file = "params.in"
			results_file = "results.out"
			file_tag 
			#file_save 	

		responses
			objective_functions = 2
			no_gradients
			no_hessians	

		method
		    moga
            seed = 10983
            max_function_evaluations = %s
            initialization_type unique_random
            population_size= 48		
            crossover_type shuffle_random
            num_offspring = 2 num_parents = 2
            crossover_rate = 0.8
            mutation_type replace_uniform
            mutation_rate = 0.1
            fitness_type domination_count
            replacement_type below_limit = 6
            shrinkage_fraction = 0.9
            convergence_type metric_tracker
            percent_change = 0.05 num_generations = 100
            final_solutions = 3
            output silent


		variables 

        ''' %(num_eval) 

    var_num=int(len(var_names))	    
    m=''		
    m+='    continuous_design=%s\n'%var_num
    m+='        		initial_point'		
    for i in range(var_num):
        m+=' %s'%nominals[i]
    m+='\n'    
    m+='        		lower_bounds'	
    for i in range(var_num):
        m+=' %s'%lbs[i]
    m+='\n' 
    m+='        		upper_bounds'	
    for i in range(var_num):
        m+=' %s'%ubs[i]
    m+='\n' 		
    m+='        		descriptors'	
    for i in range(var_num):
        m+=' "%s"'%var_names[i]
    m+='\n' 						
        
    dkt_in+=m

    with open('sample.in', 'w') as f:
        f.write(dkt_in)		


def gen_interface_bb(model_name, location, P_load_des=500e3, solar_data_fn=None, wind_data_fn=None):
    '''
    This function generate the interface_bb.py file in the casedir
    which will be excuted by DAKOTA	
    '''

    bb='''#!/usr/bin/env python3
# Dakota will execute this python script
# The command line arguments will be extracted by the interface automatically.

import dakota.interfacing as di	
params, results = di.read_parameters_file()			
names=params.descriptors

var_sets={}

for n in names: 
    var_sets[str(n)] = params.__getitem__(n)
    print('variable   : ', n, '=', params.__getitem__(n))

if 'r_pv' in names:
    r_pv=params.__getitem__('r_pv')
else:
    r_pv=None

if 'P_heater' in names:
    P_heater=params.__getitem__('P_heater')
else:
    P_heater=None

if 'bat_pmax' in names:
    bat_pmax=int(params.__getitem__('bat_pmax'))*1000.
else:
    bat_pmax=None


from greenheatpy.master import master

try:
    LCOH, CF, CAPEX =master(model_name='%s', location='%s', RM=var_sets['RM'], t_storage=var_sets['t_storage'], P_load_des=%s, r_pv=r_pv, P_heater=P_heater, bat_pmax=bat_pmax, casedir='.', solar_data_fn=%s, wind_data_fn=%s, verbose=False)
except:
    LCOH=9999
    CF=0
    CAPEX=9e14


print('LCOH', LCOH)
res=[CAPEX, -CF]

for i, r in enumerate(results.responses()):
	if r.asv.function:
		r.function = res[i]
results.write()

'''%(model_name, location, P_load_des, solar_data_fn, wind_data_fn)


    with open('interface_bb.py', 'w') as f:
        f.write(bb)  



if __name__=='__main__':

    location='Burnie'
    model_name='pv_wind_TES_heat' #'pv_wind_battery_heat' #'CST_TES_heat' 
    casedir='results/optimisation_%s_%s'%(model_name, location)
    var_names=['RM', 't_storage', 'P_heater'] #TODO,  note bat_pmax must be integer for MW
    nominals=[2, 8, 2000e3]
    lbs=[1, 1e-6, 500e3]
    ubs=[20, 60, 5000e3]

    if not os.path.exists(casedir):
        os.makedirs(casedir)

    # generate interface_bb.py that dakota can run
    gen_interface_bb(casedir, model_name, location, P_load_des=500e3)

    # generate dakota input file
    gen_dakota_input(casedir, var_names, nominals, lbs, ubs)

    subprocess.call('chmod a+x %s/interface_bb.py'%casedir, shell=True)
    # run dakota
    np=mp.cpu_count()
    #subprocess.call('mpirun --use-hwthread-cpus -np %s dakota -i sample.in -o sample.out > sample.stdout'%np, shell=True)
    #subprocess.call('dakota -i %s/sample.in -o %s/sample.out > %s/sample.stdout'%(casedir, casedir, casedir), shell=True)
    subprocess.call('mpirun --use-hwthread-cpus -np %s dakota -i %s/sample.in -o %s/sample.out > %s/sample.stdout'%(4, casedir, casedir, casedir), shell=True)



