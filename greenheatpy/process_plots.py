import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib import cm
import matplotlib
import pandas as pd
from greenheatpy.get_green_h2 import get_data, get_best_location, get_storage_data
from greenheatpy.get_single_design import get_CST_design, get_CST_modular_design, get_TES_design, get_BAT_design,get_PHES_design
from greenheatpy.process_cost import future_cost

def plot_cf_curves(resdir, case, location, title, rm_max, sh_max, year=2020):
    """
    plot CF-SH-RM curves
    resdir   (str): the main directory of the results
    case     (str): 'CST', 'CST-modular', 'TES-HYBRID', 'TES-PV', 'TES-WIND', 'BAT-HYBRID', 'BAT-PV', 'BAT-WIND', 'PHES-HYBRID', 'PHES-PV', 'PHES-WIND'
    location (str): 'Pilbara', 'Burnie', 'Gladstone', 'Pinjarra', 'Upper Spencer Gulf', 'Kerang'
    title    (str): name of the case
    rm_max (float): the maximal renewable multiple
    sh_max (float): the maximal storage hour
    year     (int): year of the cost basis
    

    """

    COL=[ 'grey', 'cornflowerblue', 'black']
    fts=14
    norm = matplotlib.colors.Normalize(vmin=1, vmax=9)
    c_map=cm.jet
    scalar_map=cm.ScalarMappable(cmap=c_map, norm=norm)

    t_storage=np.r_[1e-6,2,4,6,8,10,12,14,17,20,25,40,60]
    multiple=np.append(np.arange(1, 5, 0.5), np.arange(5, 11, 2))
    #if 'HYBRID' in case:
    #    if year==2020:
    #        casedir='%s/%s/%s'%(resdir, case, location)
    #    else:
    #        casedir='%s/%s/%s-%s'%(resdir, case, location, year)
    #else:
    casedir='%s/%s/%s'%(resdir, case, location)

    print(case, location)
    results=np.array([])
    if rm_max>9 or sh_max>60:            
        multiple=np.append(multiple, np.arange(11, rm_max+3, 3))
        t_storage=np.append(t_storage, np.linspace(120, sh_max, 3))

    m=int(len(multiple))
    n=int(len(t_storage))

    for rm in multiple:
        for sh in t_storage:
            res_fn=casedir+'/summary_%.3f_%.2f.csv'%(rm, sh)
            if os.path.exists(res_fn):
                data=np.loadtxt(res_fn, dtype=str, delimiter=',')
                if len(data[:,1])==29:
                    data=np.vstack((data[:4], np.array(['num_modules', 1, '-']).reshape(1, 3), data[4:]))                       
            else:
                data=np.zeros(np.shape(data))
            results=np.append(results, data[:,1])

    nd=int(len(data))

    results=results.reshape(int(len(results)/nd), nd)
    RM=results[:,0].reshape(m,n).astype(float)
    SH=results[:,1].reshape(m,n).astype(float)
    LCOH=results[:,2].reshape(m,n).astype(float)
    CF=results[:,3].reshape(m,n).astype(float)
    savedata=np.vstack((t_storage, CF))
    savedata=np.hstack((np.append(0, multiple).reshape(m+1, 1), savedata))
    np.savetxt('%s/post/%s/%s-%s-data_CF.csv'%(resdir, year, case, location), savedata, fmt='%.6f', delimiter=',')

    savedata=np.vstack((t_storage, LCOH))
    savedata=np.hstack((np.append(0, multiple).reshape(m+1, 1), savedata))
    np.savetxt('%s/post/%s/%s-%s-data_LCOH.csv'%(resdir, year, case, location), savedata, fmt='%.6f', delimiter=',')

    if 'HYBRID' in case:

        F_pv=results[:,4].reshape(m,n).astype(float)
        savedata=np.vstack((t_storage, F_pv))
        savedata=np.hstack((np.append(0, multiple).reshape(m+1, 1), savedata))
        np.savetxt('%s/post/%s/%s-%s-data_F_pv.csv'%(resdir, year, case, location), savedata, fmt='%.6f', delimiter=',')

    elif 'CST' in case:
        Hrecv=results[:,5].reshape(m,n).astype(float)
        Drecv=results[:,6].reshape(m,n).astype(float)
        Htower=results[:,7].reshape(m,n).astype(float)
        Nhelio=results[:,8].reshape(m,n).astype(float)
        Aland=results[:,9].reshape(m,n).astype(float)
        #print(Aland)
        Rland=np.sqrt(Aland/np.pi)
        #print(Rland)   

        savedata=np.append(multiple, Htower[:,0]).reshape(2, m)
        savedata=np.vstack((np.array(['SM', 'Tower height (m)']).reshape(1,2), savedata.T))
        np.savetxt('%s/post/%s/%s-%s-data_Htower.csv'%(resdir, year, case, location), savedata, fmt='%s', delimiter=',')

        savedata=np.append(multiple, Hrecv[:,0]).reshape(2, m)
        savedata=np.vstack((np.array(['SM', 'Receiver height (m)']).reshape(1,2), savedata.T))    
        np.savetxt('%s/post/%s/%s-%s-data_Hrecv.csv'%(resdir, year, case, location), savedata, fmt='%s', delimiter=',')

        savedata=np.append(multiple, Drecv[:,0]).reshape(2, m)
        savedata=np.vstack((np.array(['SM', 'Receiver diameter (m)']).reshape(1,2), savedata.T))  
        np.savetxt('%s/post/%s/%s-%s-data_Drecv.csv'%(resdir, year, case, location), savedata, fmt='%s', delimiter=',')

        savedata=np.append(multiple, Nhelio[:,0]).reshape(2, m)
        savedata=np.vstack((np.array(['SM', 'Number of heliostats']).reshape(1,2), savedata.T))    
        np.savetxt('%s/post/%s/%s-%s-data_Nhelio.csv'%(resdir, year, case, location), savedata, fmt='%s', delimiter=',')

        savedata=np.append(multiple, Aland[:,0]).reshape(2, m)
        savedata=np.vstack((np.array(['SM', 'Land area (m2)']).reshape(1,2), savedata.T))   
        np.savetxt('%s/post/%s/%s-%s-data_Aland.csv'%(resdir, year, case, location), savedata, fmt='%s', delimiter=',')

    if 'CST-modular' in case:
        num_modules=results[:,4].reshape(m,n).astype(float)
        savedata=np.vstack((t_storage, num_modules))
        savedata=np.hstack((np.append(0, multiple).reshape(m+1, 1), savedata))
        np.savetxt('%s/post/%s/%s-%s-data_num_modules.csv'%(resdir, year, case, location), savedata, fmt='%s', delimiter=',')

    if 'BAT' in case:
        P_bat=results[:,9].reshape(m,n).astype(float) 

        savedata=np.vstack((t_storage, P_bat))
        savedata=np.hstack((np.append(0, multiple).reshape(m+1, 1), savedata))
        np.savetxt('%s/post/%s/%s-%s-data_P_bat.csv'%(resdir, year, case, location), savedata, fmt='%.2f', delimiter=',')  

    elif 'PHES' in case:
        P_PHES=results[:,9].reshape(m,n).astype(float) 

        savedata=np.vstack((t_storage, P_PHES))
        savedata=np.hstack((np.append(0, multiple).reshape(m+1, 1), savedata))
        np.savetxt('%s/post/%s/%s-%s-data_P_PHES.csv'%(resdir, year, case, location), savedata, fmt='%.2f', delimiter=',')  

    elif 'TES' in case:
        P_heater=results[:,7].reshape(m,n).astype(float)  

        savedata=np.vstack((t_storage, P_heater))
        savedata=np.hstack((np.append(0, multiple).reshape(m+1, 1), savedata))
        np.savetxt('%s/post/%s/%s-%s-data_P_heater.csv'%(resdir, year, case, location), savedata, fmt='%.2f', delimiter=',')            

    for i in range(m):
        if RM[i,0]>9:
            col=i-11
            plt.plot(SH[i], CF[i]*100., label='RM = %s'%RM[i,0], c=COL[col])
        else:

            plt.plot(SH[i], CF[i]*100., label='RM = %s'%RM[i,0], c=scalar_map.to_rgba(RM[i,0]))
    plt.ylim([0,100])
    plt.xlabel('SH (h)', fontsize=fts)
    plt.ylabel('CF (%)', fontsize=fts)
    plt.title(title, fontsize=fts)
    plt.legend(loc=1, bbox_to_anchor=(1.4,1.), fontsize=fts)
    plt.xticks(fontsize=fts)
    plt.yticks(fontsize=fts)
    plt.savefig(open('%s/post/%s/%s-%s-CF.png'%(resdir, year, case, location), 'wb'),  bbox_inches='tight')
    #plt.show()
    plt.close()    

    for i in range(m):
        if RM[i,0]>9:
            col=i-11
            plt.plot(SH[i], LCOH[i], label='RM = %s'%RM[i,0], c=COL[col])
        else:
            plt.plot(SH[i], LCOH[i], label='RM = %s'%RM[i,0], c=scalar_map.to_rgba(RM[i,0]))
    if 'BAT' in case:
        plt.ylim([30,600])
    else:
        plt.ylim([30,300])
    plt.xlabel('SH (h)', fontsize=fts)
    plt.ylabel('LCOH (USD/MWh$_\mathrm{th}$)', fontsize=fts)
    plt.title(title, fontsize=fts)
    #plt.legend(loc=1, bbox_to_anchor=(1.4,1.), fontsize=fts)
    plt.xticks(fontsize=fts)
    plt.yticks(fontsize=fts)
    plt.savefig(open('%s/post/%s/%s-%s-CF-LCOH.png'%(resdir, year, case, location), 'wb'),  bbox_inches='tight')
    #plt.show()
    plt.close()    


    if 'HYBRID' in case:
        for i in range(m):
            if RM[i,0]>9:
                col=i-11
                plt.plot(SH[i], F_pv[i], label='RM = %s'%RM[i,0], c=COL[col])
            else:
                plt.plot(SH[i], F_pv[i], label='RM = %s'%RM[i,0], c=scalar_map.to_rgba(RM[i,0]))
        plt.ylim([0,1.1])
        plt.xlabel('SH (h)', fontsize=fts)
        plt.ylabel('PV fraction', fontsize=fts)
        #plt.title(title, fontsize=fts)
        plt.legend(loc=1, bbox_to_anchor=(1.4,1.), fontsize=fts)
        plt.xticks(fontsize=fts)
        plt.yticks(fontsize=fts)
        plt.savefig(open('%s/post/%s/%s-%s-CF-Fpv.png'%(resdir, year, case, location), 'wb'),  bbox_inches='tight')
        #plt.show()
        plt.close()   

    elif 'CST' in case: 

        plt.plot(RM[:,0], Hrecv[:,0],  c=scalar_map.to_rgba(RM[i,0]))
        #plt.ylim([0,1.1])
        plt.xlabel('RM', fontsize=fts)
        plt.ylabel('Receiver height (m)', fontsize=fts)
        #plt.title(title, fontsize=fts)
        plt.xticks(fontsize=fts)
        plt.yticks(fontsize=fts)
        plt.savefig(open('%s/post/%s/%s-%s-CF-Hrecv.png'%(resdir, year, case, location), 'wb'),  bbox_inches='tight')
        #plt.show()
        plt.close()   

        
        plt.plot(RM[:,0], Drecv[:,0], c=scalar_map.to_rgba(RM[i,0]))
        #plt.ylim([0,1.1])
        plt.xlabel('RM', fontsize=fts)
        plt.ylabel('Receiver diameter (m)', fontsize=fts)
        #plt.title(title, fontsize=fts)
        plt.xticks(fontsize=fts)
        plt.yticks(fontsize=fts)
        plt.savefig(open('%s/post/%s/%s-%s-CF-Drecv.png'%(resdir, year, case, location), 'wb'),  bbox_inches='tight')
        #plt.show()
        plt.close()   


        plt.plot(RM[:,0], Htower[:,0],  c=scalar_map.to_rgba(RM[i,0]))
        #plt.ylim([0,1.1])
        plt.xlabel('RM', fontsize=fts)
        plt.ylabel('Tower height (m)', fontsize=fts)
        #plt.title(title, fontsize=fts)
        plt.xticks(fontsize=fts)
        plt.yticks(fontsize=fts)
        plt.savefig(open('%s/post/%s/%s-%s-CF-Htower.png'%(resdir, year, case, location), 'wb'),  bbox_inches='tight')
        #plt.show()
        plt.close()   


        plt.plot(RM[:,0], Nhelio[:,0],  c=scalar_map.to_rgba(RM[i,0]))
        #plt.ylim([0,1.1])
        plt.xlabel('RM', fontsize=fts)
        plt.ylabel('Number of heliostats', fontsize=fts)
        #plt.title(title, fontsize=fts)
        plt.xticks(fontsize=fts)
        plt.yticks(fontsize=fts)
        plt.savefig(open('%s/post/%s/%s-%s-CF-Nhelio.png'%(resdir, year, case, location), 'wb'),  bbox_inches='tight')
        #plt.show()
        plt.close()   


        plt.plot(RM[:,0], Rland[:,0],  c=scalar_map.to_rgba(RM[i,0]))
        #plt.ylim([0,1.1])
        plt.xlabel('RM', fontsize=fts)
        plt.ylabel('Tower to the most distant heliost (m)', fontsize=fts)
        #plt.title(title, fontsize=fts)
        plt.xticks(fontsize=fts)
        plt.yticks(fontsize=fts)
        plt.savefig(open('%s/post/%s/%s-%s-CF-Rland.png'%(resdir, year, case, location), 'wb'),  bbox_inches='tight')
        #plt.show()
        plt.close()   

    elif 'CST-modular' in case: 
        plt.plot(RM[:,0], num_modules[:,0],  c=scalar_map.to_rgba(RM[i,0]))
        #plt.ylim([0,1.1])
        plt.xlabel('RM', fontsize=fts)
        plt.ylabel('Number of modules', fontsize=fts)
        #plt.title(title, fontsize=fts)
        plt.xticks(fontsize=fts)
        plt.yticks(fontsize=fts)
        plt.savefig(open('%s/post/%s/%s-%s-CF-num_modules.png'%(resdir, year, case, location), 'wb'),  bbox_inches='tight')
        #plt.show()
        plt.close() 

    if 'BAT' in case:
        for i in range(m):
            plt.plot(SH[i], P_bat[i], label='RM = %s'%RM[i,0], c=scalar_map.to_rgba(RM[i,0]))
        #plt.ylim([0,1.1])
        plt.xlabel('SH (h)', fontsize=fts)
        plt.ylabel('Battery power (MW)', fontsize=fts)
        #plt.title(title, fontsize=fts)
        plt.legend(loc=1, bbox_to_anchor=(1.4,1.), fontsize=fts)
        plt.xticks(fontsize=fts)
        plt.yticks(fontsize=fts)
        plt.savefig(open('%s/post/%s/%s-%s-CF-P_bat.png'%(resdir, year, case, location), 'wb'),  bbox_inches='tight')
        #plt.show()
        plt.close()   

    if 'PHES' in case:
        for i in range(m):
            plt.plot(SH[i], P_PHES[i], label='RM = %s'%RM[i,0], c=scalar_map.to_rgba(RM[i,0]))
        #plt.ylim([0,1.1])
        plt.xlabel('SH (h)', fontsize=fts)
        plt.ylabel('Power of PHES (MW)', fontsize=fts)
        #plt.title(title, fontsize=fts)
        plt.legend(loc=1, bbox_to_anchor=(1.4,1.), fontsize=fts)
        plt.xticks(fontsize=fts)
        plt.yticks(fontsize=fts)
        plt.savefig(open('%s/post/%s/%s-%s-CF-P_PHES.png'%(resdir, year, case, location), 'wb'),  bbox_inches='tight')
        #plt.show()
        plt.close()  


    if 'TES' in case:
        for i in range(m):
            plt.plot(SH[i], P_heater[i], label='RM = %s'%RM[i,0], c=scalar_map.to_rgba(RM[i,0]))
        #plt.ylim([0,1.1])
        plt.xlabel('SH (h)', fontsize=fts)
        plt.ylabel('Heater power (MW)', fontsize=fts)
        #plt.title(title, fontsize=fts)
        plt.legend(loc=1, bbox_to_anchor=(1.4,1.), fontsize=fts)
        plt.xticks(fontsize=fts)
        plt.yticks(fontsize=fts)
        plt.savefig(open('%s/post/%s/%s-%s-CF-P_heater.png'%(resdir, year, case, location), 'wb'),  bbox_inches='tight')
        #plt.show()
        plt.close()   


