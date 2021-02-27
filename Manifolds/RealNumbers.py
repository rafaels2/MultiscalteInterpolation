import numpy as np

from .AbstractManifold import AbstractManifold
from . import register_manifold


@register_manifold("numbers")
class RealNumbers(AbstractManifold):
    def exp(self, x, y):
        return x + y

    def log(self, x, y):
        return y - x

    def _to_numbers(self, x):
        return x

    def zero_func(self, x_0, x_1):
        return 2

    def _get_geodetic_line(self, x, y):
        def line(t):
            return x + (y - x) * (1 - t)
        return line


@register_manifold("no_norm")
class NoNormalizationNumbers(RealNumbers):
    def average(self, values_to_average, weights):
        return sum([w_i * v_i for w_i, v_i in zip(weights, values_to_average)])


class PositiveNumbers(RealNumbers):
    def exp(self, x, y):
        return x ** y

    def log(self, x, y):
        # TODO: Think if we want to change to log(1+x)
        if x == 1:
            epsilon = 0.00001
        else:
            epsilon = 0
        return np.log(y) / (np.log(x) + epsilon)
