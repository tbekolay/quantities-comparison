import numpy as np
import numericalunits

import base


class BenchNumericalunits(base.BenchModule):
    facts = {
        'LOC': 270,
        'First release': '2012-07',
        'Most recent release': '2013-06',
        'Implementation': 'Unique!',
        'URL': 'https://github.com/sbyrnes321/numericalunits',
        'PyPI': 'numericalunits',
    }

    def __init__(self, np_obj):
        numericalunits.reset_units()
        base.BenchModule.__init__(self, np_obj)

    @property
    def name(self):
        return numericalunits.__name__

    @property
    def make_syntax(self):
        return "multiply"

    def make(self, ndarray, units):
        return ndarray * getattr(numericalunits, units)


if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore')
    np.seterr(all='ignore')
    base.bench(BenchNumericalunits)
