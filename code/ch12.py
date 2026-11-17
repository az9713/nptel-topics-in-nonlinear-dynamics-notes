"""Use exact arithmetic to check the cat map and the glass quiz."""

from fractions import Fraction
from itertools import product
from math import isclose, log


def cat(point, modulus):
    x, y = point
    return (x+y) % modulus, (x+2*y) % modulus


def glass_cycle(heights):
    x, y, z = heights
    mean_ab = (x+y)/2
    mean_bc = (mean_ab+z)/2
    mean_ca = (mean_bc+mean_ab)/2
    return mean_ca, mean_bc, mean_ca


def main():
    modulus = 5
    grid = list(product(range(modulus), repeat=2))
    assert len({cat(point, modulus) for point in grid}) == len(grid)
    assert sum(cat(point, modulus) == point for point in grid) == 1
    period_dividing_two = sum(
        cat(cat(point, modulus), modulus) == point for point in grid
    )
    assert period_dividing_two == 5
    print('Denominator 5: 1 fixed point and 2 exact period-2 cycles')

    state = tuple(map(Fraction, (7, 1, 8)))
    mean = sum(state)/3
    first = glass_cycle(state)
    current = state
    for n in range(1, 7):
        current = glass_cycle(current)
        factor = Fraction(-1, 8)**(n-1)
        assert current == tuple(mean + factor*(v-mean) for v in first)
    heights = ', '.join(map(str, first))
    print(f'Glass heights after one cycle: {heights}')

    # Partial Gauss transfer operator at x = 1/2.
    x, count = 0.5, 1000
    total = sum(1/((x+k)*(x+k+1)) for k in range(1, count+1))/log(2)
    tail = 1/((x+count+1)*log(2))
    assert isclose(total+tail, 1/((1+x)*log(2)), rel_tol=1e-14)


if __name__ == '__main__':
    main()
