import numpy as np
import sklearn.metrics as metrics
from common import *
import sys

verbose = True


class Evaluation:
    aggregation_types = ["weighted", "uniform"]

    def __init__(self,
                 df,
                 policy,
                 weighted_by_student=False,
                 agg_all_kcs_type="by_threshold",
                 integral_lower_bound=0.0,
                 debug=False):
        # TODO: I don' think white should receive the dataframe.. it should operate on the policy only!
        # hy: But evaluation.py is also responsible for getting auc...
        self.df = df
        self.policy = policy
        self.weighted_by_student  = weighted_by_student
        self.agg_all_kcs_type = agg_all_kcs_type
        self.integral_lower_bound = integral_lower_bound
        self.debug = debug
        # TODO: what' the difference between self.scores, self.policy.scores and self.agg_grades? ... This is getting messy... you are creating instance variables for each method...
        # this is the same problem we had with recommender.py.... i don' think we need all this instance variables.
        self.agg_grade = {}  # scalar
        self.agg_practice = {}  # scalar
        self.agg_student = {}  # scalar
        self.scores = None
        self.practices = None
        self.students = None
        self.thresholds = None
        self.kcs = None

        #KC specific?: correspond to the entire df
        self.grade_all = -1.0
        self.practice_all = -1.0
        self.ratio_all = -1.0


    #TODO: I don' think evaluation.py should know about "KCs"... This is policy specific, and not all policies have KCs
    def aggregate_all_kcs(self, thresholds=None):
        #print "Aggregating all ", self.agg_all_kcs_type, " using ", self.weighted_by_student, " ..."

        self.kcs = self.df["kc"].unique()
        if verbose:
            print self.policy
        if self.agg_all_kcs_type == "by_kc":
            self.aggregate_each_kc()
            self.grade_all = np.mean(self.agg_grade.values())
            self.practice_all = np.sum(self.agg_practice.values()) #/ (1.0 * sum(self.agg_student.values()))
            self.ratio_all = (1.0 * self.practice_all) / self.grade_all
        else:
            ''' Allows to get for just one threshold, or a specified set of thresholds'''
            if thresholds is None:
                thresholds = self.policy.get_thresholds(self.df)  #TODO: this method is only for a Single KC policy...
            self.thresholds = thresholds
            ''' each element corresponds to a threshold '''
            self.scores = []
            self.practices = []
            self.students = []
            if verbose:
                print pretty(thresholds)
            for threshold in thresholds:
                if verbose:
                    print "threhsold=", threshold
                score = 0.0
                practice = 0.0
                student = 0
                scores = []
                practices = []
                for kc in self.kcs:
                    threshold_pos = next(i for i, v in enumerate(self.policy.thresholds[kc]) if v >= threshold)
                    score_a_kc = self.policy.scores[kc][threshold_pos] #list or scalar
                    practice_a_kc = self.policy.practices[kc][threshold_pos] #list or scalar
                    student_a_kc = self.policy.students[kc][threshold_pos] #scalar
                    if verbose:
                        print threshold_pos, kc, score_a_kc, practice_a_kc, student_a_kc
                    score += score_a_kc / (1.0 * len(self.kcs))
                    practice += practice_a_kc
                    student += student_a_kc # Caution: reading threshold of a kc is different from reaching threshold of another kc, so i didn't collect set
                # get score, practice, student at each threshold
                if len(self.scores) > 0:
                    self.scores.append(max(self.scores[-1], score))
                    self.practices.append(max(self.practices[-1], practice))
                else:
                    self.scores.append(score)
                    self.practices.append(practice)
                self.students.append(student)
            if self.weighted_by_student:
                self.scores = (np.array(self.scores) * np.array(self.students) / self.students[0]).tolist()
                self.practices = (np.array(self.practices) * np.array(self.students) / self.students[0]).tolist()

            ratios = np.divide(self.practices, self.scores)
            self.ratio_all = self.integration(thresholds, ratios)
            #self.grade_all = self.integration(thresholds, self.scores, integral_lower_bound)  #self.grade_all = np.mean(self.scores)
            #self.practice_all = self.integration(thresholds, self.practices, integral_lower_bound) #self.practice_all = np.mean(self.practices)
            #self.ratio_all =  (1.0 * self.practice_all) / self.grade_all


    def aggregate_each_kc(self):
        assert self.weighted_by_student in Evaluation.aggregation_types, "Unknown parameter"
        for kc in self.policy.scores.keys():
            kc_grades = self.policy.scores[kc]
            kc_practices = self.policy.practices[kc]
            kc_students = self.policy.students[kc]
            kc_thresholds = self.policy.thresholds[kc]
            print "thresholds:\t", pretty(kc_thresholds)
            if self.weighted_by_student:
                if verbose:
                    print "scores:\t", pretty(kc_grades), "sum:", pretty(sum(kc_grades)), "average:", pretty(np.mean(kc_grades))
                    print "practices:\t", pretty(kc_practices), "sum:", pretty(sum(kc_practices)), "average:", pretty(np.mean(kc_practices))
                    print "students:\t", kc_students
                kc_grades = (np.array(kc_grades) * np.array(kc_students) / kc_students[0]).tolist()
                kc_practices = (np.array(kc_practices) * np.array(kc_students) / kc_students[0]).tolist()
                if verbose:
                    print "weighted scores:\t", pretty(kc_grades), "sum:", pretty(sum(kc_grades)), "average:", pretty(np.mean(kc_grades))
                    print "weighted practices:\t", pretty(kc_practices), "sum:", pretty(sum(kc_practices)), "average:", pretty(np.mean(kc_practices))
            self.agg_grade[kc] = self.integration(kc_thresholds, kc_grades)
            self.agg_practice[kc] = self.integration(kc_thresholds, kc_practices)
            self.agg_student[kc] = kc_students[0]
            if verbose:
                print "integrated scores: ",pretty(self.agg_grade[kc])
                print "integrated practices: ",pretty(self.agg_practice[kc])


    #!!!TODO: configure the lower bound
    def integration(self, thresholds, values):
        if self.integral_lower_bound > 0.0:
            threshold_pos = next(i for i, v in enumerate(thresholds) if v > self.integral_lower_bound)
            if threshold_pos == 0:
                print "ERROR: thresholds should start from 0!"
                exit(-1)
            thresholds = thresholds[threshold_pos:]
            thresholds.insert(0, self.integral_lower_bound)
            values = values[threshold_pos - 1:]
        thresholds_ = thresholds[:-1]
        thresholds_.insert(0, 0.0)
        thresholds_diff = np.subtract(thresholds, thresholds_).tolist()
        width = thresholds_diff[1:]
        integrated_value = np.dot(values[1:], width)
        if verbose:
            print "thresholds:", pretty(thresholds), "\nintegral values:", pretty(values[1:]), "\nintegral width:", pretty(width)
        return integrated_value


    def auc(self):
        auc = float('nan')
        if self.df['outcome'].nunique() > 1:
            fprs, tprs, thresholds = metrics.roc_curve(self.df['outcome'], self.df['pcorrect'])
            auc = metrics.auc(fprs, tprs)
        return auc


    #def __repr__(self):
    #TODO: I removed the filename that was hardwired. This class should not have any filenames wired.
    #TODO: this is messy, I would imagine this is should be in test-white :(
    def log(self, input_name):
        #type, overall_type, file=sys.stdout
        message = "\n" + ",".join([input_name, "agg_all_kcs_type="+self.agg_all_kcs_type, "integral_lower_bound="+ pretty(self.integral_lower_bound), "weighted_by_student=" + str(self.weighted_by_student), "debug="+str(self.debug)]) + "\n"
        message += ('#kcs=\t' + pretty(len(self.kcs)) + "\n")
        if self.agg_all_kcs_type == "by_threshold":
            message += '#thresholds=\t' + pretty(len(self.thresholds)) + "\n" + \
                    'thresholds=\t' + pretty(self.thresholds) +  "\n" + \
                    'scores=\t' + pretty(self.scores) +  "\n" + \
                    'practices=\t' + pretty(self.practices) +  "\n" + \
                    'students=\t' + pretty(self.students) + "\n"
        else:
            message += str(self.policy)
            message += 'agg_grade=\t' + pretty(self.agg_grade) + "\n" + \
                   'agg_practice=\t' + pretty(self.agg_practice) + "\n" + \
                   'agg_student=\t' + pretty(self.agg_student) + "\n"
            #str += 'thresholds=\t' + pretty(self.policy.thresholds) + 'scores=\t' + pretty(self.policy.scores) + 'practices=\t' + pretty(self.policy.practices) + 'students=\t' + pretty(self.policy.students)
        message += ('grade_all=\t' + pretty(self.grade_all) + "\n") if self.grade_all > -1 else ""  + \
               ('practice_all=\t' + pretty(self.practice_all) + "\n") if self.practice_all > -1 else "" + \
               'ratio_all=\t' + pretty(self.ratio_all) + "\n" + \
               'overall_auc=\t' + pretty(self.auc()) + "\n"
        print message







