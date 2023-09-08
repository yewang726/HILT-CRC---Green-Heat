from greenheatpy.parameters import Parameters, CST_SL_OM
from greenheatpy.get_single_design import get_CST_design, get_CST_modular_design, get_TES_design, get_BAT_design,get_PHES_design
from greenheatpy.master import cal_LCOH
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import qmc

def update_cost(rm, sh, location, case, year, resdir,  P_load=500.e3, costmodel='2020', design=None, verbose=False):
    '''
    rm (float): renewable multiple
    sh (float): storage hour
    location (str): location
    case (str): case name
    year (int): year of the design base
    costmodel (str): '2020', '2030', '2050', 'uncertainty'
    resdir (str): the main directory to deal with input and output 
    verbose (bool): to save the case design details or not
    '''

    if verbose:
        savename='%s-%s_%.3f_%.2f'%(case, location, rm, sh)
    else:
        savename=None
    pm=Parameters()
    if 'CST' in case:
        if design==None:
            if 'modular' in case:
                lcoh, CF=get_CST_modular_design(rm, sh, location, case, resdir, P_load, year=year, costmodel=costmodel)

            else:
                lcoh, CF=get_CST_design(rm, sh, location, case, resdir, P_load, year=year, costmodel=costmodel, fast=True)
                num_modules=1
        else:
            if 'modular' in case:
                CF, A_land, D_recv, H_recv, H_tower, n_helios, TES_capa, num_modules=design
            else:
                CF, A_land, D_recv, H_recv, H_tower, n_helios, TES_capa=design
                num_modules=1
                               
            if costmodel=='2020':
                C_recv_ref=pm.C_recv_ref
                C_tower_fix=pm.C_tower_fix
                c_helio=pm.c_helio
                c_site_cst=pm.c_site_cst
                c_TES=pm.c_TES
                c_land_cst=pm.c_land_cst
            elif costmodel=='2030':  
                C_recv_ref=pm.C_recv_ref_2030
                C_tower_fix=pm.C_tower_fix_2030
                c_helio=pm.c_helio_2030
                c_site_cst=pm.c_site_cst_2030
                c_TES=pm.c_TES_2030
                c_land_cst=pm.c_land_cst_2030
            elif costmodel=='2050':  
                C_recv_ref=pm.C_recv_ref_2050
                C_tower_fix=pm.C_tower_fix_2050
                c_helio=pm.c_helio_2050
                c_site_cst=pm.c_site_cst_2050
                c_TES=pm.c_TES_2050
                c_land_cst=pm.c_land_cst_2050
            else: # costmodel=='uncertainty':
                C_recv_ref=costmodel['C_recv_ref']
                C_tower_fix=costmodel['C_tower_fix']
                c_helio=costmodel['c_helio']
                c_site_cst=costmodel['c_site_cst']
                c_TES=costmodel['c_TES']
                c_land_cst=costmodel['c_land_cst']
            lcoh=get_LCOH_CST(CF, A_land, D_recv, H_recv, H_tower, n_helios, TES_capa, C_recv_ref, C_tower_fix, c_helio, c_site_cst, c_TES, c_land_cst, num_modules, savename=savename)

    elif 'TES' in case:
        if 'PV' in case:
            F_pv=1
        elif 'WIND' in case:
            F_pv=0
        elif 'HYBRID' in case:
            F_pv=None
        if design==None:
            lcoh, CF=get_TES_design(rm, sh, location, case, resdir, P_load, year=year, costmodel=costmodel, F_pv=F_pv)

        else:
            CF, P_heater, pv_max, wind_max, TES_capa=design
            if costmodel=='2020':
                c_pv_system=pm.c_pv_system
                c_wind_system=pm.c_wind_system
                c_heater=pm.c_heater
                c_TES=pm.c_TES
            elif costmodel=='2030':
                c_pv_system=pm.c_pv_system_2030
                c_wind_system=pm.c_wind_system_2030
                c_heater=pm.c_heater_2030
                c_TES=pm.c_TES_2030
            elif costmodel=='2050':
                c_pv_system=pm.c_pv_system_2050
                c_wind_system=pm.c_wind_system_2050
                c_heater=pm.c_heater_2050
                c_TES=pm.c_TES_2050
            else:
                c_pv_system=costmodel['c_pv_system']
                c_wind_system=costmodel['c_wind_system']
                c_heater=costmodel['c_heater']
                c_TES=costmodel['c_TES']

            lcoh=get_LCOH_TES(CF, P_heater, pv_max, wind_max, TES_capa, c_pv_system, c_wind_system, c_heater, c_TES, savename=savename)

    elif 'BAT' in case:
        if 'PV' in case:
            F_pv=1
        elif 'WIND' in case:
            F_pv=0
        elif 'HYBRID' in case:
            F_pv=None
        if design==None:
            lcoh, CF=get_BAT_design(rm, sh, location, case, resdir, P_load, year=year, costmodel=costmodel, F_pv=F_pv)
        else:
            CF, P_heater, pv_max, wind_max, bat_capa, bat_pmax=design
            if costmodel=='2020':
                c_pv_system=pm.c_pv_system
                c_wind_system=pm.c_wind_system
                c_heater=pm.c_heater
                c_bt_energy=pm.c_bt_energy
                c_bt_power=pm.c_bt_power
            elif costmodel=='2030':
                c_pv_system=pm.c_pv_system_2030
                c_wind_system=pm.c_wind_system_2030
                c_heater=pm.c_heater_2030
                c_bt_energy=pm.c_bt_energy_2030
                c_bt_power=pm.c_bt_power_2030
            elif costmodel=='2050':
                c_pv_system=pm.c_pv_system_2050
                c_wind_system=pm.c_wind_system_2050
                c_heater=pm.c_heater_2050
                c_bt_energy=pm.c_bt_energy_2050
                c_bt_power=pm.c_bt_power_2050
            else:
                c_pv_system=costmodel['c_pv_system']
                c_wind_system=costmodel['c_wind_system']
                c_heater=costmodel['c_heater']
                c_bt_energy=costmodel['c_bt_energy']
                c_bt_power=costmodel['c_bt_power']

            lcoh=get_LCOH_BAT(CF, P_heater, pv_max, wind_max, bat_capa, bat_pmax, c_pv_system, c_wind_system, c_heater, c_bt_energy, c_bt_power, savename=savename)

    elif 'PHES' in case:
        if 'PV' in case:
            F_pv=1
        elif 'WIND' in case:
            F_pv=0
        elif 'HYBRID' in case:
            F_pv=None
        if design==None:
            lcoh, CF=get_PHES_design(rm, sh, location, case, resdir, P_load, year=year, costmodel=costmodel, F_pv=F_pv)
        else:
            CF, P_heater, pv_max, wind_max, PHES_capa, PHES_pmax=design

            if costmodel=='2020':
                c_pv_system=pm.c_pv_system
                c_wind_system=pm.c_wind_system
                c_heater=pm.c_heater
                c_PHES_energy=pm.c_PHES_energy
                c_PHES_power=pm.c_PHES_power
            elif costmodel=='2030':
                c_pv_system=pm.c_pv_system_2030
                c_wind_system=pm.c_wind_system_2030
                c_heater=pm.c_heater_2030
                c_PHES_energy=pm.c_PHES_energy_2030
                c_PHES_power=pm.c_PHES_power_2030
            elif costmodel=='2050':
                c_pv_system=pm.c_pv_system_2050
                c_wind_system=pm.c_wind_system_2050
                c_heater=pm.c_heater_2050
                c_PHES_energy=pm.c_PHES_energy_2050
                c_PHES_power=pm.c_PHES_power_2050
            else:
                c_pv_system=costmodel['c_pv_system']
                c_wind_system=costmodel['c_wind_system']
                c_heater=costmodel['c_heater']
                c_PHES_energy=costmodel['c_PHES_energy']
                c_PHES_power=costmodel['c_PHES_power']

            lcoh=get_LCOH_PHES(CF, P_heater, pv_max, wind_max, PHES_capa, PHES_pmax, c_pv_system, c_wind_system, c_heater, c_PHES_energy, c_PHES_power, savename=savename)

    return lcoh

