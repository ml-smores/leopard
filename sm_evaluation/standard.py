__author__ = 'ugonzjo'
import sklearn.metrics as metrics

def compute_standard_metrics(df):
    auc = float('nan')
    if df['outcome'].nunique() > 1:
        fprs, tprs, thresholds = metrics.roc_curve(df['outcome'], df['predicted_outcome'])
        auc = metrics.auc(fprs, tprs)
    accuracy = metrics.accuracy_score(df['outcome'], df['predicted_outcome'] >= 0.5)

    standard_metrics = {}
    standard_metrics["auc"] = auc
    standard_metrics["accuracy"] = accuracy
    standard_metrics["%correct"] = sum(df['outcome']) / (1.0 * len(df['outcome']))

    return standard_metrics