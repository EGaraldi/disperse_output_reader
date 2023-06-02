__license__   = "GNU GPLv3 <https://www.gnu.org/licenses/gpl.txt>"
__author__    = "Enrico Garaldi <egaraldi@mpa-garching.mpg.de>"
__version__   = "1.0"


'''Collection of functions to load and save Disperse data.


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import h5py
import numpy as np
import pandas as pd

class DisperseSkeleton:
    def __init__(self):
        self.Ndim              = None
        self.bbox              = None
        self.Ncritical_points  = None
        self.critical_points   = None
        self.cp_type           = None
        self.cp_value          = None
        self.cp_pairID         = None
        self.cp_boundary       = None
        self.Nconnected_fil    = None
        self.other_cp_id       = None
        self.filament_id       = None
        self.Nfilaments        = None
        self.filaments         = None
        self.cp_extremes       = None
        self.Nsamples          = None
        self.Nfields_cp        = None
        self.fields_cp_name    = None
        self.fields_cp_values  = None
        self.Nfields_fil       = None
        self.fields_fil_name   = None
        self.fields_fil_values = None


def read_skeleton_from_NDskl_ascii(filename, as_dataframes=False):
    '''Parse a NDskl_ascii file and extracts properties of critical points and filaments.

Parameters
----------
filename     : string
               name of the NDskl_ascii file
as_dataframes: bool, optional (default=False)
               if True, creates two pandas DataFrames containing the critical points and
               filament properties. These are saved as *additional* members of the DisperseSkeleton 
               class named 'critical_points' and 'filaments', respectively.

