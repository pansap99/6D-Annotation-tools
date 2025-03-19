# 6D-Annotation-tools

## Installation
```
conda create -n 6dannot python=3.10 -y
conda activate 6dannot
pip install -r requirements.txt
```

## Overview

The 6D-Annotation tool is based on Agisoft Metashape and provides a way to extract 6D poses from a set of 2D-3D markers.
The approach consists of three main steps:
1. Load the images in Agisoft Metashape and get the structure from motion (SfM) results
2. Extract 2D-3D markers from the SfM results
3. Use the 2D-3D markers to extract 6D poses

## Usage

### 1. Load the images in Agisoft Metashape and get the structure from motion (SfM) results

1. Load the images in Agisoft Metashape by dragging and dropping into the chunk
2. Go to "Workflow" -> "Align photos", disable "Generic preselection" and set the accuracy to "High". Then, click "Ok".

### 2. Agisoft Metashape + Blender

1. Open Blender while keeping the Agisoft Metashape window open.
2. Spot a suitable keypoint both in the 3D model and the 2D image. 
    - Click in the image and select "Add marker", name it starting from 1.
    - Select the same point in the 3D model using the Blender picker and fill the coordinates in the "Reference" pane. To do that you have to activate Edit mode in the upper left corner. Also switch to "Geometry Nodes" tab. In the left pane activate the "Show only selected" option. Now each time you select a 3D point its coordinates are shown. These are the coordinates you fill in the "Reference" pane in Metashape.

3. Repeat this process until you have more than 4 markers in each aligned frame. 

Note: Keep in mind that Metashape will automatically infer the markers locations in other frames (blue flags) so you don't have to do it in every image. Usually 5-6 diverge images suffice. The flags must be blue or green. If they are gray you have to mannually move the marker to become green.

### 2. Extract 2D-3D markers from the SfM results

Export the markers from Metashape by going to "File" -> "Export" -> "Markers". Save the file as an XML file.

### 3. Use the 2D-3D markers to extract 6D poses

Run:
```
python meta2pose.py --marker_file <path_to_markers.xml> --results_dir <path_to_results>
```
