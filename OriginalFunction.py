"""
List of functions to examine
"""
# TODO: add option to get an image.
# TODO: add an option to get any data.
import numpy as np
from PIL import ImageOps, Image
from scipy.spatial.transform import Rotation

from Config.Options import options

register_function = options.get_type_register("original_function")


@register_function("numbers")
def numbers(x, y):
    return np.sin(4 * x) * np.cos(5 * y)


@register_function("numbers_gauss")
def numbers_gauss(x, y):
    return 5 * (np.exp(-(x ** 2) - y ** 2))


@register_function("one")
def one(*_):
    return 1


@register_function("numbers_sin")
def numbers_sin(x, y):
    return np.sin(2 * (x + 0.5)) * np.cos((3 * (y + 0.5)))


@register_function("anomaly_synthetic")
def anomaly_synthetic(x, y):
    ans = np.sin(x) + np.cos(y)
    if 0.1 < x < 0.25 and 0.2 < y < 0.4:
        ans = ans * 1.01

    return ans


FILENAME = r"C:\Users\lelu9\PycharmProjects\MultiscalteInterpolation\input_data\1150.PNG"
FILENAME = r"C:\Users\lelu9\PycharmProjects\MultiscalteInterpolation\input_data\img.png"
FILENAME = r"C:\Users\lelu9\PycharmProjects\MultiscalteInterpolation\input_data\011.png"
_IMAGE = ImageOps.grayscale(Image.open(FILENAME).rotate(90))
IMAGE = np.array(_IMAGE) / 255


@register_function("image")
def image(x, y):
    if x > 1 or x < -1:
        import ipdb

        ipdb.set_trace()
    try:
        x = int(((x + 0.95) / 2) * IMAGE.shape[0])
        y = int(((y + 0.95) / 2) * IMAGE.shape[1])

        return IMAGE[x, y]
    except:
        import ipdb

        ipdb.set_trace()


@register_function("rotations_euler_gauss")
def rotations_euler_gauss(x, y):
    return Rotation.from_euler(
        "xyz",
        [
            0.5 * (1 - np.exp(-(x ** 2))),
            0.5 * (1 - np.exp(-(y ** 2))),
            0.2 * np.cos(2 * x * y),
            ],
    ).as_matrix()


@register_function("rotations_euler")
def rotations_euler(x, y):
    return Rotation.from_euler("xyz", [1.2 * np.sin(5 * x - 0.1), y**2 / 2 - np.sin(3 * x), 1.5 * np.cos(2 * x)]).as_matrix()


@register_function("spd")
def spd(x, y):
    # TODO: add check if function returns a valid manifold point.
    z = (0.3 * np.abs(np.cos(2 * y)) + 0.6) * np.exp(-(x ** 2) - y ** 2) * (
            5 * np.eye(3) + np.array([[np.sin(5 * y), y, x * y], [0, 0, y ** 2], [0, 0, 0]])
    ) + 0.3 * np.eye(3)
    return z + np.transpose(z)
