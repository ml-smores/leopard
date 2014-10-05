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
        kcs = self.df["kc"].unique()
        print "#kcs=", len(kcs)
        for kc in kcs:
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


class White:
    aggregation_types = ["weighted", "uniform"]
    aggregation_types_for_all = ["by_kc", "by_threshold"]

    def __init__(self, df):
        self.policy = None
        self.df = df
        #self.agg_grades = {}
        #self.agg_practices = {}
        #self.agg_students = {}
        self.agg_grade = {}  # scalar
        self.agg_practice = {}  # scalar
        self.agg_student = {}  # scalar
        # self.agg_grade_practice_ratio = {}
        self.grades = None
        self.practices = None
        self.students = None
        self.thresholds = None
        self.grade_all = 0.0
        self.practice_all = 0.0
        self.ratio_all = 0.0
        self.auc_all = 0.0

    def aggregate_all_by_threshold(self, thresholds=None, type="uniform"):
        print "Aggregating all KCs by threshold using ", type, " ..."
        ''' Allows to get for just one threshold, or a specified set of thresholds'''
        if thresholds is None:
            thresholds = SingleKCPolicy.get_thresholds(self.df)
        print "#threshold=", len(thresholds)
        if verbose:
            print thresholds
        self.thresholds = thresholds
        self.grades = []
        self.practices = []
        self.students = []
        for threshold in thresholds:
            if verbose:
                print "threhsold=", threshold
            grade = 0.0
            practice = 0.0
            student = 0
            kcs = self.df["kc"].unique()
            for kc in kcs:
                df_kc = self.df[self.df["kc"] == kc]
                grade_a_kc, student_a_kc = SingleKCPolicy.grade(df_kc, threshold)
                practice_a_kc = SingleKCPolicy.practice(df_kc, threshold)
                if verbose:
                    print kc, grade_a_kc, practice_a_kc, student_a_kc
                grade += grade_a_kc
                practice += practice_a_kc
                student += student_a_kc
            grade = grade / (1.0 * len(kcs))
            if len(self.grades) > 0:
                self.grades.append(max(self.grades[-1], grade))
                self.practices.append(max(self.practices[-1], practice))
            else:
                self.grades.append(grade)
                self.practices.append(practice)
            self.students.append(student)
        if type == "uniform":
            self.grade_all = np.mean(self.grades)
            self.practice_all = np.mean(self.practices)
            self.ratio_all = self.grade_all / (1.0 * self.practice_all)
        else:
            print "To implement..."
            exit(-1)

    def aggregate_all_by_kc(self, type="uniform"):
        print "Aggregating all KCs by KC using ", type, " ..."
        self.policy = SingleKCPolicy(self.df)
        self.policy.calculate()
        self.aggregate_each_kc(type)
        self.grade_all = np.mean(self.agg_grade.values())
        self.practice_all = np.sum(self.agg_practice.values()) #/ (1.0 * sum(self.agg_student.values()))
        self.ratio_all = self.grade_all / (1.0 * self.practice_all)


    def aggregate_each_kc(self, type="uniform"):
        assert type in White.aggregation_types, "Unknown parameter"

        for kc in self.policy.grades.keys():
            kc_grades = self.policy.grades[kc]
            kc_practices = self.policy.practices[kc]
            kc_students = self.policy.students[kc]

            self.agg_student[kc] = sum(kc_students)
            if type == "weighted":
                #self.agg_grades[kc] = (np.array(kc_grades) * np.array(kc_students) / sum(kc_students)).tolist()  #
                #self.agg_practices[kc] = (np.array(kc_practices) * np.array(kc_students) / sum(kc_students)).tolist()  #
                self.agg_grade[kc] = np.dot(kc_grades, kc_students) / sum(kc_students)
                self.agg_practice[kc] = np.dot(kc_practices, kc_students) / sum(kc_students)
            elif type == "uniform":
                #self.agg_grades[kc] = kc_grades
                #self.agg_practices[kc] = kc_practices
                self.agg_grade[kc] = np.mean(kc_grades)
                self.agg_practice[kc] = np.mean(kc_practices)

    def auc(self):
        auc = float('nan')
        if self.df['outcome'].nunique() > 1:
            fprs, tprs, thresholds = metrics.roc_curve(self.df['outcome'], self.df['pcorrect'])
            auc = metrics.auc(fprs, tprs)
        self.auc_all = auc

    def __repr__(self):
        #'\nagg_grade_practice_ratio=\t' + pretty(self.agg_grade_practice_ratio) + \
        #('\nagg_grades=\t' + pretty(self.agg_grades) if self.policy is not None else "") + \
        #('\nagg_practices=\t' + pretty(self.agg_practices) if self.policy is not None else "") + \
        return ('thresholds=\t' + pretty(self.policy.thresholds) if self.policy is not None else "") + \
               ('\ngrades=\t' + pretty(self.policy.grades) if self.policy is not None else "")+ \
               ('\npractices=\t' + pretty(self.policy.practices) if self.policy is not None else "") + \
               ('\nstudents=\t' + pretty(self.policy.students) if self.policy is not None else "")+ \
               ('\nagg_grade=\t' + pretty(self.agg_grade) if self.policy is not None else "") + \
               ('\nagg_practice=\t' + pretty(self.agg_practice) if self.policy is not None else "") + \
               ('\nagg_student=\t' + pretty(self.agg_student) if self.policy is not None else "") + \
               ('\nthresholds=\t' + pretty(self.thresholds) if self.thresholds is not None else "") + \
               ('\ngrades=\t' + pretty(self.grades) if self.grades is not None else "") + \
               ('\npractices=\t' + pretty(self.practices) if self.practices is not None else "") + \
               ('\nstudents=\t' + pretty(self.students) if self.students is not None else "") + \
               '\ngrade_all=\t' + pretty(self.grade_all) + \
               '\npractice_all=\t' + pretty(self.practice_all) + \
               '\nratio_all=\t' + pretty(self.ratio_all) + \
               '\noverall_auc=\t' + pretty(self.auc_all)


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
def main(filenames="example_data/tom_predictions_chapter1.tsv", sep="\t"):
    whites = []
    for input in filenames.split(","):
        print input
        df = pd.read_csv(input, sep=sep)
        w = White(df)
        #w.aggregate_all_by_kc(type="uniform")
        w.aggregate_all_by_threshold(type="uniform")
        w.auc()
        print w
        whites.append(w)

        v = WhiteVisualization(w)
        v.plot_by_threshold("all", "images/tom_")
        # output = os.path.splitext(input)[0] + "_{}.png"
        # v.graph_wuc(output)

    print "done"

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

