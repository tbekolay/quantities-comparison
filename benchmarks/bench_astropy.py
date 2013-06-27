import numpy as np
import astropy.units

import base


class BenchAstropy(base.BenchModule):
    facts = {
        'LOC': 3448,
        'First release': '2013-01',
        'Most recent release': '2013-05',
        'Implementation': 'Container',
        'URL': 'https://astropy.readthedocs.org/en/latest/units/index.html',
        'PyPI': 'astropy',
    }

    @property
    def name(self):
        return astropy.units.__name__

    @property
    def make_syntax(self):
        return "multiply"

    def make(self, ndarray, units):
        return getattr(astropy.units, units) * ndarray


if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore')
    np.seterr(all='ignore')
    base.bench(BenchAstropy)
