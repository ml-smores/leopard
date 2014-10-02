import pandas as pd
import numpy as np
from matplotlib import pyplot as pl, pyplot, cm, colors


class White:
    aggregation_types = ["weighted"]
    policies = ["single_kc"]

    def __init__(self, df):
        """ df has a column for student, kc, timestep, pcorrect, outcome """
        self.thresholds = {}
        self.grades = {}
        self.practices = {}
        self.students = {}
        self.agg_grades = {}
        self.agg_practices = {}
        self.agg_grade_practice = {}
        self.df = df


    def __repr__(self):
        return 'thresholds=\t' + pretty(self.thresholds) + \
               '\ngrades=\t' + pretty(self.grades) + \
               '\npractices=\t' + pretty(self.practices) + \
               "\nstudents=\t" + pretty(self.students) + \
               "\nagg_grades=\t" + pretty(self.agg_grades) + \
               "\nagg_practices=\t" + pretty(self.agg_practices) + \
               "\nagg_grade_practice=\t" + pretty(self.agg_grade_practice)



    @staticmethod
    def expected_grade(df_kc, threshold):
        grade = 0.0
        nstu = 0
        df_after_threshold = df_kc[df_kc["pcorrect"] >= threshold]
        if len(df_after_threshold) > 0:
            grade = np.sum(df_after_threshold["outcome"]) / (1.0 * len(df_after_threshold["outcome"]))
            nstu = df_after_threshold.student.nunique()
        return grade, nstu


    @staticmethod
    def expected_practice(df_kc, threshold):
        practice = 0
        df_before_threshold = df_kc[df_kc["pcorrect"] <= threshold]
        if len(df_before_threshold) > 0:
            seq_npractice = df_before_threshold.groupby(by=["student"], sort=False).size()  # return Series
            stats = seq_npractice.describe(percentiles=[.25, .50, .75, .90])  # its also a series
            practice = stats["50%"]
            # mean = stats["mean"]
        return practice


    @staticmethod
    def get_thresholds(df_kc):
        thresholds = df_kc.pcorrect.unique().tolist()
        thresholds.sort()
        # do_something_with(df)
        if 0 not in thresholds:
            thresholds.insert(0, 0.0)
        if 1 not in thresholds:
            thresholds.append(1.0)
        return thresholds


    def calculate(self, policy="single_kc"):
        assert policy in self.policies, " We only support " + list(self.policies)
        self.grades = {}
        self.practices = {}
        self.students = {}

        kcs = self.df["kc"].unique()
        for kc in kcs:
            df_kc = self.df[self.df["kc"] == kc]
            kc_thresholds = White.get_thresholds(df_kc)
            self.thresholds[kc] = kc_thresholds
            previous_grade = 0
            previous_practice = 0
            kc_grades = []
            kc_practices = []
            kc_students = []
            for threshold in kc_thresholds:
                grade, nstu = White.expected_grade(df_kc, threshold)
                kc_grades.append(max(grade, previous_grade))
                kc_students.append(nstu)  # of students that reach this threshold
                previous_grade = grade
                practice = White.expected_practice(df_kc, threshold)
                kc_practices.append(max(practice, previous_practice))
                previous_practice = practice
            self.grades[kc] = kc_grades
            self.practices[kc] = kc_practices
            self.students[kc] = kc_students


    def aggregate(self, type="weighted"):
        assert type in self.aggregation_types, "Unknown parameter"
        for kc in self.grades.keys():
            kc_grades = self.grades[kc]
            kc_practices = self.practices[kc]
            kc_students = self.students[kc]
            kc_grade_practice = np.divide(np.array(kc_grades, dtype=float), np.array(kc_practices + np.finfo(np.float32).eps, dtype=float))
            self.agg_grades[kc] = np.dot(kc_grades, kc_students) / sum(kc_students)
            self.agg_practices[kc] = np.dot(kc_practices, kc_students) / sum(kc_students)
            #self.agg_grade_practice[kc] = np.dot(kc_grade_practice[1:], kc_students[1:]) / sum(kc_students[1:])
            self.agg_grade_practice[kc] = np.dot(kc_grade_practice, kc_students) / sum(kc_students)


class WhiteVisualization():

    def __init__(self, white_obj):
        self.white_obj = white_obj


    def graph_wuc(self, figure_name="wuc{}.png"):
        for kc in self.white_obj.grades.keys():
            fig, ax = pl.subplots()
            fig.subplots_adjust(bottom=0.12)

            x = self.white_obj.thresholds[kc]
            y = self.white_obj.grades[kc]
            pl.scatter(x, y, color='green')
            pl.plot(x, y,color='green')
            #pl.xticks(x, x, fontsize=5, rotation=45)  # 5
            pl.yticks(color='green')  # 5
            pl.ylim([0, 1])
            pl.xlabel("threshold", fontsize=12)
            pl.ylabel("expected grade", color='green', fontsize=12)

            ax2 = ax.twinx()
            ax2.yaxis.tick_right()
            y = self.white_obj.practices[kc]
            pl.scatter(x, y, color='red')
            pl.plot(x, y, color='red')
            pl.yticks(color='red')  # 5
            pl.ylim([0, max(y)])
            ax2.set_ylabel("expected practice", color="red", fontsize=12)

            pl.xlim([0, 1])
            pl.savefig(figure_name.format(kc))
            pl.close(fig)


    def graph_path(self, filename, threshold=None):
        ''' this should save the image to file '''
        if threshold == None:
            # draw path for aggregated
            pass
        else:
            # draw a single path
            pass


def pretty(x):

    if isinstance(x, dict):
        ans = []
        for (k, v) in x.items():
            ans.append("{}:{}".format(k, pretty(v)))
        return "{" + ",".join(ans) + "}"
    elif isinstance(x,list):
        return "[" + ", ".join([pretty(e) for e in x] ) + "]"
    elif isinstance(x, float):
        return "%4.2f" % x
    else:
        return str(x)
def main(filename="input/df_2.1.119.tsv", sep="\t"):#df_2.4.278.tsv"):#
#def main(filename="example_data/example1.csv", sep=",")
    df = pd.read_csv(filename, sep=sep)
    print df.columns
    # should sort the df ?
    w = White(df)
    w.calculate()
    w.aggregate()
    print w
    v = WhiteVisualization(w)
    v.graph_wuc()


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