def fmt(x):
    s = f"{x:.1f}"
    if s.endswith("0"):
        s = f"{x:.0f}"
    return rf"{s} \%" if plt.rcParams["text.usetex"] else f"{s} %"



def get_cf_lcoh_optimal(location, case, resdir, year=2020, plot=True):

 
    data=np.loadtxt('%s/post/%s/%s-%s-data_LCOH.csv'%(resdir, year, case, location), delimiter=',')
    LCOH=data[1:, 1:]
    data=np.loadtxt('%s/post/%s/%s-%s-data_CF.csv'%(resdir, year, case, location), delimiter=',')
    CF=data[1:, 1:]  
      
    multiple=data[1:, 0]
    t_storage=data[0,1:]
    SH, RM=np.meshgrid(t_storage, multiple)
    
    fts=18
    fig,ax=plt.subplots()
    levels=np.r_[40, 50, 60, 70, 80, 90,  95, 99]
    CS = ax.contour(t_storage, multiple, CF*100., levels, cmap='jet')


    results=np.array([])
    manual_locations=[]
    for a in range(len(levels)):
        L0=9999
        sh0=0
        rm0=0
        for b in range(len(CS.collections[a].get_paths())):
            p=CS.collections[a].get_paths()[b]
            v=p.vertices
            x=v[:,0]
            y=v[:,1]

            #if a==0:
            #manual_locations.append((x[1], y[1]))
            #else:
            #    manual_locations.append((x[1], y[1]))
            for i in range(len(x)):
                sh=x[i]
                rm=y[i]
                
                idx=np.argmin(abs(multiple-rm))
                if multiple[idx]!=1:
                    row=idx-1
                else:
                    row=idx

                idx=np.argmin(abs(t_storage-sh))
                if t_storage[idx]>0:
                    col=idx-1
                else:
                    col=idx

                x_1=t_storage[col]
                x_2=t_storage[col+1]
                y_1=multiple[row]
                y_2=multiple[row+1]
                Q_11=LCOH[row,col]
                Q_12=LCOH[row+1,col]
                Q_21=LCOH[row,col+1]
                Q_22=LCOH[row+1,col+1]
                lcoh=1/((x_2-x_1)*(y_2-y_1))*(Q_11*(x_2-sh)*(y_2-rm)+Q_21*(sh-x_1)*(y_2-rm)+Q_12*(x_2-sh)*(rm-y_1)+Q_22*(sh-x_1)*(rm-y_1))                
                if lcoh<=L0:
                    L0=lcoh
                    sh0=sh
                    rm0=rm
        results=np.append(results, (levels[a], sh0, rm0, L0)) 
        plt.plot([sh0], [rm0], 'r*')
        
    results=results.reshape(int(len(results)/4), 4)   
    title=np.array(['CF','SH','RM','LCOH']).reshape(1,4)
    summary=np.vstack((title, results))
    np.savetxt('%s/post/%s/%s-%s-LCOH-CF.csv'%(resdir, year, case, location), summary, fmt='%s', delimiter=',')
          
    if plot:
        #cmap_reversed = matplotlib.cm.get_cmap('bone_r')
        llabels=['CF=%.0f%%'%l for l in levels]
        fmt0={}
        for l,s in zip(CS.levels, llabels):
            fmt0[l]=s
        plt.clabel(CS, inline=True, manual=manual_locations, fmt=fmt0, fontsize=fts)
        #plt.pcolormesh(t_storage, multiple, LCOH, cmap='binary')
        #plt.imshow(LCOH, cmap='binary', extent=[np.min(t_storage),np.max(t_storage),np.max(multiple),np.min(multiple)], interpolation='catrom', aspect='auto')
        cbr=plt.contourf(SH, RM, LCOH, 7, cmap=plt.cm.bone_r, origin='lower')
        cbar=plt.colorbar(cbr)
        cbar.ax.tick_params(labelsize=fts)
        cbar.set_label('LCOH (USD/MWh$_\mathrm{th}$)', fontsize=fts)
        plt.xlabel('Storage hour', fontsize=fts)
        plt.ylabel('Renewable multiple', fontsize=fts)
        plt.xticks(fontsize=fts)
        plt.yticks(fontsize=fts)
        plt.xlim([0,np.max(t_storage)])
        plt.ylim([1,np.max(multiple)])
        plt.savefig(open('%s/post/%s/%s-%s-RM-SH-LCOH.png'%(resdir, year, case, location), 'wb'),  bbox_inches='tight')
        #plt.show()
        plt.close()


        CS = plt.contour(t_storage, multiple, CF*100., levels, cmap='jet')
        plt.clabel(CS, inline=True, fmt=fmt, fontsize=fts)
        #plt.pcolormesh(t_storage, multiple, CF*100., cmap='binary')
        #plt.imshow(CF*100., cmap='binary', extent=[np.min(t_storage),np.max(t_storage),np.max(multiple),np.min(multiple)], interpolation='catrom', aspect='auto')
        cbr=plt.contourf(SH, RM, CF*100., 7, cmap=plt.cm.bone, origin='lower')
        cbar=plt.colorbar(cbr)
        cbar.ax.tick_params(labelsize=fts)
        cbar.set_label('Capacity factor (%)', fontsize=fts)
        plt.xlabel('Storage hour', fontsize=fts)
        plt.ylabel('Renewable multiple', fontsize=fts)
        plt.xticks(fontsize=fts)
        plt.yticks(fontsize=fts)
        plt.xlim([0,np.max(t_storage)])
        plt.ylim([1,np.max(multiple)])
        plt.savefig(open('%s/post/%s/%s-%s-RM-SH-CF.png'%(resdir, year, case, location), 'wb'),  bbox_inches='tight')
        #plt.show()
        plt.close()
        
        idx=(results[:,-1]<9999) # (results[:,0]!=50)*(results[:,-1]<9999) 
        plt.plot(results[:,0][idx], results[:,-1][idx], 'r')
        #plt.plot(results[:,0], results[:,-1])
        plt.xlabel('Capacity factor (%)', fontsize=fts)
        plt.ylabel('LCOH (USD/MWh$_\mathrm{th}$)', fontsize=fts)
        plt.xticks(fontsize=fts)
        plt.yticks(fontsize=fts)
        plt.savefig(open('%s/post/%s/%s-%s-LCOH-CF.png'%(resdir, year, case, location), 'wb'),  bbox_inches='tight')
        #plt.show()
        plt.close()
    else:
        plt.close()


        

