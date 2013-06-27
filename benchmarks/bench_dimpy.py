import numpy as np
import dimpy

import base


class BenchDimpy(base.BenchModule):
    facts = {
        'LOC': 1900,
        'First release': '2008-08',
        'Most recent release': '2008-08',
        'Implementation': 'Container',
        'URL': 'http://www.inference.phy.cam.ac.uk/db410/',
        'PyPI': False,
    }

    def __init__(self, np_obj):
        dimpy.m = dimpy.meter
        dimpy.s = dimpy.second
        base.BenchModule.__init__(self, np_obj)

    @property
    def name(self):
        return "dimpy"

    @property
    def make_syntax(self):
        return "multiply"

    def make(self, ndarray, units):
        return getattr(dimpy, units) * ndarray



if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore')
    np.seterr(all='ignore')
    base.bench(BenchDimpy)
