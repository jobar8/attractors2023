"""
Support for working with a family of attractor equations (https://en.wikipedia.org/wiki/Attractor#Strange_attractor)

Each attractor has:
- Executable Python code for calculating trajectories, optimized using Numba (numba.pydata.org)
- Readable equations displayable with KaTeX
- Examples of interesting patterns stored in a separate attractors.yml file

Support is provided for reading the attractors.yml file and working with the examples in it.

**This file has been copied from:**
https://github.com/holoviz-topics/examples/blob/main/attractors/attractors.py
and slightly modified by Joseph Barraud to fit the requirements of this project (attractors2023).

Changes include:
- linting and formatting with Ruff
- set data folder relative to this file
- rename attractor classes using CapWords convention (Fractal_Dream -> FractalDream)
- use 'item_type' instead of 'class_' attribute on 'param.List'
- use '.param.update' instead of 'set_param' on 'attractor.param'
- rename `.sig()` method `.signature()`
- use `np.random.default_rng()`
- move `trajectory_coords()` and `trajectory()` functions to maths.py module
"""
import inspect
from pathlib import Path

import numpy as np
import pandas as pd
import param
import yaml
from numba import jit
from numpy import cos, fabs, sin, sqrt
from numpy.typing import ArrayLike, NDArray
from param import concrete_descendents

from attractors2023.maths import compute_multiple, trajectory

RNG = np.random.default_rng(12)


class Attractor(param.Parameterized):
    """Base class for a Parameterized object that can evaluate an attractor trajectory."""

    x = param.Number(0, softbounds=(-2, 2), doc='Starting x value', precedence=-1)
    y = param.Number(0, softbounds=(-2, 2), doc='Starting y value', precedence=-1)

    a = param.Number(1.7, bounds=(-3, 3), doc='Attractor parameter a')
    b = param.Number(1.7, bounds=(-3, 3), doc='Attractor parameter b')

    colormap = param.ObjectSelector(
        'kgy',
        precedence=0.7,
        check_on_set=False,
        doc='Palette of colors to use for plotting',
        objects=['bgy', 'bmw', 'bgyw', 'bmy', 'fire', 'gray', 'kgy', 'kbc', 'viridis', 'inferno'],
    )

    equations = param.List(
        [],
        item_type=str,
        precedence=-1,
        readonly=True,
        doc="""
        LaTeX-formatted list of equations""",
    )

    __abstract = True

    def __call__(self, n: int, x: float | None = None, y: float | None = None) -> pd.DataFrame:
        """Return a dataframe with `n` points."""
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        args = [getattr(self, p) for p in self.signature()]
        return trajectory(self.fn, *args, n=n)

    def compute(
        self, xlim: tuple[float, float] = (-2, 2), ylim: tuple[float, float] = (-2, 2), n_points: int = 1000000
    ) -> pd.DataFrame:
        """Return a list of dataframes with *n* points"""
        args = [getattr(self, p) for p in self.signature()]
        global partial_fn  # hack to ensure multiprocessing works

        def partial_fn(x: ArrayLike, y: ArrayLike) -> NDArray:
            """Partial version of attractor equation with only (x,y) arguments."""
            return self.fn(x, y, *args[2:])

        all_dfs = compute_multiple(partial_fn, xlim, ylim, n_points=n_points, n_origins=4, nprocs=8)
        return pd.concat(all_dfs)

    def vals(self):
        return [self.__class__.name] + [self.colormap] + [getattr(self, p) for p in self.signature()]

    def signature(self) -> list[str]:
        """Returns the calling signature expected by this attractor function"""
        return list(inspect.signature(self.fn).parameters.keys())[:-1]


class FourParamAttractor(Attractor):
    """Base class for most four-parameter attractors"""

    c = param.Number(0.6, softbounds=(-3, 3), doc='Attractor parameter c')
    d = param.Number(1.2, softbounds=(-3, 3), doc='Attractor parameter d')

    __abstract = True


class Clifford(FourParamAttractor):
    equations = param.List([r'$x_{n+1} = \sin\ ay_n + c\ \cos\ ax_n$', r'$y_{n+1} = \sin\ bx_n + d\ \cos\ by_n$'])

    @staticmethod
    @jit(nopython=True)
    def fn(x, y, a, b, c, d, *o):
        return sin(a * y) + c * cos(a * x), sin(b * x) + d * cos(b * y)


