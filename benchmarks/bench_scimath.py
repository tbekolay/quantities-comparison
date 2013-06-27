import numpy as np
import scimath.units.api as scimath

import base


class BenchScimath(base.BenchModule):
    facts = {
        'LOC': 4488,
        'First release': '2009-03',
        'Most recent release': '2013-03',
        'Implementation': 'Subclass',
        'URL': 'http://docs.enthought.com/scimath/',
        'PyPI': "scimath",
    }

    @property
    def name(self):
        return "scimath"

    @property
    def make_syntax(self):
        return "constructor"

    def make(self, ndarray, units):
        d = scimath.unit_parser.parse_unit(units)
        return scimath.UnitArray(ndarray, units=d)


if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore')
    np.seterr(all='ignore')
    base.bench(BenchScimath)