def future_cost(location, case, year, costmodel, resdir, P_load=500.e3, verbose=False):
    '''
    location (str): location
    case (str): case name
    year (int): year of the design base
    costmodel (str): '2020', '2030', '2050'
    resdir (str): the main directory to deal with input and output 
    verbose (bool): to save the case design details or not
    '''

    data=np.loadtxt('%s/post/%s/%s-%s-data_CF.csv'%(resdir, year, case, location), delimiter=',')

    CF=data[1:,1:]
    RM=data[1:, 0]
    SH=data[0,1:]
    m=int(len(RM))
    n=int(len(SH))

    LCOH=np.array([])

    for rm in RM:
        for sh in SH:
            lcoh=update_cost(rm, sh, location, case, year, resdir,  P_load, costmodel, verbose=verbose) 
            LCOH=np.append(LCOH, lcoh)

    LCOH=LCOH.reshape(m,n)

    savedata=np.vstack((SH, LCOH))
    savedata=np.hstack((np.append(0, RM).reshape(m+1, 1), savedata))
    np.savetxt('%s/post/%s/%s-%s-data_LCOH.csv'%(resdir, costmodel, case, location), savedata, delimiter=',', fmt='%.2f') 
    savedata=np.vstack((SH, CF))
    savedata=np.hstack((np.append(0, RM).reshape(m+1, 1), savedata))
    np.savetxt('%s/post/%s/%s-%s-data_CF.csv'%(resdir, costmodel, case, location), savedata, delimiter=',', fmt='%.2f') 

