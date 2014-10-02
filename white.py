import pandas as pd
import numpy as np
from matplotlib import pyplot as pl, pyplot, cm, colors


class SingleKCPolicy:
    def __init__(self, df):
        """ df has a column for student, kc, timestep, pcorrect, outcome """
        self.thresholds = {}
        self.grades = {}
        self.practices = {}
        self.students = {}
        #JPG: Do we need to sort??
        self.df = df
        #self.df = df.sort(columns=["kc", "student", "timestep"])


    @staticmethod
    def expected_grade(df_kc, threshold):
        grade = 0.0
        nstu = 0
        #TODO: There is a bug here, I think.  We need to consider timesteps.
        df_after_threshold = df_kc[df_kc["pcorrect"] >= threshold]
        if len(df_after_threshold) > 0:
            grade = np.sum(df_after_threshold["outcome"]) / (1.0 * len(df_after_threshold["outcome"]))
            nstu = df_after_threshold.student.nunique()
        return grade, nstu


    @staticmethod
    def expected_practice(df_kc, threshold):
        practice = 0
        #TODO: There is a bug here, I think.  We need to consider timesteps.
        # Imagine that the threshold changed at timestep = 3, but then pcorrect decreased again at timestep=5
        df_before_threshold = df_kc[df_kc["pcorrect"] <= threshold]
        if len(df_before_threshold) > 0:
            seq_npractice = df_before_threshold.groupby(by=["student"], sort=False).size()  # return Series
            #JPG: changed to mean instead of median
            #stats = seq_npractice.describe(percentiles=[.25, .50, .75, .90])  # its also a series
            #practice = int(stats["50%"])
            practice = seq_npractice.mean()
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


    def calculate(self):
        kcs = self.df["kc"].unique()
        for kc in kcs:
            df_kc = self.df[self.df["kc"] == kc]
            kc_thresholds = SingleKCPolicy.get_thresholds(df_kc)
            self.thresholds[kc] = kc_thresholds
            previous_grade = 0
            previous_practice = 0
            kc_grades = []
            kc_practices = []
            kc_students = []
            for threshold in kc_thresholds:
                grade, nstu = SingleKCPolicy.expected_grade(df_kc, threshold)
                kc_grades.append(max(grade, previous_grade))
                kc_students.append(nstu)  # of students that reach this threshold
                previous_grade = grade
                practice = SingleKCPolicy.expected_practice(df_kc, threshold)
                kc_practices.append(max(practice, previous_practice))
                previous_practice = practice
            self.grades[kc] = kc_grades
            self.practices[kc] = kc_practices
            self.students[kc] = kc_students


class White:
    aggregation_types = "weighted"
    def __init__(self, df):
        self.policy = SingleKCPolicy(df)
        self.policy.calculate()
        self.agg_grades = {}
        self.agg_practices = {}
        self.agg_grade_practice_ratio = {}

    def aggregate_all(self):
        #TODO: I think we need one more function!
        # The aggregate KCs function collapses within kcs, but do we need something to collapse the whole dataset?
        # We should add the practice, and average the KCS... I think
        return None

    def aggregate_kcs(self, type):
        assert type in White.aggregation_types, "Unknown parameter"

        agg_grade_practice_ratio1 = {}
        agg_grade_practice_ratio2 = {}
        for kc in self.policy.grades.keys():
            kc_grades     = self.policy.grades[kc]
            kc_practices  = self.policy.practices[kc]
            kc_students   = self.policy.students[kc]

            self.agg_grades[kc] = np.dot(kc_grades, kc_students) / sum(kc_students)
            self.agg_practices[kc] = np.dot(kc_practices, kc_students) / sum(kc_students)

            #TODO: Check
            #Not sure how we should calculate this ratio:
            agg_grade_practice_ratio1[kc] = np.sum(self.agg_grades[kc]) / np.sum(self.agg_practices[kc])
            agg_grade_practice_ratio2[kc] = np.sum(np.divide(self.agg_grades[kc], (self.agg_practices[kc])))
            # But I think they are equivalent:
            assert(agg_grade_practice_ratio1[kc] == agg_grade_practice_ratio2[kc]), "Are this the same??"

            # This is how you had it before, which I think it's very very complicated, and it looks like it wasn't working
            #kc_grade_practice = np.divide(np.array(kc_grades, dtype=float), np.array(kc_practices + np.finfo(np.float32).eps, dtype=float))


            self.agg_grade_practice_ratio[kc] = agg_grade_practice_ratio1[kc]


    def __repr__(self):
        return 'thresholds=\t' + pretty(self.policy.thresholds) + \
               '\ngrades=\t' + pretty(self.policy.grades) + \
               '\npractices=\t' + pretty(self.policy.practices) + \
               '\nstudents=\t' + pretty(self.policy.students) + \
               '\nagg_grades=\t' + pretty(self.agg_grades) + \
               '\nagg_practices=\t' + pretty(self.agg_practices) + \
               '\nagg_grade_practice=\t' + pretty(self.agg_grade_practice_ratio)


class WhiteVisualization():

    def __init__(self, white_obj):
        self.white_obj = white_obj


    # TODO: Fix bug that interpolates thresholds
    def graph_wuc(self, figure_name="wuc{}.png"):
        for kc in self.white_obj.policy.grades.keys():
            fig, ax = pl.subplots()
            fig.subplots_adjust(bottom=0.12)

            x = self.white_obj.policy.thresholds[kc]
            y = self.white_obj.policy.grades[kc]
            pl.scatter(x, y, color='green')
            pl.plot(x, y,color='green', linewidth=3)
            #pl.xticks(x, x, fontsize=5, rotation=45)  # 5
            pl.yticks(color='green')  # 5
            pl.ylim([0, 1])
            pl.xlabel("threshold", fontsize=12)
            pl.ylabel("expected grade", color='green', fontsize=12)

            #JPG: shouldn' be a twin graph... they are on different scales
            ax2 = ax.twinx()
            ax2.yaxis.tick_right()
            y = self.white_obj.policy.practices[kc]
            pl.scatter(x, y, color='red')
            pl.plot(x, y, color='red', linewidth=3)
            pl.yticks(color='red')  # 5
            pl.ylim([0, max(y)])
            ax2.set_ylabel("expected practice", color="red", fontsize=12)

            pl.xlim([0, 1])
            pl.savefig(figure_name.format(kc))
            pl.close(fig)


    '''white_objs is a list of white objects... it may only have a single object'''
    def graph_path(self, white_objs, threshold=None):
        ''' this should save the image to file '''
        if threshold == None:
            # draw path for aggregated
            for white in white_objs:
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
#def main(filename="example_data/example1.csv", sep=","):
    df = pd.read_csv(filename, sep=sep)
    w = White(df)
    w.aggregate_kcs("weighted")
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

