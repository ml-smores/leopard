__author__ = 'ugonzjo'
import numpy as np
from common import *
import math
import pandas as pd

class SimulationResult:
    def __init__(self, n_students, effort, mean_pre_outcome = -1, mean_post_outcome = -1):
        self.n_students = n_students
        self.effort = effort
        self.mean_pre_outcome = mean_pre_outcome
        self.mean_post_outcome = mean_post_outcome
    def __repr__(self):
        return "< ({}) {}  [ {} | {}  ] >".format(self.n_students, self.effort, self.mean_pre_outcome, self.mean_post_outcome)




class Policy():
    def __init__(self):
        pass

    def simulate(self):
        pass





class SingleKCPolicy (Policy):
    def __init__(self, df):
        """ df has a column for student, kc, timestep, pcorrect, outcome """
        Policy.__init__(self)
        self.df = df

    def split_kc(self, threshold):
        df_kcs = self.df.groupby("kc")
        for g, df_kc in df_kcs:
            #  Add timestep column

            df_kc["timestep"] = 1
            df_kc["timestep"] = df_kc.groupby("student")["timestep"].cumsum()


            # Get boundary:
            decisions =  self.get_boundaries(df_kc, threshold)
            decisions = df_kc.merge(decisions, on=["student"], how="left")
            print decisions

            # split
            mastered_rows = (decisions["timestep"]  >=  decisions["boundary"])
            mastered   = decisions[  mastered_rows ]
            unmastered = decisions[ ~ mastered_rows ]  # this takes account of NaN

            # calculate:
            pre = self.get_score(unmastered, "pre")
            pos = self.get_score(mastered, "pos")

            #join previously split:
            print "!!!!!"
            print pre.join(pos, how="outer", rsuffix="1")

            #join again
            #assert mas.n_students == unm.n_students
            #assert mas.n_students == unm.n_students





    def get_boundaries(self, df_kc, threshold):
        df_filtered = df_kc[ df_kc["predicted_outcome"]  >= threshold  ]
        df_filtered["boundary"] = df_filtered["timestep"]
        df_students = df_filtered.groupby("student")
        return  df_students.first().reset_index()[ ["student", "boundary"] ]


    def get_score(self, df, prefix):
        df = df.copy()
        # Unfortunately, pandas' groupby doesn't work on NaN values.
        # Remove NaNs:
        df["boundary"] = df["boundary"].fillna(-1)

        students = df.groupby("student")

        ans = students.agg({ "boundary" : ['count', 'max'], "outcome": lambda(l): np.sum([e for e in l if e == 1]) })
        ans = ans.rename(columns={"count"   : prefix+"_n",
                                  "max"     : prefix+"_effort",
                                  "<lambda>": prefix+"_correct"})


        ans.columns = ans.columns.get_level_values(1)
        # Add NaNs back:
        for c in ans.columns:
            ans.loc[ ans[c] == -1 , c ] = float("nan")

        return ans



    # @staticmethod
    # def score_per_kc(df_kc, threshold):
    #     score = 0.0
    #     scores = []
    #     student = 0
    #     #if self.agg_a_kc_type == "per_student":
    #     for student in df_kc.student.unique():
    #         df_a_stu = df_kc[df_kc["student"] == student]
    #         # !!!TODO(hy): May need to ensure non-decreasing on student level (now only considers non-decreasing on kc level or on entire dataset level)
    #         if len(df_a_stu[df_a_stu["pcorrect"] >= threshold]) > 0:
    #             threshold_pos = next(i for i, v in enumerate(df_a_stu["pcorrect"]) if v >= threshold)
    #             df = df_a_stu.iloc[threshold_pos:]
    #             scores.append(np.sum(df["outcome"]) / (1.0 * len(df["outcome"])))
    #             student += 1
    #     score = np.mean(scores)
    #     # else:
    #     #     df_after_threshold = df_kc[df_kc["pcorrect"] >= threshold]
    #     #     if len(df_after_threshold) > 0:
    #     #         score = np.sum(df_after_threshold["outcome"]) / (1.0 * len(df_after_threshold["outcome"]))
    #     #         student = df_after_threshold.student.nunique()
    #     return score, student
    #
    #
    # @staticmethod
    # def practice_per_kc(df_kc, threshold):
    #     practice = 0
    #     practices = []
    #     for student in df_kc.student.unique():
    #         df_a_stu = df_kc[df_kc["student"] == student]
    #         # !!!TODO(hy): May need to ensure non-decreasing on student level (now only considers non-decreasing on kc level or on entire dataset level)
    #         if len(df_a_stu[df_a_stu["pcorrect"] >= threshold]) > 0:
    #             threshold_pos = next(i for i, v in enumerate(df_a_stu["pcorrect"]) if v >= threshold)
    #             if threshold_pos >= 1:
    #                 df = df_a_stu.iloc[threshold_pos - 1:]
    #                 practices.append(len(df))
    #             else:
    #                 practices.append(0)
    #     practice = np.mean(practices)
    #     # df_before_threshold = df_kc[df_kc["pcorrect"] < threshold]
    #     # if len(df_before_threshold) > 0:
    #     #     seq_npractice = df_before_threshold.groupby(by=["student"], sort=False).size()  # return Series
    #     #     stats = seq_npractice.describe(percentiles=[.25, .50, .75, .90])  # its also a series
    #     #     #TODO: Consider int or float?
    #     #     practice = seq_npractice.mean()
    #     return practice
    #
    #

    @staticmethod
    def get_thresholds(df_kc):
        thresholds = df_kc.pcorrect.unique().tolist()
        thresholds.sort()
        if 0 not in thresholds:
            thresholds.insert(0, 0.0)
        if 1 not in thresholds:
            thresholds.append(1.0)
        return thresholds

    def calculate(self, df):
        kcs = df["kc"].unique()
        for kc in kcs:
            df_kc = df[df["kc"] == kc]
            kc_thresholds = SingleKCPolicy.get_thresholds(df_kc)  # [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]#
            self.thresholds[kc] = kc_thresholds
            previous_score = 0
            previous_practice = 0
            kc_scores = []
            kc_practices = []
            kc_students = []
            for threshold in kc_thresholds:
                # if self.agg_a_kc_type == "per_student":
                #     # !!!TODO(hy): May need to ensure non-decreasing per student (now only considers non-decreasing on kc level or on entire dataset level)
                #     # scores is a list across students
                #     scores, student = SingleKCPolicy.score_practice_per_student(df_kc, threshold)
                #     kc_scores.append(scores)
                #     kc_students.append(student)
                # else:
                #score, student = SingleKCPolicy.score_per_kc(df_kc, threshold)
                score, practice, student = self.score_practice_per_kc(df_kc, threshold)
                if self.component_non_decreasing:
                    kc_scores.append(max(score, previous_score))
                    kc_practices.append(max(practice, previous_practice))
                    previous_score = max(score, previous_score)
                    previous_practice = max(practice, previous_practice)
                else:
                    kc_scores.append(score)
                    kc_practices.append(practice)
                kc_students.append(student)  # of students that reach this threshold
            self.scores[kc] = kc_scores
            self.practices[kc] = kc_practices
            self.students[kc] = kc_students

    def __str__(self):
        #'SingleKCPolicy:\n#kcs=\t' + pretty(len(self.kcs)) + \
        return  'thresholds=\t' + pretty(self.thresholds) + \
                '\nscores=\t' + pretty(self.scores) + \
                '\npractices=\t' + pretty(self.practices) + \
                '\nstudents=\t' + pretty(self.students) + "\n"