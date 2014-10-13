__author__ = 'ugonzjo'
import numpy as np
from common import *
import math
import pandas as pd

class Policy():
    def __init__(self):
        ''' All of them: key=kc, value=score/practice per student '''
        #TODO: do thresholds need to be sorted?
        self.thresholds = {}
        self.scores = {}
        self.practices = {}
        self.students = {}
        # self.students = {} #value is #students reaching threshold for a kc
        # self.nb_obs_reach = {} #value is the #observations corresponding to the part reaching threshold for a kc, in order to recover #correct with self.scores


class SyntheticPolicy(Policy):
    def __init__(self, file):
        #TODO this should fill the self.thresholds, self.scores, self.practices, self.students from a file (the file was possibly generated using synthetic data)
        pass

    @staticmethod
    def score_generator(omega):
        return omega ^ 2
    @staticmethod
    def practice_generator(omega):
        return omega * 10
    @staticmethod
    def student_generator(omega):
        return math.round(1000 - 1000 * omega)


class SingleKCPolicy (Policy):
    def __init__(self, df, debug=False):
        """ df has a column for student, kc, timestep, pcorrect, outcome """
        Policy.__init__(self)
        self.debug = debug
        self.calculate(df)

    def score_practice_per_kc(self, df_kc, threshold):
        score = 0.0
        scores = []
        practice = 0.0
        practices = []
        nb_student = 0
        # grouped = df_kc.groupby(by="student",sort=False)
        # reached_per_stu = pd.DataFrame({"reached_threshold": grouped["pcorrect"].max() >= threshold})
        # for student in reached_per_stu.index.unique():
        if self.debug:
            # TODO (hy): this can be a bug for running models where pcorrect is decreasing; but so far works well for pfa
            df_after_threshold = df_kc[df_kc["pcorrect"] >= threshold]
            if len(df_after_threshold) > 0:
                score = np.sum(df_after_threshold["outcome"]) / (1.0 * len(df_after_threshold["outcome"]))
                nb_student = df_after_threshold.student.nunique()
                # TODO(hy): Different from previous. Previously, even student doesn't reach thresheld, still count the practice
                df_before_threshold = df_kc[df_kc["pcorrect"] < threshold]
                if len(df_before_threshold) > 0:
                    practice = df_before_threshold.groupby(by=["student"], sort=False).size().mean()  # return Series #TODO: Consider int or float?
        else:
            # TODO (hy): Following code is super slow!
            for student in df_kc.student.unique():
                df_a_stu = df_kc[df_kc["student"] == student]
                # !!!TODO(hy): May need to ensure non-decreasing on student level (now only considers non-decreasing on kc level or on entire dataset level)
                if len(df_a_stu[df_a_stu["pcorrect"] >= threshold]) > 0:
                    threshold_pos = next(i for i, v in enumerate(df_a_stu["pcorrect"]) if v >= threshold)
                    df = df_a_stu.iloc[threshold_pos:]
                    scores.append(np.sum(df["outcome"]) / (1.0 * len(df["outcome"])))
                    if threshold_pos > 0:
                        df = df_a_stu.iloc[: threshold_pos]
                        practices.append(len(df))
                    else:
                        practices.append(0)
                    nb_student += 1
            score = np.mean(scores) if len(scores) > 0 else 0.0
            practice = np.mean(practices) if len(practices) > 0 else 0
        return score, practice, nb_student

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
    # # TODO: deprecated
    # @staticmethod
    # def score_practice_per_student(df_kc, threshold):
    #     scores = []
    #     practices = []
    #     students = []
    #     nb_stu = 0
    #     # TODO: There is a bug here, I think.  We need to consider timesteps.
    #     # Imagine that the threshold changed at timestep = 3, but then pcorrect decreased again at timestep=5
    #     for student in df_kc.student.unique():
    #         df_a_stu = df_kc[df_kc["student"] == student]
    #         df_after_threshold = df_a_stu[df_a_stu["pcorrect"] >= threshold]
    #         df_before_threshold = df_a_stu[df_a_stu["pcorrect"] < threshold]
    #         # !!!TODO(hy): May need to ensure non-decreasing per student (now only considers non-decreasing on kc level or on entire dataset level)
    #         if len(df_after_threshold) > 0:
    #             scores.append(np.sum(df_after_threshold["outcome"]) / (1.0 * len(df_after_threshold["outcome"])))
    #             practices.append(len(df_before_threshold))
    #             students.append(student)
    #             nb_stu += 1
    #     return scores, practices, students, nb_stu


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
                kc_scores.append(max(score, previous_score))
                kc_students.append(student)  # of students that reach this threshold
                previous_score = max(score, previous_score)
                #practice = SingleKCPolicy.practice_per_kc(df_kc, threshold)
                kc_practices.append(max(practice, previous_practice))
                previous_practice = max(practice, previous_practice)
            self.scores[kc] = kc_scores
            self.practices[kc] = kc_practices
            self.students[kc] = kc_students

    def __str__(self):
        #'SingleKCPolicy:\n#kcs=\t' + pretty(len(self.kcs)) + \
        return  'thresholds=\t' + pretty(self.thresholds) + \
                '\nscores=\t' + pretty(self.scores) + \
                '\npractices=\t' + pretty(self.practices) + \
                '\nstudents=\t' + pretty(self.students) + "\n"