__author__ = 'ugonzjo'
import numpy as np
import math
import pandas as pd

class WhitePolicy():
    def __init__(self):
        pass

    def simulate(self):
        pass

class SingleKCPolicy (WhitePolicy):
    def __init__(self, df, threshold):
        """ df has a column for student, kc, timestep, pcorrect, outcome """
        WhitePolicy.__init__(self)
        self.df = df
        self.threshold = threshold

    def simulate(self):
        df_kcs = self.df.groupby("kc")

        ans = []
        for g, df_kc in df_kcs:
            #  Add timestep column

            df_kc["timestep"] = 1
            df_kc["timestep"] = df_kc.groupby("student")["timestep"].cumsum()

            # Get boundary:
            decisions =  self.get_boundaries(df_kc, self.threshold)
            decisions = df_kc.merge(decisions, on=["student"], how="left")

            # split
            mastered_rows = (decisions["timestep"]  >=  decisions["boundary"])
            mastered   = decisions[  mastered_rows ]
            unmastered = decisions[ ~ mastered_rows ]  # this takes account of NaN

            # calculate:
            pre = self.get_student_stats(unmastered, "pre")
            pos = self.get_student_stats(mastered, "pos")

            #join previously split:
            kc = pre.join(pos, how="outer")
            kc["id"] = g
            ans.append(kc)

        return pd.concat(ans)




    def get_boundaries(self, df_kc, threshold):
        df_filtered = df_kc[ df_kc["predicted_outcome"]  >= threshold  ]
        df_filtered["boundary"] = df_filtered["timestep"]
        df_students = df_filtered.groupby("student")
        return  df_students.first().reset_index()[ ["student", "boundary"] ]


    def get_student_stats(self, df, prefix):
        df = df.copy()
        # Unfortunately, pandas' groupby doesn't work on NaN values.
        # Remove NaNs:
        df["boundary"] = df["boundary"].fillna(-1)

        students = df.groupby("student")

        ans = students.agg({ "boundary" : ['count', 'max'], "outcome": lambda(l): np.sum([e for e in l if e == 1]) })
        ans.columns = ans.columns.get_level_values(1)
        ans = ans.rename(columns={"count"   : prefix+"_n",
                                  "max"     : prefix+"_effort",
                                  "<lambda>": prefix+"_correct"})



        # Add NaNs back:
        for c in ans.columns:
            ans.loc[ ans[c] == -1 , c ] = float("nan")

        return ans



