import numpy as np
import sklearn.metrics as metrics
from common import *
import sys

verbose = True


class Evaluation:
    aggregation_types = ["weighted", "uniform"]

    def __init__(self, df, policy):
        self.policy = policy
        #TODO: I don' think white should receive the dataframe.. it should operate on the policy only!
        self.df = df

        # TODO: what' the difference between self.grades, self.policy.grades and self.agg_grades? ... This is getting messy...
        self.agg_grade = {}  # scalar
        self.agg_practice = {}  # scalar
        self.agg_student = {}  # scalar
        self.grades = None
        self.practices = None
        self.students = None
        self.thresholds = None
        self.kcs = None

        #KC specific?:
        self.grade_all = 0.0
        self.practice_all = 0.0
        self.ratio_all = 0.0


    #TODO: I don' think evaluation.py should know about "KCs"... This is policy specific, and not all policies have KCs
    def aggregate_all_kcs(self, thresholds=None, type="uniform", overall_type="by_kc"):
        print "Aggregating all ", overall_type, " using ", type, " ..."

        self.kcs = self.df["kc"].unique()
        if verbose:
            print self.policy
        if overall_type == "by_kc":
            self.aggregate_each_kc(type)
            self.grade_all = np.mean(self.agg_grade.values())
            self.practice_all = np.sum(self.agg_practice.values()) #/ (1.0 * sum(self.agg_student.values()))
            self.ratio_all = (1.0 * self.practice_all) / self.grade_all
        else:
            ''' Allows to get for just one threshold, or a specified set of thresholds'''
            if thresholds is None:
                thresholds = self.policy.get_thresholds(self.df)
            self.thresholds = thresholds
            self.grades = []
            self.practices = []
            self.students = []
            if verbose:
                print pretty(thresholds)
            for threshold in thresholds:
                if verbose:
                    print "threhsold=", threshold
                grade = 0.0
                practice = 0.0
                student = 0
                for kc in self.kcs:
                    threshold_pos = next(i for i, v in enumerate(self.policy.thresholds[kc]) if v >= threshold)
                    grade_a_kc = self.policy.grades[kc][threshold_pos]
                    practice_a_kc = self.policy.practices[kc][threshold_pos]
                    student_a_kc = self.policy.students[kc][threshold_pos]
                    if verbose:
                        print threshold_pos, kc, grade_a_kc, practice_a_kc, student_a_kc
                    grade += grade_a_kc
                    practice += practice_a_kc
                    student += student_a_kc
                grade = grade / (1.0 * len(self.kcs))
                if len(self.grades) > 0:
                    self.grades.append(max(self.grades[-1], grade))
                    self.practices.append(max(self.practices[-1], practice))
                else:
                    self.grades.append(grade)
                    self.practices.append(practice)
                self.students.append(student)
            if type == "weighted":
                # TODO: change to count #students
                self.grades = (np.array(self.grades) * np.array(self.students) / self.students[0]).tolist()
                self.practices = (np.array(self.practices) * np.array(self.students) / self.students[0]).tolist()
            self.grade_all = self.integration(thresholds, self.grades)  #self.grade_all = np.mean(self.grades)
            self.practice_all = self.integration(thresholds, self.practices) #self.practice_all = np.mean(self.practices)
            self.ratio_all =  (1.0 * self.practice_all) / self.grade_all


    def aggregate_each_kc(self, type="uniform"):
        assert type in Evaluation.aggregation_types, "Unknown parameter"
        for kc in self.policy.grades.keys():
            kc_grades = self.policy.grades[kc]
            kc_practices = self.policy.practices[kc]
            kc_students = self.policy.students[kc]
            kc_thresholds = self.policy.thresholds[kc]
            print "thresholds:\t", pretty(kc_thresholds)
            if type == "weighted":
                print "grades:\t", pretty(kc_grades), "sum:", pretty(sum(kc_grades)), "average:", pretty(np.mean(kc_grades))
                print "practices:\t", pretty(kc_practices), "sum:", pretty(sum(kc_practices)), "average:", pretty(np.mean(kc_practices))
                print "students:\t", kc_students
                kc_grades = (np.array(kc_grades) * np.array(kc_students) / kc_students[0]).tolist()
                kc_practices = (np.array(kc_practices) * np.array(kc_students) / kc_students[0]).tolist()
                print "weighted grades:\t", pretty(kc_grades), "sum:", pretty(sum(kc_grades)), "average:", pretty(np.mean(kc_grades))
                print "weighted practices:\t", pretty(kc_practices), "sum:", pretty(sum(kc_practices)), "average:", pretty(np.mean(kc_practices))
            self.agg_grade[kc] = self.integration(kc_thresholds, kc_grades)
            print "integrated grades: ",pretty(self.agg_grade[kc])
            self.agg_practice[kc] = self.integration(kc_thresholds, kc_practices)
            print "integrated practices: ",pretty(self.agg_practice[kc])
            self.agg_student[kc] = kc_students[0]


    def integration(self, thresholds, values):
        thresholds_ = thresholds[:-1]
        thresholds_.insert(0, 0.0)
        thresholds_diff = np.subtract(thresholds, thresholds_).tolist()
        width = thresholds_diff[1:]
        if verbose:
            print "integral values:", pretty(values[1:]), "\nintegral width:", pretty(width)
        integrated_value = np.dot(values[1:], width)
        return integrated_value


    #TODO: We don' need to have an instance variable for every method.  That' very bad style. JPG removed self.auc.
    def auc(self):
        auc = float('nan')
        if self.df['outcome'].nunique() > 1:
            fprs, tprs, thresholds = metrics.roc_curve(self.df['outcome'], self.df['pcorrect'])
            auc = metrics.auc(fprs, tprs)
        return auc


    #def __repr__(self):
    #TODO: I removed the filename that was hardwired. This class should not have any filenames wired.
    #TODO: this is messy, I would imagine this is should be in test-white :(
    def log(self, input_name, type, overall_type, file=sys.stdout):
        message = "\n" + ",".join([input_name, type, overall_type]) + "\n"
        message += ('#kcs=\t' + pretty(len(self.kcs)) + "\n")
        if overall_type == "by_threshold":
            message += '#thresholds=\t' + pretty(len(self.thresholds)) + "\n" + \
                    'thresholds=\t' + pretty(self.thresholds) +  "\n" + \
                    'grades=\t' + pretty(self.grades) +  "\n" + \
                    'practices=\t' + pretty(self.practices) +  "\n" + \
                    'students=\t' + pretty(self.students) + "\n"
        else:
            message += str(self.policy)
            message += 'agg_grade=\t' + pretty(self.agg_grade) + "\n" + \
                   'agg_practice=\t' + pretty(self.agg_practice) + "\n" + \
                   'agg_student=\t' + pretty(self.agg_student) + "\n"
            #str += 'thresholds=\t' + pretty(self.policy.thresholds) + 'grades=\t' + pretty(self.policy.grades) + 'practices=\t' + pretty(self.policy.practices) + 'students=\t' + pretty(self.policy.students)
        message += 'grade_all=\t' + pretty(self.grade_all) + "\n" + \
               'practice_all=\t' + pretty(self.practice_all) + "\n" + \
               'ratio_all=\t' + pretty(self.ratio_all) + "\n" + \
               'overall_auc=\t' + pretty(self.auc()) + "\n"
        print message







