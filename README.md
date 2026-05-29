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

## Catalog format

The output from DisPerSE is re-arranged in an [HDF5](https://www.hdfgroup.org/solutions/hdf5) file with a structure similar to other THESAN data product.
Each catalog contains three main groups: an `Header`, whose *attributes* contain general information about the simulation and filaments,
a `CriticalPoint` group, whose *datasets* contain the properties of the critical points of the density field identified by DisPerSE, and
a `Filaments` group, whose *datasets* host the propertied of the filaments identified by DisPerSE.

The available attributes in the `Header` group are listed here.

### Header attributes

| Attribute | Dimensions | Units | Description |
|---|---|---|---|
| BoundingBox | 6 | kpc/h | Coordinates of two corners of the bounding box (computed by DisPerSE) that encloses all tracer points. The six values correspond to \( x_{min}, y_{min}, z_{min}, x_{max}, y_{max}, z_{max} \) of the tracers. |
| BoxSize | 1 | ckpc/h | Spatial extent of the periodic box (in comoving units). |
| HubbleParam | 1 | 100 km/s/Mpc | Hubble constant (little \(h\) in standard units). |
| NumCriticalPoints | 1 | - | Number of critical points identified by DisPerSE. |
| NumDimensions | 1 | - | Number of dimensions of the space of tracer points. Always equal to 3 for THESAN. |
| NumFilaments | 1 | - | Number of filaments identified by DisPerSE. |
| Omega0 | 1 | - | The cosmological density parameter for matter. |
| OmegaBaryon | 1 | - | The cosmological density parameter for baryonic matter. |
| OmegaLambda | 1 | - | The cosmological density parameter for the cosmological constant. |
| Redshift | 1 | - | The redshift corresponding to the current output. |
| Time | 1 | - | The scale factor \(a=1/(1+z)\) corresponding to the current output. |
| UnitLength_in_cm | 1 | - | Code length units in cm. |
| UnitMass_in_g | 1 | - | Code mass units in g. |
| UnitVelocity_in_cm_per_s | 1 | - | Code velocity units in cm/s. |

The available datasets in the `CriticalPoints` and `Filaments` groups are listed here.

### CriticalPoints datasets

| Dataset | Dim. | Units | Description |
|---|---|---|---|
| AssociatedFields | (NumCriticalPoints, NumAssociatedFields) | - | Value of fields associated to each critical point. The number and name of these fields are stored in the `NumAssociatedFields` and `AssociatedFieldsNames` attributes of the `CriticalPoints` dataset |
| BoundaryFlag | NumCriticalPoints | - | |
| Coordinates | (NumCriticalPoints, 3) | kpc/h | Coordinates of each critical point |
| CriticalIndex | NumCriticalPoints | - | Critical index of each critical point |
| DensityDTFE | NumCriticalPoints | ? | Density estimate for each Critical point |
| IndexFilament | NumFilaments | - | Index of the filament associated to each critical point |
| IndexOtherFilamentExtreme | NumFilaments | - | Index of the critical point at the other extreme of the filament associated to each given critical point |
| NumConnectedFilaments | NumCriticalPoints | - | Number of filaments connected to each critical point |
| OffsetFilamentAndExtreme | NumCriticalPoints | - | Offset of the first filament or critical point associated to each critical point in the `IndexFilament` and `IndexOtherFilamentExtreme` arrays |
| PersistencePairIndex | NumCriticalPoints | - | Index of the persistence pair of each critical point |

### Filaments datasets

| Dataset | Dim. | Units | Description |
|---|---|---|---|
| AssociatedFields | (NumFilaments, NumAssociatedFields) | - | Value of fields associated to each filament. The number and name of these fields are stored in the `NumAssociatedFields` and `AssociatedFieldsNames` attributes of the `Filament` dataset |
| CoordinatesSamplingPoints | (NumSamplingPoints, 3) | kpc/h | Coordinates of the sampling points associated to each filament |
| IndexExtremalCriticalPoints | (Nfilaments, 2) | - | Index of the critical points at the extremities of each filament |
| NumSamplingPoints | NumFilaments | - | Number of sampling points associated to each filament |
| OffsetSamplingPoints | NumFilaments | - | Offset of the first sampling point or critical points pair associated to each filament in the `CoordinatesSamplingPoints` and `IndexExtremalCriticalPoints` arrays |
