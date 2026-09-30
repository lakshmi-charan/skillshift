import numpy as np


def energy_kwh(timestamps_s, power_w):
    if len(timestamps_s) < 2:
        return 0.0
    return float(np.trapezoid(power_w, x=timestamps_s) / 3.6e6)
