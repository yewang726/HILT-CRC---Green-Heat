# -*- coding: utf-8 -*-
"""
Originally created on Fri May 6 12:46:54 2022 by Ahmad Mojiri

Modified by Ye Wang
"""

from greenheatpy.projdirs import datadir

import numpy as np
import json, io, requests
import PySAM.Pvwattsv8 as PVWatts, Windpower
import PySAM.TcsmoltenSalt as CSP
import platform
import os


def pv_gen(capacity, location, casedir,  wea_fn=None, tilt=0., azimuth=180., array_type=2, modeldir=None):
    """
    Arguments:
        capacity (float): system capacity (kW)
        location   (str): location of the system
 
        casedir    (str): case directory
        wea_fn     (str): directory of the weather data file for the SAM PV model
                the default 'None' will load the weather file in the 'data' directory
        tilt     (float): tilt angle of pv panel, 0 is horizontal 
					      it is normall set to the location's latitude according to SAM manual (SAM/runtime/help/html/index.html?pvwatts_system_design.htm)
        azimuth  (float):  An azimuth value of zero is facing north, 90 degrees = east, 180 degrees = south, and 270 degrees = west
                           a typical azimuth value would be 180 degrees. For systems south of the equator, a typical value would be 0 degrees.
        array_type (int):  0: fixed open rack, 2: one-axis tracking	     
    Return:
        output    (list): energy production (kW) by the PV system in time series in a year 
    
    """
    from greenheatpy.projdirs import datadir
    output_fn=casedir+'/pv_gen_%s_%.1fMWe.dat'%(location, capacity/1000)

    if modeldir==None:
        datadir=datadir
    else:
        datadir=modeldir	
    	
      
    module = PVWatts.new()

    if platform.system()=='Windows':
        json_fn=datadir+'\json_pvWatts\default_pvwattsv8.json' 
    elif platform.system()=='Linux':
        json_fn=datadir+'/json_pvWatts/default_pvwattsv8.json'   
  
    with open(json_fn, 'r') as f:
        data = json.load(f)
    f.close()
    for k,v in data.items():
        if k != "number_inputs":
            module.value(k, v)

    if wea_fn==None:
        module.value('solar_resource_file', datadir+'/SolarSource.csv')
    else:
        module.value('solar_resource_file', wea_fn)

        
    module.SystemDesign.system_capacity = capacity
    module.SystemDesign.tilt=tilt
    module.SystemDesign.azimuth=azimuth
    module.SystemDesign.array_type=array_type # 0: fixed open rack, 2: 1-axis tracking	
    module.execute()
    output = np.array(module.Outputs.gen)
    output=output.tolist()
    
    with open(output_fn, "w") as text_file:
        text_file.write(str(output))
                  
    return output_fn


def wind_gen(capacity, location, casedir, wea_fn=None, modeldir=None):
    """
    Arguments:
        capacity (float): system capacity (kW)
        location   (str): location of the system
        casedir    (str): case directory        
        wea_fn     (str): directory of the weather data file for the SAM Wind model
                the default 'None' will load the weather file in the 'data' directory
    Return:
        output    (list): energy production (kW) by the Wind system in time series in a year 
 
    """
    from greenheatpy.projdirs import datadir
    if modeldir==None:
        datadir=datadir
    else:
        datadir=modeldir

    output_fn=casedir+'/wind_gen_%s_%.1fMWe.dat'%(location, capacity/1000)

            
    module = Windpower.new()

    if platform.system()=='Windows':
        json_fn=datadir+'\json_windpower\default_windpower.json' 
    elif platform.system()=='Linux':
        json_fn=datadir+'/json_windpower/default_windpower.json'   
    
    with open(json_fn, 'r') as f:
        data = json.load(f)
    f.close()

    for k,v in data.items():
        if k != "number_inputs":
            module.value(k, v)

    if wea_fn==None:
        module.value('wind_resource_filename', datadir+'/WindSource.csv')
    else:
        module.value('wind_resource_filename', wea_fn)

    module.value('system_capacity', capacity)
    module.execute()

    output = np.array(module.Outputs.gen)
    output=output.tolist()
    with open(output_fn, "w") as text_file:
        text_file.write(str(output))    

    return output_fn



