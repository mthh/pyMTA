#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: mz
"""
import unittest
import geopandas as gpd
import pandas as pd
import sys
from mta import gdev, sdev, tdev

       
class TestMTA(unittest.TestCase):
    def setUp(self):
        self.precision = 4 if sys.version_info.major == 3 else 3
        self.data_verif = pd.read_csv('tests/result_R_MTA.csv', sep=";")
        self.gdf = gpd.read_file('tests/GrandParis.shp')
        data = pd.read_csv('tests/GrandParisData.csv', sep=";")
        data.columns = ['_UID', '_DEPCOM', 'LIBCOM', 'EPT', 'LIBEPT', 'DEP', 'INC', 'TH']
        self.gdf = self.gdf.join(data)
        self.data_verif = self.data_verif[
            ['DEPCOM', 'gdevrel', 'gdevabs', 'tdevrel', 'tdevabs',
             'sdevrel_order', 'sdevrel_dist', 'sdevabs_order', 'sdevabs_dist']
            ].applymap(lambda x: float(x.replace(',','.')) if isinstance(x, str) else x)

    def verif_serie(self, s1, s2):
        for i,j in zip(s1.values.tolist(), s2.values.tolist()):
            self.assertAlmostEqual(i, j, places=self.precision)

    def test_global_dev(self):
        gdf = self.gdf
        gdf['gdevrel'] = gdev(gdf, 'INC', 'TH', 'rel')
        self.verif_serie(self.gdf['gdevrel'], self.data_verif['gdevrel'])
        gdf['gdevabs'] = gdev(gdf, 'INC', 'TH', 'abs')
        self.verif_serie(self.gdf['gdevabs'], self.data_verif['gdevabs'])

    def test_territorial_dev(self):
        gdf = self.gdf
        gdf['tdevrel'] = tdev(gdf, 'INC', 'TH', 'EPT', 'rel')
        self.verif_serie(gdf['tdevrel'], self.data_verif['tdevrel'])
        gdf['tdevabs'] = tdev(gdf, 'INC', 'TH', 'EPT', 'abs')
        self.verif_serie(gdf['tdevabs'], self.data_verif['tdevabs'])

    def test_spatial_dev(self):
        gdf = self.gdf
        # Use order and relative deviation:
        self.gdf['sdevrel_order'] = sdev(gdf, 'INC', 'TH', 'rel', order=5)
        self.verif_serie(gdf['sdevrel_order'], self.data_verif['sdevrel_order'])
        # Use distance and relative deviaiton:
        self.gdf['sdevrel_dist'] = sdev(gdf, 'INC', 'TH', 'rel', dist=20000)
        self.verif_serie(gdf['sdevrel_dist'], self.data_verif['sdevrel_dist'])
        # Use order and absolute deviation:
        self.gdf['sdevabs_order'] = sdev(gdf, 'INC', 'TH', 'abs', order=5)
        self.verif_serie(self.gdf['sdevabs_order'], self.data_verif['sdevabs_order'])
        # Use distance and absolute deviation:
        self.gdf['sdevabs_dist'] = sdev(gdf, 'INC', 'TH', 'abs', dist=20000)
        self.verif_serie(self.gdf['sdevabs_dist'], self.data_verif['sdevabs_dist'])