Returns
-------
skeleton     : DisperseSkeleton
               class containing the loaded data'''

    skeleton = DisperseSkeleton()

    with open(filename, 'r') as f:
        lines = f.readlines()


    # Header
    assert(lines[0].strip() == 'ANDSKEL')
    skeleton.Ndim = int(lines[1].strip())
    assert(skeleton.Ndim==2 or skeleton.Ndim==3)

    #skip comments
    l=2
    while(lines[l].strip()[0] == '#'):
        l += 1

    assert(lines[l].strip()[:4] == 'BBOX')
    xyz0, xyz1 = lines[l].strip()[6:-1].split()
    x0, y0, z0 = xyz0[:-1].split(',')
    x1, y1, z1 = xyz1[1: ].split(',')
    skeleton.bbox = [[float(x0), float(y0), float(z0)], [float(x1), float(y1), float(z1)]]
    l += 1

    # Critical points
    assert(lines[l].strip() == '[CRITICAL POINTS]')
    l += 1
    skeleton.Ncritical_points = int(lines[l].strip())

    skeleton.critical_points=[]
    skeleton.cp_type=[]
    skeleton.cp_value=[]
    skeleton.cp_pairID=[]
    skeleton.cp_boundary=[]
    skeleton.Nconnected_fil = []
    skeleton.other_cp_id=[]
    skeleton.filament_id=[]
    for cr in range(skeleton.Ncritical_points):
        l += 1
        t, x, y, z, value, pairID, boundary = lines[l].split()
        skeleton.critical_points.append( np.array([ float(x), float(y), float(z) ]) )
        skeleton.cp_type.append(int(t))
        skeleton.cp_value.append(float(value))
        skeleton.cp_pairID.append(int(pairID))
        skeleton.cp_boundary.append(int(boundary))
        l += 1
        this_Nconnected_fil = int(lines[l].strip())
        skeleton.Nconnected_fil.append( this_Nconnected_fil )
        #l += Nconnected_fil
        this_other_cp_id=[]
        this_filament_id=[]
        for i in range(this_Nconnected_fil):
            l += 1
            other_cp, fil = lines[l].split()
            this_other_cp_id.append( int(other_cp) )
            this_filament_id.append( int(fil) )
        skeleton.other_cp_id.append(this_other_cp_id)
        skeleton.filament_id.append(this_filament_id)
    l += 1

    # Filaments
    assert(lines[l].strip() == '[FILAMENTS]')
    l += 1
    skeleton.Nfilaments = int(lines[l].strip())

    skeleton.cp_extremes = []
    skeleton.filaments = []
    skeleton.Nsamples = []
    for fil in range(skeleton.Nfilaments):
        l += 1
        cp1, cp2, this_Nsamples = lines[l].split()
        skeleton.cp_extremes.append( [int(cp1), int(cp2)] )
        this_Nsamples = int(this_Nsamples)
        skeleton.Nsamples.append(this_Nsamples)
        this_filament = []
        for s in range(this_Nsamples):
            l += 1
            x,y,z = lines[l].split()
            this_filament.append( [float(x), float(y), float(z)] )
        skeleton.filaments.append( np.array(this_filament) )
    l += 1

    # Critical point data
    assert(lines[l].strip() == '[CRITICAL POINTS DATA]')
    l += 1
    skeleton.Nfields_cp = int(lines[l].strip())

    skeleton.fields_cp_name = []
    for i in range(skeleton.Nfields_cp):
        l += 1
        skeleton.fields_cp_name.append( lines[l].strip() )

    skeleton.fields_cp_values = []
    for i in range(skeleton.Ncritical_points):
        l += 1
        _values = lines[l].split()
        skeleton.fields_cp_values.append( [float(v) for v in _values] )
    l += 1

    # Filaments data
    assert(lines[l].strip() == '[FILAMENTS DATA]')
    l += 1
    skeleton.Nfields_fil = int(lines[l].strip())

    skeleton.fields_fil_name = []
    for i in range(skeleton.Nfields_fil):
        l += 1
        skeleton.fields_fil_name.append( lines[l].strip() )

    skeleton.fields_fil_values = []
    for ifil in range(skeleton.Nfilaments):
        this_fields_fil_values = []
        for isam in range(skeleton.Nsamples[ifil]):
            l += 1
            _values = lines[l].split()
            this_fields_fil_values.append( [float(v) for v in _values] )
        skeleton.fields_fil_values.append( this_fields_fil_values )

    #check we have reached the end of file
    assert(l+1 == len(lines))

    if as_dataframes:
        skeleton.df_critical_points = pd.DataFrame(zip(skeleton.critical_points , 
                                                       skeleton.cp_type         , 
                                                       skeleton.cp_value        , 
                                                       skeleton.cp_pairID       , 
                                                       skeleton.cp_boundary     , 
                                                       skeleton.Nconnected_fil  , 
                                                       skeleton.other_cp_id     , 
                                                       skeleton.filament_id     
                                                      ), 
                                                   columns = ['critical_points', 'cp_type', 
                                                              'cp_value', 'cp_pairID', 'cp_boundary',
                                                              'Nconnected_fil', 'other_cp_id', 'filament_id']
                                                  )
        for ifield, field in enumerate(skeleton.fields_cp_name):
            skeleton.df_critical_points[field] = [v[ifield] for v in skeleton.fields_cp_values]
        
        skeleton.df_filaments = pd.DataFrame(zip(skeleton.filaments        , 
                                                 skeleton.cp_extremes      , 
                                                 skeleton.Nsamples         
                                                ), 
                                             columns = ['filaments', 'cp_extremes', 'Nsamples']
                                           )
        for ifield, field in enumerate(skeleton.fields_fil_name):
            skeleton.df_filaments[field] = [[s[ifield] for s in v] for v in skeleton.fields_fil_values]
    
    return skeleton


def save_skeleton_to_hdf5(skeleton, filename_hdf5):
    '''Save the data un a DisperseSkeleton class into an hdf5 file.
    
Notice that the other_cp_id, filament_id and filaments members of the class will 
be flattened and an array of offsets is provided, such that e.g. the filament_id 
associated to the i-th critical point are
    > num_connected_filaments = filament_hdf5_file['NumConnectedFilaments']
    > offsets = filament_hdf5_file['OffsetFilamentAndExtreme']
    > associated_filament_ids = filament_hdf5_file['IndexFilament'][offsets[i] : offsets[i]+num_connected_filaments[i] ]


Parameters
----------
skeleton      : DisperseSkeleton
                class containing the loaded data
