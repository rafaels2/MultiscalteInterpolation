import numpy as np


def original_function(x, y):
    return np.sin(4*x)*np.cos(5*y) + 5 * (np.exp(-x**2 - y**2))