def uncertainty_cost(location, case, resdir, num_sample, dev=0.25, verbose=False, plot=False):
    '''
    location (str): location
    case (str): case name
    resdir (str): the main directory to deal with input and output 
    num_sample (int): number of samples
    dev (float): range of deviation (uncertainty), e.g. +/-25%
    verbose (bool): to save the case design details or not
    '''
    year=2020 # year of the design base and cost base
    data=np.loadtxt('%s/post/%s/%s-%s-LCOH-CF.csv'%(resdir, year, case, location), delimiter=',', skiprows=1)

    CF=data[:,0]
    SH=data[:,1]
    RM=data[:, 2]
    LCOH_n=data[:,3]
    pm=Parameters()
    summary=np.array(['CF', 'LCOH nominal', 'LCOH min', 'LCOH max', 'LCOH avg', 'LCOH std' ])
    if 'PV' in case:
        F_pv=1
    elif 'WIND' in case:
        F_pv=0
    elif 'HYBRID' in case:
        F_pv=None

    for i in range(len(CF)):
        print('CF=', CF[i], 'LCOH_n=', LCOH_n[i])
        if LCOH_n[i]<999:
            rm=RM[i]
            sh=SH[i]
            if 'CST' in case:
                if 'modular' in case:
                    design=get_CST_modular_design(rm, sh, location, case, resdir, year=year)
                else:
                    design=get_CST_design(rm, sh, location, case, resdir, year=year)
                    num_modules=1
                nd=6
                names=['C_recv_ref', 'C_tower_fix', 'c_helio', 'c_site_cst', 'c_TES', 'c_land_cst']
                nominals=np.r_[pm.C_recv_ref, pm.C_tower_fix, pm.c_helio, pm.c_site_cst, pm.c_TES, pm.c_land_cst]

            elif 'TES' in case:
                design=get_TES_design(rm, sh, location, case, resdir, year=year, F_pv=F_pv)
                nd=4
                names=['c_pv_system', 'c_wind_system', 'c_heater', 'c_TES']
                nominals=np.r_[pm.c_pv_system, pm.c_wind_system, pm.c_heater, pm.c_TES]

            elif 'BAT' in case:
                design=get_BAT_design(rm, sh, location, case, resdir, year=year, F_pv=F_pv)
                nd=5
                names=['c_pv_system', 'c_wind_system', 'c_heater', 'c_bt_energy', 'c_bt_power']
                nominals=np.r_[pm.c_pv_system, pm.c_wind_system, pm.c_heater, pm.c_bt_energy, pm.c_bt_power]

            elif 'PHES' in case:
                design=get_PHES_design(rm, sh, location, case, resdir, year=year, F_pv=F_pv)
                nd=5
                names=['c_pv_system', 'c_wind_system', 'c_heater', 'c_PHES_energy', 'c_PHES_power']
                nominals=np.r_[pm.c_pv_system, pm.c_wind_system, pm.c_heater, pm.c_PHES_energy, pm.c_PHES_power]

            samples=gen_lhs(nd, ns=num_sample)
            l_bounds=nominals*(1.-dev)
            u_bounds=nominals*(1.+dev)
            vals=qmc.scale(samples, l_bounds, u_bounds)
            costmodel={}
            for n in range(nd):
                key=names[n]
                costmodel[key]=vals[:,n]
            lcoh=update_cost(rm, sh, location, case, year, resdir, costmodel=costmodel, design=design, verbose=False)
            lcoh_min=np.min(lcoh)
            lcoh_max=np.max(lcoh)
            lcoh_avg=np.average(lcoh)
            lcoh_sdev=np.std(lcoh)
            #TODO check
            # CI https://www.mathsisfun.com/data/confidence-interval.html
            # CI=Z*s/sqrt(n)
            # Z=1.96 for 95%
            # Z=2.576 for 99%
            # Z=3.291 for 99.9%
            ci=3.291*lcoh_sdev/np.sqrt(num_sample)
            
            lcoh_lb=lcoh_avg-ci
            lcoh_ub=lcoh_avg+ci          
            print('min=%.2f, max=%.2f, avg=%.2f, sdev=%.2f, lb=%.2f, ub=%.2f, ci=%.3f'%(lcoh_min, lcoh_max, lcoh_avg, lcoh_sdev, lcoh_lb, lcoh_ub, ci))
            summary=np.append(summary, (CF[i], LCOH_n[i],lcoh_min, lcoh_max, lcoh_avg, lcoh_sdev ))           
            if plot:
                plt.hist(lcoh, bins=20)
                plt.show()
                plt.close()

    summary=summary.reshape(int(len(summary)/6),6)
    np.savetxt('%s/post/uncertainty/LCOH_statistics_%s_%s.csv'%(resdir, case, location), summary, delimiter=',', fmt='%s')
        
