# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import numpy as np


def convert_to_polar_coordinates(x_cartesian, y_cartesian, radius, center_x=0.25, center_y=0):
    if not isinstance(x_cartesian, np.ndarray):
        x_cartesian = np.array(x_cartesian)
    if not isinstance(y_cartesian, np.ndarray):
        y_cartesian = np.array(y_cartesian)

    thetas = x_cartesian * (2 * np.pi / x_cartesian.max())
    radiuses = np.abs(y_cartesian + radius * 2.5)

    # if max_value is not None:
    #     radius_differences = radiuses - radius
    #     max_radius = radius_differences.max()
    #     normalized_radiuses_diffs = (radius_differences / max_radius) * max_value
    #     radiuses =  radius + normalized_radiuses_diffs

    x_polar = np.array([radiuses[i] * np.cos(thetas[i]) for i in range(len(radiuses))]) + center_x
    y_polar = np.array([radiuses[i] * np.sin(thetas[i]) for i in range(len(radiuses))]) + center_y

    return {'x': x_polar, 'y': y_polar}
