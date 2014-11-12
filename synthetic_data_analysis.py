__author__ = 'hy'

from sm_evaluation.white import *
from sm_evaluation.visualization import *
from sm_evaluation.policies import *
import pandas as pd


def get_synthetic_data_results(path):
    filenames = ""
    df = pd.read_csv(path + "identifiers_obj.txt")
    kcs = df.kc.unique()
    for kc in kcs:
        filenames += "," + path + kc + "_pcorrect.csv"
    return filenames


# def main(filenames="input/df_2.1.119.tsv", sep="\t"):#df_2.4.278.tsv"):#tom_predictions_chapter1.tsv #tdx_1.3.2.61_16.csv #obj_predictions_chapter1_tries_model_linear
def main(filenames="private_data/obj_predictions_chapter1.tsv", threshold=0.6, plot=True): #example_data/example1.csv"
    filenames = get_synthetic_data_results("example_data/")
    whites = []
    aucs = []
    for input in filenames.split(","):
        if len(input) == 0:
            continue
        print input
        df = pd.read_csv(input, sep=("\t" if "tsv" in input else ","))
        df = df.rename(columns={'pcorrect': 'predicted_outcome'})
        print "Datapoints:", len(df)
        policy = SingleKCPolicy(df, threshold=threshold)
        e = White(policy)
        print e
        whites.append(e)
        aucs.append(compute_standard_metrics(df))

    WhiteVisualization.plot_auc_vs_white(whites, aucs, "images/synthetic_data_auc_vs_{}.pdf")

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
