import pandas as pd
import numpy as np
import os
from projdirs import datadir #load the path that contains the data files 
from PACKAGE.optimisation_green_heat import make_dzn_file, optimise
from PACKAGE.component_model import WindSource, SolarResource,pv_gen, wind_gen,solcast_weather, SolarResource_solcast, WindSource_solcast
from master_heat import master

import unittest
import matplotlib.pyplot as plt

def AUD2USD(value):
    return(0.746 * value)

class TestMasterHeat(unittest.TestCase):

    def setUp(self):
        location='Port Augusta'
        RM=2
        t_storage=8
        self.casedir='./test'
        master(location, RM=RM, t_storage=t_storage, P_load_des=500e3, casedir=self.casedir, verbose=True)

    def test(self):

        pv_out=np.loadtxt(self.casedir+'/pv_out.csv', delimiter=',')
        wind_out=np.loadtxt(self.casedir+'/wind_out.csv',delimiter=',')
        P_ele=np.loadtxt(self.casedir+'/P_ele.csv',delimiter=',')
        P_curt=np.loadtxt(self.casedir+'/P_curt.csv', delimiter=',')
        P_st_in=np.loadtxt(self.casedir+'/P_st_in.csv', delimiter=',')
        P_st_out=np.loadtxt(self.casedir+'/P_st_out.csv', delimiter=',')

        # check
        pv_wind_direct=P_ele-P_st_out
        check=sum(pv_out+ wind_out - P_curt - pv_wind_direct - P_st_in)
        print('check=', check)
        self.assertTrue(check<1e-2)

        #os.system('rm *.csv')

        


if __name__=='__main__':
    unittest.main()
    







