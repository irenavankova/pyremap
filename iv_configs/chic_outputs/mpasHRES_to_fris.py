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

from pyremap import MpasMeshDescriptor, Remapper, get_fris_descriptor

# --------SPECIFIC--------------------------------------------------------

print('Defining projections')

# IN - mesh to map from
nres = 8
inGridName = f'FRISwISC0{nres}to60E3r1'
inGridFileName_path = f'/usr/projects/e3sm/inputdata/ocn/mpas-o/FRISwISC0{nres}to60E3r1/'
if nres == 8 or nres == 4:
    tstamp = '20230913'
elif nres == 2:
    tstamp = '20230914'
elif nres == 1:
    tstamp = '20230915'
inGridFileName = f'{inGridFileName_path}mpaso.{inGridName}.{tstamp}.nc'
inDescriptor = MpasMeshDescriptor(inGridFileName, inGridName, vertices=False)

# OUT - mesh to be mapped to
outDescriptor = get_fris_descriptor(dx=1.)
outGridName = outDescriptor.meshName

# OUTPUT to remap from
outputFileName_path = '/lustre/scratch4/turquoise/vankova/E3SM/scratch/chicoma-cpu/'
run_name = '20231005.GMPAS-JRA1p5-DIB-PISMF.TL319_FRISwISC08to60E3r1.tPElay03.chicoma-cpu'
outputFile = '20231005.GMPAS-JRA1p5-DIB-PISMF.TL319_FRISwISC08to60E3r1.tPElay03.chicoma-cpu.mpaso.inst.0001-01-06_01800.nc'
outputFileName = f'{outputFileName_path}{run_name}/run/{outputFile}'
var_name = ['gmKappaScaling', 'gmBolusKappa', 'gmHorizontalTaper', 'kineticEnergyCell']

remapped_path = f'{outputFileName_path}/remapped'
remappedFileName = 'remapped_{}_{}.nc'.format(outGridName, run_name)
remappedFileName = f'{remapped_path}{remappedFileName}'

# --------GENERAL--------------------------------------------------------
print('Creating remapper object')
remapper_path = '/usr/projects/climate/vankova/pyremap/remappers/'
mappingFileName = 'map_{}_to_{}_bilinear.nc'.format(inGridName, outGridName)
mappingFileName = f'{remapper_path}{mappingFileName}'

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
    if var in ['gmKappaScaling']:
        dsOut[var] = ds[var].isel(nVertLevelsP1=0)
    if var in ['kineticEnergyCell']:
        dsOut[var] = ds[var].isel(nVertLevels=0)


print('remapping with python remapping')
dsOut = remapper.remap(dsOut)
dsOut.to_netcdf(remappedFileName)

'''
print('remapping with ncremap')
outFileName = 'temp_{}_file.nc'.format(outGridName)  # string f string change
remapper.remap_file(inGridFileName, outFileName)
'''
