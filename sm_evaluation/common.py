__author__ = 'ugonzjo'

import sklearn.metrics as metrics

def pretty(x):
    if isinstance(x, dict):
        ans = []
        for (k, v) in x.items():
            ans.append("{}:{}".format(k, pretty(v)))
        return "{" + ",".join(ans) + "}"
    elif isinstance(x, list):
        return "[" + ", ".join([pretty(e) for e in x]) + "]"
    elif isinstance(x, float):
        return "%4.3f" % x
    else:
        return str(x)

def intstr(x):
    return str(int(x))

def compute_standard_metrics(df):
    auc = float('nan')
    if df['outcome'].nunique() > 1:
        fprs, tprs, thresholds = metrics.roc_curve(df['outcome'], df['predicted_outcome'])
        auc = metrics.auc(fprs, tprs)
    #accuracy = metrics.accuracy_score(df['outcome'], df['pcorrect'] >= 0.5)
    #standard_metrics["auc"] = auc
    #standard_metrics["accuracy"] = accuracy
    #standard_metrics["%correct"] = sum(df['outcome']) / (1.0 * len(df['outcome']))
    return auc
