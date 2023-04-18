import os
import nibabel
import numpy
from nilearn.image import new_img_like
import gzip

def get_key_from_label(d,val):
    keys = [k for k,v in d.items() if v["label"] == val ]
    if keys:
        return keys[0]
    return None

def save_image_to_disk(img,newimgdata,output_file):
       
    img_dtype = img.header.get_data_dtype()

    data_to_save=newimgdata.astype(img_dtype)

    new_img=new_img_like(img, data_to_save,copy_header=True)
    nibabel.nifti1.save(new_img, output_file)  


def get_parser():
    from argparse import ArgumentParser
    from argparse import RawTextHelpFormatter

    parser = ArgumentParser(description="Customize Atlas."
        "Assumes that ROI indices are contiguous and start from 1.",formatter_class=RawTextHelpFormatter)
    parser.add_argument('atlas_file', action='store',
        help='3D MaxProb Atlas.')
    parser.add_argument('label_file', action='store',
        help='Label text file.')
    parser.add_argument('assign_file', action='store',
        help='Assignment file specifying merged rois')
    parser.add_argument('--new_atlas_file', action='store',
        help='new atlas file')
    parser.add_argument('--new_label_file', action='store',
        help='new label file')
    parser.add_argument('--action_type', action='store',
        help='governs how atlas is customized',default="contig_down")
    return parser


def customize_atlas(atlas_file, label_file, assignment_file, output_file,output_label,action_type):

    ATLASCHANGE = False
    ATLASEXCEPTION = False

    atlasimg = nibabel.load(atlas_file)
    atlasdata = atlasimg.get_fdata()

    with open(label_file,'r') as infile:
        labelLines = infile.readlines()

    with open(assignment_file,'r') as infile:
        assignmentLines = infile.readlines()

    labellist=[x.replace('\n','') for x in labelLines]
    assignments=[x.replace('\n','') for x in assignmentLines]

    labeldict={}
    labelid=0
    for labelentry in labellist:
        labelid=labelid+1
        labeldict[labelid]={}
        labeldict[labelid]["label"]=labelentry
        labeldict[labelid]["status"]="orig"
        labeldict[labelid]["status_history"]=labelentry
        labeldict[labelid]["roi_history"]=str(labelid)
    
    for assignment in assignments:
        try:
            indices=[]
            newlabel=assignment.split('=')[0]
            oldlabels=assignment.split('=')[1].split(',')
            for oldlabel in oldlabels:
                labelid = get_key_from_label(labeldict,oldlabel)
                if labelid is not None:
                    indices.append(labelid)


            indices.sort()
            
            # assign minimum roi value to related rois
            if action_type == "contig_down":
                for index in range(len(indices)):
                    if index == 0:
                        min_index=indices[index]
                        labeldict[min_index]["label"]=newlabel
                        labeldict[min_index]["status"]="roi_new"
                        labeldict[min_index]["status_history"]=labeldict[min_index]["status_history"] + ' > ' + assignment
                        labeldict[min_index]["roi_history"]= labeldict[min_index]["roi_history"] + ' > ' + ','.join([str(x) for x in indices])
                    else:
                        old_index = indices[index] 
                        labeldict[old_index]["label"]=labeldict[old_index]["label"]
                        labeldict[old_index]["status"]="roi_new_merge"
                        labeldict[old_index]["status_history"]=labeldict[old_index]["status_history"] + ' > ' + assignment
                        labeldict[old_index]["roi_history"]= labeldict[old_index]["roi_history"] + ' > ' + str(min_index)

                        atlasmask = atlasdata[:,:,:] == old_index
                        atlasdata[atlasmask]=min_index
                        ATLASCHANGE = True

                # shift roi values so they are contiguous
                newlabeldict={}
                new_label_index=indices[1]
                target_index = new_label_index
                for key, value in labeldict.items():
                    if key < new_label_index:
                        newlabeldict[key]=labeldict[key]
                    elif key >= new_label_index:
                        if labeldict[key]["status"] == "roi_new_merge":
                            continue
                        else:
                            newlabeldict[target_index] = labeldict[key]
                            newlabeldict[target_index]["label"] = labeldict[key]["label"]
                            newlabeldict[target_index]["status"] = "shifted"
                            newlabeldict[target_index]["status_history"]=labeldict[key]["status_history"] + ' > ' + newlabeldict[target_index]["status"]
                            newlabeldict[target_index]["roi_history"]= labeldict[key]["roi_history"] + ' > ' + str(target_index)
                            atlasmask = atlasdata[:,:,:] == key
                            atlasdata[atlasmask]=target_index
                            ATLASCHANGE = True
                            target_index = target_index + 1
            else:
                print("Action type {} not recognized - aborting atlas change".format(action_type))
                ATLASCHANGE = False
                break

            if len(newlabeldict)>0:
                labeldict=newlabeldict.copy()
                
        except Exception as e:
            print("Exception thrown: {}".format(str(e)))
            print("Problem processing assignment {} - atlas change will be aborted".format(assignment))
            ATLASEXCEPTION = True


        if ATLASCHANGE and not ATLASEXCEPTION:
            save_image_to_disk(atlasimg, atlasdata, output_file)
            with open(output_label,'w') as outfile:
                for key, value in newlabeldict.items():
                    labelstring = newlabeldict[key]["label"] + '  (' + newlabeldict[key]["status_history"] + ' : ' + newlabeldict[key]["roi_history"] + ')'
                    outfile.write('{}\n'.format(labelstring))


def main():

    opts = get_parser().parse_args()

    atlas_file=os.path.abspath(opts.atlas_file)

    label_file=os.path.abspath(opts.label_file)

    assign_file=os.path.abspath(opts.assign_file)

    if opts.new_atlas_file is None:
        new_atlas_file = os.path.join(os.path.dirname(atlas_file),os.path.basename(atlas_file).split('.nii')[0] + '_custom.nii.gz')
    else:
        new_atlas_file=os.path.abspath(opts.new_atlas_file)

    if opts.new_label_file is None:
        new_label_file = os.path.join(os.path.dirname(label_file),os.path.basename(label_file).split('.')[0] + '_custom.txt')
    else:
        new_label_file=os.path.abspath(opts.new_label_file)

    action_type=opts.action_type


    customize_atlas(atlas_file, label_file, assign_file, new_atlas_file, new_label_file, action_type)


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
    main()