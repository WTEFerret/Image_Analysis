#title           : image_measurments.py
#description     : Measure single cells in several channels
#author          : Tobias Wechsler
#usage           : Start the script and choose the input directory and number of channels to analyze. 
#                   The input directory needs to contain a Tiff stack for each channel and a Tiff stack 
#                   with the object identities. In the object identity each individual cell needs to have a unique
#                   color which serves as an ID to create individual ROIs. 
#=======================================================================================================================

# Import modules
import os
import re
from ij import IJ, ImagePlus, ImageStack
from ij.gui import GenericDialog
from ij.plugin.frame import RoiManager
from ij.measure import ResultsTable


# Setup working directory and number of channels
#@ File (label="Choose a position directory", style="directory") workingDir
#@ Integer (label="Select the number of channels", min=1, max=12, value=8) numberChn


def select_input_files(W_DIR, CH_NUM):
    '''
    Prompt user to select input files for analysis
    '''
    file_choices = [f for f in os.listdir(W_DIR) if f.endswith('.tif')] + ['NA']

    gd = GenericDialog("Set input Files")
    for i in range(CH_NUM):
        gd.addChoice("Channel %d:" % i, file_choices, file_choices[-1])
    gd.addChoice("Cell IDs:", file_choices, file_choices[-1])
    gd.showDialog()
    if gd.wasCanceled():
        IJ.log("Operation canceled by user")
        return 1
    ch_img = [os.path.join(W_DIR, gd.getNextChoice()) for _ in range(CH_NUM)]
    id_img = os.path.join(W_DIR,gd.getNextChoice())
    return ch_img, id_img


def create_folder(W_DIR, name):
    '''
    Create a folder if it not already exists and returns the path
    '''
    if not os.path.exists(os.path.join(W_DIR, name)):
        os.makedirs(os.path.join(W_DIR, name))
        IJ.log("Created output directory {0}".format(name))
    else:
        IJ.log("Output directory {0} already exists.".format(name))
    return os.path.join(W_DIR, name)

def create_output_folders(CH_IMG, ID_IMG, W_DIR):
    '''
    Create folders for individual images and ROIs
    '''
    ch_dirs = []
    bin_dir = None
    track_dir = None
    for i, c in enumerate(CH_IMG):
        new_dir = 'C_{0}'.format(i)
        ch_dirs.append(create_folder(W_DIR, new_dir))
        if i > 0:
            create_folder(W_DIR, new_dir + '_BS')


    if ID_IMG != 'NA':
        new_dir = 'IDS'
        id_dir = create_folder(W_DIR, new_dir)

    roi_dir = create_folder(W_DIR, 'ROIs')

    bgr_dir = create_folder(W_DIR, 'BGR')

    return ch_dirs, id_dir, roi_dir, bgr_dir


def save_single_images(CH_IMG, ID_IMG, CH_DIRS, ID_DIR ):
    '''
    Save image stacks to individual images in the respectiv output folder
    '''
    IJ.log("#### SAVE INDV. IMGS ####")

    for d,c in enumerate(CH_IMG):
        stack_to_image(CH_DIRS[d], c)

    if ID_IMG != 'NA':
        stack_to_image(ID_DIR , ID_IMG)

def stack_to_image(folder, img_path):
    '''
    Open imagestack and save individual tif images
    '''
    img =  IJ.openImage(img_path)
    img.hide()
    stack = img.getImageStack()
    img.close()
    filename = os.path.basename(img_path).replace('.tif','')
    for i in range(1,stack.getSize()+1):
        p = stack.getProcessor(i)
        indv = ImagePlus(str(i),p)
        IJ.save(indv, os.path.join(folder, filename + '_T=%d.tif' % i))

def get_id_set(IMG):
    vals = []
    hist = IMG.getRawStatistics().histogram16
    for i in range(1, len(hist)):
        if hist[i] > 0:
            vals.append(i)

    return vals

def create_rois(ROI_DIR, ID_DIR):
    '''
    Create ROIS from object identity image
    '''
    IJ.log("#### CREATE ROIS ####")

    bin_imgs = list_files(ID_DIR, '.tif', 'sort')

    for f in bin_imgs:
        time = get_time_info(f)
        img = IJ.openImage(os.path.join(ID_DIR, f))
        title_ROI = f.replace("_Object Identities","")

        id_set = get_id_set(img)
        for ID in id_set:
            IJ.setRawThreshold(img, ID,ID,'null')

            IJ.run(img, "Analyze Particles...", "size=0-Infinity circularity=0.00-1.00 exclude add")
            
            RM = RoiManager.getInstance()
            if not RM:
                RM = RoiManager(False)

        rois_list = RM.getRoisAsArray()
        RM.reset()

        for i, ID in enumerate(id_set):
            new_name = '{0:02}_{1:04}'.format(time, ID)
            rois_list[i].setName(new_name)
            RM.addRoi(rois_list[i])

        RM.setPosition(time)
        RM.runCommand("Save",os.path.join(ROI_DIR, title_ROI + ".zip"))
        n_rois = RM.getCount()


        RM.reset()
        img.close()
        IJ.log("\tCreated %i ROIs from %s" % (n_rois, f))

    RM = RoiManager.getInstance()
    if not RM:
        RM = RoiManager(False)
    RM.close()


