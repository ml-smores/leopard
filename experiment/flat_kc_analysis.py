__author__ = 'ugonzjo'

from sm_evaluation.white import White
from sm_evaluation.policies import SingleKCPolicy
from sm_evaluation.common import *
from sm_evaluation.standard import *
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

#private_data
def main(filenames="example_data/tdx_predictions_chapter1.tsv", threshold=0.6, plot=True):
    df_flat_kcs = pd.read_csv("example_data/tdx_summary_chapter1.tsv", sep="\t")
    df_flat_kcs = df_flat_kcs[df_flat_kcs["got_correct"] == 0]
    whites = []
    for input in filenames.split(","):
        print input
        df = pd.read_csv(input, sep=("\t" if "tsv" in input else ","))
        print "Datapoints:", len(df), "kcs:", df.kc.nunique()
        df = df[df["kc"].isin(df_flat_kcs["kc"].unique())]
        print "Datapoints of flat kcs:", len(df), "kcs:", df.kc.nunique()

        policy = SingleKCPolicy(df, threshold=threshold)
        e = White(policy)
        print e
        auc, pct_correct = compute_standard_metrics(df)
        print "auc=", pretty(auc), "pct_correct=", pretty(pct_correct)

        #if plot:
        #    v = WhiteVisualization(w)
        #    kctype = input.split('/')[1].split('_')
        #    if agg_all_kcs_type == "by_kc":
        #        v.plot_by_threshold("single", "images/"+kctype[0]+"_")
        #    else:
        #        v.plot_by_threshold("all", "images/"+kctype[0]+"_")

    print "Done"

    # If you need to do multi-dataset comparison do them here:
    #foo(whites)


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

