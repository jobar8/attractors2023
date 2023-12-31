"""Panel dashboard to visualise attractors of various types.

This is a direct conversion to a simple script of the panel notebook available here:
https://github.com/holoviz-topics/examples/blob/main/attractors/attractors_panel.ipynb

The app can be launched with:

    > panel serve --show src/attractors2023/attractors_explorer.py

"""
import numpy as np
import panel as pn
import param
from colorcet import palette
from panel.layout import HSpacer
from panel.pane import LaTeX

from attractors2023 import attractors as at
from attractors2023.shared import render_attractor

RNG = np.random.default_rng(12)

pn.extension('katex')
pn.config.throttled = True


params = at.ParameterSets(name='Attractors')


class AttractorsExplorer(param.Parameterized):
    """Select and render attractors."""

    attractor_type = param.ObjectSelector(params.attractors['Clifford'], objects=params.attractors, precedence=0.9)
    parameters = param.ObjectSelector(params, precedence=-0.5, readonly=True)
    link_xy = param.Boolean(True)
    xlim = param.Range((-3, 3), bounds=(-3, 3), softbounds=(-3, 3), step=0.1)
    ylim = param.Range((-3, 3), bounds=(-3, 3), softbounds=(-3, 3), step=0.1)

    plot_type = param.ObjectSelector(
        'points', precedence=0.8, objects=['points', 'line'], doc='Type of aggregation to use'
    )

    n_points = param.Integer(
        2000000, bounds=(1, None), softbounds=(1, 50000000), doc='Number of points', precedence=0.85
    )

    @pn.depends('xlim', 'link_xy', watch=True)
    def copy_xslider(self):
        if self.link_xy:
            self.ylim = self.xlim

    @pn.depends('ylim', 'link_xy', watch=True)
    def copy_yslider(self):
        if self.link_xy:
            self.xlim = self.ylim

    @param.depends('parameters.param', watch=True)
    def _update_from_parameters(self):
        a = params.get_attractor(*self.parameters())
        if a is not self.attractor_type:
            self.param.update(attractor_type=a)

    @param.depends('attractor_type.param', 'plot_type', 'n_points', 'xlim', 'ylim')
    def view(self):
        all_points = self.attractor_type.compute(xlim=self.xlim, ylim=self.ylim, n_points=self.n_points)
        return render_attractor(all_points, self.plot_type, palette[self.attractor_type.colormap][::-1])  # type: ignore

    @param.depends('attractor_type')
    def equations(self):
        if not self.attractor_type.equations:
            return pn.Column()
        return pn.Column(
            '<b>' + self.attractor_type.__class__.name + ' attractor<b>',
            *[LaTeX(e) for e in self.attractor_type.equations],
        )


ats = AttractorsExplorer(name='Explorer')
params.current = lambda: ats.attractor_type

text = pn.panel(
    """
<img src="https://panel.pyviz.org/_static/logo_stacked.png" width=180 height=151>

<br><br><i>This [Panel](https://github.com/pyviz/panel) app lets you explore 
[strange attractors](attractors.ipynb) -- 
fractal-like patterns that can emerge from the trajectory of a particle 
in 2D space.<br><br>

Here you can choose between different attractor families, selecting from
predefined examples or adjusting your own values and adding them to the 
saved list when you discover something interesting.<br><br>

The trajectories are calculated quickly using [Numba](http://numba.pydata.org),
aggregated using [Datashader](http://datashader.org), and colorized using
[Colorcet](http://colorcet.pyviz.org).<i>""",
    width=200,
)

pn.Row(
    HSpacer(),
    pn.Column(text, pn.panel(ats.equations, margin=(0, -500, 0, 0))),
    pn.Spacer(max_width=20),
    pn.Column(ats.view),
    pn.Spacer(max_width=20),
    pn.Column(pn.Param(ats.param, expand=True, width=220)),
    HSpacer(),
).servable('Attractors')
