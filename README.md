# customize-atlas
Utility to combine rois in neuroimaging  atlases

## Info
This initial version of the tool supports 3D non-probabilistic atlases with sequential roi numbers used to represent rois starting from 1. When 2 or more Rois are merged into one then the smallest original roi number is used to respresent the new merged roi.

## usage
`customize-atlas.py` can be run from the command line as follows:
`python3 customize-atlas.py [atlas_filename] [label_filename] [assignment_filename] --new_atlas_file [my_new_atlas_filename] --new_label_file [my_new_label_filename]`

where

`[atlas_filename]` is the file path of the original atlas file
`[label_filename]` is a text file that contains each roi label on a single text line (see `Brainnetome_basic.txt` in `brainnetome-example` folder)
`[assignment_filename]` is a text file that assigns a new roi to a set of existing roi labels on a single text line without spaces (see `assign.txt` in `brainnetome-example` folder)

So for example the line:

`HippAmyg_LR_21_21=Hipp_L_2_2,Hipp_R_2_2,Amyg_L_2_1,Amyg_R_2_1`

will create a new ROI called HippAmyg_LR_21_21 from the rois Hipp_L_2_2,Hipp_R_2_2,Amyg_L_2_1 and Amyg_R_2_1.
In this example because Amyg_L_2_1 has the smallest roi number (i.e. 211 as determined from the label file `Brainnetome_basic.txt`) then the new ROI will initially have 211 as its roi number. Of course this could change if additional assignments in the assignment file cause knock-on changes.


## outputs
if `--new_atlas_file` and `--new_label_file` are not defined then the changed atlas file is automatically stored using the original filename with `_custom.nii.gz` as the suffix. The same will occur with the label file with `_custom.txt` as the suffix. 


## test
Testing can be carried out on the provided example as follows:

### Specifying new names for atlas and label

`python3 customize-atlas.py BNA-maxprob-thr0-2mm.nii.gz Brainnetome_basic.txt assign.txt my_new_atlas.nii.gz my_new_label.txt`

### Using defaults

`python3 -m pdb customize-atlas.py BNA-maxprob-thr0-2mm.nii.gz Brainnetome_basic.txt assign.txt`