def get_cf_lcoh_optimal_hydrogen(year=2020):

    CF, LCOH, LCOH2, locations, PV, WIND, EL, H2ST =get_data(year=year)  
    best=get_best_location(year=year)
    regions=[ 'Burnie', 'Pinjarra',  'Pilbara', 'Upper Spencer Gulf',  'Gladstone']
    LCOH_best={}
    PV_best={}
    WIND_best={}
    EL_best={}
    H2ST_best={}

    LCOH_storage={}
    PV_storage={}
    WIND_storage={}
    EL_storage={}
    H2ST_storage={}
    for region in regions:
        bid=best[region]
        for i in range(len(locations)):
            location=locations[i]
            if location=='%s %s'%(region, bid):
                lcoh=LCOH[i]
                LCOH_best[region]=lcoh
                PV_best[region]=PV[i]
                WIND_best[region]=WIND[i]
                EL_best[region]=EL[i]
                H2ST_best[region]=H2ST[i]
                if 'Pinjarra' in location:
                    location='Pinjara '+location[-1]
                cf, lcoh, lcoh2, pv, wind, electrolyser, h2_storage =get_storage_data(year=year, location=location, cost=1000)
                LCOH_storage[region]=lcoh
                PV_storage[region]=pv
                WIND_storage[region]=wind
                EL_storage[region]=electrolyser
                H2ST_storage[region]=h2_storage
    return LCOH_best, CF, LCOH_storage, PV_best, WIND_best, EL_best, H2ST_best, PV_storage, WIND_storage, EL_storage, H2ST_storage