def gen_lhs(nd, ns=200):
    '''
    ns (int): number of samples
    nd (ind): number of dimentions
    '''
    sampler=qmc.LatinHypercube(d=nd)
    sample=sampler.random(n=ns)
   
    return sample


def get_reduction_ratio(array, symbol, label):
    a=array[0]
    b=array[1]
    c=array[2]

    r1=b/a
    r2=c/b*r1
    if r1==0.8 and abs(r2-0.64)<1e-5:
        fixed=True
    else:
        fixed=False
    year=np.r_[2020, 2030, 2050]

    if not fixed:
        plt.plot(year, np.r_[1, r1, r2], symbol, label=label)
    else:
        plt.plot(year, np.r_[1, r1, r2], 'black', label=label)


def plot_reduction(resdir):

    fts=14
    pm=Parameters()


    c_site_cst=np.r_[pm.c_site_cst, pm.c_site_cst_2030, pm.c_site_cst_2050]
    c_land_cst=np.r_[pm.c_land_cst, pm.c_land_cst_2030, pm.c_land_cst_2050]
    c_recv_ref=np.r_[pm.C_recv_ref, pm.C_recv_ref_2030, pm.C_recv_ref_2050]
    c_tower_fix=np.r_[pm.C_tower_fix, pm.C_tower_fix_2030, pm.C_tower_fix_2050]
    c_helio=np.r_[pm.c_helio, pm.c_helio_2030, pm.c_helio_2050]
    c_pv_system=np.r_[pm.c_pv_system, pm.c_pv_system_2030, pm.c_pv_system_2050]
    c_wind_system=np.r_[pm.c_wind_system, pm.c_wind_system_2030, pm.c_wind_system_2050]
    c_bt_energy=np.r_[pm.c_bt_energy, pm.c_bt_energy_2030, pm.c_bt_energy_2050]
    c_bt_power=np.r_[pm.c_bt_power, pm.c_bt_power_2030, pm.c_bt_power_2050]
    c_PHES_energy=np.r_[pm.c_PHES_energy, pm.c_PHES_energy_2030, pm.c_PHES_energy_2050]
    c_PHES_power=np.r_[pm.c_PHES_power, pm.c_PHES_power_2030, pm.c_PHES_power_2050]
    c_TES=np.r_[pm.c_TES, pm.c_TES_2030, pm.c_TES_2050]
    c_heater=np.r_[pm.c_heater, pm.c_heater_2030, pm.c_heater_2050]

    get_reduction_ratio(c_site_cst, 'r-.', 'cst site')
    get_reduction_ratio(c_land_cst, 'r:', label='cst land')
    get_reduction_ratio(c_helio, 'r--', label='cst helios')
    get_reduction_ratio(c_recv_ref, 'r-', label='cst recv')
    get_reduction_ratio(c_tower_fix,'rx', label='cst tower')
    get_reduction_ratio(c_pv_system, 'g', label='pv')
    get_reduction_ratio(c_wind_system,'b', label='wind')
    get_reduction_ratio(c_bt_energy ,'y-', label='batt en')
    get_reduction_ratio( c_bt_power, 'y--', label='batt power')
    get_reduction_ratio(c_PHES_energy, 'p-',  label='PHES en')
    get_reduction_ratio(c_PHES_power , 'p--', label='PHES power')
    get_reduction_ratio(c_TES,'orange', label='TES')
    get_reduction_ratio(c_heater,'blueviolet', label='heater')


    plt.legend(loc=1, bbox_to_anchor=(1.5,1.), fontsize=fts)
    plt.xlabel('Year', fontsize=fts)
    plt.ylabel('Cost reduction rate', fontsize=fts)
    plt.xticks(np.arange(2020, 2060, 10), fontsize=fts)
    plt.yticks(fontsize=fts)
    plt.savefig(open('%s/future-cost-reductoin.png'%resdir, 'wb'),  dpi=200, bbox_inches='tight')
    #plt.show()
    plt.close()

