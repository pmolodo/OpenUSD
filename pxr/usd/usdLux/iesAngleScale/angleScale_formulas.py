# execfile(r"C:\src\NVIDIA\usd-ci\USD\pxr\usd\usdLux\iesAngleScale\angleScale_formulas.py")
from attrs import frozen
import dataclasses
import inspect
import math
import os

import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d
import numpy
from numpy import angle
import spb
import sympy

from typing import Optional, Tuple

# from sympy import *
from spb import plot, plot3d

INTERACTIVE_VIEW = True


THIS_FILE = os.path.abspath(inspect.getsourcefile(lambda: None) or __file__)
THIS_DIR = os.path.dirname(THIS_FILE)

IMAGE_SAVE_FOLDER = THIS_DIR
os.makedirs(IMAGE_SAVE_FOLDER, exist_ok=True)


def Clamp(x, min, max):
    return sympy.Min(sympy.Max(x, min), max)


theta, angleScale = sympy.symbols("theta angleScale")

# angle_units = "radians"
ANGLE_UNITS = "degrees"

if ANGLE_UNITS == "radians":
    THETA_MAX = sympy.pi
elif ANGLE_UNITS == "degrees":
    THETA_MAX = 180

# in latex format
THETA_INPUT_LABEL = r"$\theta_{light}$"
THETA_OUTPUT_LABEL = r"$\theta_{ies}$"
THETA_INPUT_LABEL = f"{THETA_INPUT_LABEL} ({ANGLE_UNITS})"
THETA_OUTPUT_LABEL = f"{THETA_OUTPUT_LABEL} ({ANGLE_UNITS})"

THETA_MIN_MAX = (0, THETA_MAX)
ANGLESCALE_MIN_MAX = (-1, 1)

@dataclasses.dataclass(frozen=True)
class ViewAngles:
    elev: Optional[float] = None
    azim: Optional[float] = None
    roll: Optional[float] = None

    def is_null(self):
        return self.elev is None and self.azim is None and self.roll is None

    def set_on_axes(self, axes):
        if self.is_null():
            return
        if not hasattr(axes, "view_init"):
            return
        axes.view_init(elev=self.elev, azim=self.azim, roll=self.roll)

BIMODAL_VIEW_ANGLE = ViewAngles(azim=25.97402597402598, elev=42.792207792207805)
DEFAULT_VIEW_ANGLE = ViewAngles()


@dataclasses.dataclass(frozen=True)
class GraphOptions:
    theta_min_max: Tuple[float, float] = THETA_MIN_MAX
    angleScale_min_max: Tuple[float, float] = ANGLESCALE_MIN_MAX
    box_aspect: Tuple[float, float, float] = (1, 1, 1)
    view_angles: ViewAngles = DEFAULT_VIEW_ANGLE

    def set_on_graph(self, graph):
        axes = graph.ax
        if not "theta" in axes.get_xlabel():
            raise ValueError("expected x-axis to be theta")

        axes.set_xlabel(THETA_INPUT_LABEL)
        axes.set_xlim(*self.theta_min_max)
        if hasattr(axes, "set_zlim"):
            axes.set_ylim(*self.angleScale_min_max)
            axes.set_zlim(*self.theta_min_max)
            axes.set_zlabel(THETA_OUTPUT_LABEL)
            if self.box_aspect != (1, 1, 1):
                print(f"{self.box_aspect=}")
                axes.set_box_aspect(self.box_aspect)
        else:
            axes.set_ylim(*self.theta_min_max)
            axes.set_ylabel(THETA_OUTPUT_LABEL)
            aspect = (self.box_aspect[0], self.box_aspect[2])
            if aspect != (1, 1):
                aspectRatio = aspect[1] / aspect[0]
                axes.set_aspect(aspectRatio)

        self.view_angles.set_on_axes(axes)

    def theta_lim(self):
        return (theta,) + self.theta_min_max

    def angleScale_lim(self):
        return (angleScale,) + self.angleScale_min_max

    def make_graph2d(self, function, title):
        graph = spb.plot(function, self.theta_lim(), show=False, title=title)
        self.set_on_graph(graph)
        return graph

    def make_graph3d(self, function, title):
        graph = spb.plot3d(function, self.theta_lim(), self.angleScale_lim(), show=False, title=title)
        self.set_on_graph(graph)
        return graph


DEFAULT_GRAPH = GraphOptions()

def save_graph(graph, filename, dpi=300):
    ext = os.path.splitext(filename)[-1].lstrip(".")
    if not ext or ext.isdigit():
        filename = filename + ".jpg"
    print(f"Saving: {filename}")
    filepath = os.path.join(IMAGE_SAVE_FOLDER, filename)
    # this also ensures the graph is evaluated... I tried using
    # "graph.process_series()", but that seemed to make a second copy of the
    # graph, that didn't respect the zlim
    axes = graph.ax
    graph.fig.savefig(filepath, dpi=dpi)


def save_graph_slices(function, title, filename, num_slices, graph_options=DEFAULT_GRAPH):
    start, end = graph_options.angleScale_min_max
    dist = end - start
    step = dist / (num_slices - 1)
    for i in range(num_slices):
        angleScale_val = round((i * step) + start, 6)
        angleScale_str = f"{angleScale_val:+.02f}"
        title_i = f"{title} (angleScale = {angleScale_str})"
        filename_i = f"{filename}_{angleScale_str}"
        slice_func = function.subs(angleScale, angleScale_val)
        graph = graph_options.make_graph2d(slice_func, title=title_i)
        if any(
            isinstance(x, sympy.core.numbers.ComplexInfinity)
            for x in slice_func.atoms()
        ):
            del graph.series[0]
            graph_options.set_on_graph(graph)
            axes = graph.ax
            x_center = sum(axes.get_xlim()) / 2
            y_center = sum(axes.get_ylim()) / 2
            axes.text(
                x_center,
                y_center,
                "Undefined\nAsymptote",
                verticalalignment="center",
                horizontalalignment="center",
                fontsize=50,
            )
        else:
            graph.ax.get_lines()[0].set_linewidth(5)
        save_graph(graph, filename_i)
        plt.close(graph.fig)