def plot_cf_lcoh_comparison(location, resdir, year=2020):

    cases=['CST', 'CST-modular', 'TES-PV','BAT-PV', 'PHES-PV', 'TES-WIND','BAT-WIND','PHES-WIND', 'TES-HYBRID','BAT-HYBRID','PHES-HYBRID', 'H2', 'H2-storage']
    linestyles=['-', '-',  '-', '--', '-.',   '-', '--', '-.', 'o-', '^-',  's-', ':', ':'] 

    #summary=np.array([])	
    norm = matplotlib.colors.Normalize(vmin=1, vmax=20)
    c_map=cm.tab20c
    scalar_map=cm.ScalarMappable(cmap=c_map, norm=norm)
    colors=[ scalar_map.to_rgba(5), scalar_map.to_rgba(6), scalar_map.to_rgba(9), scalar_map.to_rgba(9), scalar_map.to_rgba(9), scalar_map.to_rgba(1), scalar_map.to_rgba(1), scalar_map.to_rgba(1), scalar_map.to_rgba(13), scalar_map.to_rgba(13), scalar_map.to_rgba(13), 'crimson', 'fuchsia'] #
    alphas=[1,1,1,1,1,1,1,1,0.5,0.5,0.5,1,1]
    plot_lines = []
    fts=14
    fig, ax = plt.subplots()
    for i in range(len(cases)):
        case=cases[i]

        if 'H2' in case: 
            LCOH_h2, CF, LCOH_storage, PV_best, WIND_best, EL_best, H2ST_best, PV_storage, WIND_storage, EL_storage, H2ST_storage=get_cf_lcoh_optimal_hydrogen(year)
            if 'storage' in case:
                lcoh=LCOH_storage[location]
                sh=H2ST_storage[location]
                rm=PV_storage[location]+WIND_storage[location]
            else:
                lcoh=LCOH_h2[location]
                sh=H2ST_best[location]
                rm=PV_best[location]+WIND_best[location]
            cf=CF*100.
        else:
            try:
                fn='%s/post/%s/%s-%s-LCOH-CF.csv'%(resdir, year, case, location)
                data=np.loadtxt(fn, delimiter=',', skiprows=1)
            except:
                if location=='Pinjarra':
                    fn='%s/post/%s/%s-%s-LCOH-CF.csv'%(resdir, year, case, 'Pinjara')
                    data=np.loadtxt(fn, delimiter=',', skiprows=1)
            cf=data[:,0]
            sh=data[:,1]
            rm=data[:, 2]
            lcoh=data[:,3]

        idx=(lcoh<9990)
        l,=ax.plot(cf[idx], lcoh[idx], linestyles[i], c=colors[i], alpha=alphas[i])
        plot_lines.append(l)
    #    data= np.append(cf, (sh, rm, lcoh))
    #    title=np.array([case, 'SH' , 'RM', 'LCOH'])
    #    data=data.reshape(4, len(cf))
    #    data=data.T
    #    title=title.reshape(1, 4)
    #    data=np.vstack((title, data))
    #    summary=np.append(summary, data)

    #summary=summary.reshape(int(len(summary)/4), 4)
    #np.savetxt('%s/post/summary-LCOH-CF-%s-%s.csv'%(resdir, location, year), summary, fmt='%s', delimiter=',')

    ax2 = ax.twinx()
    ll=["TES", "Batt", "PHES"]
    ls=['-', '--', '-.']
    for ss, sty in enumerate(ls):
        ax2.plot(np.NaN, np.NaN, ls=ls[ss],
                 label=ll[ss], c='black')
    ax2.get_yaxis().set_visible(False)

    legend_labels=['CST (single-tower)', 'CST (multi-tower)', 'PV+TES', 'PV+Batt', 'PV+PHES','Wind+TES', 'Wind+Batt', 'Wind+PHES', 'PV+Wind+TES',  'PV+Wind+Batt',  'PV+Wind+PHES', 'H$_2$+Lined rock cavern',"H$_2$+Aboveground storage" ] #LRC is 40--115 USD/kg, aboveground is 1000 USD/kg
    #legend1 = plt.legend([plot_lines[0],plot_lines[1],plot_lines[2],plot_lines[3]], ["CST", "CST-md", "PV", "Wind"], loc=1, bbox_to_anchor=(1.33,1.), fontsize=fts)
    #ax.legend([plot_lines[4],plot_lines[7], plot_lines[10], plot_lines[11], plot_lines[12]] , ["PV+Wind+TES", "PV+Wind+Batt", "PV+Wind+PHES", "H$_2$", "H$_2$ (high c$_\mathrm{H₂,storage}$)"], loc=1, bbox_to_anchor=(1.54,0.66), fontsize=fts)
    #plt.gca().add_artist(legend1)

    #ax2.legend(loc=1, bbox_to_anchor=(1.58,1), fontsize=fts)
    ax.legend(plot_lines, legend_labels, bbox_to_anchor=(1.01,1.03), fontsize=fts)
    #plt.legend()
    #plt.xlim([0.15,1])
    ax.set_ylabel('LCOH (USD/MWh$_\mathrm{th}$)', fontsize=fts)
    ax.set_xlabel('Capacity factor (%)', fontsize=fts)
    ax.xaxis.set_tick_params(labelsize=fts)
    ax.yaxis.set_tick_params(labelsize=fts)
    ax.set_ylim([0, 300])
    #plt.title(case)
    if 'Pinjar' in location:
        location='Peel'
    plt.title(location+' %s'%year)
    plt.savefig(open('%s/post/%s/Comparison-LCOH-CF-%s.png'%(resdir, year, location),'wb'), bbox_inches='tight', dpi=200)
    #plt.show()
    plt.close()