def get_LCOH_CST(CF, A_land, D_recv, H_recv, H_tower, n_helios, TES_capa, C_recv_ref, C_tower_fix, c_helio, c_site_cst, c_TES, c_land_cst, num_modules=1, OM_method='SL', savename=None):

    P_load=500.e3
    pm=Parameters()
    C_recv = C_recv_ref * ( H_recv * D_recv * np.pi / pm.A_recv_ref)**pm.f_recv_exp*num_modules
    C_tower = C_tower_fix * np.exp(pm.f_tower_exp * (H_tower - H_recv/2.+pm.H_helio/2.))*num_modules
    C_field = c_helio * n_helios * pm.A_helio*num_modules
    C_site = c_site_cst * pm.A_helio * n_helios*num_modules
    C_TES = c_TES * TES_capa
    C_land = c_land_cst * A_land*num_modules

    CAPEX = C_recv + C_tower + C_field + C_site + C_TES 

    C_direct= CAPEX*(1.+pm.r_conting_cst)
    C_indirect = pm.r_EPC_owner*C_direct + C_land 
    C_cap=C_direct + C_indirect

    if OM_method=='SAM':
        OM_fixed=pm.c_om_cst_fix * P_load_des
        c_OM_var = pm.c_om_cst_var
    elif OM_method=='SL':
        A_helios=n_helios * pm.A_helio
        OM_fixed=CST_SL_OM(A_helios)
        c_OM_var=0 

    LCOH, epy, OM_total=cal_LCOH(CF, P_load, C_cap, OM_fixed, c_OM_var, r_discount=pm.r_disc_real, t_life=pm.t_life, t_cons=pm.t_constr_cst)

    if savename!=None:
        summary=np.array([
                ['SM',rm, '-'],
                ['t_storage', sh, 'h'],
                ['LCOH', LCOH, 'USD/MWh_th'],
                ['CF', CF, '-'],
                ['H_recv', H_recv, 'm'],
                ['D_recv', D_recv, 'm'],
                ['H_tower', H_tower, 'm'],
                ['n_helios', n_helios, '-'],
                ['A_land', A_land, 'm2'],
                ['TES_capa',TES_capa/1e3, 'MWh'],
                ['EPY', epy, 'MWh'],
                ['C_cap_tot', C_cap/1e6, 'M.USD'],
                ['OM_tot', OM_total/1e6, 'M.USD'],
                ['C_recv', C_recv/1e6, 'M.USD'],
                ['C_tower', C_tower/1e6, 'M.USD'],
                ['C_field', C_field/1e6, 'M.USD'],
                ['C_site', C_site/1e6, 'M.USD'],
                ['C_TES', C_TES/1e6, 'M.USD'],
                ['C_land', C_land/1e6, 'M.USD'],
                ['C_equipment', CAPEX/1e6, 'M.USD'],
                ['C_direct', C_direct/1e6, 'M.USD'],
                ['C_indirect', C_indirect/1e6, 'USD'],
                ['r_real_discount', pm.r_disc_real, '-'],
                ['t_construction', pm.t_constr_cst, 'year'],
                ['t_life', pm.t_life, 'year'],
                ['num_modules', num_modules, '-'],
        ])
        np.savetxt('./summary_%s.csv'%(savename), summary, fmt='%s', delimiter=',')
    return LCOH


