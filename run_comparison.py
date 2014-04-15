import benchmarks.bench_astropy
import benchmarks.bench_dimensions
import benchmarks.bench_dimpy
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
import pandas as pd

warnings.simplefilter('ignore')
np.seterr(all='ignore')

CLASSES = (bm.bench_astropy.BenchAstropy,
           bm.bench_dimensions.BenchDimensions,
           bm.bench_dimpy.BenchDimpy,
           bm.bench_magnitude.BenchMagnitude,
           bm.bench_numericalunits.BenchNumericalunits,
           bm.bench_physical_quantities.BenchPhysicalQuantities,
           bm.bench_pint.BenchPint,
           bm.bench_piquant.BenchPiquant,
           bm.bench_quantities.BenchQuantities,
           bm.bench_scimath.BenchScimath,
           bm.bench_unum.BenchUnum,
           )


def run_comparisons(classes=CLASSES):
    for cls in classes:
        print cls.__name__
        yield bm.base.bench(cls)


def save_comparisons(res, fname=None):
    if fname is None:
        fname = 'results.json'

    with open(fname, 'w') as outfile:
        json.dump(list(res), outfile, indent=2, separators=(',', ': '))


def get_comparisons(classes=CLASSES, fname=None):
    res = run_comparisons(classes)
    save_comparisons(res, fname)


def process_pandas(res):
    facts = {}
    syntax = {}
    speed = {}
    compatibility = {}

    for ires in res:
        name = ires['name']
        facts[name] = ires['facts']
        syntax[name] = ires['syntax']

        # We want to transpose the speed dict so it is organized
        # by operation type rather than measurement.
        # With pandas 1.4 we should be ablle to add error bars as well.
        for key, value in ires['speed'].items():
            for key1, value1 in value.items():
                if key1 not in speed:
                    speed[key1] = {}
                if key not in speed[key1]:
                    speed[key1][key] = {}
                speed[key1][key][name] = value1

        for key, value in ires['compatibility'].items():
            if key not in compatibility:
                compatibility[key] = {}
            compatibility[key][name] = value

    facts = pd.DataFrame.from_dict(facts, orient='index')
    syntax = pd.DataFrame.from_dict(syntax, orient='index')

    facts = facts.sort(axis=0).sort(axis=1)
    syntax = syntax.sort(axis=0).sort(axis=1)

    for key, value in speed.items():
        value = pd.DataFrame.from_dict(value, orient='columns')
        speed[key] = value.sort(axis=0).sort(axis=1)
    for key, value in compatibility.items():
        value = pd.DataFrame.from_dict(value, orient='index')
        compatibility[key] = value.sort(axis=0).sort(axis=1)

    resdict = {'facts': facts,
               'syntax': syntax,
               'speed': speed,
               'compatibility': compatibility}

    return resdict


def get_pandas(classes=CLASSES):
    res = run_comparisons(classes)
    return process_pandas(res)


if __name__ == "__main__":
    get_comparisons()
