import json
import xml.etree.ElementTree as ET
import glob
import tqdm
import os
import dataclasses
from utils.JsonEncoder import NoIndent, NoIndentEncoder
import cv2
import numpy as np

@dataclasses.dataclass
class Meta2pose_args:
    marker_file: str
    # image_dir: str
    # model_3d: str
    results_dir: str
    # vis: bool = False

def write_json_no_indent(data, out_file):
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w') as f:
        json.dump(data, f, indent=2)

class Meta2Pose:

    def __init__(self, marker_file, image_dir, model_3d, camera_intrinsics, dist_coeffs, results_dir='./results',vis=False):
        self.marker_file = marker_file
        self.results_dir = results_dir
        self.K = camera_intrinsics
        self.dist_coeffs = dist_coeffs
        #self.images = glob.glob(image_dir + "/*.png") + glob.glob(image_dir + "/*.jpg")
    
    def __call__(self):
        self._parse_metashape_xml()
        self._meta2pose()
        
        return self.poses
    def _parse_metashape_xml(self, out_dir='./data'):

        xml_tree = ET.parse(self.marker_file)
        root = xml_tree.getroot()
        
        chunk = root[0]
        markers = chunk.find("markers")
        cameras = chunk.find("cameras")
        frames = chunk.find("frames")

        camera_ids = {}
        for cam in cameras:
            camera_ids[cam.get('id')] = cam.get('label')

        markers_3d_dict = {}
        for marker in markers:
            markers_3d_dict[marker.get('id')] = {
                "x": marker[0].get("x"),
                "y": marker[0].get("y"),
                "z": marker[0].get("z")
            }
        
        markers_3d = []
        out_dict = {}

        for c in camera_ids:
            out_dict[camera_ids[c]] = {}
            for m2d in frames[0][0]:
                for loc in m2d:
                    if loc.get('camera_id') == c:
                        out_dict[camera_ids[c]][m2d.get('marker_id')] = {
                            "x": loc.get("x"),
                            "y": loc.get("y")
                        }
        self.markers_3d = markers_3d_dict
        self.markers_2d = out_dict
        write_json_no_indent(out_dict, out_dir + '/2d_markers.json')
        write_json_no_indent(markers_3d_dict, out_dir + '/3d_markers.json')

    def _meta2pose(self):

        poses = {}
        for image_id in self.markers_2d:
            correspodences = []
            for marker_label in self.markers_2d[image_id]:
                marker_3d = self.markers_3d[marker_label]
                marker_2d = self.markers_2d[image_id][marker_label]
                if marker_2d['x'] is not None and marker_2d['y'] is not None and \
                   marker_3d['x'] is not None and marker_3d['y'] is not None and marker_3d['z'] is not None:
                    correspodences.append([
                        float(marker_2d['x']),
                        float(marker_2d['y']),
                        float(marker_3d['x']),
                        float(marker_3d['y']),
                        float(marker_3d['z'])
                    ])
            correspodences = np.array(correspodences)
            if correspodences.shape[0] >= 4:
                _, rvec, tvec, inliers = cv2.solvePnPRansac(
                    correspodences[:, 2:],
                    correspodences[:, :2],
                    self.K,
                    self.dist_coeffs,
                    flags=cv2.SOLVEPNP_EPNP
                )
                rotation = cv2.Rodrigues(rvec)[0].flatten().tolist()
                translation = tvec.flatten().tolist()
                poses[image_id] =[{
                    'cam_2_m2c': rotation,
                    'cam_2_m2c_t': translation,
                    'obj_id': 0
                }]
            else:
                print(f"Not enough correspondences for image {image_id}")
        
        self.poses = poses
        write_json_no_indent(poses, self.results_dir + '/poses.json')

    @staticmethod
    def vis_pose(K,R,t,model_3d,savePath,opacity=0.7):
        pass
                