def get_LCOH_TES(CF, P_heater, pv_max, wind_max, TES_capa, c_pv_system, c_wind_system, c_heater, c_TES, savename=None):
    P_load=500.e3
    pm=Parameters()
    C_pv=c_pv_system*pv_max
    C_wind=c_wind_system*wind_max
    C_heater=P_heater*c_heater*1000.
    C_TES=TES_capa*c_TES

    CAPEX=C_pv+C_wind+C_heater+C_TES

    # heater replacement
    C_replace_heater=P_heater*pm.c_replace_heater*1000.
    n_replace_heater=int(pm.t_life/pm.t_life_heater)
    C_replc_heater_NPV=0
    for i in range(n_replace_heater):
        t=(i+1)*pm.t_life_heater+pm.t_constr_pv
        C_replc_heater_NPV+=C_replace_heater/(1+pm.r_disc_real)**t

    C_replace_NPV=C_replc_heater_NPV

    C_cap=CAPEX*(1+pm.r_conting_pv)+C_replace_NPV

    OM_fixed=pm.c_om_pv_fix*pv_max+pm.c_om_wind_fix*wind_max
    c_OM_var = 0.

    LCOH, epy, OM_total=cal_LCOH(CF,  P_load, C_cap, OM_fixed, c_OM_var, r_discount=pm.r_disc_real, t_life=pm.t_life, t_cons=pm.t_constr_pv)

    #print(LCOH)
    #print('TES CF=%.4f, LCOH=%.2f'%(CF, LCOH))	

    if savename!=None:
        summary=np.array([
                ['RM',rm, '-'],
                ['t_storage', sh, 'h'],
                ['LCOH', LCOH, 'USD/MWh_th'],
                ['CF', cf, '-'],
                ['r_pv', F_pv, '-'],
                ['pv_max', pv_max/1e3, 'MW'],
                ['wind_max', wind_max/1e3, 'MW'],
                ['P_heater',P_heater/1e3, 'MW'],
                ['TES_capa',TES_capa/1e3, 'MWh'],
                ['EPY', epy, 'MWh'],
                ['C_cap_tot', C_cap/1e6, 'M.USD'],
                ['OM_tot', OM_total/1e6, 'M.USD'],
                ['C_equipment', CAPEX/1e6, 'M.USD'],
                ['C_pv', C_pv/1e6, 'M.USD'],            
                ['C_wind', C_wind/1e6, 'M.USD'],  
                ['C_TES', C_TES/1e6, 'M.USD'],  
                ['C_heater', C_heater/1e6, 'M.USD'],  
                ['C_replace_heater_NPV', C_replc_heater_NPV/1e6, 'M.USD'],  
                ['C_replace_NPV', C_replace_NPV/1e6, 'M.USD'],  
                ['r_real_discount', pm.r_disc_real, '-'],
                ['t_construction', pm.t_constr_pv, 'year'],
                ['t_life', pm.t_life, 'year'],
                ['Location', location, '-']                   
        ])
        np.savetxt('./summary_%s.csv'%(savename), summary, fmt='%s', delimiter=',')
    return LCOH

