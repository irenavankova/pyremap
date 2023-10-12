#!/usr/bin/env python
# This software is open source software available under the BSD-3 license.
#
# Copyright (c) 2019 Triad National Security, LLC. All rights reserved.
# Copyright (c) 2019 Lawrence Livermore National Security, LLC. All rights
# reserved.
# Copyright (c) 2019 UT-Battelle, LLC. All rights reserved.
#
# Additional copyright and license information can be found in the LICENSE file
# distributed with this code, or at
# https://raw.githubusercontent.com/MPAS-Dev/pyremap/main/LICENSE

'''
Creates a mapping file that can be used with ncremap (NCO) to remap MPAS files
to a latitude/longitude grid.

Usage: Copy this script into the main MPAS-Analysis directory (up one level).
Modify the grid name, the path to the MPAS grid file and the output grid
resolution.
'''

import xarray
import pyproj

from pyremap import Remapper, ProjectionGridDescriptor, get_fris_descriptor
# --------SPECIFIC--------------------------------------------------------

print('Defining projections')

# IN - mesh to map from
inGridName = 'S71W70_CATS_ustar'
inGridFileName_path = '/Users/irenavankova/Work/data_sim/pyremap_files/input/'
inGridFileName = f'{inGridFileName_path}ustar_CATS2008_S71W70.nc'
projection_in = pyproj.Proj('+proj=stere +lat_ts=-71.0 +lat_0=-90 +lon_0=-70.0 +k_0=1.0 +x_0=0.0 +y_0=0.0 +ellps=WGS84')
inDescriptor = ProjectionGridDescriptor.read(projection=projection_in, fileName=inGridFileName, meshName=inGridName,
                                             xVarName='x', yVarName='y')

# OUT - mesh to be mapped to
outDescriptor = get_fris_descriptor(dx=10.)
outGridName = outDescriptor.meshName

# OUTPUT to remap from
outputFileName_path = inGridFileName_path
outputFileName = inGridFileName
var_name = ['velocityTidalRMS']
run_name = 'ustar_CATS2008_S71W70'
remappedFileName = 'remapped_{}_{}.nc'.format(outGridName, run_name)

# --------GENERAL--------------------------------------------------------
print('Creating remapper object')
mappingFileName = 'map_{}_to_{}_bilinear.nc'.format(inGridName, outGridName)

remapper = Remapper(inDescriptor, outDescriptor, mappingFileName)

print('Creating matrix (mapping file)')
remapper.build_mapping_file(method='bilinear', mpiTasks=1)

print('Selecting variable to remap')
ds = xarray.open_dataset(outputFileName)
dsOut = xarray.Dataset()
# dsOut[in_var_name] = ds[in_var_name].isel(nVertLevels=0, Time=0) # if want only specific dimension

for var in var_name:
    print(var)
    dsOut[var] = ds[var]

print('remapping with python remapping')
dsOut = remapper.remap(dsOut)
dsOut.to_netcdf(remappedFileName)

'''
print('remapping with ncremap')
outFileName = 'temp_{}_file.nc'.format(outGridName)  # string f string change
remapper.remap_file(inGridFileName, outFileName)
'''