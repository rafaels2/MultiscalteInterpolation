import scipy
import numpy as np
from numpy import linalg as la

from pyquaternion import Quaternion
from scipy.stats import special_ortho_group
from scipy.spatial.transform import Rotation

from Tools.KarcherMean import KarcherMean
from Tools.Visualization import RotationVisualizer

from .AbstractManifold import AbstractManifold
from . import register_manifold

SPECIAL_TOLERANCE = 0.001
ORTHOGONAL_TOLERANCE = 0.001


@register_manifold("rotations")
class RigidRotations(AbstractManifold):
    def __init__(self, dim=3):
        super().__init__()
        self.dim = dim

        # TODO: this is specific for n=3
        self._tangent_basis = np.array(
            [
                np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 0]]),
                np.array([[0, 0, 1], [0, 0, 0], [-1, 0, 0]]),
                np.array(
                    [
                        [
                            0,
                            0,
                            0,
                        ],
                        [0, 0, 1],
                        [0, -1, 0],
                    ]
                ),
            ]
        )

    def zero_func(self, x_0, x_1):
        return np.eye(self.dim)

    def distance(self, x, y):
        return la.norm(self.log(x, y))

    def _quaternion_from_matrix(self, matrix):
        """
        :param matrix: Rotation matrix.
        :return: Quaternion representation of the given matrix.
        """
        return Quaternion(Rotation.from_matrix(matrix).as_quat())

    def _matrix_from_quaternion(self, quaternion):
        """
        :param quaternion: Quaternion representation of a given rotation matrix.
        :return: The rotation matrix.
        """
        return Rotation.from_quat(quaternion.elements).as_matrix()

    def log(self, x, y):
        return scipy.linalg.logm(np.matmul(la.inv(x), y))

    def exp(self, x, y):
        # TODO: validate, exp(log(x) + y).
        return np.matmul(x, scipy.linalg.expm(y))

    def gen_point(self):
        matrix = np.array(special_ortho_group.rvs(self.dim))
        return matrix

    def zero_func(self, x_0, x_1):
        return np.eye(self.dim)

    def is_in_manifold(self, matrix):
        """
        Is in SO(3) predicate.
        :param matrix: Examined matrix.
        :return: bool
        """
        is_orthogonal = (
            la.norm(np.matmul(matrix, np.transpose(matrix)) - np.eye(self.dim))
            < ORTHOGONAL_TOLERANCE
        )
        is_special = np.abs(la.det(matrix) - 1) < SPECIAL_TOLERANCE
        answer = is_special and is_orthogonal
        if not answer:
            print(matrix, is_special, is_orthogonal)
        return answer

    def geodesic_l2_mean_step(
        self, current_estimator, noisy_samples, weights, tolerance=0.00000001
    ):
        projected_diff_samples = [
            w_i
            * scipy.linalg.logm(
                np.matmul(np.linalg.inv(current_estimator), noisy_sample)
            )
            for w_i, noisy_sample in zip(weights, noisy_samples)
        ]
        matrices_sum = np.zeros(projected_diff_samples[0].shape, dtype="complex128")
        for projected_diff_matrix in projected_diff_samples:
            matrices_sum += projected_diff_matrix
        r = matrices_sum / sum(weights)
        projected_avg_norm = np.linalg.norm(r, ord=2)
        if projected_avg_norm < tolerance:
            state_of_convergence = True
            return current_estimator, state_of_convergence
        else:
            new_estimator = np.matmul(current_estimator, scipy.linalg.expm(r))
            state_of_convergence = False
            return new_estimator, state_of_convergence

    def geodesic_l2_mean(
        self, noisy_samples, weights, tolerance=0.00000001, maximum_iteration=10
    ):
        """L2 mean From my weiszfeld project, adapted to weighted averaging"""
        mean_estimator = noisy_samples[0]
        mean_estimator_list = [mean_estimator]
        state_of_convergence = False
        run_index = 0
        while not state_of_convergence and run_index < maximum_iteration:
            mean_estimator, state_of_convergence = self.geodesic_l2_mean_step(
                mean_estimator, noisy_samples, weights, tolerance
            )
            mean_estimator_list.append(mean_estimator)
            run_index += 1
        return mean_estimator_list

    def average(self, values_to_average, weights, base=np.eye(3)):
        return self.geodesic_l2_mean(values_to_average, weights)[-1]

    def _to_numbers(self, x):
        return self.distance(x, np.eye(3))

    def plot(self, data, title, filename, norm_visualization=False):
        if norm_visualization:
            return super().plot(data, title, filename)
        centers = np.zeros_like(data, dtype=object)
        for index in np.ndindex(data.shape):
            centers[index] = np.array([index[1], -index[0], 0])
        print("start to visualize")
        RotationVisualizer(data, centers).save(filename, title)

    def from_euclid_to_tangent(self, euclid):
        return np.einsum("i, ijk -> jk", euclid, self._tangent_basis)

    @staticmethod
    def from_tangent_to_euclid(tangent):
        return np.array([tangent[0, 1], tangent[0, 2], tangent[1, 2]])


def main():
    m = RigidRotations()

    e = np.eye(3)
    a = m.gen_point()
    b = m.gen_point()
    c = m.gen_point()
    A = 0.2 * m.log(e, a) / m.distance(e, a)
    B = 0.2 * m.log(e, b) / m.distance(e, c)
    C = 0.2 * m.log(e, c) / m.distance(e, c)
    a = m.exp(e, A)
    b = m.exp(e, B)
    c = m.exp(e, C)
    d = m.average([a, b, c], [1, 1, 1])
    d_tag = m.exp(e, (A + B + C) / 3)
    print("D - D tag: ", m.distance(d, d_tag))
    e = m.log(a, b)
    f = m.exp(a, e)
    print("dist", m.distance(f, b))
    print("dist", m.distance(a, b))
    print("a, a", m.log(a, a))
    return a, b, c, d, m


if __name__ == "__main__":
    a, b, c, d, m = main()
