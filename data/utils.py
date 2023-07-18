from dataclasses import dataclass


def calculate_slope(x1, x2, y1, y2):
    slope = (y2 - y1) / (x2 - x1)
    return slope


@dataclass
class GraphFilterParams:
    min_screentime: float
    min_edge_weight: float
    node_types_to_include: list()