def plot_breakdown_bars(location, resdir, P_load=500e3, year=2020, OM_method='SL', fast=True):

    cases=['CST', 'CST-modular','TES-PV', 'TES-WIND', 'TES-HYBRID',  'BAT-PV', 'BAT-WIND', 'BAT-HYBRID','PHES-PV','PHES-WIND','PHES-HYBRID']
    #LABELS=['CST+TES', 'PV+TES',  'WT+TES', 'PV+WT+TES',  'PV+BAT', 'WT+BAT', 'PV+WT+BAT', 'PV+PHES', 'WT+PHES','PV+WT+PHES']
    LABELS2=[50,80,'90\nCST+TES',95,99,50,80,'90\nCST-m+TES',95,99, 50,80,'90\nPV+TES',95,99, 50,80,'90\nWind+TES',95,99, 50,80,'90\nHybrid+TES',95,99, 50,80,'90\nPV+Batt',95,99,50,80,'90\nWind+Batt',95,99,50,80,'90\nHybrid+Batt',95,99,50,80,'90\nPV+PHES',95,99,50,80,'90\nWind+PHES',95,99,50,80,'90\nHYBRID+PHES',95,99]
    print(len(LABELS2))


    CF0=np.r_[60., 70., 80., 90., 95., 99.]

    width = 0.5 
    fig, ax = plt.subplots(figsize=(12,6))
    #ax2=ax.twinx()

    norm = matplotlib.colors.Normalize(vmin=1, vmax=20)
    c_map1=cm.tab20c
    scalar_map1=cm.ScalarMappable(cmap=c_map1, norm=norm)
    c_map=cm.tab20b
    scalar_map=cm.ScalarMappable(cmap=c_map, norm=norm)

    label_pos=np.array([])
    fts=14
    for i in range(len(cases)):
        C_RECV=np.array([])
        C_TOWER=np.array([]) 
        C_FIELD=np.array([]) 
        C_PV=np.array([])
        C_WIND=np.array([])
        CTES=np.array([]) 
        CBAT=np.array([]) 
        CBAT_replace=np.array([])
        CPHES=np.array([]) 
        C_HEATER=np.array([]) 
        C_HEATER_replace=np.array([])
        C_OTHERS=np.array([]) 
        C_OM=np.array([])  
        CFs=np.array([])  

        case=cases[i]
        fn='%s/post/%s/%s-%s-LCOH-CF.csv'%(resdir, year, case, location)
        data=np.loadtxt(fn, delimiter=',', skiprows=1)
        cfs=data[:,0]
        SHs=data[:,1]
        RMs=data[:,2]
        LCOHs=data[:,3] 
        if 'CST' in case:
            des_details=np.array(['CF', 'C_field', 'C_recv', 'C_tower', 'C_site', 'C_TES',' C_om'])
        for j in range(len(CF0)):
            cf0=CF0[j]
            idx=abs(cf0-cfs)<0.01

            if LCOHs[idx]<999:
                sh=SHs[idx][0]
                rm=RMs[idx][0]
                lcoh=LCOHs[idx][0]
                cf=cfs[idx][0]
                savename='design_%s_%s_CF=%.0f%%'%(location, case, cf0)
 
                if case=='CST':
                    lcoh_1, cf_1=get_CST_design(rm, sh, location, case, resdir, P_load=P_load, savename=savename, OM_method=OM_method, fast=fast)
                if case=='CST-modular':
                    lcoh_1, cf_1=get_CST_modular_design(rm, sh, location, case, resdir, P_load=P_load, savename=savename)
                elif case=='TES-PV':
                    lcoh_1, cf_1=get_TES_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=1)
                elif case=='TES-WIND':
                    lcoh_1, cf_1=get_TES_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=0)
                elif case=='TES-HYBRID':
                    lcoh_1, cf_1=get_TES_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=None)
                elif case=='BAT-PV':
                    lcoh_1, cf_1=get_BAT_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=1)
                elif case=='BAT-WIND':
                    lcoh_1, cf_1=get_BAT_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=0)
                elif case=='BAT-HYBRID':
                    lcoh_1, cf_1=get_BAT_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=None)
                elif case=='PHES-PV':
                    lcoh_1, cf_1=get_PHES_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=1)
                elif case=='PHES-WIND':
                    lcoh_1, cf_1=get_PHES_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=0)
                elif case=='PHES-HYBRID':
                    lcoh_1, cf_1=get_PHES_design(rm, sh, location, case, resdir, P_load=P_load, savename=savename, F_pv=None)

                print(case, "CF=%s%%"%cf0, "%.1f%%"%(cf_1*100.), 'LCOH diff: %.1f%%'%((lcoh_1-lcoh)/lcoh*100.))    

                fn_des=resdir+'/post/%s/summary_design_%s_%s_CF=%.0f%%.csv'%(year, location, case, cf0)
                res=np.loadtxt(fn_des, delimiter=',', dtype=str)
                cf=res[3,1].astype(float)

                if 'TES' in case:
                    epy=res[9,1].astype(float)
                    r=res[19,1].astype(float)
                    f=r*(r+1)**25/((r+1)**25-1)
                    C_cap_tot=res[10,1].astype(float)

                    C_recv=0
                    C_tower=0
                    C_field=0
                    C_pv=res[13,1].astype(float)*f/epy*1e6
                    C_wind=res[14,1].astype(float)*f/epy*1e6
                    C_TES=res[15,1].astype(float)*f/epy*1e6
                    C_BAT=0
                    C_BAT_replace=0
                    C_PHES=0
                    C_heater=res[16,1].astype(float)*f/epy*1e6
                    C_heater_replace= res[17, 1].astype(float)*f/epy*1e6   
                    C_others=C_cap_tot*f/epy*1e6-C_heater_replace-C_pv-C_TES-C_heater-C_wind
                    C_om=res[11,1].astype(float)/epy*1e6

                    #lcoh1=((C_pv+C_wind+C_TES+C_heater+C_heater_replace+C_others)*f+C_om)/epy*1.e6   
              
                elif 'BAT' in case:
                    epy=res[10,1].astype(float)
                    r=res[21,1].astype(float)
                    f=r*(r+1)**25/((r+1)**25-1)
                    C_cap_tot=res[11,1].astype(float)

                    C_recv=0.
                    C_tower=0
                    C_field=0
                    C_pv=res[14,1].astype(float)*f/epy*1e6
                    C_wind=res[15,1].astype(float)*f/epy*1e6
                    C_TES=0
                    C_BAT=res[16,1].astype(float)*f/epy*1e6
                    C_BAT_replace=res[19, 1].astype(float)*f/epy*1e6 
                    C_PHES=0
                    C_heater=res[17,1].astype(float)*f/epy*1e6
                    C_heater_replace= res[18, 1].astype(float) *f/epy*1e6     
                    C_others=C_cap_tot*f/epy*1e6-C_heater_replace-C_pv-C_BAT-C_heater-C_wind-C_BAT_replace
                    C_om=res[12,1].astype(float)/epy*1e6

                    #lcoh1=((C_pv+C_wind+C_BAT+C_BAT_replace+C_heater+C_heater_replace+C_others)*f+C_om)/epy*1.e6   

                elif 'PHES' in case:
                    epy=res[10,1].astype(float)
                    r=res[20,1].astype(float)
                    f=r*(r+1)**25/((r+1)**25-1)
                    C_cap_tot=res[11,1].astype(float)

                    C_recv=0.
                    C_tower=0
                    C_field=0
                    C_pv=res[14,1].astype(float)*f/epy*1e6
                    C_wind=res[15,1].astype(float)*f/epy*1e6
                    C_TES=0
                    C_BAT=0
                    C_BAT_replace=0
                    C_PHES=res[16,1].astype(float)*f/epy*1e6
                    C_heater=res[17,1].astype(float)*f/epy*1e6
                    C_heater_replace= res[18, 1].astype(float) *f/epy*1e6     
                    C_others=C_cap_tot*f/epy*1e6-C_heater_replace-C_pv-C_PHES-C_heater-C_wind
                    C_om=res[12,1].astype(float)/epy*1e6

                    #lcoh1=((C_pv+C_wind+C_BAT+C_BAT_replace+C_heater+C_heater_replace+C_others)*f+C_om)/epy*1.e6 

                elif case=='CST':
                    epy=res[10,1].astype(float)
                    r=res[22,1].astype(float)
                    f=r*(r+1)**25/((r+1)**25-1)

                    C_site=res[16,1].astype(float)
                    C_direct=res[20,1].astype(float)
                    C_equipment=res[19,1].astype(float)
                    C_contingency=C_direct-C_equipment
                    C_indirect=res[21,1].astype(float)

                    C_recv=res[13,1].astype(float)*f/epy*1e6
                    C_tower=res[14,1].astype(float)*f/epy*1e6
                    C_field=res[15,1].astype(float)*f/epy*1e6
                    C_pv=0
                    C_wind=0
                    C_TES=res[17,1].astype(float)*f/epy*1e6
                    C_BAT=0
                    C_BAT_replace=0
                    C_PHES=0
                    C_heater=0
                    C_heater_replace=0        
                    C_others=(C_contingency+C_indirect+C_site)*f/epy*1e6
                    C_om=res[12,1].astype(float)/epy*1e6
                    des_details=np.append(des_details, (cf, C_field, C_recv, C_tower, C_site, C_TES, C_om))

                elif case=='CST-modular':
                    epy=res[10,1].astype(float)
                    r=res[22,1].astype(float)
                    f=r*(r+1)**25/((r+1)**25-1)

                    C_site=res[16,1].astype(float)
                    C_direct=res[20,1].astype(float)
                    C_equipment=res[19,1].astype(float)
                    C_contingency=C_direct-C_equipment
                    C_indirect=res[21,1].astype(float)

                    C_recv=res[13,1].astype(float)*f/epy*1e6
                    C_tower=res[14,1].astype(float)*f/epy*1e6
                    C_field=res[15,1].astype(float)*f/epy*1e6
                    C_pv=0
                    C_wind=0
                    C_TES=res[17,1].astype(float)*f/epy*1e6
                    C_BAT=0
                    C_BAT_replace=0
                    C_PHES=0
                    C_heater=0
                    C_heater_replace=0        
                    C_others=(C_contingency+C_indirect+C_site)*f/epy*1e6
                    C_om=res[12,1].astype(float)/epy*1e6


            else:
                print('OUT OF RANGE:', cf0, case)
                cf=0
                C_recv=0
                C_tower=0
                C_field=0
                C_pv=0
                C_wind=0
                C_TES=0
                C_BAT=0
                C_BAT_replace=0
                C_PHES=0
                C_heater=0
                C_heater_replace=0        
                C_others=0
                C_om=0

            lcoh1=C_recv+C_tower+C_field+C_pv+C_wind+C_TES+C_BAT+C_BAT_replace+C_heater+C_heater_replace+C_others+C_om  

            C_RECV=np.append(C_RECV, C_recv)
            C_TOWER=np.append(C_TOWER, C_tower)
            C_FIELD=np.append(C_FIELD, C_field) 
            C_PV=np.append(C_PV, C_pv)
            C_WIND=np.append(C_WIND, C_wind)
            CTES=np.append(CTES, C_TES)
            CBAT=np.append(CBAT, C_BAT) 
            CBAT_replace=np.append(CBAT_replace, C_BAT_replace)
            CPHES=np.append(CPHES, C_PHES) 
            C_HEATER=np.append( C_HEATER, C_heater)
            C_HEATER_replace=np.append(C_HEATER_replace, C_heater_replace)
            C_OTHERS=np.append( C_OTHERS, C_others)
            C_OM=np.append(C_OM, C_om)  
            CFs=np.append(CFs, cf)
        if 'CST' in case:
            print(int(len(des_details)/7), len(des_details), location, case)
            des_details=des_details.reshape(int(len(des_details)/7), 7)
            np.savetxt('%s/%s-des-details-%s.csv'%(resdir, case, location), des_details, fmt='%s,', delimiter=',')            

        bar_width=0.5
        index=np.arange(len(CF0))*0.8
        
        l1=ax.bar(index+i*(len(CF0)*bar_width*2), C_RECV, width, label='C_receiver', color=scalar_map1.to_rgba(5))
        l2=ax.bar(index+i*(len(CF0)*bar_width*2), C_TOWER, width, bottom=C_RECV, label='C_tower', color=scalar_map1.to_rgba(6))
        l3=ax.bar(index+i*(len(CF0)*bar_width*2), C_FIELD, width, bottom=C_RECV+C_TOWER, label='C_heliostats', color=scalar_map1.to_rgba(7))
        l4=ax.bar(index+i*(len(CF0)*bar_width*2), C_PV, width, bottom=C_RECV+C_TOWER+C_FIELD, label='C_PV', color=scalar_map1.to_rgba(10))
        l5=ax.bar(index+i*(len(CF0)*bar_width*2), C_WIND, width, bottom=C_RECV+C_TOWER+C_FIELD+C_PV, label='C_wind', color=scalar_map1.to_rgba(3))
        l6=ax.bar(index+i*(len(CF0)*bar_width*2), CTES, width, bottom=C_RECV+C_TOWER+C_FIELD+C_PV+C_WIND, label='C_TES', color=scalar_map1.to_rgba(13))
        l7=ax.bar(index+i*(len(CF0)*bar_width*2), CBAT, width, bottom=C_RECV+C_TOWER+C_FIELD+C_PV+C_WIND+CTES, label='C_battery', color=scalar_map.to_rgba(10))
        l8=ax.bar(index+i*(len(CF0)*bar_width*2), CBAT_replace, width, bottom=C_RECV+C_TOWER+C_FIELD+C_PV+C_WIND+CTES+CBAT, label='C_bat_replace', color=scalar_map.to_rgba(11))
        l9=ax.bar(index+i*(len(CF0)*bar_width*2), CPHES, width, bottom=C_RECV+C_TOWER+C_FIELD+C_PV+C_WIND+CTES+CBAT+CBAT_replace, label='C_PHES', color=scalar_map.to_rgba(1))
        l10=ax.bar(index+i*(len(CF0)*bar_width*2), C_HEATER, width, bottom=C_RECV+C_TOWER+C_FIELD+C_PV+C_WIND+CTES+CBAT+CBAT_replace+CPHES, label='C_heater', color=scalar_map.to_rgba(15))
        l11=ax.bar(index+i*(len(CF0)*bar_width*2), C_HEATER_replace, width, bottom=C_RECV+C_TOWER+C_FIELD+C_PV+C_WIND+CTES+CBAT+CBAT_replace+CPHES+C_HEATER, label='C_hter_replace', color=scalar_map.to_rgba(14))
        l12=ax.bar(index+i*(len(CF0)*bar_width*2), C_OTHERS, width, bottom=C_RECV+C_TOWER+C_FIELD+C_PV+C_WIND+CTES+CBAT+CBAT_replace+CPHES+C_HEATER+C_HEATER_replace, label='C_others', color=scalar_map1.to_rgba(19))
        l13=ax.bar(index+i*(len(CF0)*bar_width*2), C_OM, width, bottom=C_RECV+C_TOWER+C_FIELD+C_PV+C_WIND+CTES+CBAT+CBAT_replace+CPHES+C_HEATER+C_HEATER_replace+C_OTHERS, label='C_om', color=scalar_map.to_rgba(20))

        #ax2.plot(index+i*(len(CF0)*bar_width*2), CFs*100., 'x', color='red')
        label_pos=np.append(label_pos, index+i*(len(CF0)*bar_width*2))


    legends=['C_receiver', 'C_tower', 'C_heliostats', 'C_pv', 'C_wind', 'C_TES',  'C_batt', 'C_batt_replace', 'C_PHES', 'C_heater', 'C_heater_replace', 'C_others', 'C_om']
    plt.xticks(label_pos, LABELS2, fontsize=fts)
    plt.yticks(fontsize=fts)
    ax.set_ylabel('LCOH (USD/MWh)', fontsize=fts)
    #ax2.set_ylabel('Capacity factor (%)', fontsize=fts)
    ax.set_xticklabels( LABELS2, rotation=0)
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=fts)
    #ax2.tick_params(axis='y', labelsize=fts)

    ax.legend([l1, l2, l3, l4, l5, l6, l7, l8 ,l9, l10, l11, l12, l13], legends, loc=1, bbox_to_anchor=(1.3,1.), fontsize=fts)

    ax.set_ylim([0,300.])
    plt.savefig(open('%s/LCOH-breakdown-%s.png'%(resdir, location), 'wb'),  bbox_inches='tight')
    #plt.show()
    plt.close()

