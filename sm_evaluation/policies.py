__author__ = 'ugonzjo'
import numpy as np
import math
import pandas as pd

verbose = False

class WhitePolicy():
    def __init__(self):
        pass

    def simulate(self):
        pass

    @staticmethod
    def get_thresholds(df):
        thresholds = df["predicted_outcome"].unique().tolist()
        thresholds.sort()
        if 0 not in thresholds:
            thresholds.insert(0, 0.0)
        if 1 not in thresholds:
            thresholds.append(1.0)
        return thresholds

class SingleKCPolicy (WhitePolicy):
    def __init__(self, df, threshold):
        """ df has a column for student, kc, timestep, pcorrect, outcome """
        WhitePolicy.__init__(self)
        self.df = df
        self.threshold = threshold
        self.name = "single_kc"


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

            # hy: changed >= to >
            mastered_rows = (decisions["timestep"]  >  decisions["boundary"])

            decisions["mastered"] = mastered_rows
            if verbose:
                print decisions

            # calculate:
            pre = self.get_student_stats(decisions, False)
            pos = self.get_student_stats(decisions, True)

            kc =  pre.join(pos, how="outer", rsuffix="_pos", lsuffix="_pre")
            kc["id"] = g
            kc["mastered"] = ~ kc["effort_pos"].isnull()

            ans.append(kc)
            if verbose:
                print kc

        return pd.concat(ans)




    def get_boundaries(self, df_kc, threshold):
        df_filtered = df_kc[ df_kc["predicted_outcome"]  >= threshold  ]
        df_filtered["boundary"] = df_filtered["timestep"] - 1

        df_students = df_filtered.groupby("student")
        df_boundaries = df_students.first().reset_index()

        if len(df_boundaries) == 0:
            df_boundaries["student"] = [] # Bug fix

        return  df_boundaries[ ["student", "boundary"] ]


    def get_student_stats(self, df, mastery):
        #Filter data.  Make a copy so to not get warnings....
        df = df[ df["mastered"] == mastery ].copy()

        # Unfortunately, pandas' groupby doesn't work on NaN values.
        # Remove NaNs:
        df.loc[:, "boundary"] = df["boundary"].fillna(-1)

        students = df.groupby("student")

        ans = students.agg({ "boundary" : ['count', 'max'], "outcome": lambda(l): np.sum([e for e in l if e == 1]) })
        ans.columns = ans.columns.get_level_values(1)
        ans = ans.rename(columns={"count"   :   "n",
                                  "max"     :   "effort",
                                  "<lambda>":   "correct"})

        # hy changed:
        if not mastery:
            #hy: commented original
            #     ans["effort"] = students["timestep"].max() + 1 #
            ans["effort"] = students["timestep"].max()

        # Add NaNs back:
        for c in ans.columns:
            ans.loc[ ans[c] <= -1 , c ] = float("nan")

        return ans

    # hy:
    # def adjust(self, df):
    #     print "apply df:", df
    #     print "timestep max:", df["timestep"].max(), "\nboundary max:", df["boundary"].max()
    #     value= df["timestep"].max() if df["boundary"].max() == -1 else (df["boundary"].max() - 1)
    #     print "return:", value
    #     return value


# to slow
class SingleStudentPolicy (WhitePolicy):
    def __init__(self, df, threshold):
        """ df has a column for student, kc, timestep, pcorrect, outcome """
        WhitePolicy.__init__(self)
        self.df = df
        self.threshold = threshold
        self.name = "single_student"


    def simulate(self):
        df_stus = self.df.groupby("student")

        ans = []
        i = 0
        for g, df_stu in df_stus:
            if (i % 100) == 0:
                print i, "th student out of ", self.df.student.nunique()
            i += 1
            #  Add timestep column
            df_stu["timestep"] = 1
            df_stu["timestep"] = df_stu.groupby("kc")["timestep"].cumsum()

            # Get boundary:
            decisions =  self.get_boundaries(df_stu, self.threshold)
            decisions = df_stu.merge(decisions, on=["kc"], how="left")

            # hy: changed >= to >
            mastered_rows = (decisions["timestep"]  >  decisions["boundary"])
            decisions["mastered"] = mastered_rows
            if verbose:
                print decisions

            # calculate:
            pre = self.get_kc_stats(decisions, False)
            pos = self.get_kc_stats(decisions, True)

            stu =  pre.join(pos, how="outer", rsuffix="_pos", lsuffix="_pre")
            stu["id"] = g
            stu["mastered"] = ~ stu["effort_pos"].isnull()

            ans.append(stu)
            if verbose:
                print stu

        return pd.concat(ans)

    def get_boundaries(self, df_stu, threshold):
        df_filtered = df_stu[ df_stu["predicted_outcome"]  >= threshold  ]
        df_filtered["boundary"] = df_filtered["timestep"] - 1

        df_kcs = df_filtered.groupby("kc")
        df_boundaries = df_kcs.first().reset_index()

        if len(df_boundaries) == 0:
            df_boundaries["kc"] = [] # Bug fix

        return  df_boundaries[ ["kc", "boundary"] ]


    def get_kc_stats(self, df, mastery):
        #Filter data.  Make a copy so to not get warnings....
        df = df[ df["mastered"] == mastery ].copy()

        # Unfortunately, pandas' groupby doesn't work on NaN values.
        # Remove NaNs:
        df.loc[:, "boundary"] = df["boundary"].fillna(-1)

        kcs = df.groupby("kc")

        ans = kcs.agg({ "boundary" : ['count', 'max'], "outcome": lambda(l): np.sum([e for e in l if e == 1]) })
        ans.columns = ans.columns.get_level_values(1)
        ans = ans.rename(columns={"count"   :   "n",
                                  "max"     :   "effort",
                                  "<lambda>":   "correct"})

        # hy changed:
        if not mastery:
            for ind in ans.index:
                kc = kcs.get_group(ind)#ans.loc[pos, "kc"])
                boundary = kc["boundary"].max()
                timestep = kc["timestep"].max()
                ans.ix[ind, "effort"] = timestep if boundary == -1 else (boundary - 1)
        # if not mastery:
        #     ans["effort"] = students["timestep"].max() #+1 #


        for c in ans.columns:
            ans.loc[ ans[c] <= -1 , c ] = float("nan")

        return ans

