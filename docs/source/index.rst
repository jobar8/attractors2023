.. Attractors 2023


Attractors 2023 Documentation
=============================
..
   Note: Items in this toctree form the top-level navigation. See `modules.rst` for the `autosummary` directive, and for why `modules.rst` isn't called directly.

.. toctree::
   :hidden:

   Home Page <self>
   Reference <_autosummary/attractors2023>

This project, *Attractors 2023*, has two objectives:

- to provide an updated version of the original dashboard
- to provide a new dashboard that can allow the user to *zoom* into the attractor's trajectory

My contribution has first consisted in re-organising the original code into a proper Python package, with unit tests and documentation. I then added a new method for
calculating the trajectory (the set of points formed by the imaginary movement of a particle according to the attractor's equations). The method uses multiprocessing to calculate
the trajectory from several initial points in parallel.

Check out the :doc:`Reference<_autosummary/attractors2023>` section for further information about each class and function.

----------

Find anything with:
^^^^^^^^^^^^^^^^^^^

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
