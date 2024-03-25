import pandas as pd
import numpy as np
import os
from greenheatpy.projdirs import datadir  # load the path that contains the data files
from greenheatpy.master import master
from greenheatpy.get_green_h2 import get_best_location

import unittest
import matplotlib.pyplot as plt


class TestMasterHeat(unittest.TestCase):

    def setUp(self):
        region = 'Pilbara'
        # best=get_best_location(2020)
        # location=region+' %s'%best[region]
        location = region + ' 3'
        print(location)
        solcast_TMY = False

        RM = 2
        t_storage = 8

        model_name = 'pv_wind_TES_heat'
        self.casedir = 'test-TES-mnz'
        self.LCOH, self.CF, self.C_cap = master(model_name, location, RM=RM, t_storage=t_storage, P_load_des=500e3,
                                                r_pv=0.5, P_heater=1000e3, casedir=self.casedir, verbose=True,
                                                solcast_TMY=solcast_TMY)

    def test(self):
        pv_out = np.loadtxt(self.casedir + '/pv_out.csv', delimiter=',')
        wind_out = np.loadtxt(self.casedir + '/wind_out.csv', delimiter=',')
        P_curt = np.loadtxt(self.casedir + '/P_curt.csv', delimiter=',')
        P_heater_in = np.loadtxt(self.casedir + '/P_heater_in.csv', delimiter=',')
        P_heater_out = np.loadtxt(self.casedir + '/P_heater_out.csv', delimiter=',')
        P_heat_direct = np.loadtxt(self.casedir + '/P_heat_direct.csv', delimiter=',')
        P_TES_in = np.loadtxt(self.casedir + '/P_TES_in.csv', delimiter=',')
        P_TES_out = np.loadtxt(self.casedir + '/P_TES_out.csv', delimiter=',')
        P_heat = np.loadtxt(self.casedir + '/P_heat.csv', delimiter=',')

        # check
        balance_1 = sum(pv_out + wind_out - P_heater_in - P_curt)
        balance_2 = sum(P_heater_out - P_heat_direct - P_TES_in)
        balance_3 = sum(P_TES_out + P_heat_direct - P_heat)

        print('balance 1', balance_1)
        print('balance 2', balance_2)
        print('balance 3', balance_3)
        self.assertTrue(balance_1 < 2e-2)
        self.assertTrue(balance_2 < 2e-2)
        self.assertTrue(balance_3 < 2e-2)
        self.assertTrue(abs(self.LCOH - 52.67) / 52.67 < 0.05)
        self.assertTrue(abs(self.CF - 0.71) / 0.71 < 0.05)
        self.assertTrue(abs(self.C_cap - 1705513327.4) / 1705513327.4 < 0.05)

        os.system('rm -r ' + self.casedir)


if __name__ == '__main__':
    unittest.main()