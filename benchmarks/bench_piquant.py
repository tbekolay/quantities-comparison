import numpy as np
import piquant

import base


class BenchPiquant(base.BenchModule):
    facts = {
        'LOC': 5888,
        'First release': '2008-05',
        'Most recent release': '2008-05',
        'Implementation': 'Subclass',
        'URL': 'http://sourceforge.net/p/piquant/code/HEAD/tree/trunk/',
        'PyPI': 'piquant',
    }

    def __init__(self, np_obj):
        piquant.m = piquant.meter
        piquant.mile = piquant.m
        piquant.s = piquant.second
        base.BenchModule.__init__(self, np_obj)

    @property
    def name(self):
        return piquant.__name__

    @property
    def make_syntax(self):
        return "multiply"

    def make(self, ndarray, units):
        return ndarray * getattr(piquant, units)


if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore')
    np.seterr(all='ignore')
    base.bench(BenchPiquant)
