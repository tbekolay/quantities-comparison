Comparing Python quantities packages
====================================

This repository contains files for testing
various Python packages for representing physical quantities.
It's still in early stages,
but some useful information can be collected
by running `run_comparisons.py`.

Some more information about quantities
and the current state of representing physical quantities
in Python can be found in
[this talk](https://www.youtube.com/watch?v=N-edLdxiM40).

Packages tested
---------------

* [`astropy.units`](https://astropy.readthedocs.org/en/latest/units/index.html)
* [`dimensions.py`](http://code.activestate.com/recipes/577333-numerical-type-with-units-dimensionspy/)
* [`dimpy`](http://www.inference.phy.cam.ac.uk/db410/)
* [`ipython-physics`](https://bitbucket.org/birkenfeld/ipython-physics)
* [`magnitude`](http://juanreyero.com/open/magnitude/index.html)
* [`numericalunits`](https://github.com/sbyrnes321/numericalunits)
* [`pint`](https://pint.readthedocs.org/en/latest/)
* [`piquant`](http://sourceforge.net/p/piquant/code/HEAD/tree/trunk/)
* [`quantities`](http://pythonhosted.org/quantities/)
* [`scimath`](http://docs.enthought.com/scimath/)
* [`SP.PhysicalQuantities`](https://bitbucket.org/khinsen/scientificpython)
* [`unum`](http://home.scarlet.be/be052320/Unum.html)


Packages not tested
-------------------

* firkin -- Not compatible with numpy
* udunitspy -- Installation problems
* units -- Not compatible with numpy
* [buckingham](https://code.google.com/p/buckingham/)
  -- Not compatible with numpy
* [simtk.units](https://simtk.org/home/python_units)
  -- source not available, from what I can see...
* [python-units](https://github.com/doublereedkurt/python-units)
  -- fails
