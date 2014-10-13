__author__ = 'ugonzjo'

from white.evaluation import *
from white.visualization import *
from white.policies import *
import pandas as pd

# def main(filenames="input/df_2.1.119.tsv", sep="\t"):#df_2.4.278.tsv"):#tom_predictions_chapter1.tsv #tdx_1.3.2.61_16.csv
def main(filenames="example_data/obj_predictions_chapter1.tsv",
         weighted_by_student=False,
         agg_all_kcs_type="by_threshold",
         integral_lower_bound=0.0,
         plot=False,
         debug=True):
    '''agg_all_type: by_threshold | by_kc '''
    whites = []
    for input in filenames.split(","):
        print input
        df = pd.read_csv(input, sep=("\t" if "tsv" in input else ","))
        policy = SingleKCPolicy(df, debug)
        w = Evaluation(df, policy=policy, weighted_by_student=weighted_by_student, agg_all_kcs_type=agg_all_kcs_type, integral_lower_bound=integral_lower_bound, debug=debug)
        w.aggregate_all_kcs()
        w.compute_standard_metrics()
        w.log(input)
        whites.append(w)

        if plot:
            v = WhiteVisualization(w)
            if agg_all_kcs_type == "by_kc":
                v.plot_by_threshold("single", "images/tdx_")
            else:
                v.plot_by_threshold("all", "images/tdx_")
            # output = os.path.splitext(input)[0] + "_{}.png"
            # v.graph_wuc(output)
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
