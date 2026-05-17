from time import time

def time_measure(func):
    def delta(*args, **kwargs):
        started = time()
        res = func(*args, **kwargs)
        res_time = time() - started
        return res, res_time
    return delta

def iter_measure(func):
    def measuring(*args, **kwargs):
        total_iters = 0
        for item in func(*args,**kwargs):
            total_iters += 1
        result = func(*args,**kwargs)
        return result, total_iters
    return measuring