def background_subtraction(CH_DIRS, ROI_DIR, BGR_DIR):
    '''
    Measure the background and subtract the mean value from the image.
    The first channel (phase contrast) is omitted. 
    '''
    IJ.log("#### BACKGROUND SUBTRACTION ####")
    RM = RoiManager(False)

    rois = list_files(ROI_DIR, '.zip', 'sort')
    imgs = [list_files(c_dir, '.tif', 'sort') for c_dir in CH_DIRS[1:]]

    for i, rf in enumerate(rois):
        IJ.showProgress(i, len(rois))
        RM.runCommand('Open', os.path.join(ROI_DIR, rf))
        time = get_time_info(rf)

        n_rois = RM.getCount()

        combine = True
        single_cell = False

        assert (n_rois > 0), 'No ROIs in {0} found'.format(rf) 
        if n_rois == 1:
            single_cell = True

        for j, c_dir in enumerate(CH_DIRS[1:]):
               
            img = IJ.openImage(os.path.join(c_dir,imgs[j][i]))
                    
            if single_cell and combine:
                RM.select(img, 0)
                RM.runCommand(img, "Delete")
                IJ.run(img, "Make Inverse", "")
                RM.runCommand(img, "Add")
                combine = False
            elif combine:
                RM.runCommand(img, "Select All")
                RM.runCommand(img, "Combine")
                RM.runCommand(img, "Delete")
                IJ.run(img, "Make Inverse", "")
                RM.runCommand(img, "Add")
                combine = False
                                        
            results = RM.multiMeasure(img)
            average = results.getStringValue("Mean1", 0)
            average = float(average)
            IJ.log('{0}:{1}'.format(imgs[j][i],average))
            RM.resetMultiMeasureResults()
            RM.runCommand(img, "Deselect")
            IJ.run(img, "Remove Overlay", "")
            IJ.run(img, "Subtract...", "value=%d" % average)
            IJ.save(img, os.path.join(c_dir + '_BS', os.path.basename(imgs[j][i])))

        RM.setPosition(time)
        RM.runCommand("Save", os.path.join(BGR_DIR, rf))
        RM.runCommand(img,"Delete")
        img.close()
    RM.close()


def measure_cells(ROI_DIR, CH_DIRS, ID_DIR):
    '''
    Measures cells and returns the result table.
    The first channel (phase contrast) is omitted. 

    '''
    IJ.log("#### MEASUREMENTS ####")

    RM = RoiManager(False)

    last_line = 0

    rois = list_files(ROI_DIR, '.zip', 'sort')
    imgs = [list_files(c_dir + '_BS', '.tif', 'sort') for c_dir in CH_DIRS[1:]]

    for i, rf in enumerate(rois):
        IJ.showProgress(i, len(rois))

        time = get_time_info(rf)

        RM.runCommand('Open', os.path.join(ROI_DIR, rf))
        n_rois = RM.getCount()
        # Measure fluor. channels

        for j, ch_dir in enumerate(CH_DIRS[1:]):
            img = IJ.openImage(os.path.join(ch_dir + '_BS', imgs[j][i]))
            RM.runCommand(img, "Measure")
            RT = ResultsTable.getResultsTable()

            for k in range(n_rois):
                RT.setValue("Time", last_line + k, time)
                RT.setValue("Channel", last_line + k, os.path.basename(ch_dir) + '_BS')
            last_line += n_rois
            img.close()
        
        RM.reset()

    return RT   
    
def get_time_info(filename):
    '''
    Returns the time-point of an image,
    indicated by the prefix "T=" in the filename
    '''
    time = re.findall('T=\d+', filename)
    return(int(time[0].replace('T=','')))

def list_files(dir_path, file_extension, *args):
    '''
    List files with a specific file extension and optionally sorts the list
    '''
    files = [f for f in os.listdir(dir_path) if f.endswith(file_extension)]
    if 'sort' in args:
        files.sort()
    return files



def run():
        
    # set working directory and number of channels
    W_DIR = str(workingDir)
    CH_NUM = numberChn

    # set input files
    CH_IMG, ID_IMG = select_input_files(W_DIR, CH_NUM)

    # make folders for individual images 
    CH_DIRS, ID_DIR, ROI_DIR, BGR_DIR = create_output_folders(CH_IMG, ID_IMG, W_DIR)
    CH_DIRS.sort()

    # make individual images
    save_single_images(CH_IMG, ID_IMG, CH_DIRS, ID_DIR )

    # create ROIs
    create_rois(ROI_DIR, ID_DIR)

    # background subtraction
    background_subtraction(CH_DIRS, ROI_DIR, BGR_DIR)

    # measurments    
    RESULTS = measure_cells(ROI_DIR, CH_DIRS, ID_DIR)
    RESULTS.save(os.path.join(W_DIR, "Results.csv"))


if __name__ == '__main__':
    run()
    print("END")

