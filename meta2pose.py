from utils.io import write_json, read_camera_calib
import xml.etree.ElementTree as ET
import cv2
import numpy as np

class Meta2Pose:

    def __init__(self, marker_file,camera_intrinsics, dist_coeffs, results_dir='./results'):
        self.marker_file = marker_file
        self.results_dir = results_dir
        self.K = read_camera_calib(camera_intrinsics)
        self.dist_coeffs = dist_coeffs
    
    def __call__(self):
        self._parse_metashape_xml()
        self._meta2pose()
        
        return self.poses
    def _parse_metashape_xml(self):

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
        write_json(out_dict, self.results_dir + '/2d_markers.json')
        write_json(markers_3d_dict, self.results_dir + '/3d_markers.json')

    def _meta2pose(self):

        poses = {}
        intrinsics = {}
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
                poses[str(int(image_id))] =[{
                    'cam_R_m2c': rotation,
                    'cam_t_m2c': translation,
                    'obj_id': 1
                }]
                intrinsics[str(int(image_id))] = {
                    'cam_K': self.K.flatten().tolist(),
                    'depth_scale': 1.0
                }
            else:
                print(f"Not enough correspondences for image {image_id}")
        
        self.poses = poses
        write_json(poses, self.results_dir + '/poses.json')
        write_json(intrinsics, self.results_dir + '/intrinsics.json')