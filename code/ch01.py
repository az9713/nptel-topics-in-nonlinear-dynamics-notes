"""Check exact solutions for the illustrative bead and scalar flow."""

from math import cos, exp, isclose, sin


def oscillator(t, q, v):
    return q * cos(t) + v * sin(t), -q * sin(t) + v * cos(t)


def critical_bead(t, q, v):
    decay = exp(-t)
    return decay * (q + t * (q + v)), decay * (v - t * (q + v))


def scalar_flow(t, q):
    denominator = 1 - t * q
    if denominator <= 0:
        raise ValueError("Time lies outside the solution interval")
    return q / denominator


if __name__ == "__main__":
    initial = (1.0, -0.5)
    first = oscillator(0.6, *initial)
    sequential = oscillator(0.7, *first)
    direct = oscillator(1.3, *initial)
    assert all(isclose(a, b, abs_tol=1e-14) for a, b in zip(sequential, direct))
    assert isclose(sum(x**2 for x in direct), sum(x**2 for x in initial))

    position, velocity = critical_bead(1, 0, 1)
    assert isclose(position, exp(-1))
    assert velocity == 0
    assert isclose(scalar_flow(0.49, 2), 100)
    assert isclose(scalar_flow(2, -2), -0.4)
    try:
        scalar_flow(0.5, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("The pole must be outside the solution interval")

    print(f"Critically damped bead at t=1: q={position:.6f}, v={velocity:.6f}")
    print(f"Scalar flow at t=0.49 from q=2: q={scalar_flow(0.49, 2):.1f}")