def get_LCOH_BAT(CF, P_heater, pv_max, wind_max, bat_capa, bat_pmax, c_pv_system, c_wind_system, c_heater, c_bt_energy, c_bt_power, savename=None):
    P_load=500.e3
    pm=Parameters()
    C_pv=c_pv_system*pv_max
    C_wind=c_wind_system*wind_max
    C_heater=P_heater*c_heater
    C_bat=bat_capa*c_bt_energy+bat_pmax*c_bt_power

    CAPEX=C_pv+C_wind+C_heater+C_bat

    # heater replacement
    C_replace_heater=P_heater*pm.c_replace_heater
    n_replace_heater=int(pm.t_life/pm.t_life_heater)

    # battery replacement
    C_replace_bt=bat_capa*pm.c_replace_bt
    n_replace_bt=int(pm.t_life/pm.t_life_bt)

    C_replc_heater_NPV=0
    for i in range(n_replace_heater):
        t=(i+1)*pm.t_life_heater+pm.t_constr_pv
        C_replc_heater_NPV+=C_replace_heater/(1+pm.r_disc_real)**t

    C_replc_bt_NPV=0
    for i in range(n_replace_bt):
        t=(i+1)*pm.t_life_bt+pm.t_constr_pv
        C_replc_bt_NPV+=C_replace_bt/(1+pm.r_disc_real)**t

    C_replace_NPV=C_replc_heater_NPV+C_replc_bt_NPV

    C_cap=CAPEX*(1+pm.r_conting_pv)+C_replace_NPV

    OM_fixed=pm.c_om_pv_fix*pv_max+pm.c_om_wind_fix*wind_max
    c_OM_var = 0.

    LCOH, epy, OM_total=cal_LCOH(CF,  P_load, C_cap, OM_fixed, c_OM_var, r_discount=pm.r_disc_real, t_life=pm.t_life, t_cons=pm.t_constr_pv)
    #print('BAT CF=%.4f, LCOH=%.2f'%(CF, LCOH))	

    if savename!=None:
        np.savetxt('./summary_%s.csv'%savename, summary, fmt='%s', delimiter=',')
        summary=np.array([
                ['RM',rm, '-'],
                ['t_storage', sh, 'h'],
                ['LCOH', LCOH, 'USD/MWh_th'],
                ['CF', cf, '-'],
                ['F_pv', F_pv, '-'],
                ['pv_max', pv_max/1e3, 'MW'],
                ['wind_max', wind_max/1e3, 'MW'],
                ['P_heater',P_heater/1e3, 'MW'],
                ['bat_capa',bat_capa/1e3, 'MWh'],
                ['bat_pmax',bat_pmax/1e3, 'MW'],
                ['EPY', epy, 'MWh'],
                ['C_cap_tot', C_cap/1e6, 'M.USD'],
                ['OM_tot', OM_total/1e6, 'M.USD'],
                ['C_equipment', CAPEX/1e6, 'M.USD'],
                ['C_pv', C_pv/1e6, 'M.USD'],            
                ['C_wind', C_wind/1e6, 'M.USD'],  
                ['C_bat', C_bat/1e6, 'M.USD'],  
                ['C_heater', C_heater/1e6, 'M.USD'],  
                ['C_replace_heater_NPV', C_replc_heater_NPV/1e6, 'M.USD'],  
                ['C_replace_bt_NPV', C_replc_bt_NPV/1e6, 'M.USD'],  
                ['C_replace_NPV', C_replace_NPV/1e6, 'M.USD'],  
                ['r_real_discount', pm.r_disc_real, '-'],
                ['t_construction', pm.t_constr_pv, 'year'],
                ['t_life', pm.t_life, 'year'],
                ['Location', location, '-']                 
        ])

    return LCOH

