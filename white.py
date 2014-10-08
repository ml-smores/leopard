import pandas as pd
import numpy as np
from matplotlib import pyplot as pl, pyplot, cm, colors
import sklearn.metrics as metrics
import os

verbose = False

class SingleKCPolicy:
    def __init__(self, df):
        """ df has a column for student, kc, timestep, pcorrect, outcome """
        self.thresholds = {}
        self.grades = {}
        self.practices = {}
        self.students = {}
        self.kcs = None
        # JPG: Do we need to sort??
        self.df = df #self.df = df.sort(columns=["kc", "student", "timestep"])


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

    def calculate(self):
        self.kcs = self.df["kc"].unique()
        for kc in self.kcs:
            df_kc = self.df[self.df["kc"] == kc]
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

class White:
    aggregation_types = ["weighted", "uniform"]

    def __init__(self, df):
        self.policy = None
        self.df = df
        self.agg_grade = {}  # scalar
        self.agg_practice = {}  # scalar
        self.agg_student = {}  # scalar
        self.grades = None
        self.practices = None
        self.students = None
        self.thresholds = None
        self.kcs = None
        self.grade_all = 0.0
        self.practice_all = 0.0
        self.ratio_all = 0.0
        self.auc_all = 0.0


    def aggregate_all_kcs(self, thresholds=None, type="uniform", overall_type="by_kc"):
        print "Aggregating all ", overall_type, " using ", type, " ..."
        self.policy = SingleKCPolicy(self.df)
        self.policy.calculate()
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
                thresholds = SingleKCPolicy.get_thresholds(self.df)
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
        assert type in White.aggregation_types, "Unknown parameter"
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


    def auc(self):
        auc = float('nan')
        if self.df['outcome'].nunique() > 1:
            fprs, tprs, thresholds = metrics.roc_curve(self.df['outcome'], self.df['pcorrect'])
            auc = metrics.auc(fprs, tprs)
        self.auc_all = auc


    #def __repr__(self):
    def log(self, file_name, type, overall_type):
        message = "\n" + ",".join([file_name, type, overall_type]) + "\n"
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
               'overall_auc=\t' + pretty(self.auc_all) + "\n"
        print message
        file = open("log/white.log", "a")
        file.write(message)


