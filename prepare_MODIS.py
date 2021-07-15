# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 10:21:20 2021

@author: karlo
"""


import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import numpy as np
import rioxarray as rxr
from shapely.geometry import mapping
from datetime import datetime
import datetime as dt


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
        Clipped numpy arrays.
    """
    clipps = list()
    rasters = [ras for ras in os.listdir(raster_folder) if ras.endswith(".hdf")] # lists all rasters
    shape = gpd.read_file(shape_file, crs="epsg:4326") # reads the shapefile for clipping
    for idx, raster in enumerate(rasters):
        doy = raster[13:16] 
        year = raster[9:13]
        xds = rxr.open_rasterio(raster_folder + raster, masked=True, chunks=True)
        clipped = xds.rio.clip(shape.geometry.apply(mapping), shape.crs, drop=True) # clipping the rasters
        """ Creating the datetime date of the data paoint, and snow data .""" 
        date = datetime.strptime(year + "-" + doy, "%Y-%j")
        snow = np.nan_to_num(clipped.Maximum_Snow_Extent.values.squeeze())
        # converting the date to string wit CRO format
        data = (date, snow) # creatingthe data tuple
        if clipps: # if list not empty
            prev_date = clipps[-1][0] # checkign last entry in the list
            now_date = date
            diff = abs(prev_date - now_date) - dt.timedelta(1) # calculating the number of "missing" days
            print ("The difference is {}.".format(diff)) 
            if diff > dt.timedelta(50): 
                print ("The difference is {}. Check the {} raster!".format(diff, date))
            else:
                for _ in range(diff.days): # iterating over day difference
                    date_ = clipps[-1][0]
                    date_time, snow = date_ + dt.timedelta(1), clipps[-1][1]
                    """ Creating the datetime date of the data paoint, and 
                    copying snow data from the last entry in the list."""
                    clipps.append((date_time, snow)) # appending the copied data to the list
                    prev_date += dt.timedelta(1)
        clipps.append(data) # appending the clipped raster data to the list 
    print("Clipping rasters has been finished. The raster have been saved to the list clipps.")
    return clipps 
            

def create_raster_files(basin_name, input_folder, output_folder):
    """
    The function takes default Modis rasters, executes the hadf_clip function for the desired basin
    and returns seperate .npy files for each day in the desired output folder.

    Parameters
    ----------
    basin_name : str
        Name of the basin (should be in basin folder).
    input_folder : str
        Path to the input folder with uncuit MODIS .hdf rasters.
    output_folder : str
        Path to the output folder.

    Returns
    -------
    None.

    """
    hdf_raster_folder = "D:\\OneDrive\\Python\\12_pyModis\\" + input_folder + "\\"
    shape_file = "D:\\OneDrive\\Python\\12_pyModis\\basin\\" + basin_name + "\\" +basin_name +"_Basin.shp"
    clipps = hdf_clip(hdf_raster_folder, shape_file)
    if not os.path.isdir(output_folder +"\\"):
        os.mkdir(output_folder +"\\")
    for (date, raster) in clipps:
        date = str(date)[:10]
        np.save(output_folder + "\\" + date + ".npy", raster)
    print ("Creating files have been finished. The files have been saved to the folder {}.".format(output_folder)) 




    





if __name__ == '__main__':
    
    basin_name = "Isel"
    input_folder = "data_modis_complete"
    output_folder = "D:\\Isel_modis"
    
    clipps = create_raster_files(basin_name, input_folder, output_folder)
    
    
















