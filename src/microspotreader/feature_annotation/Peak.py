from dataclasses import dataclass, field

import pandas as pd


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
