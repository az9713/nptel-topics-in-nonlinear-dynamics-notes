"""Compare physical energy, modified energy, and canonical brackets."""

import numpy as np


def main():
    step = 0.5
    euler = np.array([[1.0, step], [-step, 1.0]])
    kick_drift = np.array([[1.0 - step**2, step], [-step, 1.0]])
    bracket = np.array([[0, 1], [-1, 0]])
    modified_energy = np.array([[1, -step / 2], [-step / 2, 1]])
    assert np.allclose(kick_drift @ bracket @ kick_drift.T, bracket)
    assert np.isclose(np.linalg.det(euler), 1 + step**2)
    assert np.allclose(kick_drift.T @ modified_energy @ kick_drift,
                       modified_energy)
    assert np.all(np.linalg.eigvalsh(modified_energy) > 0)

    state_euler = np.array([1.0, 0.0])
    state_kick_drift = state_euler.copy()
    for index in range(1, 201):
        state_euler = euler @ state_euler
        state_kick_drift = kick_drift @ state_kick_drift
        energy = state_euler @ state_euler / 2
        invariant = state_kick_drift @ modified_energy @ state_kick_drift / 2
        assert np.isclose(energy, 0.5 * (1 + step**2)**index)
        assert np.isclose(invariant, 0.5)

    print("Euler energy growth and kick–drift modified energy verified.")


if __name__ == "__main__":
    main()