def plot_breakdown_compare(cf0, resdir, year=2020, process=False):

    locations=np.array([ 'Pilbara', 'Burnie',  'Gladstone', 'Pinjarra',   'Upper Spencer Gulf'])
    cases=np.array(['CST-modular', 'TES-PV', 'TES-WIND', 'TES-HYBRID',  'BAT-PV', 'BAT-WIND', 'BAT-HYBRID','PHES-PV','PHES-WIND','PHES-HYBRID', 'H2'])
    LABELS=['TES+CST', 'TES+PV',  'TES+Wind', 'TES+PV+Wind',  'BAT+PV', 'BAT+Wind', 'BAT+PV+Wind', 'PHES+PV', 'PHES+Wind','PHES+PV+Wind', 'Hydrogen']
    loc_labels=[ 'Pilbara', 'Burnie',  'Gladstone',   'Peel',  'Upper Spencer Gulf']
    COLORS=[5,6,7,8,13,14,15,1,2,3,9, 11] 

    fig, ax = plt.subplots(figsize=(12,6))
    #ax2=ax.twinx()

    norm = matplotlib.colors.Normalize(vmin=1, vmax=20)
    c_map1=cm.tab20c
    scalar_map1=cm.ScalarMappable(cmap=c_map1, norm=norm)
    c_map=cm.tab20b
    scalar_map=cm.ScalarMappable(cmap=c_map, norm=norm)

    label_pos=[]
    fts=14


    if process:
        DATA=locations
        for i in range(len(cases)):
            LCOH=np.array([])
            case=cases[i]
            
            for j in range(len(locations)):
                location=locations[j]

                if case=='H2':
                    LCOH_best, CF, LCOH_storage, PV_best, WIND_best, EL_best, H2ST_best, PV_storage, WIND_storage, EL_storage, H2ST_storage=get_cf_lcoh_optimal_hydrogen()
                    lcoh=interp_lcoh(LCOH_best[location], CF*100., cf0)
                    LCOH=np.append(LCOH, lcoh)
                else:
                    fn='%s/post/%s/%s-%s-LCOH-CF.csv'%(resdir, year, case, location)
                    data=np.loadtxt(fn, delimiter=',', skiprows=1)
                    CF=data[:,0]
                    lcoh=data[:,3]
                    lcoh=interp_lcoh(lcoh, CF, cf0)
                    if lcoh>999:
                        lcoh=0
                    LCOH=np.append(LCOH, lcoh)
          

            #LCOH=DATA[i, 1:].astype(float)
            DATA=np.append(DATA, LCOH)
            width=0.08
            index=np.arange(len(locations))

            l1=ax.bar(index+i*width, LCOH, width, label=LABELS[i], color=scalar_map1.to_rgba(COLORS[i]))

        DATA=DATA.reshape(12,5)
        DATA=np.hstack((np.append(0,cases).reshape(12,1), DATA))
        np.savetxt('%s/post/%s/data_lcoh_%s.csv'%(resdir, year, cf0), DATA, delimiter=',', fmt='%s')

    else:
        DATA=np.loadtxt('%s/post/%s/data_lcoh_%.1f.csv'%(resdir, year, cf0), delimiter=',', dtype=str, skiprows=1)
        for i in range(len(cases)):
            LCOH=DATA[i, 1:].astype(float)
            width=0.08
            index=np.arange(len(locations))

            l1=ax.bar(index+i*width, LCOH, width, label=LABELS[i], color=scalar_map1.to_rgba(COLORS[i]))            
        

    plt.xticks(index+5*width, loc_labels, fontsize=fts)
    plt.yticks(fontsize=fts)
    ax.set_ylabel('LCOH (USD/MWh)', fontsize=fts)

    ax.set_xticklabels(loc_labels, rotation=0)
    ax.tick_params(axis='x', labelsize=fts)
    ax.tick_params(axis='y', labelsize=fts)

    ax.legend(loc=1, bbox_to_anchor=(1.3,1.), fontsize=fts)

    ax.set_ylim([0,300.])
    plt.savefig(open('%s/post/%s/compare-LCOH-breakdown-CF%s.png'%(resdir, year, cf0), 'wb'),  bbox_inches='tight')
    #plt.show()
    plt.close()


