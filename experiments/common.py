__author__ = 'ugonzjo'

import sklearn.metrics as metrics
#import scikits.bootstrap as bootstrap
import pandas as pd
import scipy
import matplotlib.pyplot as pl
from scipy import stats
import datetime


def time():
    return datetime.datetime.now().time().isoformat()

def pretty(x):
    if isinstance(x, dict):
        ans = []
        for (k, v) in x.items():
            ans.append("{}:{}".format(k, pretty(v)))
        return "{" + ",".join(ans) + "}"
    elif isinstance(x, list):
        return "[" + ", ".join([pretty(e) for e in x]) + "]"
    elif isinstance(x, float):
        return "%4.2f" % x
    else:
        return str(x)

def intstr(x):
    return str(int(x))




