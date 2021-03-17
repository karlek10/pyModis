# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 10:21:20 2021

@author: karlo
"""

import rasterio
import pandas as pd
import tables
import geopandas as gpd
import xarray as xr
import os
import matplotlib.pyplot as plt
from osgeo import gdal
import numpy as np
import rioxarray as rxr
from shapely.geometry import mapping
import glob
from datetime import datetime
from pyproj import Transformer
from rasterio.plot import show
import datetime as dt
import h5py

def hdf_clip(raster_folder, shape_file):
    """
    Function reads the 8-day.hdf raster from raster folder, and .shp shapefile
    used to clip them.
    It creates a list of tuples, which hold the date and the snow data.
    Since, data is available only each 8th day, the 1st day data gets copied
    until next day (data) is available. 
    
    Parameters
    ----------
    raster_folder : string 
        - path to folder with .hdf rasters
    shape_file : string
        - path to the shapefile of the basin

    Returns
    -------
    clipps : list of tuples
        Clipped rasters.
    """
    clipps = list()
    rasters = [ras for ras in os.listdir(raster_folder) if ras.endswith(".hdf")] # lists all rasters
    shape = gpd.read_file(shape_file, crs="epsg:4326") # reads the shapefile for clipping
    for idx, raster in enumerate(rasters):
        doy = raster[13:16] 
        year = raster[9:13]
        xds = rxr.open_rasterio(raster_folder + raster, masked=True, chunks=True)
        clipped = xds.rio.clip(shape.geometry.apply(mapping), shape.crs, drop=True) # clippingthe rasters
        date_time, snow = dt.datetime.strptime(year + "-" + doy, "%Y-%j"), clipped.Maximum_Snow_Extent.values 
        """ Creating the datetime date of the data paoint, and snow data ."""
        date = date_time.strftime("%d.%m.%Y") 
        # converting the date to string wit CRO format
        data = (date, snow) # creatingthe data tuple
        if clipps: # if list not empty
            last_date = datetime.strptime(clipps[-1][0], "%d.%m.%Y") # checkign last entry in the list
            diff = abs(last_date - date_time).days - 1 # calculating the number of "missing" days
            print ("The difference in {} days.".format(diff)) 
            if diff > 50: 
                print ("The difference is {} days. Check the {} raster!".format(diff, date))
            else:
                for _ in range(diff): # iterating over day difference
                    date_ = datetime.strptime(clipps[-1][0], "%d.%m.%Y") 
                    date_time, snow = date_ + dt.timedelta(days=1), clipps[-1][1]
                    """ Creating the datetime date of the data paoint, and 
                    copying snow data from the last entry in the list."""
                    clipps.append((date_time.strftime("%d.%m.%Y"), snow)) # appending the copied data to the list
        clipps.append(data) # appending the clipped raster data to the list 
    return clipps 
            


hdf_raster_folder = "D:\\OneDrive\\Python\\12_pyModis\\test_data_folder\\"
shape_file = "D:\\OneDrive\\Python\\12_pyModis\\basin\\Drava\\Drava_Basin.shp"


#clipps = [hdf_clip(hdf_raster_folder, raster, shape_file) for raster in rasters]


clipps = hdf_clip(hdf_raster_folder, shape_file)