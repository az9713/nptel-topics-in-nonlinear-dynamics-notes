"""Validate invariant densities, slow passage, and exact baker inversion."""

from fractions import Fraction
from math import atan, isclose, pi, sin, sqrt

from scipy.integrate import quad


def cusp_density(x):
    return (1 - x)/2


def channel_count(epsilon, boundary):
    state = -boundary
    count = 0
    while state < boundary:
        state += epsilon + state**2
        count += 1
    return count


def baker(x, y):
    bit = int(2*x)
    return 2*x - bit, (y + bit)/2


def baker_inverse(x, y):
    bit = int(2*y)
    return (x + bit)/2, 2*y - bit


def main():
    for x in (Fraction(1, 3), Fraction(1, 5), Fraction(4, 5)):
        preimage = (1 - x)**2/4
        transferred = (1 - x)/2 * (
            cusp_density(preimage) + cusp_density(-preimage)
        )
        assert transferred == cusp_density(x)
        assert (1 - x)/2 + (1 + x)/2 == 1

    # Substitute x=sin(theta)**2 before integrating the endpoint singularity.
    density_mass, error = quad(
        lambda theta: 2/pi, 0, pi/6, epsabs=1e-12,
    )
    assert isclose(density_mass, 1/3, abs_tol=error)
    assert isclose(sin(pi/6)**2, 1/4)

    boundary = 0.1
    samples = [(epsilon, channel_count(epsilon, boundary))
               for epsilon in (1e-4, 2.5e-5)]
    for epsilon, steps in samples:
        approximation = 2*atan(boundary/sqrt(epsilon))/sqrt(epsilon)
        assert abs(steps - approximation) <= 2
        print(f"Channel epsilon={epsilon:g}: {steps} steps")
    assert 1.95 < samples[1][1]/samples[0][1] < 2.1

    initial = Fraction(5, 8), Fraction(1, 4)
    state = initial
    for _ in range(5):
        state = baker(*state)
    for _ in range(5):
        state = baker_inverse(*state)
    assert state == initial
    print(f"Logistic lower-quarter mass: {density_mass:.6f}")
    print("Baker map: exact recovery after five steps")


if __name__ == "__main__":
    main()