class DeJong(FourParamAttractor):
    equations = param.List([r'$x_{n+1} = \sin\ ay_n - c\ \cos\ bx_n$', r'$y_{n+1} = \sin\ cx_n - d\ \cos\ dy_n$'])

    @staticmethod
    @jit(nopython=True)
    def fn(x, y, a, b, c, d, *o):
        return sin(a * y) - cos(b * x), sin(c * x) - cos(d * y)


class Svensson(FourParamAttractor):
    equations = param.List([r'$x_{n+1} = d\ \sin\ ax_n - \sin\ by_n$', r'$y_{n+1} = c\ \cos\ ax_n + \cos\ by_n$'])

    @staticmethod
    @jit(nopython=True)
    def fn(x, y, a, b, c, d, *o):
        return d * sin(a * x) - sin(b * y), c * cos(a * x) + cos(b * y)


class FractalDream(Attractor):
    equations = param.List([r'$x_{n+1} = \sin\ by_n + c\ \sin\ bx_n$', r'$y_{n+1} = \sin\ ax_n + d\ \sin\ ay_n$'])

    c = param.Number(1.15, softbounds=(-0.5, 1.5), doc='Attractor parameter c')
    d = param.Number(2.34, softbounds=(-0.5, 1.5), doc='Attractor parameter d')

    @staticmethod
    @jit(nopython=True)
    def fn(x, y, a, b, c, d, *o):
        return sin(b * y) + c * sin(b * x), sin(a * x) + d * sin(a * y)


class Bedhead(Attractor):
    equations = param.List(
        [r'$x_{n+1} = y_n\ \sin\ \frac{x_ny_n}{b} + \cos(ax_n-y_n)$', r'$y_{n+1} = x_n+\frac{\sin\ y_n}{b}$']
    )

    a = param.Number(0.64, bounds=(-1, 1))
    b = param.Number(0.76, bounds=(-1, 1))

    @staticmethod
    @jit(nopython=True)
    def fn(x, y, a, b, *o):
        return y * sin(x * y / b) + cos(a * x - y), x + sin(y) / b

    def __call__(self, n):
        # Avoid interactive divide-by-zero errors for b
        epsilon = 3 * np.finfo(float).eps
        if -epsilon < self.b < epsilon:
            self.b = epsilon
        return super(Bedhead, self).__call__(n)


class Hopalong1(Attractor):
    equations = param.List([r'$x_{n+1} = y_n-\mathrm{sgn}(x_n)\sqrt{\left|\ bx_n-c\ \right|}$', r'$y_{n+1} = a-x_n$'])

    a = param.Number(9.8, bounds=(0, 10))
    b = param.Number(4.1, bounds=(0, 10))
    c = param.Number(3.8, bounds=(0, 10), doc='Attractor parameter c')

    @staticmethod
    @jit(nopython=True)
    def fn(x, y, a, b, c, *o):
        return y - sqrt(fabs(b * x - c)) * np.sign(x), a - x


class Hopalong2(Hopalong1):
    equations = param.List(
        [r'$x_{n+1} = y_n-1-\mathrm{sgn}(x_n-1)\sqrt{\left|\ bx_n-1-c\ \right|}$', r'$y_{n+1} = a-x_n-1$']
    )

    @staticmethod
    @jit(nopython=True)
    def fn(x, y, a, b, c, *o):
        return y - 1.0 - sqrt(fabs(b * x - 1.0 - c)) * np.sign(x - 1.0), a - x - 1.0


@jit(nopython=True)
def G(x, mu):
    return mu * x + 2 * (1 - mu) * x**2 / (1.0 + x**2)


