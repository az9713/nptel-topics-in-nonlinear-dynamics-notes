"""Verify the period-two cycles of doubling and logistic maps."""

from fractions import Fraction
from math import isclose, sqrt


def doubling(x):
    return 2*x % 1


def logistic(x, mu):
    return mu*x*(1 - x)


def main():
    candidates = [Fraction(k, 3) for k in range(3)]
    assert all(doubling(doubling(x)) == x for x in candidates)
    assert [doubling(x) for x in candidates] == [candidates[i] for i in (0, 2, 1)]

    mu = 3.2
    discriminant = sqrt((mu - 3)*(mu + 1))
    low = (mu + 1 - discriminant)/(2*mu)
    high = (mu + 1 + discriminant)/(2*mu)
    assert isclose(logistic(low, mu), high, abs_tol=1e-14)
    assert isclose(logistic(high, mu), low, abs_tol=1e-14)
    multiplier = mu**2*(1 - 2*low)*(1 - 2*high)
    assert isclose(multiplier, -mu**2 + 2*mu + 4, abs_tol=1e-14)

    x = 0.37
    for _ in range(80):
        x = logistic(x, mu)
    observed = sorted((x, logistic(x, mu)))
    assert isclose(observed[0], low, abs_tol=1e-12)
    assert isclose(observed[1], high, abs_tol=1e-12)
    print(f"Doubling two-cycle: {candidates[1]} <-> {candidates[2]}")
    print(f"Logistic two-cycle at mu={mu}: {low:.6f}, {high:.6f}")
    print(f"Two-step multiplier: {multiplier:.6f}")


if __name__ == "__main__":
    main()