def interp_lcoh(LCOH, CF, cf):
    lcoh=np.interp(cf, CF, LCOH)
    return lcoh


def hydrogen_table():

    LCOH_best, CF, LCOH_storage, PV_best, WIND_best, EL_best, H2ST_best, PV_storage, WIND_storage, EL_storage, H2ST_storage=get_cf_lcoh_optimal_hydrogen(year=2020)

    CF, LCOH, LCOH2, locations=get_data(year=year)  
    best=get_best_location(year=year)
    regions=[ 'Burnie', 'Pinjara',  'Pilbara', 'Upper Spencer Gulf',  'Gladstone']
    LCOH_best={}
    LCOH_storage={}
    for region in regions:
        bid=best[region]
        for i in range(len(locations)):
            location=locations[i]
            if location=='%s %s'%(region, bid):
                lcoh=LCOH[i]
                LCOH_best[region]=lcoh
                cf, lcoh, lcoh2=get_storage_data(year=year, location=location, cost=1000)
                LCOH_storage[region]=lcoh


def get_CST_breakdown(location):
    resdir='/media/yewang/Data/Work/Research/Topics/yewang/HILTCRC/results/CF-curves-new-wind/post/2020/design-details'
    CFS=np.r_[40, 50, 60, 70, 80, 90, 95, 99]
    for cf in CFS:
        fn=resdir+'/summary_design_%s_CST_CF=%.0f%%.csv'%(location, cf)  
        data=np.loadtxt(fn, delimiter=',', dtype=str)
        if cf==50:  
            summary=data[:,0]
        summary=np.append(summary, data[:,1])
        if cf==99:
            summary=np.append(summary, data[:,2])

    summary=summary.reshape(len(CFS)+2, int(len(summary)/(len(CFS)+2)))
    summary=summary.T
    np.savetxt(resdir+'/summary_%s_CST.csv'%location, summary, fmt='%s', delimiter=',')

    for cf in CFS:
        fn=resdir+'/summary_design_%s_CST-modular_CF=%.0f%%.csv'%(location, cf)  
        data=np.loadtxt(fn, delimiter=',', dtype=str)
        if cf==50:  
            summary=data[:,0]
        summary=np.append(summary, data[:,1])
        if cf==99:
            summary=np.append(summary, data[:,2])

    summary=summary.reshape(len(CFS)+2, int(len(summary)/(len(CFS)+2)))
    summary=summary.T
    np.savetxt(resdir+'/summary_%s_CST-modular.csv'%location, summary, fmt='%s', delimiter=',')

