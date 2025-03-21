import json
import os
import dataclasses
import numpy as np

@dataclasses.dataclass
class Meta2pose_args:
    # Path to the extraxted markers.xml 
    marker_file: str
    # Path to camera calibration file (3x3 matrix with ',' as delimiter)
    camera_calib_file: str
    # Path to save results
    results_dir: str


def write_json(data, out_file):
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w') as f:
        json.dump(data, f, indent=2)

def read_camera_calib(calib_file):
    return np.loadtxt(calib_file, delimiter=',').astype(float)

                