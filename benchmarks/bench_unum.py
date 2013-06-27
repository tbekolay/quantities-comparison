import numpy as np
import unum.units

import base


class BenchUnum(base.BenchModule):
    facts = {
        'LOC': 778,
        'First release': '2000',
        'Most recent release': '2010-06',
        'Implementation': 'Container',
        'URL': 'http://home.scarlet.be/be052320/Unum.html',
        'PyPI': 'unum',
    }

    @property
    def name(self):
        return unum.__name__

    @property
    def make_syntax(self):
        return "multiply"

    def make(self, ndarray, units):
        # NB! units must be on the left!
        return getattr(unum.units, units) * ndarray


if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore')
    np.seterr(all='ignore')
    base.bench(BenchUnum)
