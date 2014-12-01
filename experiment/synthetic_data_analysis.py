__author__ = 'hy'

from sm_evaluation.white import *
from sm_evaluation.visualization import *
from sm_evaluation.policies import *
from sm_evaluation.standard import *
import pandas as pd

root_path = "/Users/hy/inf/Study/CS/Projects_Codes_Data/Data/Data_white/synthetic_data/"
exp_path = "data_20kc_perchapter_with_learning/"

def get_synthetic_data_results(path):
    df = pd.read_csv(path + "identifiers_obj.txt")
    df_grouped = df.groupby("chapter", as_index=False).agg({"kc": ",".join})
    dfs = []
    for pos in range(len(df_grouped)):
        #print df_grouped.loc[pos, "chapter"]
        kcs = df_grouped.loc[pos, "kc"].split(",")
        df_chapter = pd.DataFrame()
        for kc in kcs:
            #print kc
            df_chapter = pd.concat([df_chapter, pd.read_csv(path + kc + "_pcorrect.csv")])
        dfs.append(df_chapter)
    return dfs

# def main(filenames="input/df_2.1.119.tsv", sep="\t"):#df_2.4.278.tsv"):#tom_predictions_chapter1.tsv #tdx_1.3.2.61_16.csv #obj_predictions_chapter1_tries_model_linear
def main(threshold=0.6, plot=True): #example_data/example1.csv"
    dfs = get_synthetic_data_results(root_path + exp_path) #"../synthetic_data/")
    whites = []
    aucs = []
    for df in dfs:
        df = df.rename(columns={'pcorrect': 'predicted_outcome'})
        print "Datapoints:", len(df)
        policy = SingleKCPolicy(df, threshold=threshold)
        e = White(policy)
        print e
        whites.append(e)
        auc, pct_correct = compute_standard_metrics(df)
        aucs.append(auc)
    if plot:
        WhiteVisualization.plot_auc_vs_white(whites, aucs, "../images/" + exp_path + "synthetic_data_auc_vs_{}.pdf")
        WhiteVisualization.plot_histogram(whites, aucs, "../images/" + exp_path + "synthetic_data_histogram_{}.pdf")
    print "Done"

    #If you need to do multi-dataset comparison do them here:
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
