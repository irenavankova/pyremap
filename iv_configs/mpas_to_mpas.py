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

from pyremap import MpasMeshDescriptor, Remapper, ProjectionGridDescriptor
# --------SPECIFIC--------------------------------------------------------

print('Defining projections')

# Interpolation method
#interp_method = 'bilinear'
#interp_method = 'neareststod'
interp_method = 'conserve'

# IN - mesh to map from
inGridName = 'MALIsample'
inGridFileName_path = '/Users/irenavankova/Work/data_sim/sgr_files/sample_output/'
inGridFileName = f'{inGridFileName_path}output_state_2205_lastDt.nc'
inDescriptor = MpasMeshDescriptor(inGridFileName, inGridName, vertices=False)

# OUT - mesh to be mapped to
outGridName = 'ECwISC30to60E2r1'
outGridFileName_path = '/Users/irenavankova/Work/data_sim/E3SM_initial_condition/'
outGridFileName = f'{outGridFileName_path}ocean.ECwISC30to60E2r1.230220.nc'
outDescriptor = MpasMeshDescriptor(outGridFileName, outGridName, vertices=False)

# OUTPUT to remap from
outputFileName_path = inGridFileName_path
outputFileName = inGridFileName
var_name = ['totalGroundingLineDischargeCell']
run_name = 'SGR'
remappedFileName = '{}_{}_remapped_{}.nc'.format(run_name, outGridName, interp_method)
remappedFileName = f'{outputFileName_path}{remappedFileName}'

# --------GENERAL--------------------------------------------------------
print('Creating remapper object')
mappingFileName = 'map_{}_to_{}_{}.nc'.format(inGridName, outGridName, interp_method)
mappingFileName = f'{outputFileName_path}{mappingFileName}'

remapper = Remapper(inDescriptor, outDescriptor, mappingFileName)

print('Creating matrix (mapping file)')
remapper.build_mapping_file(method=interp_method, mpiTasks=1)

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