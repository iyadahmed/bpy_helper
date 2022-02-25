import numpy as np


# Based on https://github.com/sdg002/RANSAC/blob/f3d8ae9377792f049df6f188e87977f5adc54193/Algorithm/BullockCircleFitting.py#L84
# Original method by Randy Bullock https://dtcenter.org/sites/default/files/community-code/met/docs/write-ups/circle_fit.pdf
def fit_circle_through_points_2d(points_2d: np.ndarray):
    """Fit circle with boundary passing through points"""
    x = points_2d[:, 0]
    y = points_2d[:, 1]
    x_mean, y_mean = points_2d.mean(axis=0)

    u = x - x_mean
    v = y - y_mean

    Suu = (u * u).sum()
    Svv = (v * v).sum()
    Suv = (u * v).sum()
    Suuu = (u * u * u).sum()
    Svvv = (v * v * v).sum()
    Suvv = (u * v * v).sum()
    Svuu = (v * u * u).sum()

    C1 = 0.5 * (Suuu + Suvv)
    C2 = 0.5 * (Svvv + Svuu)
    Uc = (C2 * Suv - C1 * Svv) / (Suv * Suv - Suu * Svv)
    Vc = (C1 * Suv - C2 * Suu) / (Suv * Suv - Suu * Svv)
    alpha = Uc**2 + Vc**2 + (Suu + Svv) / len(points_2d)

    real_x = x_mean + Uc
    real_y = y_mean + Vc
    radius = alpha**0.5
    return real_x, real_y, radius
