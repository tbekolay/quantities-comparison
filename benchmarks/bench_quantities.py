import numpy as np
import quantities as pq

import base


class BenchQuantities(base.BenchModule):
    facts = {
        'LOC': 7030,
        'First release': '2009-10',
        'Most recent release': '2011-09',
        'Implementation': 'Subclass',
        'URL': 'http://pythonhosted.org/quantities/',
        'PyPI': 'quantities',
    }

    @property
    def name(self):
        return pq.__name__

    @property
    def make_syntax(self):
        return "multiply"

    def make(self, ndarray, units):
        return ndarray * getattr(pq, units)


if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore')
    np.seterr(all='ignore')
    base.bench(BenchQuantities)
