__author__ = 'hy'

import numpy as np
import pandas as pd
from white.common import *


class TriesModel():
    def __init__(self, df, nb_correct=3, type="binary"):
        '''
        type: "binary": predicts prob(correct) either 0 or 1
              "linear": predicts prob(correct) linearly by nb_correct'''
        group_columns = ["student","kc"] #["user_id", kc]
        df["prior_outcome"] = df.groupby(by=group_columns, sort=False)["outcome"].shift(1).fillna(0).astype(np.uint8)
        df["prior_correct"]  = df.groupby(by=group_columns, sort=False)["prior_outcome"].cumsum()
        self.df = df
        self.nb_correct = nb_correct
        self.type = type

    def predict_proba(self):
        if self.type == "linear":
            step = 1.0 / self.nb_correct
            print "To implement..."
            exit(-1)
            df["pcorrect"] = df.prior_correct.apply(self.linear_predictor)
        else:
            self.df["pcorrect"] = self.df.prior_correct.apply(lambda x: 0 if x < self.nb_correct else 1)
        self.df.to_csv("../example_data/obj_predictions_chapter1_tries_model.tsv", sep="\t")

    def linear_predictor(self):
        #lambda x: 0 if x == 0 else (0.333 if x == 1 else (0.666 if x == 2 else 1))
        pass


def main(filename="../example_data/obj_predictions_chapter1.tsv"):
    df = pd.read_csv(filename, sep=("\t" if "tsv" in filename else ","))
    t = TriesModel(df)
    t.predict_proba()



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

