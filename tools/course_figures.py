"""Render the rotating-hoop branch diagram and logistic invariant law."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ASSETS = Path(__file__).resolve().parents[1] / "assets"
BACKGROUND = "#111923"
INK = "#e9edf3"
GRID = "#344756"
BLUE = "#80d0f2"
ORANGE = "#ffd087"


def plot():
    figure, axis = plt.subplots(figsize=(6.2, 3.8), layout="constrained")
    figure.patch.set_facecolor(BACKGROUND)
    axis.set_facecolor(BACKGROUND)
    axis.tick_params(colors=INK)
    axis.xaxis.label.set_color(INK)
    axis.yaxis.label.set_color(INK)
    for spine in axis.spines.values():
        spine.set_color(GRID)
    axis.grid(color=GRID, alpha=0.5, zorder=0)
    return figure, axis


def finish(figure, axis, filename):
    axis.legend(facecolor=BACKGROUND, edgecolor=GRID, labelcolor=INK)
    figure.savefig(ASSETS / filename, dpi=185, facecolor=BACKGROUND)
    plt.close(figure)


def hoop():
    figure, axis = plot()
    low_spin = np.linspace(0, 1, 121)
    high_spin = np.linspace(1, 2, 251)
    side_positions = np.sqrt(1 - high_spin**-4)
    axis.plot(low_spin, np.zeros_like(low_spin), color=BLUE, label="Center")
    axis.plot(high_spin, side_positions, color=BLUE)
    axis.plot(high_spin, -side_positions, color=BLUE)
    axis.plot(high_spin, np.zeros_like(high_spin), "--", color=ORANGE, label="Saddle")
    axis.scatter(1, 0, facecolor=BACKGROUND, edgecolor=INK, zorder=4,
                 label="Degenerate equilibrium")
    axis.set(xlabel="Spin / threshold spin", ylabel="Signed position / radius",
             xlim=(0, 2), ylim=(-1.05, 1.05))
    finish(figure, axis, "hoop-branches.png")


def invariant_mass():
    figure, axis = plot()
    boundaries = np.linspace(0, 1, 33)
    cumulative = 2 * np.arcsin(np.sqrt(boundaries)) / np.pi
    masses = np.diff(cumulative)
    assert np.isclose(sum(masses), 1)
    axis.stairs(masses, boundaries, color=ORANGE, fill=False,
                label="Logistic invariant law at parameter 4")
    axis.axhline(1 / 32, color=BLUE, linestyle="--", label="Uniform law")
    axis.set(xlabel="State", ylabel="Probability per bin", xlim=(0, 1), ylim=(0, 0.13))
    finish(figure, axis, "logistic-bin-masses.png")


if __name__ == "__main__":
    hoop()
    invariant_mass()