def get_breakdown_design(location, resdir, P_load=500e3, year=2020, OM_method='SL', fast=True):

    cases=[ 'CST-modular']#,'CST','TES-PV', 'TES-WIND', 'TES-HYBRID',  'BAT-PV', 'BAT-WIND', 'BAT-HYBRID','PHES-PV','PHES-WIND','PHES-HYBRID']
    #LABELS=['CST+TES', 'PV+TES',  'WT+TES', 'PV+WT+TES',  'PV+BAT', 'WT+BAT', 'PV+WT+BAT', 'PV+PHES', 'WT+PHES','PV+WT+PHES']
 
    CF0=np.r_[40., 50., 60., 70., 80., 90., 95., 99.]

    fts=14
    for i in range(len(cases)):

        case=cases[i]
        fn='%s/post/%s/%s-%s-LCOH-CF.csv'%(resdir, year, case, location)
        try:
            data=np.loadtxt(fn, delimiter=',', skiprows=1)
        except:
            fn='%s/post/%s/%s-%s-LCOH-CF.csv'%(resdir, year, case, 'Pinjara')
            data=np.loadtxt(fn, delimiter=',', skiprows=1)
        cfs=data[:,0]
        SHs=data[:,1]
        RMs=data[:,2]
        LCOHs=data[:,3] 
        if 'CST' in case:
            des_details=np.array(['CF', 'C_field', 'C_recv', 'C_tower', 'C_site', 'C_TES',' C_om'])
        for j in range(len(CF0)):
            cf0=CF0[j]
            idx=abs(cf0-cfs)<0.01

            if LCOHs[idx]<999:
                sh=SHs[idx][0]
                rm=RMs[idx][0]
                lcoh=LCOHs[idx][0]
                cf=cfs[idx][0]
                savename='design_%s_%s_CF=%.0f%%'%(location, case, cf0)
                print(savename)
                if case=='CST':
                    lcoh_1, cf_1=get_CST_design(rm, sh, location, case, resdir, P_load=P_load, savename=savename, OM_method=OM_method, fast=fast, year=year)
                if case=='CST-modular':
                    lcoh_1, cf_1=get_CST_modular_design(rm, sh, location, case, resdir, P_load=P_load, savename=savename, year=year)
                elif case=='TES-PV':
                    lcoh_1, cf_1=get_TES_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=1, year=year)
                elif case=='TES-WIND':
                    lcoh_1, cf_1=get_TES_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=0, year=year)
                elif case=='TES-HYBRID':
                    lcoh_1, cf_1=get_TES_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=None, year=year)
                elif case=='BAT-PV':
                    lcoh_1, cf_1=get_BAT_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=1, year=year)
                elif case=='BAT-WIND':
                    lcoh_1, cf_1=get_BAT_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=0, year=year)
                elif case=='BAT-HYBRID':
                    lcoh_1, cf_1=get_BAT_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=None, year=year)
                elif case=='PHES-PV':
                    lcoh_1, cf_1=get_PHES_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=1, year=year)
                elif case=='PHES-WIND':
                    lcoh_1, cf_1=get_PHES_design(rm, sh, location, case, resdir, P_load=P_load,savename=savename, F_pv=0, year=year)
                elif case=='PHES-HYBRID':
                    lcoh_1, cf_1=get_PHES_design(rm, sh, location, case, resdir, P_load=P_load, savename=savename, F_pv=None, year=year)

                print(case, "CF=%s%%"%cf0, "%.1f%%"%(cf_1*100.), 'LCOH diff: %.1f%%'%((lcoh_1-lcoh)/lcoh*100.))    




if __name__=='__main__':
    locations=[ 'Upper Spencer Gulf', 'Burnie',   'Gladstone', 'Pinjarra', 'Pilbara']
    cases=['CST',
           'CST-modular',
           'TES-HYBRID',
           'TES-PV',
           'TES-WIND',
           'BAT-HYBRID',
           'BAT-PV',
           'BAT-WIND',
           'PHES-HYBRID',
           'PHES-PV',
           'PHES-WIND'
            ]
    titles=['CST',
            'CST-modular',
            'PV+Wind+TES',
            'PV+TES',
            'Wind+TES',
            'PV+Wind+Batt',
            'PV+Batt',
            'Wind+Batt',
            'PV+Wind+PHES',
            'PV+PHES',
            'Wind+PHES',
            ]

    workdir='/media/yewang/Data/Work/Research/Topics/yewang/HILTCRC/results/CF-curves-new-wind'
    year=2020

    # plot CF-RM-SH curves
    if 0:
        info=np.loadtxt('%s/max_rm_sh.csv'%workdir, delimiter=',', dtype=str, skiprows=1)
        INFO={}
        for i in range(len(info)):
            case=info[i,0][1:-1]
            location=info[i,1][1:-1]
            rm_max=info[i,2].astype(float)
            sh_max=info[i,3].astype(float)
            if case in INFO.keys():
                INFO[case][location]=[rm_max, sh_max]
            else:
                INFO[case]={location: [rm_max, sh_max]}

        #for i in range(len(cases)):
        #    case=cases[i]
        #    title=titles[i]
        #    for location in locations:
        #        rm_max, sh_max=INFO[case][location]  
        #        plot_cf_curves(workdir, case, location, title, rm_max, sh_max, year=year)

        #for case in cases:
        #    for location in locations:
        #        #print(case, location)
        #        costmodel=str(year)
        #        future_cost(location, case, P_load=500.e3, year=2020, costmodel=costmodel, resdir= workdir)
        #        get_cf_lcoh_optimal(location, case, resdir= workdir, year=year, plot=False)
         
    if 1:
        for location in locations:
            plot_cf_lcoh_comparison(location, workdir, year)		
     
            #plot_breakdown_bars(location, workdir)

        plot_breakdown_compare(cf0=90., resdir=workdir, year=2050, process=True)
    if 0:
	    #get_CST_breakdown('Pilbara')
	    for location in locations:
	        get_breakdown_design(location, resdir=workdir, P_load=500e3, year=year, OM_method='SL', fast=True)
