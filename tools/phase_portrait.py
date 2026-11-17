"""Generate the Chapter 1 portrait from three linear bead equations."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import expm


def main():
    background = "#111923"
    axis = "#b8c9dc"
    palettes = ["#80d0f2", "#ffd087", "#eac0f0"]
    figure, panels = plt.subplots(1, 3, figsize=(9, 3.25), layout="constrained")
    figure.patch.set_facecolor(background)
    starts = np.array([[0.7, 0.25], [-0.4, 0.7], [-0.65, -0.6]])
    for panel, (gamma, curvature, title) in zip(panels, [
        (0.0, 1.0, "Center"),
        (0.8, 1.0, "Spiral sink"),
        (0.4, -1.0, "Saddle"),
    ]):
        matrix = np.array([[0, 1], [-curvature, -gamma]])
        horizon = 6.3 if curvature > 0 else 2.4
        steps = np.linspace(0, horizon, 200)
        flows = np.array([expm(time * matrix) for time in steps])
        for start, color in zip(starts, palettes):
            q, v = (flows @ start).T
            panel.plot(q, v, color=color, lw=1.55)
            panel.scatter(*start, color=color, s=16, zorder=3)
            target = 28
            panel.annotate("", xy=(q[target], v[target]),
                           xytext=(q[target - 5], v[target - 5]),
                           arrowprops={"arrowstyle": "-|>", "color": color})
        if curvature < 0:
            values, vectors = np.linalg.eig(matrix)
            for value, vector in zip(values, vectors.T):
                direction = 1.4 * vector
                style = "--" if value < 0 else ":"
                panel.plot([-direction[0], direction[0]],
                           [-direction[1], direction[1]], style, color=axis, lw=1.2)
        panel.scatter(0, 0, color="white", s=13, zorder=4)
        panel.set(xlim=(-1.05, 1.05), ylim=(-1.05, 1.05), aspect="equal",
                  xticks=[-1, 0, 1], yticks=[-1, 0, 1])
        panel.set_xlabel("Displacement q", color=axis)
        panel.set_ylabel("Velocity v", color=axis)
        panel.set_title(title, color="white", weight="bold")
        panel.set_facecolor(background)
        panel.tick_params(colors=axis)
        panel.grid(color="#344756", alpha=0.4)
        for spine in panel.spines.values():
            spine.set_color("#344756")
    path = Path(__file__).resolve().parents[1] / "assets" / "bead-portraits.png"
    figure.savefig(path, dpi=175, facecolor=background)
    plt.close(figure)


if __name__ == "__main__":
    main()
