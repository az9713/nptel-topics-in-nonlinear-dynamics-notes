"""Check the rotating hoop equilibrium, softening, and quartic period."""

from math import acos, cos, pi, sin, sqrt

from scipy.integrate import quad


def potential(theta, spin):
    one_minus_cos = 2*sin(theta/2)**2
    return (1 - spin**2)*one_minus_cos + spin**2*one_minus_cos**2/2


def curvature(theta, spin):
    return cos(theta) - spin**2*cos(2*theta)


def period_about_bottom(amplitude, spin):
    energy = potential(amplitude, spin)
    quarter, _ = quad(
        lambda angle: 1/sqrt(2*(energy - potential(angle, spin))),
        0, amplitude,
    )
    return 4*quarter


def main():
    spin = 1.2
    equilibrium = acos(1/spin**2)
    assert abs(sin(equilibrium)*(1 - spin**2*cos(equilibrium))) < 1e-14
    step = 1e-4
    for angle in (0, equilibrium, -equilibrium, pi):
        second_difference = (
            potential(angle + step, spin) - 2*potential(angle, spin)
            + potential(angle - step, spin)
        )/step**2
        assert abs(second_difference - curvature(angle, spin)) < 1e-6
    epsilon = 1e-5
    side = sqrt(1 - (1 + epsilon)**-4)
    assert abs(side/(2*sqrt(epsilon)) - 1) < 2e-5

    period = period_about_bottom(0.03, 0.8)
    assert abs(period - 2*pi/sqrt(1 - 0.8**2)) < 0.003
    critical_ratio = period_about_bottom(0.025, 1)
    critical_ratio /= period_about_bottom(0.05, 1)
    assert abs(critical_ratio - 2) < 0.001
    print(f"Side angle at normalized spin 1.2: {equilibrium:.6f} rad")
    print(f"Bottom period at spin 0.8 and amplitude 0.03: {period:.6f}")
    print(f"Critical period ratio on halving amplitude: {critical_ratio:.6f}")


if __name__ == "__main__":
    main()
