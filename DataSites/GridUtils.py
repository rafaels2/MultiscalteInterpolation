from collections import namedtuple

import numpy as np
from matplotlib import pyplot as plt

from Config.Options import options


def calculate_max_derivative(original_function, grid_params, manifold):
    """Calculate max directional differences in the function on the test grid"""

    def derivative(x, y):
        y = -y
        delta = grid_params.fill_distance / 2
        evaluations_around = [
            original_function(x + (delta / np.sqrt(2)), y + (delta / np.sqrt(2))),
            original_function(x, y + delta),
            original_function(x, y - delta),
            original_function(x + (delta / np.sqrt(2)), y - (delta / np.sqrt(2))),
            original_function(x + delta, y),
            original_function(x - (delta / np.sqrt(2)), y + (delta / np.sqrt(2))),
            original_function(x - delta, y),
            original_function(x - (delta / np.sqrt(2)), y - (delta / np.sqrt(2))),
        ]
        f_0 = original_function(x, y)

        _result = max(
            [
                manifold.distance(direction, f_0) / delta
                for direction in evaluations_around
            ]
        )
        return _result

    sites = options.get_option("generation_method", "grid")(*grid_params)
    evaluation = options.get_option("data_storage", "grid")(
        sites, 1, derivative, grid_params.fill_distance
    ).evaluation

    result = np.zeros_like(evaluation, dtype=np.float32)
    for index in np.ndindex(result.shape):
        result[index] = evaluation[index]

    return result


def evaluate_on_grid(
    func, grid_size, resolution, scale, points=None, should_log=False, dtype=object
):
    """Probably deprecated, use the evaluation in {Storage} module"""
    if points is not None:
        x, y = points
    else:
        x, y = options.get_option("generation_method", "grid")(
            -grid_size,
            grid_size,
            -grid_size,
            grid_size,
            scale / resolution,
            should_ravel=False,
        )

    z = np.zeros(x.shape, dtype=dtype)
    print("Z shape", z.shape)

    for index in np.ndindex(x.shape):
        if index[1] == 0 and should_log:
            print("current percentage: ", index[0] / x.shape[0])
        z[index] = func(x[index], y[index])

    return x, y, z


# Defining the parameters for generation and storage of data.
GridParameters = namedtuple(
    "GridParameters", ["x_min", "x_max", "y_min", "y_max", "fill_distance"]
)


def symmetric_grid_params(grid_size, fill_distance):
    return GridParameters(-grid_size, grid_size, -grid_size, grid_size, fill_distance)


def main():
    def func(x, y):
        if x > 0 and y > 0.2:
            return 10
        else:
            return 0

    evaluation = evaluate_on_grid(func, 1, 10, 0.8, dtype=float)
    import ipdb

    ipdb.set_trace()
    plt.figure()
    plt.imshow(evaluation)
    plt.colorbar()
    plt.show()


if __name__ == "__main__":
    main()
