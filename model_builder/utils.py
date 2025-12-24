import numpy as np


def point_on_arc(center: list[float], radius: float, theta: float) -> list[float]:
    """
    Returns a point [x, y, 0] in polar coordinates with respect to a given center and radius.
    """
    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)
    return [x, y, 0]


def get_normal_np(p1: list[float], p2: list[float], p3: list[float]) -> list[float]:
    import math

    try:
        v = [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]]
        w = [p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2]]
        x = (v[1] * w[2]) - (v[2] * w[1])
        y = (v[2] * w[0]) - (v[0] * w[2])
        z = (v[0] * w[1]) - (v[1] * w[0])
        modulo = math.sqrt(x * x + y * y + z * z)
        v_normal = [x / modulo, y / modulo, z / modulo]
        return v_normal
    except ZeroDivisionError:
        v_normal: list[float] = [0, 0, 0]
    return v_normal
