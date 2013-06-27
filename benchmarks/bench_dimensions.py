import numpy as np
import klaffenbach.dimensions as dimensions

import base


class BenchDimensions(base.BenchModule):
    facts = {
        'LOC': 403,
        'First release': '2010-07',
        'Most recent release': '2010-07',
        'Implementation': 'Container',
        'URL': 'http://code.activestate.com/recipes/577333-numerical-type-with-units-dimensionspy/',
        'PyPI': False,
    }

    @property
    def name(self):
        return "dimensions.py"

    @property
    def make_syntax(self):
        return "constructor"

    def make(self, ndarray, units):
        return dimensions.Q(ndarray, units)


if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore')
    np.seterr(all='ignore')
    base.bench(BenchDimensions)
