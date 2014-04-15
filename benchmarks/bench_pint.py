import numpy as np
import pint

import base


class BenchPint(base.BenchModule):
    facts = {
        'LOC': 2914,
        'First release': '2012-07',
        'Most recent release': '2014-02',
        'Implementation': 'Container',
        'URL': 'https://pint.readthedocs.org/en/latest/',
        'PyPI': 'pint',
    }

    def __init__(self, np_obj):
        self.unitreg = pint.UnitRegistry()
        base.BenchModule.__init__(self, np_obj)

    @property
    def name(self):
        return pint.__name__

    @property
    def make_syntax(self):
        return "multiply"

    def make(self, ndarray, units):
        return ndarray * getattr(self.unitreg, units)


if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore')
    np.seterr(all='ignore')
    base.bench(BenchPint)
