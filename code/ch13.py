"""Check thermal Langevin covariances without a time-stepping approximation."""

from math import exp, expm1, isclose

from scipy.integrate import quad


def mean_square_displacement(t, gamma, variance):
    decay_length = -expm1(-gamma*t)/gamma
    return 2*variance/gamma * (t - decay_length)


def main():
    gamma = 2.0
    variance = 3.0
    diffusion, _ = quad(lambda s: variance*exp(-gamma*s), 0, float('inf'))
    assert isclose(diffusion, variance/gamma, rel_tol=1e-12)
    for t in (0.001, 0.5, 5.0, 50.0):
        exact = mean_square_displacement(t, gamma, variance)
        integral, _ = quad(lambda s: 2*(t-s)*variance*exp(-gamma*s), 0, t)
        assert isclose(exact, integral, rel_tol=1e-10)
        print(f't={t:6.3f}, mean square displacement={exact:.6f}')
    early = mean_square_displacement(0.001, gamma, variance) / 0.001**2
    late = mean_square_displacement(500, gamma, variance) / (2*500)
    assert isclose(early, variance, rel_tol=0.001)
    assert isclose(late, diffusion, rel_tol=0.0011)
    print(f'D = {diffusion:.6f}')


if __name__ == '__main__':
    main()
