import pandas as pd
import numpy as np
import os
from projdirs import datadir #load the path that contains the data files 
from master_heat import master

import unittest
import matplotlib.pyplot as plt


class TestMasterHeat(unittest.TestCase):

    def setUp(self):
        location='Port Augusta'
        RM=2
        t_storage=8

        model_name='pv_wind_battery_heat'
        self.casedir='test/'+model_name
        master(model_name, location, RM=RM, t_storage=t_storage, P_load_des=500e3, casedir=self.casedir, verbose=True)

    def test(self):

        pv_out=np.loadtxt(self.casedir+'/pv_out.csv', delimiter=',')
        wind_out=np.loadtxt(self.casedir+'/wind_out.csv',delimiter=',')
        P_ele=np.loadtxt(self.casedir+'/P_ele.csv',delimiter=',')
        P_curt=np.loadtxt(self.casedir+'/P_curt.csv', delimiter=',')
        P_bat_in=np.loadtxt(self.casedir+'/P_bat_in.csv', delimiter=',')
        P_bat_out=np.loadtxt(self.casedir+'/P_bat_out.csv', delimiter=',')

        # check
        pv_wind_direct=P_ele-P_bat_out
        check=sum(pv_out+ wind_out - P_curt - pv_wind_direct - P_bat_in)
        print('check=', check)
        self.assertTrue(check<1e-2)

        #os.system('rm *.csv')

        


if __name__=='__main__':
    unittest.main()
    







