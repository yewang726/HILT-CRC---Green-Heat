import pandas as pd
import numpy as np
import os
from greenheatpy.projdirs import datadir #load the path that contains the data files 
from greenheatpy.run_minizinc import run_minizinc
from greenheatpy.pySAM_models import pv_gen, wind_gen, cst_gen
from greenheatpy.get_weather_data import SolarResource_solcast_TMY, WindSource_solcast_TMY
from greenheatpy.get_location import get_location
from greenheatpy.parameters import Parameters
from greenheatpy.outputs import Outputs
from greenheatpy.gen_minizinc_input_data import GenDZN


def AUD2USD(value):
    return(0.746 * value)

def master(model_name, location, RM, t_storage, P_load_des=500e3, r_pv=None, P_heater=None, bat_pmax=None, casedir=None, solar_data_fn=None, wind_data_fn=None, verbose=False):
    '''
    Arguments:
        model_name (str)  : minizic model name
        location   (str)  : site location
        RM         (float): renewable multiple, the total size of the renewable energy collection system (e.g. PV+Wind) to the load
        t_storage  (float): storage hour (h)
		r_pv       (float): fraction of pv, 1 is 100% pv, 0 is 100% wind, required by the pv+wind hybrid model
		P_heater   (float): electric power of the heater (kW), required by the pv/wind/hybrid+TES model
		bat_pmax   (float): power of the battery (kW), required by the pv/wind/hybrid+battery model
        P_load_des (float): system load design power (kW)
        casedir    (str)  : the case directory, if the default None is kept, it will load/save data in 'datadir'
        verbose    (bool) : to save and plot the time series results or not

    Returns:

    '''
    if not os.path.exists(casedir):
        os.makedirs(casedir)

    #Lat,Lon = get_location(location)



    #TODO the weather data is loaded from the pre-saved data in data dir
    # it is Newman TMY from Solcast, sent by AM on 24 Jun
    # this part will be updated when the Solcast access is solved
    if 'pv' in model_name:
        # Get solar data
        #if not os.path.exists(casedir+'/SolarSource.epw'):
        #    SolarResource(Lat,Lon, casedir)
        # Get SAM reference system outputs
        if solar_data_fn ==None:
            solar_data_fn=SolarResource_solcast_TMY(location, casedir=casedir)        
        pv_ref_capa = 1e3 #(kW)
        output_fn = pv_gen(pv_ref_capa, location=location, casedir=casedir, wea_fn=solar_data_fn)      

        with open(output_fn) as f:
            output=f.read().splitlines()
        f.close()          
            
        pv_ref_out=list(np.float_(output[0][1:-1].split(',')))     
         

    if 'wind' in model_name:
        # Get wind data
        #if not os.path.exists(casedir+'/WindSource.csv'):
        #    WindSource(Lat, Lon, casedir)
        # Get SAM reference system outputs
        if wind_data_fn==None:
            wind_data_fn=WindSource_solcast_TMY(location, casedir=casedir)        
        wind_ref_capa = 200e3 #(kW)
        output_fn = wind_gen(wind_ref_capa, location=location, casedir=casedir, wea_fn=wind_data_fn)
            
        with open(output_fn) as f:
            output=f.read().splitlines()
        f.close()            
            
        wind_ref_out=list(np.float_(output[0][1:-1].split(',')))     
      
        

    if 'CST' in model_name:
        #if not os.path.exists(casedir+'/SolarSource.epw'):
        #    SolarResource(Lat,Lon, casedir)
        # Get SAM output 
        if solar_data_fn ==None:
            solar_data_fn=SolarResource_solcast_TMY(location, casedir=casedir)       
        output_fn= cst_gen(Q_des_th=P_load_des, SM=RM, location=location, casedir=casedir, wea_fn=solar_data_fn)

        with open(output_fn) as f:
            cst_output=f.read().splitlines()
        f.close()
       
        H_recv, D_recv, H_tower, n_helios, A_land = np.float_(cst_output[2].split(','))
        P_recv_out = list(np.float_(cst_output[3][1:-1].split(',')))  

        

    #solcast_weather(Newman)
    #SolarResource_solcast()
    #WindSource_solcast()


    # Set the inputs for plant optimisation and run the optimisation
    # These inputs are used by make_dzn_file function to create an input text file called hydrogen_plant_data.dzn. 
    pm=Parameters()
    if model_name=='pv_wind_battery_heat':
        #P_heater=P_load_des/pm.eta_heater
        simparams = dict(DT = 1.,# [h] time steps
                         RM = RM, # renewable multiple
                         t_storage = t_storage, # [h] storage hour
						 bat_pmax = bat_pmax, #[kW] battery power
                         eta_BAT_in = pm.eta_bat_in,   # charging efficiency of battery
                         eta_BAT_out = pm.eta_bat_out,  # discharg efficiency of battery
                         P_heater = P_heater, # [kW] heater designed power
                         eta_heater = pm.eff_heater, # heater efficiency
                         c_PV = pm.c_pv_system,  # [USD/kW] unit cost of PV
                         c_Wind = pm.c_wind_system, # [USD/kW] unit cost of W
                         c_BAT_energy = pm.c_bat_energy, # [USD/kWh] unit cost of battery energy storage
                         c_BAT_power = pm.c_bat_power,  # [USD/kW] unit cost of battery power capacpity
                         c_heater = pm.c_heater, # [USD/kW] unit cost of heater
                         PV_ref_capa = pv_ref_capa,    #capacity of reference PV plant (kW)
                         PV_ref_out = pv_ref_out,           #power output from reference PV plant (kW)
                         Wind_ref_capa = wind_ref_capa,      #capacity of reference wind farm (kW)
                         Wind_ref_out = wind_ref_out,        #power output from the reference wind farm (kW)
                         L = [P_load_des for i in range(len(pv_ref_out))],  #[kW] load profile timeseries
                         r_pv= r_pv)  # pv ratio



    elif model_name=='pv_wind_TES_heat':
        eta_TES_in=pm.eff_rdtrip_TES**0.5
        simparams = dict(DT = 1.,# [h] time steps
                         RM = RM, # renewable multiple
                         t_storage = t_storage, # [h] storage hour
                         eta_TES_in = eta_TES_in,   # charging efficiency of battery
                         eta_TES_out = eta_TES_in,  # discharg efficiency of battery
                         P_heater = P_heater, # [kW] heater designed power
                         eta_heater = pm.eff_heater, # heater efficiency
                         c_PV = pm.c_pv_system,  # [USD/kW] unit cost of PV
                         c_Wind = pm.c_wind_system, # [USD/kW] unit cost of W
                         c_TES = pm.c_TES, # [USD/kWh] unit cost of TES
                         c_heater = pm.c_heater, # [USD/kW] unit cost of heater
                         PV_ref_capa = pv_ref_capa,    # capacity of reference PV plant (kW)
                         PV_ref_out = pv_ref_out,           #power output from reference PV plant (kW)
                         Wind_ref_capa = wind_ref_capa,      #capacity of reference wind farm (kW)
                         Wind_ref_out = wind_ref_out,        #power output from the reference wind farm (kW)
                         L = [P_load_des for i in range(len(pv_ref_out))],  #[kW] load profile timeseries
                         r_pv= r_pv)  # pv ratio


    elif model_name=='CST_TES_heat':
        eta_TES_in=pm.eff_rdtrip_TES**0.5
        simparams = dict(DT = 1.,# [h] time steps
                         t_storage = t_storage, # [h] storage hour
                         eta_TES_in = eta_TES_in,   # charging efficiency of battery
                         eta_TES_out = eta_TES_in,  # discharg efficiency of battery
                         P_recv_out = P_recv_out,        #power output from the reference wind farm (kW)
                         L = [P_load_des for i in range(len(P_recv_out))])  #[kW] load profile timeseries


    #run the optimisation function and get the results in a dictionary:
    casename=model_name+'_%.3f_%.2f'%(RM, t_storage)
    genDZN=GenDZN(model_name, simparams, casename, casedir)
    dzn_fn=genDZN.dzn_fn
    results = run_minizinc(model_name, dzn_fn, casedir)

    output=Outputs(verbose)

    CF=results['CF'][0]
    if 'pv_wind_battery_heat' in model_name:

        CAPEX=results['CAPEX'][0]
        pv_max = results['pv_max'][0]
        wind_max = results['wind_max'][0]
        OM_fixed=pm.c_om_fixed_pv*pv_max+pm.c_om_fixed_wind*wind_max
        c_OM_var = 0.
        C_direct= CAPEX*(1.+pm.r_conting)
        C_indirect = (pm.r_EPC+pm.r_tax)*C_direct #TODO and C_land
        C_cap=C_direct + C_indirect
        LCOH, epy, OM_total=cal_LCOH(CF,  P_load_des, C_cap, OM_fixed, c_OM_var, r_discount=pm.r_disc_real, t_life=pm.t_life, t_cons=pm.t_cons)
        output.pv_wind_battery_heat_outputs(results, casedir, LCOH, location, solar_data_fn, wind_data_fn)


    elif model_name=='pv_wind_TES_heat':
        pv_max = results['pv_max'][0]
        wind_max = results['wind_max'][0]
        P_heater=results["P_heater"][0]
        TES_capa=results["TES_capa"][0]
        C_pv=pm.c_pv_system*pv_max
        C_wind=pm.c_wind_system*wind_max
        C_TES=TES_capa*pm.c_TES
        C_heater=P_heater*pm.c_heater
        CAPEX=results['CAPEX'][0]
        
        # heater replacement
        C_replace_heater=P_heater*pm.c_replace_heater
        n_replace=int(pm.t_life/pm.t_life_heater)
        C_replace_NPV=0
        for i in range(n_replace):
            t=(i+1)*pm.t_life_heater+pm.t_constr_pv
            C_replace_NPV+=C_replace_heater/(1+pm.r_disc_real)**t

        C_cap = CAPEX*(1+pm.r_conting_pv)+C_replace_NPV

        OM_fixed=pm.c_om_pv_fix*pv_max+pm.c_om_wind_fix*wind_max
        c_OM_var = 0

        LCOH, epy, OM_total = cal_LCOH(CF, P_load_des, C_cap, OM_fixed, c_OM_var, r_discount=pm.r_disc_real, t_life=pm.t_life, t_cons=pm.t_constr_pv)

        output.pv_wind_TES_heat_outputs(results, casedir, LCOH, location, solar_data_fn, wind_data_fn, epy, OM_total, C_cap, CAPEX, C_pv, C_wind, C_TES, C_heater, C_replace_NPV,  pm.r_disc_real, pm.t_life, pm.t_constr_pv)


    elif model_name=='CST_TES_heat':

        C_recv = pm.C_recv_ref * ( H_recv * D_recv * np.pi / pm.A_recv_ref)**pm.f_recv_exp
        C_tower = pm.C_tower_fix * np.exp(pm.f_tower_exp * (H_tower - H_recv/2.+pm.H_helio/2.))
        C_field = pm.c_helio * n_helios * pm.A_helio
        C_site = pm.c_site_cst * pm.A_helio * n_helios
        C_TES = pm.c_TES * results['TES_capa'][0]
        C_land = pm.c_land_cst * A_land
        CAPEX = C_recv + C_tower + C_field + C_site + C_TES 
        
        C_direct= CAPEX*(1.+pm.r_conting_cst)
        C_indirect = pm.r_EPC_owner*C_direct + C_land 
        C_cap=C_direct + C_indirect

        OM_fixed=pm.c_om_cst_fix * P_load_des
        c_OM_var = pm.c_om_cst_var

        LCOH, epy, OM_total=cal_LCOH(CF,  P_load_des, C_cap, OM_fixed, c_OM_var, r_discount=pm.r_disc_real, t_life=pm.t_life, t_cons=pm.t_constr_cst)

        output.CST_TES_heat_outputs(results, casedir, RM, H_recv, D_recv, H_tower, n_helios, A_land, LCOH, location, solar_data_fn, epy, OM_total, C_cap, C_indirect, C_direct, CAPEX, C_recv, C_tower, C_field, C_site, C_TES,  C_land, r_disc_real, t_life, t_cons)


    print('LCOH', LCOH)
    print('CF', CF)
    print('C_cap', C_cap)
    if not verbose:
        os.system('rm '+ genDZN.dzn_fn)

    return LCOH, CF, CAPEX