class GumowskiMira(Attractor):
    equations = param.List(
        [
            r'$G(x) = \mu x + \frac{2(1-\mu)x^2}{1+x^2}$',
            r'$x_{n+1} = y_n + ay_n(1-by_n^2) + G(x_n)$',
            r'$y_{n+1} = -x_n + G(x_{n+1})$',
        ]
    )

    x = param.Number(0, softbounds=(-20, 20), doc='Starting x value', precedence=0.1)
    y = param.Number(0, softbounds=(-20, 20), doc='Starting y value', precedence=0.1)
    a = param.Number(0.64, softbounds=(-1, 1))
    b = param.Number(0.76, softbounds=(-1, 1))
    mu = param.Number(0.6, softbounds=(-2, 2), doc='Attractor parameter mu')

    @staticmethod
    @jit(nopython=True)
    def fn(x, y, a, b, mu, *o):
        xn = y + a * (1 - b * y**2) * y + G(x, mu)
        yn = -x + G(xn, mu)
        return xn, yn


class SymmetricIcon(Attractor):
    a = param.Number(0.6, softbounds=(-20, 20), bounds=(None, None), doc='Attractor parameter alpha')
    b = param.Number(1.2, softbounds=(-20, 20), bounds=(None, None), doc='Attractor parameter beta')
    g = param.Number(0.6, softbounds=(-1, 1), bounds=(None, None), doc='Attractor parameter gamma')
    om = param.Number(1.2, softbounds=(-0.2, 0.2), bounds=(None, None), doc='Attractor parameter omega')
    l = param.Number(0.6, softbounds=(-3, 3), bounds=(None, None), doc='Attractor parameter lambda')
    d = param.Number(1.2, softbounds=(1, 20), bounds=(None, None), doc='Attractor parameter degree')

    @staticmethod
    @jit(nopython=True)
    def fn(x, y, a, b, g, om, l, d, *o):
        zzbar = x * x + y * y
        p = a * zzbar + l
        zreal, zimag = x, y

        for _i in range(1, d - 1):
            za, zb = zreal * x - zimag * y, zimag * x + zreal * y
            zreal, zimag = za, zb

        zn = x * zreal - y * zimag
        p += b * zn

        return p * x + g * zreal - om * y, p * y - g * zimag + om * x


class ParameterSets(param.Parameterized):
    """
    Allows selection from sets of pre-defined parameters saved in YAML.

    Assumes the YAML file returns a list of groups of values.
    """

    data_folder = Path(__file__).parent / 'data'
    input_examples_filename = param.String('attractors.yml')
    output_examples_filename = param.String('saved_attractors.yml', precedence=0.81)
    current = param.Callable(lambda: None, precedence=-1)
    remember_this_one = param.Action(lambda x: x._remember())

    load = param.Action(lambda x: x._load())
    randomize = param.Action(lambda x: x._randomize())
    sort = param.Action(lambda x: x._sort())
    save = param.Action(lambda x: x._save(), precedence=0.8)
    example = param.Selector(objects=[[]], precedence=-1)

    def __init__(self, **params):
        super().__init__(**params)

        self._load()

        self.attractors: dict[str, Attractor] = {
            k: v(name=f'{k} parameters') for k, v in sorted(concrete_descendents(Attractor).items())
        }
        # load first set of parameters for each kind of attractors
        for k in self.attractors:
            self.get_attractor(k, *self.args(k)[0])

    def _load(self):
        with Path(self.data_folder / self.input_examples_filename).open('r') as f:
            vals = yaml.safe_load(f)
            if len(vals) > 0:
                self.param.example.objects[:] = vals
                self.example = vals[0]

    def _save(self):
        if self.output_examples_filename == self.param.input_examples_filename.default:
            msg = 'Cannot override the default attractors file.'
            raise FileExistsError(msg)
        with Path(self.data_folder / self.output_examples_filename).open('w') as f:
            yaml.dump(self.param.example.objects, f)

    def __call__(self):
        return self.example

    def _randomize(self):
        RNG.shuffle(self.param.example.objects)

    def _sort(self):
        self.param.example.objects[:] = sorted(self.param.example.objects)

    def _add_item(self, item):
        self.param.example.objects += [item]
        self.example = item

    def _remember(self):
        vals = self.current().vals()
        self._add_item(vals)

    def args(self, name):
        return [v[1:] for v in self.param.example.objects if v[0] == name]

    def get_attractor(self, name: str, *args) -> Attractor:
        """Factory function to return an Attractor object with the given name and arg values."""
        attractor = self.attractors[name]
        fn_params = ['colormap', *attractor.signature()]
        attractor.param.update(**dict(zip(fn_params, args, strict=True)))
        return attractor
