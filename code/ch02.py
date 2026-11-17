"""Check planar linearization, an exact curved separatrix, and area transport."""

import numpy as np
from scipy.integrate import solve_ivp


def main():
    oscillator = np.array([[0, 1], [-1, -1]])
    expected_roots = [-0.5 - np.sqrt(3) * 0.5j, -0.5 + np.sqrt(3) * 0.5j]
    assert np.allclose(np.sort_complex(np.linalg.eigvals(oscillator)),
                       expected_roots)

    def saddle_field(time, state):
        x, y = state
        return [-x, y + x**2]

    final_time = 2.0
    for y0 in [-1.0 / 3.0, 0.0]:
        trajectory = solve_ivp(saddle_field, (0, final_time), [1.0, y0],
                               rtol=1e-10, atol=1e-12)
        assert trajectory.success
        x_expected = np.exp(-final_time)
        y_expected = (y0 + 1.0 / 3.0) * np.exp(final_time) - x_expected**2 / 3
        assert np.allclose(trajectory.y[:, -1], [x_expected, y_expected])

    def predator_field(time, state):
        x, y, _ = state
        return [x * (1 - y), y * (x - 1), x - y]

    predator = solve_ivp(predator_field, (0, 20), [2.0, 1.0, 0.0],
                         rtol=1e-10, atol=1e-12)
    assert predator.success
    x, y, log_area = predator.y
    assert min(x.min(), y.min()) > 0
    conserved = x - np.log(x) + y - np.log(y) - 2
    assert np.max(np.abs(conserved - conserved[0])) < 1e-8
    assert np.allclose(log_area, np.log(x * y / (x[0] * y[0])), atol=1e-8)
    print("Planar eigenvalues, curved separatrix, and weighted area verified.")


if __name__ == "__main__":
    main()