def cal_LCOH(CF, load, C_cap, OM_fixed, c_OM_var, r_discount, t_life, t_cons):
    """Levelised cost of heat in USD/MWh. 
    Similar approach in SolarTherm for LCOE calculation.

    We take the convention that payments made or energy produced during a year
    are discounted at the end of that year. For example, the O&M
    costs M paid during the first year has a present value of M/(1 + r).  This
    will tend to underestimate costs but also underestimate the value of the
    energy produced. These will tend to cancel out, but there will remain a 
    difference between LCOE calculated using the start of the year.

    The capital costs are discounted at the start of the year instead, and are
    split over each year of construction. This should probably be handled with
    loans.
    Note that here the real discounted rate (i.e. r_discount) has been used to calculate
    the real LCOE.

    CF         (float): capacity factor
    load       (float): the design heat load of the system (kW)
    C_cap      (float): total capital cost (USD)
    OM_fixed   (float): cost of fixed O&M (USD/kW)
    c_OM_var   (float): unit cost of variable O&M (USD/kWh)
    r_discount (float): discount rate
    t_life     (int)  : lifetime of the system (y)   
    t_cons     (int)  : construction time (y)
    """
    nu = 0.
    de = 0.

    epy=CF*load*24.*365./1000. #MWh
    c_year=OM_fixed+c_OM_var*epy

    # Assume capital cost is evenly split between years in construction phase,
    # else if no construction phase it is all paid up front
    if t_cons == 0:
        nu += C_cap
    else:
        for i in range(t_cons):
            nu += (C_cap/t_cons)/((1 + r_discount)**i)

    for i in range(t_cons+1, t_cons+t_life+1):
        nu += c_year/((1 + r_discount)**i)
        de += epy/((1 + r_discount)**i)

    LCOH=nu/de

    return LCOH, epy, c_year

