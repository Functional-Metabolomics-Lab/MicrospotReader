from dataclasses import dataclass


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
