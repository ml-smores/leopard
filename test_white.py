__author__ = 'ugonzjo'

from sm_evaluation.white import White
#from sm_evaluation.visualization import *
from sm_evaluation.policies import SingleKCPolicy
import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


# def main(filenames="input/df_2.1.119.tsv", sep="\t"):#df_2.4.278.tsv"):#tom_predictions_chapter1.tsv #tdx_1.3.2.61_16.csv
def main(filenames="example_data/tom_predictions_chapter2.tsv", threshold=0.6, plot=True):
    whites = []
    for input in filenames.split(","):
        print input
        df = pd.read_csv(input, sep=("\t" if "tsv" in input else ","))
        #df = df[df["kc"] == "2_1_difficult"] # .head(10000)
        policy = SingleKCPolicy(df, threshold=threshold)
        e = White(policy)
        print e.evaluate()




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
