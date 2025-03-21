from utils.io import Meta2pose_args
from meta2pose import Meta2Pose
import tyro
import numpy as np

if __name__ == "__main__":
    args = tyro.cli(Meta2pose_args)
    meta2pose = Meta2Pose(args.marker_file,args.camera_calib_file, None, args.results_dir)
    poses = meta2pose()