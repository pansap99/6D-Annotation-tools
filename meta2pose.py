from utils.io import Meta2Pose, Meta2pose_args
import tyro

if __name__ == "__main__":
    args = tyro.cli(Meta2pose_args)
    meta2pose = Meta2Pose(args.marker_file, None, None, args.results_dir,vis=False)
    poses = meta2pose()
    print(poses)