import matplotlib.pyplot as plt
import pandas as pd

from src.microspotreader import *

img_loader = ImageLoader()
img_loader.set(invert_image=True)
image = img_loader.prepare_image(r"example_files\part2_a12-l22.tif")
# Spot Detection
spot_detector = SpotDetector(image)
spot_list = spot_detector.initial_detection(132)

# Grid detection for spot correction
grid_detector = GridDetector(image, spot_list)

grid = grid_detector.detect_grid()

# Spot correction
spot_corrector = SpotCorrector(spot_list)
spot_list = spot_corrector.gridbased_spotcorrection(grid)

# Indexing of spots
SpotIndexer(spot_list).assign_indexes(
    row_idx_start=1,
    col_idx_start=1,
)
spot_list.sort(serpentine=False)
# Intensity determination of spots.
spot_list.get_spot_intensities(
    image=image,
    radius=0,
)
spot_list.normalize_by_median()


# halo_detector = HaloDetector(image)
# halo_detector.perform_halo_detection()
# halo_detector.assign_halos_to_spots(spot_list)

# # scaling halos to spot intensities.
# spot_list.scale_halos_to_intensity(0.04)

fig, ax = plt.subplots()
spot_list.plot_image(image, ax=ax)

plt.show()
plt.close()
