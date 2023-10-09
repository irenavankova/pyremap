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

print('Reading input files')
# replace with the MPAS mesh name
inGridName = 'S71W70_CATS_ustar'
#outGridName = 'SOwISC12to60E2r4'
#outGridName = 'oQU240wLI'
nres = 4
#outGridName = 'ECwISC30to60E2r1'
outGridName = f'FRISwISC0{nres}to60E3r1'

# replace with the path to the desired mesh or restart file
# As an example, use:
# https://web.lcrc.anl.gov/public/e3sm/inputdata/ocn/mpas-o/oQU240/ocean.QU.240km.151209.nc
# inGridFileName_path = '/Volumes/GoogleDrive/My Drive/Research/DOVuFRIS/Fris_Apres/code/Model_outputs/E3SM/tides_from_CATS/'
# outGridFileName_path = '/Volumes/GoogleDrive/My Drive/Research/External_datasets/Bedmachine/'
inGridFileName_path = '/Users/irenavankova/Work/data_sim/pyremap_files/input/'
#outGridFileName_path = '/Users/irenavankova/Work/data_sim/E3SM_initial_condition/'
outGridFileName_path = f'/Users/irenavankova/Work/compass_meshes/anvil/F{nres}/mesh/'


inGridFileName = f'{inGridFileName_path}ustar_CATS2008_S71W70.nc'
#outGridFileName = f'{outGridFileName_path}ocean.SOwISC12to60E2r4.210107.nc'
#outGridFileName = f'{outGridFileName_path}ocean.QU.240wLI.230220.nc'
outGridFileName = f'{outGridFileName_path}culled_mesh.nc'

print('Defining projections')
# 4-km uniform polar stereographic (centered at 71oS, 70oW)
projection_in = pyproj.Proj('+proj=stere +lat_ts=-71.0 +lat_0=-90 +lon_0=-70.0 +k_0=1.0 +x_0=0.0 +y_0=0.0 +ellps=WGS84')

print('Creating remapper object')
inDescriptor = ProjectionGridDescriptor.read(projection=projection_in, fileName=inGridFileName, meshName=inGridName,
                                             xVarName='x', yVarName='y')

outDescriptor = MpasMeshDescriptor(outGridFileName, outGridName, vertices=False)

mappingFileName = 'map_{}_to_{}_bilinear.nc'.format(inGridName, outGridName)

remapper = Remapper(inDescriptor, outDescriptor, mappingFileName)

print('creating matrix (mapping file)')
# conservative remapping with 4 MPI tasks (using mpirun)
# srun: 
remapper.build_mapping_file(method='bilinear', mpiTasks=1)

print('remapping with ncremap')
# do remapping with ncremap
outFileName = 'temp_{}_file.nc'.format(outGridName)  # string f string change
remapper.remap_file(inGridFileName, outFileName)

print('remapping with python remapping')
# do remapping again, this time with python remapping
outFileName = 'temp_{}_array.nc'.format(outGridName)
dsOut = xarray.open_dataset(inGridFileName)
dsOut = remapper.remap(dsOut)
dsOut.to_netcdf(outFileName)
