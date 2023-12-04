"""Support functions for dashboards."""

from collections.abc import Generator

import datashader as ds
import pandas as pd
from colorcet import palette
from datashader import transfer_functions as tf
from datashader.colors import inferno, viridis

palette['viridis'] = viridis
palette['inferno'] = inferno


def render_attractor(
    trajectory: pd.DataFrame, plot_type: str = 'points', cmap: list | None = None, size: int = 700
) -> Generator:
    """Render attractor's trajectory into an image using datashader."""
    if cmap is None:
        cmap = palette['inferno']
    cvs = ds.Canvas(plot_width=size, plot_height=size)
    agg = getattr(cvs, plot_type)(trajectory, 'x', 'y', agg=ds.count())
    yield tf.shade(agg, cmap=cmap)
