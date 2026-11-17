"""Resolve the logistic invariant measure at successive dyadic scales."""

from math import asin, fsum, isclose, log, pi, sqrt


def cell_masses(count):
    """Compute arcsine-law masses for a positive even bin count."""
    if count < 2 or count % 2:
        raise ValueError("The bin count must be a positive even integer")
    half = [2.0 / pi * asin(sqrt(j / count)) for j in range(count // 2 + 1)]
    left = [b - a for a, b in zip(half, half[1:])]
    return left + left[::-1]


def effective_dimension(masses, order):
    scale_log = log(len(masses))
    if order == 1:
        return -fsum(mass * log(mass) for mass in masses) / scale_log
    return log(fsum(mass**order for mass in masses)) / ((1-order)*scale_log)


def main():
    print('bins    D_1 finite    D_2 finite    D_4 finite')
    results = []
    for count in (256, 4096, 65536):
        masses = cell_masses(count)
        assert isclose(fsum(masses), 1.0, abs_tol=1e-13)
        assert min(masses) > 0
        assert isclose(masses[0]*sqrt(count), 2/pi, rel_tol=0.001)
        row = [effective_dimension(masses, q) for q in (1, 2, 4)]
        assert 0 < row[2] < row[1] < row[0] <= 1
        results.append(row)
        rendered = '    '.join(f'{value:10.6f}' for value in row)
        print(f'{count:5d}   {rendered}')
    assert abs(results[-1][0]-1) < abs(results[0][0]-1)
    assert abs(results[-1][1]-1) < abs(results[0][1]-1)
    limiting_dimension = 2 / 3
    assert abs(results[-1][2]-limiting_dimension) < abs(
        results[0][2]-limiting_dimension
    )


if __name__ == '__main__':
    main()
