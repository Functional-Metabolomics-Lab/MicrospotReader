from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


@dataclass
class Peak:
    number: int
    index: int
    start_idx: int
    end_idx: int
    retention_time: float
    start_RT: float
    end_RT: float
    intensity: float
    AUC: float
    correlated_feature_ids: list = field(default_factory=lambda: list())
    correlation_coeff_features: list = field(default_factory=lambda: list())

    def get_annotated_featuretable(self, feature_table: pd.DataFrame):
        corr_feature_table = feature_table.loc[self.correlated_feature_ids].copy()
        corr_feature_table[f"correlation_peak{self.number}"] = (
            self.correlation_coeff_features
        )
        return corr_feature_table

    def plot_feature_overlap(
        self,
        feature_table: pd.DataFrame,
        feature_chroms: dict[str, pd.DataFrame],
        activity_table: pd.DataFrame,
        significance: float = 0.8,
    ):

        feature_list = sorted(
            list(zip(self.correlated_feature_ids, self.correlation_coeff_features)),
            key=lambda x: x[1],
        )

        feature_traces = pd.DataFrame(columns=["rt", "int", "id", "corr"])
        legend_label = []
        plot_label = []
        for feature_id, corr_coeff in feature_list:
            if corr_coeff >= significance:
                feature_chrom = feature_chroms[feature_id].copy()

                feature_chrom["id"] = feature_id
                feature_chrom["corr"] = corr_coeff
                feature_chrom["rt"] = (
                    feature_chrom["rt"] - feature_table.loc[feature_id, "RT"]
                )
                feature_chrom["int"] *= 1 / feature_chrom["int"].max()

                feature_traces = pd.concat(
                    [feature_traces, feature_chrom], ignore_index=True
                )
                plot_label.append(
                    f"m/z: {feature_table.loc[feature_id, 'mz']:.4f}, corr. coeff: {corr_coeff:.2f}"
                )
                legend_label.append(f"m/z: {feature_table.loc[feature_id, 'mz']:.4f}")

        grid = sns.FacetGrid(
            feature_traces,
            col="corr",
            hue="corr",
            palette="viridis_r",
            col_wrap=3,
            sharex=True,
            sharey=True,
            xlim=[
                self.start_RT - self.retention_time - 5,
                self.end_RT - self.retention_time + 5,
            ],
        )
        grid.map(plt.plot, "rt", "int", marker="")
        grid.set(xlabel="ΔRT from Peak-maximum [s]", ylabel="Norm. Intensity [a.u.]")
        for idx, ax in enumerate(grid.axes.flat):
            ax.set_title(plot_label[idx])
            ax.tick_params(labelbottom=True)
            ax.plot(
                activity_table["RT"] - self.retention_time,
                activity_table["spot_intensity"] / self.intensity,
                color="k",
            )
            ax.legend(["Feature", "Activity Peak"], loc="lower left")
        return grid.figure