class WhiteVisualization():

    def __init__(self, white_obj):
        self.white_obj = white_obj

    def plot_by_threshold(self, type, figure_path="images/"):
        if type == "single" and self.white_obj.policy is not None: #plot each KC
            for kc in self.white_obj.policy.grades.keys():
                thresholds = self.white_obj.policy.thresholds[kc]
                grades = self.white_obj.policy.grades[kc]
                practices = self.white_obj.policy.practices[kc]
                self.plot_component_relation(kc, thresholds, grades, figure_path, "threshold", "grade", [0, 1], [0, 1])
                self.plot_component_relation(kc, thresholds, practices, figure_path, "threshold", "practice", [0, 1], [0, max(practices)])
                self.plot_component_relation(kc, practices, grades, figure_path, "practice", "grade", [0, max(practices)], [0,1])
        elif type == "multiple" and self.white_obj.policy is not None: #plot multiple kcs in one figure
            fig1 = pl.figure(1)
            fig2 = pl.figure(2)
            fig3 = pl.figure(3)
            labels = []
            for kc in self.white_obj.policy.grades.keys():
                thresholds = self.white_obj.policy.thresholds[kc]
                grades = self.white_obj.policy.grades[kc]
                practices = self.white_obj.policy.practices[kc]
                color = "green" if "easy" in kc else ("yellow" if "medium" in kc else "red")
                legend = ""
                label = "easy" if "easy" in kc else ("medium" if "medium" in kc else "hard")
                if label not in labels:
                    legend = label
                    labels.append(legend)
                pl.figure(1)
                fig1 = self.plot_component_relation(kc, thresholds, grades, figure_path, "threshold", "grade", [0, 1], [0, 1], linewidth=1, ycolor=color, label=legend, dotsize=10, figure=fig1)
                pl.figure(2)
                fig2 = self.plot_component_relation(kc, thresholds, practices, figure_path, "threshold", "practices", [0, 1], [0, max(practices)], linewidth=1, ycolor=color, label=legend, dotsize=10, figure=fig2)
                pl.figure(3)
                fig3 = self.plot_component_relation(kc, practices, grades, figure_path, "practice", "grade", [0, max(practices)], [0,1], linewidth=1, ycolor=color, label=legend, dotsize=10, figure=fig3)
            pl.figure(1)
            pl.savefig(figure_path + "grade_threshold_multiple.png")
            pl.figure(2)
            pl.savefig(figure_path + "practice_threshold_multiple.png")
            pl.figure(3)
            pl.savefig(figure_path + "grade_practice_multiple.png")
        elif type == "all" and self.white_obj.thresholds is not None: #plot for all KCs
            thresholds = self.white_obj.thresholds
            grades = self.white_obj.grades
            practices = self.white_obj.practices
            self.plot_component_relation("all", thresholds, grades, figure_path, "threshold", "grade", [0,1], [0, 1])
            self.plot_component_relation("all", thresholds, practices, figure_path, "threshold", "practice", [0, 1], [0, max(practices)])
            self.plot_component_relation("all", practices, grades, figure_path, "practice", "grade", [0, max(practices)], [0,1])
        else:
            print "ERROR: Please reconfigure!"
            exit(-1)

    # def graph_path(self, white_objs, threshold=None):
    def plot_by_practice(self, white_objs, threshold=None):
        ''' white_objs is a list of white objects... it may only have a single object
           x=kc, y=practice, dot size=students, dot color=grade
           this should save the image to file
        '''
        if threshold == None:
            # draw path for aggregated
            for white in white_objs:
                pass
        else:
            # draw a single path
            pass


    def plot_component_relation(self, kc, x, y, figure_path, xlabel, ylabel,
                                xlim=None, ylim=None, linewidth=3, ycolor="black", label=None, dotsize=20,
                                figure=None, axis=None):
        if figure is None:
            fig, ax = pl.subplots()
        else:
            fig = figure

        pl.scatter(x, y, color=ycolor, s=dotsize)
        if label is None:
            pl.step(x, y, color=ycolor, linewidth=linewidth)
        else:
            pl.step(x, y, color=ycolor, linewidth=linewidth, label=label)
            pl.legend(loc="lower right", prop={'size':9}) #ncol=4,

        pl.ylabel(ylabel, fontsize=12)#ycolor
        pl.xlabel(xlabel, fontsize=12)
        if ylim is not None:
            pl.ylim(ylim)
        if xlim is not None:
            pl.xlim(xlim)
        if figure is None:
            pl.savefig(figure_path + (ylabel + "_" + xlabel + "_{}.png").format(kc))
            pl.close(fig)
        return fig


def pretty(x):
    if isinstance(x, dict):
        ans = []
        for (k, v) in x.items():
            ans.append("{}:{}".format(k, pretty(v)))
        return "{" + ",".join(ans) + "}"
    elif isinstance(x, list):
        return "[" + ", ".join([pretty(e) for e in x]) + "]"
    elif isinstance(x, float):
        return "%4.3f" % x
    else:
        return str(x)


# def main(filenames="input/df_2.1.119.tsv", sep="\t"):#df_2.4.278.tsv"):#tom_predictions_chapter1.tsv #tdx_1.3.2.61_16.csv
def main(filenames="example_data/tom_predictions_chapter1.tsv", type="uniform", overall_type="by_threshold", plot=False):
    whites = []
    for input in filenames.split(","):
        print input
        df = pd.read_csv(input, sep=("\t" if "tsv" in input else ","))
        w = White(df)
        w.aggregate_all_kcs(type=type, overall_type=overall_type)
        w.auc()
        w.log(input, type, overall_type)
        whites.append(w)

        if plot:
            v = WhiteVisualization(w)
            if overall_type == "bykc":
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