def plot3d_and_save(function, title, slices=0, graph_options=DEFAULT_GRAPH):
    graph = graph_options.make_graph3d(function, title=title)
    filename = f"ies_angleScale_{title}"
    filename = filename.replace(" - ", "-")
    filename = filename.replace("/", "over")
    for to_erase in "()":
        filename = filename.replace(to_erase, "")
    filename = filename.replace(" ", "_")

    save_graph(graph, filename)
    if slices:
        save_graph_slices(function, title, filename, num_slices=slices, graph_options=graph_options)
    return graph


karma_pos = theta / (1 - angleScale)
karma_neg = theta * (1 + angleScale)

karma = sympy.Piecewise(
    (0, angleScale < -1),
    (karma_neg, angleScale < 0),
    (karma_pos, angleScale < 1),
    (0, True),
)
karma_clamp = Clamp(karma, 0, THETA_MAX)

karma_pos_clamp = Clamp(
    sympy.Piecewise((0, angleScale < -1), (karma_pos, angleScale < 1), (0, True)),
    0,
    THETA_MAX,
)


# karma_pos_graph = plot3d_and_save(karma_pos, "Karma (positive)")
# karma_neg_graph = plot3d_and_save(karma_neg, "Karma (negative)")

# karma_graph = plot3d_and_save(karma, "Karma (unclamped)")

karma_clamp_graph = plot3d_and_save(karma_clamp, "Karma (clamped)", slices=9)

# karma_pos_clamp_graph = plot3d_and_save(
#     karma_pos_clamp, "Karma - theta / (1-angleScale) only (clamped)"
# )

profile_scale = 1 + angleScale
rman = ((theta - THETA_MAX) / profile_scale) + THETA_MAX
rman_clamp = Clamp(sympy.Piecewise((rman, angleScale > -1), (0, True)), 0, THETA_MAX)

# rman_graph = plot3d_and_save(rman, "Renderman (unclamped)")

rman_clamp_graph = plot3d_and_save(rman_clamp, "Renderman (clamped)", slices=9)


# if angleScale > 0, scale origin is at bottom (vangle=0)
# if angleScale == 0, no change
# if angleScale < 0, scale origin is at top (vangle=180)

bimodal_pos = theta / angleScale
bimodal_neg = ((theta - THETA_MAX) / -angleScale) + THETA_MAX
bimodal_neg_clamp = Clamp(bimodal_neg, 0, THETA_MAX)
# bimodal_neg_clamp_graph = plot3d_and_save(bimodal_neg_clamp, "Bimodal Neg (Clamped)", slices=9, angleScale_min_max=(-1, 0))

bimodal = sympy.Piecewise((bimodal_pos, angleScale > 0), (bimodal_neg, angleScale < 0), (theta, True))
bimodal_clamp = Clamp(bimodal, 0, THETA_MAX)


bimodal_options = GraphOptions(
    angleScale_min_max=(-2, 2),
    box_aspect=(4, 8, 3),
    view_angles=BIMODAL_VIEW_ANGLE)

bimodal_clamp_graph = plot3d_and_save(
    bimodal_clamp,
    "Bimodal (clamped)",
    slices=17,
    graph_options=bimodal_options,
)

if INTERACTIVE_VIEW:
    plt.show()
else:
    # plt.close("all")
    pass

# from sympy.solvers import solve

# rtheta, ktheta = sympy.symbols("rtheta ktheta")
# req = rtheta - rman
# keq = ktheta - karma


# # renderman - light aimed down - 22.5 vangle (real world) maps to 45 (ies lookup)
# solve(req.subs({rtheta: 45, theta: 22.5}), angleScale)
# # 1/6 = 0.16666666666666666

# # renderman - light aimed down - 67.5 vangle (real world) maps to 45 (ies lookup)
# solve(req.subs({rtheta: 45, theta: 67.5}), angleScale)
# # -1/6 = -0.16666666666666666

# # karma - light aimed down - 22.5 vangle (real world) maps to 45 (ies lookup)
# solve(keq.subs({ktheta: 45, theta: 22.5}), angleScale)
# # 1/2 = .5

# # karma - light aimed down - 67.5 vangle (real world) maps to 45 (ies lookup)
# solve(keq.subs({ktheta: 45, theta: 67.5}), angleScale)
# # -1/3 = -0.3333333333333333

# # renderman - light aimed up - 112.5 vangle (real world) maps to 135 (ies lookup)
# solve(req.subs({rtheta: 135, theta: 112.5}), angleScale)
# # 1/2 = .5

# # renderman - light aimed up - 157.5 vangle (real world) maps to 135 (ies lookup)
# solve(req.subs({rtheta: 135, theta: 157.5}), angleScale)
# # -1/2 = -.5

# # karma - light aimed up - 112.5 vangle (real world) maps to 135 (ies lookup)
# solve(keq.subs({ktheta: 135, theta: 112.5}), angleScale)
# # 1/6 =  0.16666666666666666

# # karma - light aimed up - 157.5 vangle (real world) maps to 135 (ies lookup)
# solve(keq.subs({ktheta: 135, theta: 157.5}), angleScale)
# # -1/7 = -0.14285714285714285
