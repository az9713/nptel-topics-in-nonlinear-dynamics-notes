"""Check action-angle identities by quadrature and exact oscillator data."""

import numpy as np
from scipy.integrate import quad


def action(energy, exponent):
    area, _ = quad(lambda u: np.sqrt(1 - u**exponent), 0, 1)
    return 2 * np.sqrt(2) * energy**(0.5 + 1 / exponent) * area / np.pi


def period(energy, exponent):
    integral, _ = quad(lambda u: 1 / np.sqrt(1 - u**exponent), 0, 1)
    return 2 * np.sqrt(2) * energy**(1 / exponent - 0.5) * integral


def pendulum_period(modulus):
    period_quarter, _ = quad(
        lambda u: 1 / np.sqrt(1 - modulus**2 * np.sin(u)**2), 0, np.pi / 2
    )
    return 4 * period_quarter


def main():
    energy, increment = 2.0, 1e-4
    derivative = (action(energy + increment, 4)
                  - action(energy - increment, 4)) / (2 * increment)
    assert np.isclose(2 * np.pi * derivative, period(energy, 4))
    assert np.isclose(period(16 * energy, 4), period(energy, 4) / 2)
    assert np.isclose(period(energy, 2), np.sqrt(2) * np.pi)
    assert np.isclose(pendulum_period(0), 2 * np.pi)
    assert pendulum_period(0.99) > pendulum_period(0.5) > pendulum_period(0)

    time = np.linspace(0, 2 * np.pi, 30)
    phase = 0.4
    q1, p1 = np.cos(time), -np.sin(time)
    q2, p2 = 2 * np.cos(time + phase), -2 * np.sin(time + phase)
    energy1, energy2 = (q1**2 + p1**2) / 2, (q2**2 + p2**2) / 2
    difference = (energy1 - energy2) / 2
    symmetric = (q1 * q2 + p1 * p2) / 2
    angular = (q1 * p2 - q2 * p1) / 2
    assert np.allclose(difference, -0.75)
    assert np.allclose(symmetric, np.cos(phase))
    assert np.allclose(angular, -np.sin(phase))
    assert np.allclose(difference**2 + symmetric**2 + angular**2,
                       (energy1 + energy2)**2 / 4)
    print("Action derivative, period scaling, and oscillator invariants verified.")


if __name__ == "__main__":
    main()