if __name__=='__main__':
    location='Newman'
    SH=np.arange(1e-6, 20.+1e-6, 2.)
    RM=np.append(np.arange(1, 5, 0.5), np.arange(5, 11, 2))
    model_name='pv_wind_TES_heat'#'CST_TES_heat'

    for rm in RM:
        for sh in SH:
            casedir='./results/CF-%s-wind/%s/'%(model_name, location)
            res_fn=casedir+'/summary_%.1f_%.1f.csv'%(rm, sh)
            if not os.path.exists(res_fn):

                try:
                    LCOH, CF=master(model_name, location, rm, sh, P_load_des=500e3, r_pv=0, casedir=casedir, verbose=False)
                    print('RM', rm, 'SH', sh, 'Done')
                except:
                    print('RM', rm, 'SH', sh, 'Unsolved')

            else:
                print('RM', rm, 'SH', sh, 'Done')

    for rm in RM:
        for sh in SH:
            casedir='./results/CF-%s-pv/%s/'%(model_name, location)
            res_fn=casedir+'/summary_%.1f_%.1f.csv'%(rm, sh)
            if not os.path.exists(res_fn):

                try:
                    LCOH, CF=master(model_name, location, rm, sh, P_load_des=500e3, r_pv=1., casedir=casedir, verbose=False)
                    print('RM', rm, 'SH', sh, 'Done')
                except:
                    print('RM', rm, 'SH', sh, 'Unsolved')

            else:
                print('RM', rm, 'SH', sh, 'Done')




