"""Compare Duffing boundary indices with dissipative energy evolution."""

import numpy as np
from scipy.integrate import solve_ivp


def field(x, y, drag=0.4):
    return y, x - x**3 - drag*y


def winding(center, radius, count):
    angle = 2*np.pi*np.arange(count)/count
    x = center + radius*np.cos(angle)
    y = radius*np.sin(angle)
    u, v = field(x, y)
    values = u + 1j*v
    assert np.all(np.abs(values) > 0)
    turns = np.angle(np.roll(values, -1)*values.conjugate())
    assert np.max(np.abs(turns)) < np.pi/2
    degree = np.sum(turns)/(2*np.pi)
    assert np.isclose(degree, np.rint(degree), atol=1e-12)
    return int(np.rint(degree))


def main():
    regions = [(-1, 0.2), (0, 0.2), (1, 0.2), (0, 1.8)]
    indices = [winding(*region, 256) for region in regions]
    assert indices == [winding(*region, 512) for region in regions]
    assert indices == [1, -1, 1, 1]

    times = np.linspace(0, 50, 1001)
    solution = solve_ivp(
        lambda _, state: field(*state), (0, 50), (0.6, 0),
        t_eval=times, rtol=1e-10, atol=1e-12,
    )
    assert solution.success
    x, y = solution.y
    energy = y*y/2 + x**4/4 - x*x/2
    assert np.all(energy < 0)
    assert np.all(x > 0)
    assert np.max(np.diff(energy)) < 1e-10
    assert np.linalg.norm(solution.y[:, -1] - [1, 0]) < 5e-5
    print(f"Duffing indices (left, saddle, right, all): {indices}")
    print(f"Right-well final energy: {energy[-1]:.6f}")


if __name__ == "__main__":
    main()
