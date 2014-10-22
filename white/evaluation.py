import numpy as np
import sklearn.metrics as metrics
from common import *
import sys

verbose = True


class Evaluation:
    #aggregation_types = ["weighted", "uniform"]

    def __init__(self,
                 df,
                 policy,
                 weighted_by_student=False,
                 agg_all_kcs_type="by_threshold",
                 integral_lower_bound=0.0,
                 component_non_decreasing=False):
        # TODO: I don' think white should receive the dataframe.. it should operate on the policy only!
        # hy: But evaluation.py is also responsible for getting auc...
        self.df = df
        self.kcs = None

        self.policy = policy
        self.weighted_by_student  = weighted_by_student
        self.agg_all_kcs_type = agg_all_kcs_type
        self.integral_lower_bound = integral_lower_bound
        self.component_non_decreasing = component_non_decreasing
        self.standard_metrics = {}

        # TODO: what' the difference between self.scores, self.policy.scores and self.agg_grades? ... This is getting messy... you are creating instance variables for each method...
        # this is the same problem we had with recommender.py.... i don' think we need all this instance variables.
        self.agg_grade = {}  # scalar
        self.agg_practice = {}  # scalar
        self.agg_student = {}  # scalar

        self.scores = None
        self.practices = None
        self.students = None
        self.thresholds = None
        self.ratios = None

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
            self.ratio_all = self.get_relation_of_score_practice([self.grade_all], [self.practice_all])
        else:
            ''' Allows to get for just one threshold, or a specified set of thresholds'''
            if thresholds is None:
                thresholds = self.policy.get_thresholds(self.df)  #TODO: this starts from 0; this method is only for a Single KC policy...
            self.thresholds = thresholds
            ''' each element corresponds to a threshold '''
            self.scores = []
            self.practices = []
            self.students = []
            self.ratios = []
            if verbose:
                print "thresholds:", pretty(thresholds)
            pct_correct = np.sum(self.df["outcome"]) / (1.0 * len(self.df))
            for threshold in thresholds:
                if verbose:
                    print "\nthrehsold:", threshold
                score = 0.0
                practice = 0.0
                student = 0
                nb_kcs = 0
                for kc in self.kcs:
                    threshold_pos = next(i for i, v in enumerate(self.policy.thresholds[kc]) if v >= threshold)
                    score_a_kc = self.policy.scores[kc][threshold_pos] #list or scalar
                    practice_a_kc = self.policy.practices[kc][threshold_pos] #list or scalar
                    student_a_kc = self.policy.students[kc][threshold_pos] #scalar
                    if (score_a_kc == -1 or practice_a_kc == -1): #only when self.component_non_decreasing=False, can we have -1 value
                        print "continue"
                        continue
                    if verbose:
                        print "kc:"+str(kc), ", score_a_kc:"+pretty(score_a_kc), ", practice_a_kc:"+pretty(practice_a_kc), ", student_a_kc:"+str(student_a_kc)
                    nb_kcs += 1
                    score += score_a_kc #/ (1.0 * len(self.kcs))
                    practice += practice_a_kc
                    student += student_a_kc # Caution: reading threshold of a kc is different from reaching threshold of another kc, so i didn't collect set
                score = (score / (1.0 * nb_kcs) if nb_kcs != 0 else -1)
                practice = ((practice / (1.0 * nb_kcs)) * len(self.kcs) if nb_kcs != 0 else -1)
                if len(self.scores) > 0 and self.component_non_decreasing:
                        self.scores.append(max(self.scores[-1], score))
                        self.practices.append(max(self.practices[-1], practice))
                else:
                    self.scores.append(score)
                    self.practices.append(practice)
                ratio = self.get_relation_of_score_practice(self.scores, self.practices)
                if verbose:
                    print "all kcs: ratio:"+pretty(ratio), ", score:"+pretty(score), ", practice:"+pretty(practice), ", student:"+str(student)
                # if len(self.ratios) > 0 and self.ratio_non_decreasing:
                #     self.ratios.append(max(self.ratios[-1], ratio))
                # else:
                self.ratios.append(ratio)
                self.students.append(student)
            if self.weighted_by_student:
                self.scores = (np.array(self.scores) * np.array(self.students) / self.students[0]).tolist()
                self.practices = (np.array(self.practices) * np.array(self.students) / self.students[0]).tolist()
            self.ratio_all = self.integration(thresholds, self.ratios, self.integral_lower_bound)


    def aggregate_each_kc(self):
        #assert self.weighted_by_student in Evaluation.aggregation_types, "Unknown parameter"
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
            self.agg_grade[kc] = self.integration(kc_thresholds, kc_grades, self.integral_lower_bound)
            self.agg_practice[kc] = self.integration(kc_thresholds, kc_practices, self.integral_lower_bound)
            self.agg_student[kc] = kc_students[0]
            if verbose:
                print "integrated scores: ",pretty(self.agg_grade[kc])
                print "integrated practices: ",pretty(self.agg_practice[kc])


    #!!!TODO: configure the upper bound
    def integration(self, thresholds, values, integral_lower_bound, integral_upper_bound = 1.0):
        if integral_lower_bound > 0.0:
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
        integrated_value = np.dot(values[1:], width) * (1 / (integral_upper_bound - integral_lower_bound))
        if verbose:
            print "thresholds:", pretty(thresholds), "\nintegral values:", pretty(values[1:]), "\nintegral width:", pretty(width)
        return integrated_value


    def get_relation_of_score_practice(self, scores, practices):
        ratio = 0.0
        # if self.relation_of_component == "regress":
        #     if len(set(scores)) != 1:
        #         slope, intercept, r_value, slope_pval, std_err = stats.linregress(scores, practices)
        #         ratio = intercept + slope
        #     else:
        #         print "ERROR: len(set(scores)) != 1"
        #         exit(-1)
        #if self.relation_of_component == "ratio":
            #TODO: maybe if practice == 0, use score
        ratio = 0 if practices[-1] == 0 else (scores[-1] / (1.0 * practices[-1]))#ratio = practices[0] / (1.0 * scores[0])
        # elif self.relation_of_component == "ratio_log_effort": #vs. nolog: 1_3_easy trend is the same; 1_4_medium trend in the log one can increase
        #     ratio = 0 if (practices[-1] == 0 or practices[-1] == 1.0) else (scores[-1] / (1.0 * np.log2(practices[-1])))#ratio = practices[0] / (1.0 * scores[0])
        # elif self.relation_of_component == "ratio_score_sq_log_effort": #vs. nolog: 1_3_easy trend is the same; 1_4_medium trend in the log one can increase
        #     ratio = 0 if (practices[-1] == 0 or practices[-1] == 1.0) else (scores[-1]**2 / (1.0 * np.log2(practices[-1])))#ratio = practices[0] / (1.0 * scores[0])
        # else:
        #     print "ERROR: please give correct configuration for relation_of_component()!"
        #     exit(-1)
        if practices[-1] == -1 or scores[-1] == -1:
            ratio = 0 #not defined (because there are no students at this point)
        return ratio


    def compute_standard_metrics(self):
        auc = float('nan')
        if self.df['outcome'].nunique() > 1:
            fprs, tprs, thresholds = metrics.roc_curve(self.df['outcome'], self.df['pcorrect'])
            auc = metrics.auc(fprs, tprs)
        accuracy = metrics.accuracy_score(self.df['outcome'], self.df['pcorrect'] >= 0.5)
        self.standard_metrics["auc"] = auc
        self.standard_metrics["accuracy"] = accuracy
        self.standard_metrics["%correct"] = sum(self.df['outcome']) / (1.0 * len(self.df['outcome']))


    #def __repr__(self):
    #TODO: I removed the filename that was hardwired. This class should not have any filenames wired.
    #TODO: this is messy, I would imagine this is should be in test-white :(
    def log(self, input_name, log_file="./white.log"):
        #type, overall_type, file=sys.stdout
        message = "\n" + ",".join([input_name, "agg_all_kcs_type="+self.agg_all_kcs_type, "integral_lower_bound="+ pretty(self.integral_lower_bound), "weighted_by_student=" + str(self.weighted_by_student)]) + "\n"
        message += ('#kcs=\t' + pretty(len(self.kcs)) + ('\n#original_students=\t' + pretty(self.df.student.nunique())) + "\n")
        if self.agg_all_kcs_type == "by_threshold":
            message += '#thresholds=\t' + pretty(len(self.thresholds)) + "\n" + \
                    'thresholds=\t' + pretty(self.thresholds) +  "\n" + \
                    'scores=\t' + pretty(self.scores) +  "\n" + \
                    'practices=\t' + pretty(self.practices) +  "\n" + \
                    'ratios=\t' + pretty(self.ratios) + "\n" + \
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
               'standard_metrics=\t' + pretty(self.standard_metrics) + "\n"
        print message

        if log_file is not None:
            log = open(log_file, "a")
            log.write(message)





