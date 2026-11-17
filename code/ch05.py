"""Check near-fold delay, imperfect pitchfork roots, and Hopf return."""

import numpy as np
from scipy.integrate import quad, solve_ivp


def main():
    epsilon = 0.05
    threshold = 1.0
    exact_delay = (2 / np.sqrt(epsilon)
                   * np.arctan(threshold / np.sqrt(epsilon)))
    integral_delay, _ = quad(lambda x: 1 / (epsilon + x**2),
                             -threshold, threshold)

    def fold_field(time, state):
        return [-epsilon - state[0]**2]

    def reach_threshold(time, state):
        return state[0] + threshold

    reach_threshold.terminal = True
    sweep = solve_ivp(fold_field, (0, 2 * exact_delay), [threshold],
                      events=reach_threshold, rtol=1e-10, atol=1e-12)
    assert sweep.success and len(sweep.t_events[0]) == 1
    assert np.isclose(integral_delay, exact_delay)
    assert np.isclose(sweep.t_events[0][0], exact_delay)

    for bias, root_count in [(1.5, 3), (2.5, 1)]:
        roots = np.roots([1, 0, -3, -bias])
        assert np.count_nonzero(np.isclose(roots.imag, 0)) == root_count

    gain, frequency = 0.25, 2.0
    target_radius = np.sqrt(gain)
    period = 2 * np.pi / frequency
    increment = 1e-5

    def oscillator(time, state):
        x, y = state
        radial = gain - x**2 - y**2
        return [radial * x - frequency * y, frequency * x + radial * y]

    def return_radius(radius):
        solution = solve_ivp(oscillator, (0, period), [radius, 0],
                             rtol=1e-12, atol=1e-14)
        assert solution.success and abs(solution.y[1, -1]) < 1e-9
        return np.linalg.norm(solution.y[:, -1])

    assert np.isclose(return_radius(target_radius), target_radius)
    slope = (return_radius(target_radius + increment)
             - return_radius(target_radius - increment)) / (2 * increment)
    assert np.isclose(slope, np.exp(-2 * gain * period), rtol=1e-6)
    print("Fold delay, imperfect pitchfork, and Hopf multiplier verified.")


if __name__ == "__main__":
    main()
