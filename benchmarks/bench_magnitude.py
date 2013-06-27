import numpy as np
import magnitude

import base


class BenchMagnitude(base.BenchModule):
    facts = {
        'LOC': 483,
        'First release': '2010-05',
        'Most recent release': '2010-05',
        'Implementation': 'Container',
        'URL': 'http://juanreyero.com/open/magnitude/index.html',
        'PyPI': 'magnitude',
    }

    @property
    def name(self):
        return magnitude.__name__

    @property
    def make_syntax(self):
        return "constructor"

    def make(self, ndarray, units):
        return magnitude.mg(ndarray, units)


if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore')
    np.seterr(all='ignore')
    base.bench(BenchMagnitude)
