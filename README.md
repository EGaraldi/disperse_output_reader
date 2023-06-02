# disperse_output_reader
Simple functions to read Disperse output and save it in hdf5

## Basic usage
Import this file as python module (or simply copy-paste functions in your code). 

### Reading
To read in a Disperse NDSkl_ascii file:
> read_skeleton_from_NDskl_ascii(filename, as_dataframes=False)

where filename (a string) is the name of (plus full path to) the Disperse file. 

This will return a class containing all the data as fields, as shown below. If as_dataframes=True, this structure will contain two additional members (df_critical_points and df_filaments) containing the same information (except the int values) but organized in a pandas dataframe

[for critical points]

- Ndim             : [int] number of dimensions 
- bbox             : [list of list of float] bounding box of the data, format: [[x0, y0, z0], [x1, y1, z1]] where 0 and 1 indicate two opposite corners
- Ncritical_points : [int] number of critical points
- critical_points  : [list of np.array] coordinates of the critical points, format: [..., np.array([x_i, y_i, z_i]), ...], where i indicates the i-th critical point
- cp_type          : [list of int] crtical point type
- cp_value         : [list of int] value of the DTFE-computed density at the critical point
- cp_pairID        : [list of int] persistence pair index for each critical point
- cp_boundary      : [list of int] boundary flag for each critical point
- Nconnected_fil   : [list of int] number of filaments connected to each critical point 
- other_cp_id      : [list of list of int] for each critical point, a list of the critical point at the opposite end of each connected filament
- filament_id      : [list of list of int] for each critical point, a list of the indices of the associated filaments, indexing the arrays in the filament section (below)
- Nfields_cp       : [int] number of additional fields associated to each critical point
- fields_cp_name   : [list of string] name of the additional fields associated to each critical point
- fields_cp_values : [np.array with shape (Ncritical_points, Nfields_cp)] values of the additional fields associated to each critical point

[for filaments]

- Nfilaments         : [int] number of filaments
- Nsamples           : [list of int] number of sampling points for each filament
- filaments          : [list of list of Ndim float] for each filament, a list of coordinates of the sampling points
- cp_extremes        : [list of int pairs] for each filament, the indeices of the two extrema, indexes the critical point fields
- Nfields_fil        : [int] number of additional fields associated to each filament
- fields_fil_name    : [list of string] name of the additional fields associated to each filament
- fields_fil_values  : [np.array with shape (Ncritical_points, Nfields_cp)] values of the additional fields associated to each filament


### Writing
To write in an HDF5 file the content of the class described above, use:
> save_skeleton_to_hdf5(skeleton, filename_hdf5)

where skeleton is the class to write and filename_hdf5 is the complete name of the HDF5 file to create.

The format for this file is described at: https://thesan-project.com/filaments.html
