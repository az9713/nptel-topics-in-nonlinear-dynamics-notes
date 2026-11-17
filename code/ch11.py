"""Verify tent-map return laws and a two-state Markov propagator."""

from fractions import Fraction
from itertools import product
from math import exp, isclose


def word_mass(word, left):
    mass = Fraction(1)
    for symbol in word:
        mass *= left if symbol == 'L' else 1 - left
    return mass


def main():
    left = Fraction(1, 4)
    print('n    explicit cylinder mass / initial mass')
    for n in range(1, 9):
        f = Fraction(0)
        for tail in product('LR', repeat=n):
            if tail[-1] == 'L' and 'L' not in tail[:-1]:
                f += word_mass(('L',) + tail, left) / left
        assert f == left * (1-left)**(n-1)
        avoidance = (1-left)**(n-1) - 2*(1-left)**n + (1-left)**(n+1)
        assert f == avoidance / left
        print(f'{n}    {f}')
    assert sum(word_mass(w, left) for w in product('LR', repeat=4)) == 1

    # Two-state generator with rates a = 2, b = 1.
    steady = 1 / 3
    initial = 1
    half = steady + (initial-steady)*exp(-3/2)
    combined = steady + (half-steady)*exp(-3/2)
    direct = steady + (initial-steady)*exp(-3)
    assert isclose(combined, direct, rel_tol=1e-14)
    print(f'p_1(1) from state 1 = {direct:.6f}')


if __name__ == '__main__':
    main()
