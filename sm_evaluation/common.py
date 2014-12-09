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

def analyze_correlation(x, y):
    correlation, correlation_pval = stats.spearmanr(x, y)
    correlation_str = "Spearman correlation : {:4.2f}".format(correlation) + ", p-value:{:5.3f}".format(correlation_pval)
    print correlation_str
    return correlation, correlation_pval

def bootstrap_ci():
    df_bootstrap = pd.read_csv("../example_data/obj_bootstrap_input.csv")
    #compute confidence intervals around the mean, default  95% , 10000 samples
    cis = bootstrap.ci(data=df_bootstrap["score"], statfunction=scipy.mean) #, alpha=0.2, n_samples=20000)
    print "mean", df_bootstrap["score"].mean(), "Bootstrapped 95% confidence intervals Low:", cis[0], "High:", cis[1]
    cis_effort = bootstrap.ci(data=df_bootstrap["effort"], statfunction=scipy.mean) #, alpha=0.2, n_samples=20000)
    print "mean", df_bootstrap["effort"].mean(), "Bootstrapped 95% confidence intervals Low:", cis_effort[0], "High:", cis_effort[1]
    cis_effort_filled = bootstrap.ci(data=df_bootstrap["effort_filled"], statfunction=scipy.mean) #, alpha=0.2, n_samples=20000)
    print "mean", df_bootstrap["effort_filled"].mean(), "Bootstrapped 95% confidence intervals Low:", cis_effort_filled[0], "High:", cis_effort_filled[1]



def main():
    bootstrap_ci()

if __name__ == "__main__":
    import sys

    args = sys.argv
    print args
    cl = {}
    for i in range(1, len(args)):  # index 0 is the filename
        pair = args[i].split('=')
        if pair[1].isdigit():
            cl[pair[0]] = int(pair[1])
        elif pair[1].lower() in ("true", "false"):
            cl[pair[0]] = (pair[1].lower() == 'true')
        else:
            cl[pair[0]] = pair[1]

    main(**cl)