filename_hdf5 : string
                name of the output hdf5 file'''

    #prepare some data, flattening multidimentional arrays and creating the appropriate offsets
    other_cp_id_flat = []
    for others in skeleton.other_cp_id:
        for other in others:
            other_cp_id_flat.append( other )
    skeleton.other_cp_id_flat = np.array( other_cp_id_flat )

    filament_id_flat = []
    for others in skeleton.filament_id:
        for other in others:
            filament_id_flat.append( other )
    skeleton.filament_id_flat = np.array( filament_id_flat )

    offset_cp = np.cumsum(skeleton.Nconnected_fil)
    skeleton.offset_cp = np.insert(offset_cp[:-1], 0, 0)

    filaments_flat = []
    for others in skeleton.filaments:
        for other in others:
            filaments_flat.append( other )
    skeleton.filaments_flat = filaments_flat

    fields_fil_values_flat = []
    for others in skeleton.fields_fil_values:
        for other in others:
            fields_fil_values_flat.append( other )
    skeleton.fields_fil_values_flat = fields_fil_values_flat

    offset_fil = np.cumsum(skeleton.Nsamples)
    skeleton.offset_fil = np.insert(offset_fil[:-1], 0, 0)


    with h5py.File(filename_hdf5, 'w') as fil_file:

        #HEADER
        header_group = fil_file.create_group('Header')
        header_group.attrs.create('NumDimensions'    , skeleton.Ndim                    , dtype=np.int32)
        header_group.attrs.create('BoundingBox'      , np.array(skeleton.bbox).flatten(), dtype=np.float32)
        header_group.attrs.create('NumCriticalPoints', skeleton.Ncritical_points        , dtype=np.int32)
        header_group.attrs.create('NumFilaments'     , skeleton.Nfilaments              , dtype=np.int32)


        #CRITICAL POINTS
        cp_group = fil_file.create_group('CriticalPoints')
        cp_group.attrs.create("NumAssociatedFields"  , skeleton.Nfields_cp    , dtype=np.int32)
        cp_group.attrs.create("AssociatedFieldsNames", skeleton.fields_cp_name)
        cp_group.create_dataset("CriticalIndex"            , data=np.array(skeleton.cp_type))
        cp_group.create_dataset("Coordinates"              , data=np.array(skeleton.critical_points))
        cp_group.create_dataset("DensityDTFE"              , data=np.array(skeleton.cp_value))
        cp_group.create_dataset("PersistencePairIndex"     , data=np.array(skeleton.cp_pairID))
        cp_group.create_dataset("BoundaryFlag"             , data=np.array(skeleton.cp_boundary))
        cp_group.create_dataset("NumConnectedFilaments"    , data=np.array(skeleton.Nconnected_fil))
        cp_group.create_dataset("IndexOtherFilamentExtreme", data=np.array(skeleton.other_cp_id_flat))
        cp_group.create_dataset("IndexFilament"            , data=np.array(skeleton.filament_id_flat))
        cp_group.create_dataset("OffsetFilamentAndExtreme" , data=np.array(skeleton.offset_cp))
        cp_group.create_dataset("AssociatedFields"         , data=np.array(skeleton.fields_cp_values))


        #FILAMENTS
        fil_group = fil_file.create_group("Filaments")
        fil_group.attrs.create("NumAssociatedFields"  , skeleton.Nfields_fil    , dtype=np.int32)
        fil_group.attrs.create("AssociatedFieldsNames", skeleton.fields_fil_name)
        fil_group.create_dataset("IndexExtremalCriticalPoints", data=np.array(skeleton.cp_extremes))
        fil_group.create_dataset("NumSamplingPoints"          , data=np.array(skeleton.Nsamples))
        fil_group.create_dataset("CoordinatesSamplingPoints"  , data=np.array(skeleton.filaments_flat))
        fil_group.create_dataset("AssociatedFields"           , data=np.array(skeleton.fields_fil_values_flat))
        fil_group.create_dataset("OffsetSamplingPoints"       , data=np.array(skeleton.offset_fil))

