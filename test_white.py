__author__ = 'ugonzjo'

from white.evaluation import *
from white.visualization import *
from white.policies import *
import pandas as pd


# def main(filenames="input/df_2.1.119.tsv", sep="\t"):#df_2.4.278.tsv"):#tom_predictions_chapter1.tsv #tdx_1.3.2.61_16.csv
def main(filenames="example_data/example1.csv", plot=True):
    whites = []
    for input in filenames.split(","):
        print input
        df = pd.read_csv(input, sep=("\t" if "tsv" in input else ","))

        policy = SingleKCPolicy(df)
        policy.split_kc(0.4)



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
