import numpy as np
import physics.physics as physics

import base


class BenchIpythonPhysics(base.BenchModule):
    facts = {
        'LOC': 640,
        'First release': '2011-10',
        'Most recent release': '2013-03',
        'Implementation': 'Container',
        'URL': 'https://bitbucket.org/birkenfeld/ipython-physics',
        'PyPI': False,
        'hg': 'https://bitbucket.org/birkenfeld/ipython-physics',
    }

    @property
    def name(self):
        return "ipython-physics"

    @property
    def make_syntax(self):
        return "constructor"

    def make(self, ndarray, units):
        return physics.Q(ndarray, units)


if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore')
    np.seterr(all='ignore')
    base.bench(BenchIpythonPhysics)
