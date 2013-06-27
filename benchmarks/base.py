import inspect
import operator as op
import time

import numpy as np


class Timer(object):
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs


def time_unary(ndarrays, funcs):
    with Timer() as t:
        for func in funcs:
            for nda in ndarrays:
                func(nda)
    return t.msecs


def time_binary(left, right, funcs):
    with Timer() as t:
        for func in funcs:
            for l in left:
                for r in right:
                    func(l, r)
    return t.msecs


class BenchNumpy(object):
    def __init__(self, dtype=np.float64):
        self.dtype = dtype

        self.unary_ops = [op.abs, op.neg, op.pos]
        self.binary_ops = [op.add, op.sub, op.mul,
                           op.div, op.floordiv, op.truediv,
                           op.mod, op.pow,
                           op.lt, op.le, op.eq, op.ne, op.ge, op.gt]

        # from http://docs.scipy.org/doc/numpy/reference/ufuncs.html
        self.unary_ufuncs = [
            np.negative, np.absolute, np.rint, np.sign, np.conj, np.exp,
            np.exp2, np.log, np.log2, np.log10, np.expm1, np.log1p,
            np.sqrt, np.square, np.reciprocal, np.ones_like,
            np.sin, np.cos, np.tan, np.arcsin, np.arccos, np.arctan,
            np.sinh, np.cosh, np.tanh, np.arcsinh, np.arccosh, np.arctanh,
            np.deg2rad, np.rad2deg,
            np.floor, np.ceil, np.trunc,
        ]

        self.binary_ufuncs = [
            np.add, np.subtract, np.multiply, np.divide, np.logaddexp,
            np.logaddexp2, np.true_divide, np.floor_divide, np.power,
            np.remainder, np.mod, np.fmod,
            np.arctan2, np.hypot,
            np.greater, np.greater_equal, np.less, np.less_equal,
            np.not_equal, np.equal,
            np.maximum, np.minimum,
        ]

        self.other_numpy = [
            np.where, np.sort, np.argsort,
            np.concatenate, np.mean, np.std, np.median,
        ]

    def rand(self, shape):
        return (10 * np.random.rand(*shape)).astype(self.dtype, copy=False)

    def time(self, n=100):
        shapes = [(10,), (1000,), (100, 100)]
        time = []
        for i in range(n):
            t = 0.0
            for shape in shapes:
                pos = self.rand(shape)
                pos2 = self.rand(shape)
                neg = -self.rand(shape)
                t += time_unary([pos, neg], self.unary_ops)
                t += time_unary([pos, neg], self.unary_ufuncs)
                t += time_binary([pos], [pos2, neg], self.binary_ops)
                t += time_binary([pos], [pos2, neg], self.binary_ufuncs)
            time.append(t)

        # Get rid of the top and bottom 2
        if n > 10:
            time.sort()
            time = np.asarray(time[2:-2])

        print "{:.3f} +/- {:.2f} ms".format(np.mean(time), np.std(time))
        return time


