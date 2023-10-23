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

from pyremap import MpasMeshDescriptor, Remapper, get_fris_descriptor, MpasEdgeMeshDescriptor

# --------SPECIFIC--------------------------------------------------------

print('Defining projections')

# IN - mesh to map from
inGridName = 'ECwISC30to60E2r1'
inGridFileName_path = '/Users/irenavankova/Work/data_sim/E3SM_initial_condition/'
inGridFileName = f'{inGridFileName_path}ocean.ECwISC30to60E2r1.230220.nc'
#inDescriptor = MpasMeshDescriptor(inGridFileName, inGridName, vertices=False)
inDescriptor = MpasEdgeMeshDescriptor(inGridFileName, inGridName)
ce = 'edge'

# OUT - mesh to be mapped to
outDescriptor = get_fris_descriptor(dx=10.)
outGridName = outDescriptor.meshName

# OUTPUT to remap from
outputFileName_path = inGridFileName_path
outputFileName = inGridFileName
#var_name = ['temperature', 'salinity']
var_name1 = ['normalBarotropicVelocity']
var_name2 = ['normalVelocity']
run_name = f'{inGridName}_init'
# outputFileName_path = '/Users/irenavankova/Work/data_sim/pyremap_files/output/'
# outputFileName = f'{outputFileName_path}ECwISC30to60E2r1_velocityTidalRMS_CATS2008.nc'
# var_name = 'velocityTidalRMS'
remappedFileName = 'remapped_{}_{}_{}.nc'.format(ce, outGridName, run_name)

# --------GENERAL--------------------------------------------------------
print('Creating remapper object')
mappingFileName = 'map_{}_to_{}_bilinear_{}.nc'.format(inGridName, outGridName, ce)

remapper = Remapper(inDescriptor, outDescriptor, mappingFileName)

print('Creating matrix (mapping file)')
remapper.build_mapping_file(method='bilinear', mpiTasks=1)

print('Selecting variable to remap')
ds = xarray.open_dataset(outputFileName)
dsOut = xarray.Dataset()
dsOut1 = xarray.Dataset()
dsOut2 = xarray.Dataset()
# dsOut[in_var_name] = ds[in_var_name].isel(nVertLevels=0, Time=0) # if want only specific dimension

for var in var_name1:
    print(var)
    dsOut1[var] = ds[var]

for var in var_name2:
    print(var)
    dsOut2[var] = ds[var].isel(nVertLevels=[0])

print('remapping with python remapping')
dsOut.merge([dsOut1, dsOut2])
dsOut = remapper.remap(dsOut)
dsOut.to_netcdf(remappedFileName)

'''
print('remapping with ncremap')
outFileName = 'temp_{}_file.nc'.format(outGridName)  # string f string change
remapper.remap_file(inGridFileName, outFileName)
'''
