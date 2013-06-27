import benchmarks.bench_astropy
import benchmarks.bench_dimensions
import benchmarks.bench_dimpy
import benchmarks.bench_ipython_physics
import benchmarks.bench_magnitude
import benchmarks.bench_numericalunits
import benchmarks.bench_physical_quantities
import benchmarks.bench_pint
import benchmarks.bench_piquant
import benchmarks.bench_quantities
import benchmarks.bench_scimath
import benchmarks.bench_unum
import benchmarks as bm

from pprint import pprint
import json
import warnings

import numpy as np

warnings.simplefilter('ignore')
np.seterr(all='ignore')

classes = (
    bm.bench_astropy.BenchAstropy,
    bm.bench_dimensions.BenchDimensions,
    bm.bench_dimpy.BenchDimpy,
    bm.bench_ipython_physics.BenchIpythonPhysics,
    bm.bench_magnitude.BenchMagnitude,
    bm.bench_numericalunits.BenchNumericalunits,
    bm.bench_physical_quantities.BenchPhysicalQuantities,
    bm.bench_pint.BenchPint,
    bm.bench_piquant.BenchPiquant,
    bm.bench_quantities.BenchQuantities,
    bm.bench_scimath.BenchScimath,
    bm.bench_unum.BenchUnum,
)

res = []
for cls in classes:
    print cls
    res.append(bm.base.bench(cls))

with open('results.json', 'w') as outfile:
    json.dump(res, outfile, indent=2, separators=(',', ': '))
