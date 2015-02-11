__author__ = 'ugonzjo'
import sklearn.metrics as metrics
import numpy as np
from scipy import stats

# def compute_standard_metrics(df):
# auc = float('nan')
#     if df['outcome'].nunique() > 1:
#         fprs, tprs, thresholds = metrics.roc_curve(df['outcome'], df['predicted_outcome'])
#         auc = metrics.auc(fprs, tprs)
#     accuracy = metrics.accuracy_score(df['outcome'], df['predicted_outcome'] >= 0.5)
#
#     standard_metrics = {}
#     standard_metrics["auc"] = auc
#     standard_metrics["accuracy"] = accuracy
#     standard_metrics["%correct"] = sum(df['outcome']) / (1.0 * len(df['outcome']))
#
#     return standard_metrics


def compute_standard_metrics(df, kc=False, user=False):
    auc = float('nan')
    if df['outcome'].nunique() > 1:
        fprs, tprs, thresholds = metrics.roc_curve(df['outcome'], df['predicted_outcome'])
        auc = metrics.auc(fprs, tprs)
    pct_correct = sum(df['outcome']) / (1.0 * len(df['outcome']))


    accuracy = metrics.accuracy_score(df['outcome'], df['predicted_outcome'] >= 0.5)
    fmeasure = metrics.f1_score(df['outcome'], df['predicted_outcome'] >= 0.5, average=None)[1]  #for the correct class
    mean_sq_error = metrics.mean_squared_error(df['outcome'], df['predicted_outcome'])
    rmse = np.sqrt(mean_sq_error)
    r2 = metrics.r2_score(df['outcome'], df['predicted_outcome'])
    df['predicted'] = df['predicted_outcome'].apply(lambda x: [x, 1 - x])
    log_loss = metrics.log_loss(df['outcome'].tolist(), df['predicted'].tolist())

    mean_auc_by_kc = -1
    if kc:
        auc_by_kc = []
        for kc in df["kc"].unique():
            df_kc = df[df["kc"] == kc]
            kc_auc = float('nan')
            if df_kc['outcome'].nunique() > 1:
                fprs, tprs, thresholds = metrics.roc_curve(df_kc['outcome'], df_kc['predicted_outcome'])
                kc_auc = metrics.auc(fprs, tprs)
                auc_by_kc.append(kc_auc)
        mean_auc_by_kc = np.mean(auc_by_kc)

    mean_auc_by_user = -1
    if user:
        auc_by_user = []
        for user in df["student"].unique():
            df_user = df[df["student"] == user]
            user_auc = float('nan')
            if df_user['outcome'].nunique() > 1:
                fprs, tprs, thresholds = metrics.roc_curve(df_user['outcome'], df_user['predicted_outcome'])
                user_auc = metrics.auc(fprs, tprs)
                auc_by_user.append(user_auc)
        mean_auc_by_user = np.mean(auc_by_user)


    return auc, pct_correct, accuracy, fmeasure, log_loss, rmse, r2, mean_auc_by_kc, mean_auc_by_user