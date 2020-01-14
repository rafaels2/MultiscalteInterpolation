"""
Issues:
1. should be scaled or have more points
"""

import numpy as np
import numpy.linalg as la
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt

GRID_SIZE = 4
ORIGINAL_SCALE = 2
BASE_RESOLUTION = 3
PLOT_RESOLUTION_FACTOR = 4
DIMENSION = 2
SCALE = 2
NUMBER_OF_SCALES = 3


def wendland(x):
    if x < 0:
        raise ValueError("x should be > 0, not {}".format(x))
    if x > 1:
        return 0
    else:
        return (1 + (4 * x)) * ((1 - x) ** 4)


def interpolate(phi, original_function, points):
    """
    Generating I_Xf(x) for the given kernel and points
    :param phi: Kernel
    :param original_function:
    :param points:
    :return:
    """
    x_axis, y_axis = points
    values_at_points = original_function(x_axis, y_axis)
    points_as_vectors = [np.array([x_0, y_0]) for x_0, y_0 in zip(x_axis, y_axis)]
    kernel = np.array([[phi(x_i, x_j) for x_j in points_as_vectors] for x_i in points_as_vectors])
    coefficients = np.matmul(la.inv(kernel), values_at_points)
    print(kernel)
    def interpolant(x, y):
        return sum(b_j * phi(np.array([x, y]), x_j)
                   for b_j, x_j in zip(coefficients, points_as_vectors))
    return interpolant


def generate_kernel(rbf, scale=1):
    def kernel(x, y):
        # TODO: Maybe scale should be squared?
        return (1 / scale) * rbf(la.norm(x-y) / scale)

    return kernel


def generate_original_function():
    def original_function(x, y):
        return y * (np.sin(x) - 1)

    return original_function


def mse(func_a, func_b, x, y):
    errors = np.zeros(x.shape)
    for index in np.ndindex(x.shape):
        errors[index] = np.square(func_a(x[index], y[index]) - func_b(x[index], y[index]))
    return errors.mean()


def plot_contour(ax, func, grid_size):
    x = np.linspace(-grid_size, grid_size, 2 * PLOT_RESOLUTION_FACTOR * grid_size)
    y = np.linspace(-grid_size, grid_size, 2 * PLOT_RESOLUTION_FACTOR * grid_size)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros(X.shape)
    for index in np.ndindex(X.shape):
        Z[index] = func(X[index], Y[index])
    ax.contour3D(X, Y, Z, 50, cmap='binary')


def generate_grid(grid_size, resolution, scale=1):
    x = np.linspace(-grid_size, grid_size, 2 * resolution * scale * grid_size)
    y = np.linspace(-grid_size, grid_size, 2 * resolution * scale * grid_size)
    x_matrix, y_matrix = np.meshgrid(x, y)
    return x_matrix.ravel(), y_matrix.ravel()


def scaled_interpolation(scale, grid_resolution, grid_size, original_function, rbf):
    x, y = generate_grid(grid_size, grid_resolution, scale)
    phi = generate_kernel(rbf, scale)
    return interpolate(phi, original_function, (x, y))


def main():
    rbf = wendland
    original_function = generate_original_function()

    plt.figure()
    ax = plt.axes(projection='3d')
    plot_contour(ax, original_function, GRID_SIZE)
    plt.show()

    interpolant = scaled_interpolation(
        scale=SCALE,
        grid_resolution=BASE_RESOLUTION,
        grid_size=GRID_SIZE,
        original_function=original_function,
        rbf=rbf
    )
    
    plt.figure()
    ax = plt.axes(projection='3d')
    plot_contour(ax, interpolant, GRID_SIZE)
    plt.show()

    test_x, test_y = generate_grid(GRID_SIZE, BASE_RESOLUTION * PLOT_RESOLUTION_FACTOR ,SCALE)
    print("MSE was: ", mse(original_function, interpolant, test_x, test_y))


if __name__ == "__main__":
    main()


def nonscaled_interpolation_main():
    rbf = wendland
    # Generate grid
    x, y = generate_grid(GRID_SIZE, PLOT_RESOLUTION_FACTOR)

    # fine_grid = generate_grid(GRID_SIZE, PLOT_RESOLUTION_FACTOR)

    # Create phi
    phi = generate_kernel(rbf)

    # Get original function
    original_function = generate_original_function()

    # Interpolate
    interpolant = interpolate(phi, original_function, (x, y))
    # fine_grid_interpolated_values = map(interpolant, fine_grid)

    # Plot values on finer grid
    plt.figure()
    ax = plt.axes(projection='3d')
    plot_contour(ax, original_function, GRID_SIZE)
    plt.show()
    plt.figure()
    ax = plt.axes(projection='3d')
    plot_contour(ax, interpolant, GRID_SIZE)
    plt.show()
    x = np.linspace(-GRID_SIZE, GRID_SIZE, 8 * GRID_SIZE)
    y = np.linspace(-GRID_SIZE, GRID_SIZE, 8 * GRID_SIZE)
    print("MSE was: ", mse(original_function, interpolant, x, y))
