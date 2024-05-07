from collections.abc import MutableSequence
from copy import copy, deepcopy

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import Patch

import src.microspotreader.spot_classes.Spot as Spot


class SpotList(MutableSequence):
    def __init__(self, *args):
        self._list: list[Spot.Spot] = list(args)

    def __getitem__(self, index):
        return self._list[index]

    def __setitem__(self, index, value):
        self._list[index] = value

    def __delitem__(self, index):
        del self._list[index]

    def __len__(self):
        return len(self._list)

    def insert(self, index, value):
        self._list.insert(index, value)

    def __str__(self):
        return str(self._list)

    def __repr__(self):
        return repr(self._list)

    @property
    def mean_intensity_controls(self):
        return np.mean(
            [spot.intensity for spot in self._list if spot.type == "control"]
        )

    @property
    def mean_radius(self):
        """Calculates the mean radius in pixels for the list of spots.

        Returns:
            float: Mean spot radius.
        """
        return np.mean([spot.radius for spot in self._list])

    @property
    def median_radius(self):
        """Calculates the median radius in pixels for the list of spots.

        Returns:
            float: Median spot radius.
        """
        return np.median([spot.radius for spot in self._list])

    @property
    def median_intensity(self):
        return np.median([spot.intensity for spot in self._list])

    def get_indices(self) -> tuple[list[str], list[int]]:
        row_indices = sorted(list(set([spot.row_name for spot in self._list])))
        column_indices = sorted(list(set([spot.col for spot in self._list])))

        return row_indices, column_indices

    def remove_rows(self, row_names: list[str]):
        """Removes spots with a row index in the passed list.

        Args:
            row_names (list[str]): list of row indices to remove from the spot_list.
        """
        assert (
            len([spot for spot in self._list if len(spot.row_name) < 1]) == 0
        ), "Cannot remove rows from list with spots without indices."

        self._list = [spot for spot in self._list if spot.row_name not in row_names]

    def remove_columns(self, column_names: list[int]):
        """Removes spots with a column index in the passed list.

        Args:
            column_names (list[str]): list of column indices to remove from the spot_list.
        """
        assert (
            len([spot for spot in self._list if spot.col < 0]) == 0
        ), "Cannot remove columns from list with spots without indices."

        self._list = [spot for spot in self._list if spot.col not in column_names]

    def copy(self):
        return copy(self)

    def find_topleft_bycoords(self):
        """
        ## Description

        Finds the top-left spot in the list by coordinates of the spots.

        ## Output

        spot-object
        """
        return sorted(self._list, key=lambda s: s.x + s.y)[0]

    def find_topright_bycoords(self):
        """
        ## Description

        Finds the top-right spot in the list by coordinates of the spots.

        ## Output

        spot-object
        """
        return sorted(self._list, key=lambda s: s.x - s.y)[-1]

    def sort(self, serpentine: bool = True, reverse: bool = False):
        """Sorts the spot list by index so that a retention time can be assigned to each spot.

        Args:
            serpentine (bool, optional): If true, sorts in a serpentine manner, where odd rows are sorted ascendingly and even rows are sorted descendingly. If false, sort all rows ascendingly. Defaults to True.
            reverse (bool, optional): Changes the sort direction. Defaults to False.
        """

        # Check if all spots have an index.
        assert (
            len(
                [
                    spot
                    for spot in self._list
                    if spot.row is np.nan and spot.col is np.nan
                ]
            )
            == 0
        ), "Not all spots have been assigned an index, cannot sort list!"

        if serpentine:
            self._list.sort(
                reverse=reverse,
                key=lambda x: x.row * 1000  # row gets a higher value for the sort
                + (x.row % 2)
                * x.col  # If row is odd, add the column value -> sorts row ascendingly
                - ((x.row + 1) % 2)
                * x.col,  # If row is even, subtract the column value -> sorts row descendingly
            )
        else:
            self._list.sort(reverse=reverse, key=lambda x: x.row * 1000 + x.col)

    def get_spot_intensities(self, image: np.array, radius: int = 0):
        """Extracts intensity values for each spot in the list using the specified radius.

        Args:
            image (np.array): Image to extract a spots intensity from
            radius (int, optional): radius of the disk to extract intensity with, if 0 use the spots determined radius. Defaults to 0.
        """
        for spot in self._list:
            spot.get_intensity(img=image, rad=radius)

    def normalize_by_control(self):
        """Normalises the intensities of all spots by dividing by the mean of spot intensities of type 'control'"""
        mean_control_int = self.mean_intensity_controls

        for spot in self._list:
            spot.intensity *= 1 / mean_control_int

    def normalize_by_median(self):
        """Normalises the intensities of all spots by dividing by the median spot intensity."""
        median_int = self.median_intensity

        for spot in self._list:
            spot.intensity *= 1 / median_int

    def reset_intensities(self):
        """Resets the spot intensity to its raw intensity"""
        for spot in self._list:
            spot.intensity = spot.raw_int

    def scale_halos_to_intensity(self, scaling_factor: float):
        """Replaces a spots intensity with its halos radius, scaled using a scaling factor.

        Args:
            scaling_factor (float): factor to scale the halo radius with.
        """
        for spot in self._list:
            if spot.halo_radius > 0:
                spot.intensity = spot.halo_radius * scaling_factor

    def to_df(self):
        """Create a DataFrame from the spotlist

        Returns:
            DataFrame: DataFrame of the SpotList
        """
        spot_df = pd.DataFrame(
            {
                "row": [spot.row for spot in self._list],
                "row_name": [spot.row_name for spot in self._list],
                "column": [spot.col for spot in self._list],
                "type": [spot.type for spot in self._list],
                "x_coord": [spot.x for spot in self._list],
                "y_coord": [spot.y for spot in self._list],
                "radius": [spot.radius for spot in self._list],
                "halo_radius": [spot.halo_radius for spot in self._list],
                "spot_intensity": [spot.intensity for spot in self._list],
                "raw_int": [spot.raw_int for spot in self._list],
                "note": [spot.note for spot in self._list],
            }
        )
        return spot_df

    def from_df(self, df: pd.DataFrame):
        """Creates a SpotList from a Dataframe.

        Args:
            df (pd.DataFrame): dataframe to create the spotlist from.
        """
        for idx, row in df.iterrows():
            self._list.append(
                Spot.Spot(
                    row=row["row"],
                    row_name=row["row_name"],
                    col=row["column"],
                    type=row["type"],
                    x=row["x_coord"],
                    y=row["y_coord"],
                    radius=row["radius"],
                    halo_radius=row["halo_radius"],
                    intensity=row["spot_intensity"],
                    note=row["note"],
                    raw_int=row["raw_int"],
                )
            )
        return self

    def from_list(self, datasets: list):
        """Extends the spotlist by a list of spotlists

        Args:
            datasets (list): list of spotlists.
        """
        for spot_list in datasets:
            self._list.extend(spot_list)
        return self

    def plot_image(self, image: np.array, ax=None):
        if ax is None:
            fig, ax = plt.subplots()

        df = self.to_df()

        ax.imshow(image)

        ax.scatter(
            df.loc[df["note"] == "Initial Detection", "x_coord"],
            df.loc[df["note"] == "Initial Detection", "y_coord"],
            marker="2",
            c="k",
            label="Kept Spots",
        )

        ax.scatter(
            df.loc[df["note"] == "Backfilled", "x_coord"],
            df.loc[df["note"] == "Backfilled", "y_coord"],
            marker="2",
            c="r",
            label="Backfilled Spots",
        )

        ax.set(
            ylabel="Row",
            xlabel="Column",
            xticks=df[df["row"] == df["row"].max()]["x_coord"].sort_values(),
            yticklabels=df["row_name"].unique(),
            yticks=df[df["column"] == df["column"].min()]["y_coord"],
            xticklabels=df["column"].unique(),
        )

        ax.spines[["right", "left", "top", "bottom"]].set_visible(False)
        ax.tick_params(axis="both", which="both", length=0, labelsize=7)

        # Adding legend handles for Text
        handles, labels = ax.get_legend_handles_labels()

        # Adding halo specific items
        if len([spot for spot in self._list if spot.halo_radius > 0]) > 0:
            # Adding legend item for detected halos
            patch = Patch(
                facecolor="white", edgecolor="k", linewidth=0.4, label="Halo Radii"
            )
            handles.append(patch)

            # Displaying all detected Halos with their respective radii.
            halo_df = df[df["halo_radius"] > 0]
            for idx in halo_df.index:
                ax.text(
                    halo_df.loc[idx, "x_coord"] + 12,
                    halo_df.loc[idx, "y_coord"] - 9,
                    f'{halo_df.loc[idx,"halo_radius"]:.0f}',
                    c="white",
                    size=7,
                    path_effects=[pe.withStroke(linewidth=1, foreground="k")],
                )

        ax.legend(
            handles=handles,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.1),
            fancybox=True,
            ncol=5,
        )

    def plot_heatmap(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots()

        df = self.to_df().pivot(
            index="row_name", columns="column", values="spot_intensity"
        )

        sns.heatmap(
            data=df,
            square=True,
            cmap="viridis",
            linewidths=1,
            ax=ax,
        )

        ax.set(ylabel="Row", xlabel="Column")
        ax.tick_params(axis="y", labelrotation=0)

    def plot_scatter(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots()

        df = self.to_df()
        sns.scatterplot(df, x="x_coord", y="y_coord", hue="note")
