from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from skimage.filters import threshold_otsu
from skimage.morphology import (
    binary_dilation,
    binary_opening,
    disk,
    reconstruction,
    remove_small_objects,
    skeletonize,
)
from skimage.transform import hough_circle, hough_circle_peaks

import src.microspotreader.halo_classes.Halo as Halo

if TYPE_CHECKING:
    import src.microspotreader.spot_classes.SpotList as SpotList


class HaloDetector:
    settings: dict = {
        "preprocessing": {
            "disk_radius_opening": 5,
            "minimum_object_size_px": 800,
            "disk_radius_dilation": 10,
        },
        "circle_detection": {
            "min_distance_px_x": 70,
            "min_distance_px_y": 70,
            "smallest_radius_px": 40,
            "largest_radius_px": 100,
            "detection_threshold": 0.2,
        },
        "halo_assignment": {"distance_threshold_px": 15},
    }

    def __init__(self, image: np.array) -> None:
        self.image = image
        self.halo_list = None

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

    def filter_regional_maxima(self):
        """Creates an image with removed background via morphological reconstruction. As desribed @: https://scikit-image.org/docs/stable/auto_examples/color_exposure/plot_regional_maxima.html#sphx-glr-auto-examples-color-exposure-plot-regional-maxima-py

        Returns:
            array: Image with background removed
        """
        mask = np.copy(self.image)
        seed = np.copy(self.image)
        seed[1:-1, 1:-1] = self.image.min()
        dilated = reconstruction(seed, mask, method="dilation")
        filtered_img = self.image - dilated
        return filtered_img

    def create_halo_skeleton(
        self,
        filtered_image: np.array,
        opening_disk_radius: int,
        min_object_size: int,
        dilation_disk_radius: int,
    ):
        """Creates a skeleton of (ideally) only the halos in the given image. To facilitate detection of halos, the skeleton does not have a width of 1 but rather a width defined by the dilation_disk_radius.

        Args:
            filtered_image (np.array): Image returned by the filter_regional_maxima method
            min_object_size (int): minimum size of objects in the binary mask of the image before skeletonization
            dilation_disk_radius (int): diskradius for binary dilation after skeletonization. the bigger this value, the thicker the skeleton.

        Returns:
            np.array: binary skeleton of the given image, ideally only containing the skeletons of halos.
        """
        mask = filtered_image > threshold_otsu(filtered_image)
        mask = remove_small_objects(mask, min_size=min_object_size)

        # Opening of halos such that they are not completely filled. -> would lead to a single point as a skeleton
        opened_mask = binary_opening(mask, disk(opening_disk_radius))

        skeleton = skeletonize(opened_mask)
        return binary_dilation(skeleton, disk(dilation_disk_radius))

    def detect_halos(self, skeletonized_image: np.array):
        """Detects Halos in a skeletonized image containing circular objects

        Args:
            skeletonized_image (np.array): Image obtained through the create_halo_skeleton method

        Returns:
            List[Halo]: List of Halo objects found in the given image
        """
        tested_radii = np.arange(
            self.settings["circle_detection"]["smallest_radius_px"],
            self.settings["circle_detection"]["largest_radius_px"] + 1,
        )
        # Circle detection by hough transform.
        hough_transform = hough_circle(skeletonized_image, tested_radii)
        _, cx, cy, radii = hough_circle_peaks(
            hough_transform,
            tested_radii,
            min_xdistance=self.settings["circle_detection"]["min_distance_px_x"],
            min_ydistance=self.settings["circle_detection"]["min_distance_px_y"],
            threshold=self.settings["circle_detection"]["detection_threshold"]
            * hough_transform.max(),
        )

        return [Halo(x, y, rad) for x, y, rad in zip(cx, cy, radii)]

    def perform_halo_detection(self):
        """Performs the entire halo detection pipeline using the settings in self.settinfs

        Returns:
            List[Halo]: List of Halos detected in the given image.
        """
        filtered_img = self.filter_regional_maxima()
        skeletonized_img = self.create_halo_skeleton(
            filtered_image=filtered_img,
            opening_disk_radius=self.settings["preprocessing"]["disk_radius_opening"],
            min_object_size=self.settings["preprocessing"]["minimum_object_size_px"],
            dilation_disk_radius=self.settings["preprocessing"]["disk_radius_dilation"],
        )

        self.halo_list = self.detect_halos(skeletonized_image=skeletonized_img)
        return self.halo_list

    def assign_halos_to_spots(self, spot_list: SpotList.SpotList):
        """Assigns a halo to a spot if their coordinates match. A match is defined by a distance threshold given by self.settings.

        Args:
            spot_list (SpotList): List of spots to assign halos to.
        """
        for spot in spot_list:
            for halo in self.halo_list:
                distance = np.linalg.norm(
                    np.array((halo.x, halo.y)) - np.array((spot.x, spot.y))
                )
                if distance < self.settings["halo_assignment"]["distance_threshold_px"]:
                    spot.halo_radius = halo.radius

    def plot_halo_locations(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots()

        x_coords = [halo.x for halo in self.halo_list]
        y_coords = [halo.y for halo in self.halo_list]

        ax.scatter(x_coords, y_coords, marker="o", color="magenta")