def cst_gen(Q_des_th, SM, location, casedir, helio_width, helio_height, wea_fn=None, modeldir=None):

    """
    Arguments:
        Q_des_th (float): system design thermal power (kW)
        SM       (float): solar multiple
        location   (str): location of the system
        casedir    (str): case directory            
        wea_fn     (str): directory of the weather data file for the SAM solartower model
                the default 'None' will load the weather file in the 'data' directory
    Return:
        Q_rcv_out (list): thermal output from the receiver (kW_th) in time series in a year 
        H_recv   (float): the optimal receiver height designed by SAM (m)
        D_recv   (float): the optimal receiver diameter designed by SAM (m)
        H_tower  (float): the optimal tower height designed by SAM (m)
        n_helios (float): the optimal number of heliostats designed by SAM (-)
        A_land   (float): the total land area of the optimal field layout designed by SAM (m2)
 
    """
    from greenheatpy.projdirs import datadir
    if modeldir==None:
        datadir=datadir
    else:
        datadir=modeldir

    output_fn=casedir+'/CST_gen_%s_load%.1fMWth_SM%.1f.dat'%(location, Q_des_th/1000., SM )   
      
    module = CSP.new()

    if platform.system()=='Windows':
        json_fn=datadir+'\json_cst\SAM-CSP-molten-salt_tcsmolten_salt.json' 
    elif platform.system()=='Linux':
        #json_fn=datadir+'/json_cst/SAM-CSP-molten-salt_tcsmolten_salt.json'   
        json_fn=datadir+'/json_cst/SAM-CSP-molten-salt_tcsmolten_salt.json'  
    
    with open(json_fn, 'r') as f:
        data = json.load(f)
    f.close()

    for k,v in data.items():
        if k != "number_inputs":
            module.value(k, v)

    module.value('field_model_type', 0) # SAM will optimise the field, tower and receiver size 
    module.value('f_rec_min', 1e-6) # minimal receiver turndown fraction
    module.value('solarm', SM) # solar multiple
    module.value('tshours', 100) # because this model only takes the receiver output, a very large storage is set to ignor impact from SAM control 

    # add initial guess of tower and receiver design
    if abs(Q_des_th-500e3)<0.1:
        H_recv_guess=3.603*SM+16.64
        D_recv_guess=3.05*SM+14.63
        H_tower_guess=32.21*SM+179.4
    elif abs(Q_des_th-2.3e3)<0.1:
        H_recv_guess=0.22*SM+1.29
        D_recv_guess=0.42*SM+0.56
        H_tower_guess=3.1*SM+9.68
        # smaller heliostat size
    module.value('helio_width', helio_width) 
    module.value('helio_height', helio_height) 

    module.value('rec_height', H_recv_guess) 
    module.value('D_rec', D_recv_guess) 
    module.value('h_tower', H_tower_guess) 


    if wea_fn==None:
        module.value('solar_resource_file', datadir+'/SolarSource.csv')
    else:
        module.value('solar_resource_file', wea_fn)

    P_pb_name=Q_des_th*0.412/1000. # 0.412 is the default PB efficiency, and convert to MW
    module.value('P_ref', P_pb_name) # this is capacity of electricity, 

    module.execute()

    H_recv=module.TowerAndReceiver.rec_height #Receiver height [m]
    D_recv=module.TowerAndReceiver.D_rec #The overall outer diameter of the receiver [m]
    H_tower=module.TowerAndReceiver.h_tower # Tower height [m]
    n_helios=module.HeliostatField.N_hel #Number of heliostats
    A_land=module.Outputs.csp_pt_cost_total_land_area*4046.86 # Total land area [m2] (converted [acre] to m2)
    land_area_base=module.HeliostatField.land_area_base	
    csp_pt_sf_fixed_land_area=module.HeliostatField.csp_pt_sf_fixed_land_area
    print('land_area_base', land_area_base, csp_pt_sf_fixed_land_area)
    #eta_field=module.Outputs.eta_field # field optical efficiency
    eta_recv=np.array(module.Outputs.eta_therm) # receiver thermal efficiency
    Q_recv_in=np.array(module.Outputs.q_dot_rec_inc) # incident thermal power on the receiver [MW_th]

    Q_recv_out=Q_recv_in*eta_recv*1000. # kW_th 
    #np.savetxt('sam_Q_recv_in.csv', Q_recv_in, fmt='%.4f', delimiter=',')
    #np.savetxt('sam_eta_recv.csv', eta_recv, fmt='%.6f', delimiter=',')
    Q_rcv_out=Q_recv_out.tolist()

    with open(output_fn, "w") as text_file:
        text_file.write('H_recv,D_recv,H_tower,n_helios,A_land\n')      
        text_file.write('(m),(m),(m),(-),(m2)\n')   
        text_file.write('%s,%s,%s,%s,%s\n'%(H_recv, D_recv, H_tower, n_helios, A_land))                         
        text_file.write(str(Q_rcv_out))          
    
    print('H_recv, guess: %.2f, actuall: %.2f'%(H_recv_guess, H_recv)) 
    print('D_recv, guess: %.2f, actuall: %.2f'%(D_recv_guess, D_recv)) 
    print('H_tower, guess: %.2f, actuall: %.2f'%(H_tower_guess, H_tower)) 
    return output_fn