def get_LCOH_PHES(CF, P_heater, pv_max, wind_max, PHES_capa, PHES_pmax, c_pv_system, c_wind_system, c_heater, c_PHES_energy, c_PHES_power, savename=None):
    P_load=500.e3
    pm=Parameters()
    C_pv=c_pv_system*pv_max
    C_wind=c_wind_system*wind_max
    C_heater=P_heater*c_heater
    C_PHES=PHES_capa*c_PHES_energy+PHES_pmax*c_PHES_power

    CAPEX=C_pv+C_wind+C_heater+C_PHES

    # heater replacement
    C_replace_heater=P_heater*pm.c_replace_heater
    n_replace_heater=int(pm.t_life/pm.t_life_heater)

    C_replc_heater_NPV=0
    for i in range(n_replace_heater):
        t=(i+1)*pm.t_life_heater+pm.t_constr_pv
        C_replc_heater_NPV+=C_replace_heater/(1+pm.r_disc_real)**t

    C_replace_NPV=C_replc_heater_NPV

    C_cap=CAPEX*(1+pm.r_conting_pv)+C_replace_NPV

    OM_fixed=pm.c_om_pv_fix*pv_max+pm.c_om_wind_fix*wind_max+pm.c_om_PHES_fix*PHES_pmax
    c_OM_var = 0.

    LCOH, epy, OM_total=cal_LCOH(CF,  P_load, C_cap, OM_fixed, c_OM_var, r_discount=pm.r_disc_real, t_life=pm.t_life, t_cons=pm.t_constr_pv)

    #print('PHES CF=%.4f, LCOH=%.2f'%(CF, LCOH))	

    if savename!=None:
        summary=np.array([
                ['RM',rm, '-'],
                ['t_storage', sh, 'h'],
                ['LCOH', LCOH, 'USD/MWh_th'],
                ['CF', cf, '-'],
                ['F_pv', F_pv, '-'],
                ['pv_max', pv_max/1e3, 'MW'],
                ['wind_max', wind_max/1e3, 'MW'],
                ['P_heater',P_heater/1e3, 'MW'],
                ['PHES_capa',PHES_capa/1e3, 'MWh'],
                ['PHES_pmax',PHES_pmax/1e3, 'MW'],
                ['EPY', epy, 'MWh'],
                ['C_cap_tot', C_cap/1e6, 'M.USD'],
                ['OM_tot', OM_total/1e6, 'M.USD'],
                ['C_equipment', CAPEX/1e6, 'M.USD'],
                ['C_pv', C_pv/1e6, 'M.USD'],            
                ['C_wind', C_wind/1e6, 'M.USD'],  
                ['C_PHES', C_PHES/1e6, 'M.USD'],  
                ['C_heater', C_heater/1e6, 'M.USD'],  
                ['C_replace_heater_NPV', C_replc_heater_NPV/1e6, 'M.USD'],  
                ['C_replace_NPV', C_replace_NPV/1e6, 'M.USD'],  
                ['r_real_discount', pm.r_disc_real, '-'],
                ['t_construction', pm.t_constr_pv, 'year'],
                ['t_life', pm.t_life, 'year'],
                ['Location', location, '-']                 
        ])
        np.savetxt('./summary_%s.csv'%savename, summary, fmt='%s', delimiter=',')

    
    return LCOH




