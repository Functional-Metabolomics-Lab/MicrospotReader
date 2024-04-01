import imageio.v3 as iio
import numpy as np
from skimage.color import rgb2gray
from skimage.util import invert


class ImageLoader:
    settings: dict = {"invert_image": False}

    def __init__(self) -> None:
        self.image = None

    def load(self, filepath: str):
        """Loads an image from filepath

        Args:
            filepath (str): filepath of the image.

        Returns:
            np.array: array of loaded image
        """
        self.image = iio.imread(filepath)
        return self.image

    def rgb_to_grayscale(self):
        """Converts an rgb or rgba image to grayscale.

        Returns:
            np.array: grayscale image
        """
        assert len(self.image.shape) == 3, "Array dimensions out of bounds!"
        match self.image.shape[2]:
            case 3:
                self.image = rgb2gray(self.image)
            case 4:
                self.image = rgb2gray(self.image[:, :, 0:3])
            case _:
                raise Exception("Image shape out of bounds. No rgb or rgba")

        return self.image

    def invert_image(self):
        """Inverts the colors of the image

        Returns:
            np.array: inverted image
        """
        self.image = invert(self.image)
        return self.image

    def prepare_image(self, filepath: str):
        """Image preparation workflow for the microspot reader

        Args:
            filepath (str): Filepath to the image that should be prepared

        Returns:
            array: prepared image.
        """
        self.load(filepath=filepath)

        if len(self.image.shape) != 2:
            self.rgb_to_grayscale()

        if self.settings["invert_image"]:
            self.invert_image()

        return self.image
