# Setting up and running the Zebrafish Segmentation

## Table of Contents
__Installation__

- install Anaconda (Python) and Libraries
- Setting Up Docker and segmentation model

__Run the Segmentation Workflow__

- Running the sort_images_nd2.py Python Script
- Running the segmentation.sh Shell Script to run the Segmentation Model in a Docker Container


### Scripts
__sort_images_nd2.py:__ this script is designed to convert Nikon NIS-Elements ND2 files into individual TIFF files.
It processes each series, timepoint, channel, and Z-stack within the ND2 file and saves them as TIFF images.
The output is organized into directories for each series, with separate subdirectories for 
bright-field (C = 0) and fluorescence images (C > 0).

__segmentation.sh:__ Starts a Docker container to run the segmentation model. A path to the folder containing the 'Images' and 'Fluor' folders, created with the previous script, needs to be provided.

> [!note]
> This guide is written for the setup on Mac or Linux. For the use on Windows the segmentaion.sh script needs to be exchanged with the segmentation.ps1. Other steps can also be slightly different from the description here.

# Installation 

## Install Anaconda and Libraries

### Step 1: Install Anaconda

1. **Download Anaconda**:
   - Visit the [Anaconda website](https://www.anaconda.com/products/individual) and download the Anaconda Installer for macOS.

2. **Install Anaconda**:
   - Open the downloaded `.pkg` file and follow the on-screen instructions to install Anaconda.

3. **Verify Installation**:
   - Open Terminal and type `conda --version` to verify Anaconda is installed.

### Step 2: Create a Conda Environment (Optional)

It's a good practice to create a new environment for your projects. To create one, run:

```bash
conda create --name myenv python=3.8
```

Replace `myenv` with your desired environment name.

Activate your new environment by running:

```bash
conda activate myenv
```

### Step 3: Install nd2reader and skimage Libraries

With an environment activated (or in the base environment), install the required libraries using `conda`:

```bash
conda install -c conda-forge nd2reader scikit-image
```

This command installs `nd2reader` and `scikit-image` (which includes `skimage`) from the Conda-Forge repository.


## Setting Up Docker

### Step 1: Download Docker Desktop

1. Go to the [Docker Hub](https://hub.docker.com/editions/community/docker-ce-desktop-mac/) and download the Docker Desktop application for Mac.

2. Open the downloaded `.dmg` file and drag the Docker icon to your Applications folder to install.

### Step 2: Launch Docker
 Open Docker from your Applications folder. The first launch might take a while as it sets up.
 Once Docker is running, open a Terminal and type:

 ```bash
 docker --version
 ```

  This command will display the Docker version, confirming it's installed.
  
### Step 4: Get the segmentation model as a docker image
The following command downloads and installs our segmentation model:
```bash
docker pull branhongweili/dqbm_cell_seg:v3.1
```

# Run the Segmentation Workflow

## Running the sort_images_nd2.py Python Script

Open Terminal and activate your python environment by running:
```bash
conda activate myenv
```

Navigate to the directory containing the sort_images_nd2.py script:
```bash
cd path/to/the/folder/containing/the/script
```

Run the following with the path to your .nd2-file:
```bash
python3 sort_images_nd2.py path/to/your/nd2file
```
The script creates a position folder for each imaged fish, with a folder named 'Images' containing all the bright field images and a folder named 'Fluor' containing all the fluorescence images.


## Running the segmentation.sh Shell Script to run the Segmentation Model in a Docker Container
**Make the Script Executable (only once)**:
   In Terminal, navigate to the directory containing the script and run:
   ```bash
   chmod +x segmentation.sh 
   ```

**Run the Script**:
   Execute the script by running the following and providing the path to one of the imaged positions (created in the previous step):
   ```bash
   ./segmentation.sh path/to/position/folder
   ```

   This command starts a Docker container, runs the segmentation and saves the resulting segmentation in the position folder.