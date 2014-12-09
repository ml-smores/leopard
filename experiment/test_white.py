__author__ = 'ugonzjo'

from sm_evaluation.white import White
from sm_evaluation.policies import *
from sm_evaluation.visualization import *
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

#private_data
def main(filenames="../example_data/output.csv", threshold=0.5, plot=False, compute_ci=False): #example_data/example1.csv" threshold=0.6
    whites = []
    for input in filenames.split(","):
        print input
        df = pd.read_csv(input, sep=("\t" if "tsv" in input else ","))
        print "Datapoints:", len(df), "#kcs:", df["kc"].nunique(), "threshold:", threshold, "#students:", df.student.nunique()

        policy = SingleKCPolicy(df, threshold=threshold)
        e = White(policy, compute_ci=compute_ci)
        print e
        #auc, pct_correct = compute_standard_metrics(df)
        #print "auc=", pretty(auc), "pct_correct=", pretty(pct_correct)

        if plot:
            kctype = input.split('/')[-1].split('_')[0]
            WhiteVisualization.plot_white_distribution_across_kcs(e, "../images/" + kctype + "_{}_distr_across_kcs.pdf")

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