class BenchModule(object):
    def __init__(self, np_obj):
        self.np_obj = np_obj
        self.unary_ops = [
            o for o in np_obj.unary_ops if self.test_unary(o)]
        self.binary_same_ops = [
            o for o in np_obj.binary_ops if self.test_binary_same(o)]
        self.binary_compatible_ops = [
            o for o in np_obj.binary_ops if self.test_binary_compatible(o)]
        self.binary_different_ops = [
            o for o in np_obj.binary_ops if self.test_binary_different(o)]
        self.unary_ufuncs = [
            o for o in np_obj.unary_ufuncs if self.test_unary(o)]
        self.binary_same_ufuncs = [
            o for o in np_obj.binary_ufuncs if self.test_binary_same(o)]
        self.binary_compatible_ufuncs = [
            o for o in np_obj.binary_ufuncs if self.test_binary_compatible(o)]
        self.binary_different_ufuncs = [
            o for o in np_obj.binary_ufuncs if self.test_binary_different(o)]
        self.other_numpy = self.test_other_numpy()

    ## Helpers

    def rand(self, shape):
        return self.np_obj.rand(shape)

    def test_unary(self, func):
        x = self.make(self.rand(shape=(2,)), units='m')
        try:
            func(x)
        except:
            return False
        return True

    def test_binary_same(self, func):
        x = self.make(self.rand(shape=(2,)), units='m')
        y = self.make(self.rand(shape=(2,)), units='m')
        try:
            func(x, y)
        except:
            return False
        return True

    def test_binary_compatible(self, func):
        x = self.make(self.rand(shape=(2,)), units='m')
        try:
            y = self.make(self.rand(shape=(2,)), units='mile')
        except:
            try:
                y = self.make(self.rand(shape=(2,)), units='ft')
            except:
                return False
        try:
            func(x, y)
        except:
            return False
        return True

    def test_binary_different(self, func):
        x = self.make(self.rand(shape=(2,)), units='m')
        y = self.make(self.rand(shape=(2,)), units='s')
        try:
            func(x, y)
        except:
            return False
        return True

    def test_other_numpy(self):
        # For each, if it works we add it
        good = []
        bad = []
        q1 = self.make(self.rand((10,)), 'm')
        q2 = self.make(self.rand((5,)), 'm')

        try:
            np.where(q1 > self.make(0.0, 'm'))
        except Exception as e:
            bad.append(str(e))
        else:
            good.append(np.where)

        try:
            np.sort(q1)
        except Exception as e:
            bad.append(str(e))
        else:
            good.append(np.sort)

        try:
            np.argsort(q1)
        except Exception as e:
            bad.append(str(e))
        else:
            good.append(np.argsort)

        try:
            np.mean(q1)
        except Exception as e:
            bad.append(str(e))
        else:
            good.append(np.mean)

        try:
            np.std(q1)
        except Exception as e:
            bad.append(str(e))
        else:
            good.append(np.std)

        try:
            np.median(q1)
        except Exception as e:
            bad.append(str(e))
        else:
            good.append(np.median)

        try:
            np.concatenate((q1, q2))
        except Exception as e:
            bad.append(str(e))
        else:
            good.append(np.concatenate)

        return good

    def make_args(self, argspec, shape):
        np_args = []
        args = []
        for arg in argspec.args:
            if arg == 'self':
                continue

            if arg == 'shape':
                np_args.append(shape)
                args.append(shape)
                continue

            ndarray = self.rand(shape)
            if arg.startswith('neg'):
                ndarray *= -1
            np_args.append(ndarray)
            if arg.endswith('compatible'):
                try:
                    args.append(self.make(ndarray, 'mile'))
                except:
                    args.append(self.make(ndarray, 'ft'))
            elif arg.endswith('different'):
                args.append(self.make(ndarray, 's'))
            else:
                args.append(self.make(ndarray, 'm'))

        return tuple(np_args), tuple(args)

    def time_func(self, func, shapes=((1,), (1000,), (100, 100)),
                  iters=50, timeout=2000.0, verbose=False):
        np_time = []
        time = []
        argspec = inspect.getargspec(func)

        for i in range(iters):
            for shape in shapes:
                np_args, args = self.make_args(argspec, shape)
                try:
                    np_time.append(func(*np_args))
                except:
                    np_time.append(np.inf)
                try:
                    time.append(func(*args))
                except Exception as e:
                    return -1, -1, -1
                if time[-1] > timeout:
                    if verbose:
                        print "{}.{} timed out".format(self.name, func.__name__)
                    return 20.0, 20.0, 20.0

        # Get rid of the top and bottom 2
        if iters > 10:
            np_time.sort()
            np_time = np.asarray(np_time[2:-2])
            time.sort()
            time = np.asarray(time[2:-2])

        mean = np.mean(time)
        std = np.std(time)
        np_rel = np.sum(time) / np.sum(np_time)

        if verbose:
            print "{}.{}: {:.3f} +/- {:.2f} ms, {:.2f}x numpy".format(
                self.name, func.__name__, mean, std, np_rel)

        return mean, std, min(np_rel, 20.0)

    def time_make(self, shape):
        with Timer() as t:
            self.make(self.rand(shape), units='m')
        return t.msecs

    def time_ops(self, pos, neg_same, pos_compatible, neg_different):
        t = 0.0
        t += time_unary([pos, neg_same, pos_compatible, neg_different],
                        self.unary_ops)
        t += time_binary([pos], [neg_same], self.binary_same_ops)
        t += time_binary([pos], [neg_same, pos_compatible],
                         self.binary_compatible_ops)
        t += time_binary([pos], [neg_same, pos_compatible, neg_different],
                         self.binary_different_ops)
        return t

    def time_ufuncs(self, pos, neg_same, pos_compatible, neg_different):
        t = 0.0
        t += time_unary([pos, neg_same, pos_compatible, neg_different],
                        self.unary_ufuncs)
        t += time_binary([pos], [neg_same], self.binary_same_ufuncs)
        t += time_binary([pos], [neg_same, pos_compatible],
                         self.binary_compatible_ufuncs)
        t += time_binary([pos], [neg_same, pos_compatible, neg_different],
                         self.binary_different_ufuncs)
        return t

    ## Actual test functions that gather data

    def syntax(self, verbose=False):
        q = self.make(5.0, 'm')
        if verbose:
            print q
        return {
            'make': self.make_syntax,
            'print': str(q)
        }

    def compatibility(self, verbose=False):
        compares = [
            # (BenchModule.attr, BenchNumPy.np_attr)
            ('unary_ops', 'unary_ops'),
            ('binary_same_ops', 'binary_ops'),
            ('binary_compatible_ops', 'binary_ops'),
            ('binary_different_ops', 'binary_ops'),
            ('unary_ufuncs', 'unary_ufuncs'),
            ('binary_same_ufuncs', 'binary_ufuncs'),
            ('binary_compatible_ufuncs', 'binary_ufuncs'),
            ('binary_different_ufuncs', 'binary_ufuncs'),
            ('other_numpy', 'other_numpy'),
        ]

        res = {}

        res['syntax'] = {}
        try:
            res['syntax']['print'] = str(self.make([5.0, 10.0], 'm'))
        except:
            res['syntax']['print'] = False
        try:
            res['syntax']['shape'] = str(self.make([5.0, 10.0], 'm').shape)
        except:
            res['syntax']['shape'] = False

        for attr, np_attr in compares:
            if verbose:
                self_n = len(getattr(self, attr))
                np_n = len(getattr(self.np_obj, np_attr))
                print "{}: {} / {} ({:.1%}".format(
                    attr, self_n, np_n, float(self_n) / np_n)

            res[attr] = {f.__name__: (f in getattr(self, attr))
                         for f in getattr(self.np_obj, np_attr)}

        return res

    def time(self, verbose=False):
        make_mean, make_std, make_rel = self.time_func(self.time_make)
        op_mean, op_std, op_rel = self.time_func(self.time_ops)
        ufunc_mean, ufunc_std, ufunc_rel = self.time_func(self.time_ufuncs)

        return {
            'make': {'mean': make_mean, 'std': make_std, 'np_rel': make_rel},
            'ops': {'mean': op_mean, 'std': op_std, 'np_rel': op_rel},
            'ufunc': {'mean': ufunc_mean, 'std': ufunc_std, 'np_rel': ufunc_rel},
        }

    ## To be overridden by subclasses

    @property
    def name(self):
        raise NotImplementedError()

    @property
    def make_syntax(self):
        raise NotImplementedError()

    def make(self, ndarray, units):
        raise NotImplementedError()


def bench(cls):
    np_obj = BenchNumpy()
    b = cls(np_obj)

    res = {}
    res['name'] = b.name
    res['facts'] = b.facts
    try:
        res['syntax'] = b.syntax()
    except Exception as e:
        res['syntax'] = str(e)
    try:
        res['compatibility'] = b.compatibility()
    except Exception as e:
        res['compatibility'] = str(e)
    res['speed'] = b.time()
    return res


if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore')
    np.seterr(all='ignore')
    bench = BenchNumpy()
    bench.time()
