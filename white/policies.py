__author__ = 'ugonzjo'
import numpy as np
from common import *
import math

class Policy():
    def __init__(self):
        #TODO: do thresholds need to be sorted?
        self.thresholds = {}
        self.grades = {}
        self.practices = {}
        self.students = {}


class SyntheticPolicy(Policy):
    def __init__(self, file):
        #TODO this should fill the self.thresholds, self.grades, self.practices, self.students from a file (the file was possibly generated using synthetic data)
        pass

    @staticmethod
    def grade_generator(omega):
        return omega ^ 2
    @staticmethod
    def practice_generator(omega):
        return omega * 10
    @staticmethod
    def student_generator(omega):
        return math.round(1000 - 1000 * omega)

class SingleKCPolicy (Policy):
    def __init__(self, df):
        """ df has a column for student, kc, timestep, pcorrect, outcome """
        Policy.__init__(self)
        self.calculate(df)


    @staticmethod
    def grade(df_kc, threshold):
        grade = 0.0
        student = 0
        # TODO: There is a bug here, I think.  We need to consider timesteps.
        df_after_threshold = df_kc[df_kc["pcorrect"] >= threshold]
        if len(df_after_threshold) > 0:
            grade = np.sum(df_after_threshold["outcome"]) / (1.0 * len(df_after_threshold["outcome"]))
            student = df_after_threshold.student.nunique()
        return grade, student


    @staticmethod
    def practice(df_kc, threshold):
        practice = 0
        # TODO: There is a bug here, I think.  We need to consider timesteps.
        # Imagine that the threshold changed at timestep = 3, but then pcorrect decreased again at timestep=5
        df_before_threshold = df_kc[df_kc["pcorrect"] < threshold]
        if len(df_before_threshold) > 0:
            seq_npractice = df_before_threshold.groupby(by=["student"], sort=False).size()  # return Series
            stats = seq_npractice.describe(percentiles=[.25, .50, .75, .90])  # its also a series
            #TODO: Consider int or float?
            practice = seq_npractice.mean()
        return practice


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
            previous_grade = 0
            previous_practice = 0
            kc_grades = []
            kc_practices = []
            kc_students = []
            for threshold in kc_thresholds:
                grade, student = SingleKCPolicy.grade(df_kc, threshold)
                kc_grades.append(max(grade, previous_grade))
                kc_students.append(student)  # of students that reach this threshold
                previous_grade = max(grade, previous_grade)
                practice = SingleKCPolicy.practice(df_kc, threshold)
                kc_practices.append(max(practice, previous_practice))
                previous_practice = max(practice, previous_practice)
            self.grades[kc] = kc_grades
            self.practices[kc] = kc_practices
            self.students[kc] = kc_students

    def __str__(self):
        #'SingleKCPolicy:\n#kcs=\t' + pretty(len(self.kcs)) + \
        return  'thresholds=\t' + pretty(self.thresholds) + \
                '\ngrades=\t' + pretty(self.grades) + \
                '\npractices=\t' + pretty(self.practices) + \
                '\nstudents=\t' + pretty(self.students) + "\n"