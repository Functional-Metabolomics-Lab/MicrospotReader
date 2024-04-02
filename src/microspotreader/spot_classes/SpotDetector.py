import numpy as np
from skimage.feature import canny
from skimage.filters.rank import equalize
from skimage.morphology import disk
from skimage.transform import hough_circle, hough_circle_peaks
from skimage.util import img_as_ubyte

import src.microspotreader.spot_classes.Spot as Spot
import src.microspotreader.spot_classes.SpotList as SpotList


class SpotDetector:
    settings: dict = {
        "edge_detection": {
            "sigma": 10,
            "low_threshold": 0.001,
            "high_threshold": 0.001,
        },
        "circle_detection": {
            "min_distance_px_x": 70,
            "min_distance_px_y": 70,
            "smallest_radius_px": 20,
            "largest_radius_px": 30,
            "detection_threshold": 0.3,
        },
    }

    edge_img = None
    tested_radii = None
    hough_transform = None
    spot_list = None

    def __init__(self, image: np.array) -> None:
        self.image: np.array = image

    def get_settings(self):
        return self.settings.copy()

    def change_settings_dict(self, settings: dict):
        assert type(settings) is dict, "Use a dictionary to change settings."

        for key, value in settings.items():
            if type(value) is dict:
                for k, v in value.items():
                    self.settings[key][k] = v
            else:
                self.settings[key] = value

    def get_image_edges(self):
        """Perform canny edge detection using the values from 'edge_detection' in self.settings.

        Returns:
            array: Boolean image with True for pixels containing an edge and False for pixels not containing an edge.
        """
        histeq_img = equalize(img_as_ubyte(self.image), disk(50))
        self.edge_img = canny(
            image=histeq_img,
            sigma=self.settings["edge_detection"]["sigma"],
            low_threshold=self.settings["edge_detection"]["low_threshold"],
            high_threshold=self.settings["edge_detection"]["high_threshold"],
        )

        return self.edge_img

    def get_hough_transform(self):
        """Perform a circle hough transform on result from canny edge detection using the radii from 'circle_detection' in self.settings.

        Returns:
            array: 3D array containing the circle hough transform for all radii in the specified range.
        """

        assert (
            self.edge_img is not None
        ), "No edge-detection was performed, run self.get_image_edges!"

        self.tested_radii = np.arange(
            self.settings["circle_detection"]["smallest_radius_px"],
            self.settings["circle_detection"]["largest_radius_px"] + 1,
        )

        self.hough_transform = hough_circle(
            image=self.edge_img, radius=self.tested_radii
        )

        return self.hough_transform

    def detect_spots(self, spot_nr: int):
        """Performs initial spot detection after hough transform.

        Args:
            spot_nr (int): Number of Spots to be detected in the image

        Returns:
            SpotList: List of initially detected spots.
        """
        assert (
            self.hough_transform is not None
        ), "No hough-transform was performed, run self.get_hough_transform!"

        _, spot_x, spot_y, spot_rad = hough_circle_peaks(
            hspaces=self.hough_transform,
            radii=self.tested_radii,
            total_num_peaks=spot_nr,
            min_xdistance=self.settings["circle_detection"]["min_distance_px_x"],
            min_ydistance=self.settings["circle_detection"]["min_distance_px_y"],
            threshold=self.settings["circle_detection"]["detection_threshold"]
            * self.hough_transform.max(),
        )

        self.spot_list = SpotList.SpotList(
            *[
                Spot.Spot(x=x, y=y, radius=rad, note="Initial Detection")
                for x, y, rad in zip(spot_x, spot_y, spot_rad)
            ]
        )
        return self.spot_list

    def initial_detection(self, spot_nr: int):
        """Performs the entire workflow for initial spot detection.

        Args:
            spot_nr (int): Number of Spots to be detected in the image

        Returns:
            SpotList: List of initially detected spots.
        """
        self.get_image_edges()
        self.get_hough_transform()
        self.detect_spots(spot_nr)

        return self.spot_list


if __name__ == "__main__":
    test = SpotDetector(np.array([[0, 0], [0, 0]]))
    test.inital_detection(1)
