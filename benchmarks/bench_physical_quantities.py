import numpy as np
import Scientific.Physics.PhysicalQuantities as pq

import base


class BenchPhysicalQuantities(base.BenchModule):
    facts = {
        'LOC': 486,
        'First release': '2005-12',
        'Most recent release': '2012-10',
        'Implementation': 'Container',
        'URL': 'https://bitbucket.org/khinsen/scientificpython',
        'PyPI': False,
        'hg': 'https://bitbucket.org/khinsen/scientificpython',
    }

    @property
    def name(self):
        return "SP.PhysicalQuantities"

    @property
    def make_syntax(self):
        return "constructor"

    def make(self, ndarray, units):
        return pq.PhysicalQuantity(ndarray, units)


if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore')
    np.seterr(all='ignore')
    base.bench(BenchPhysicalQuantities)
