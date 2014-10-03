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
        #JPG: I think this had a bug with our contract. I think we need to sort (?)
        self.df = df# = df.sort(columns=["kc", "student", "timestep"])


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
            # practice = int(stats["50%"])
            #TODO: Consider int or float?
            practice = stats["mean"]
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
        #kcs = ["1_5_easy"]
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
                previous_grade = max(grade, previous_grade)
                practice = SingleKCPolicy.expected_practice(df_kc, threshold)
                kc_practices.append(max(practice, previous_practice))
                previous_practice = max(practice, previous_practice)
            self.grades[kc] = kc_grades
            self.practices[kc] = kc_practices
            self.students[kc] = kc_students


class White:
    aggregation_types = "weighted"
    def __init__(self, df):
        self.policy = SingleKCPolicy(df)
        self.policy.calculate()
        self.agg_student = {} #scalar
        self.agg_grade = {} #scalar
        self.agg_practice = {} #scalar
        self.agg_grades = {}
        self.agg_practices = {}
        self.agg_grade_practice_ratio = {}
        self.grade_all = 0.0
        self.practice_all = 0.0
        self.ratio_all = 0.0

    def aggregate_all_by_kc(self):
        #TODO: I think we need one more function!
        # The aggregate KCs function collapses within kcs, but do we need something to collapse the whole dataset?
        # We should add the practice, and average the KCS... I think

        agg_grade = np.mean(self.agg_grade.values())
        agg_practice = np.sum(self.agg_practice.values())
        agg_student = np.sum(self.agg_student.values())

        grade_all = np.mean(agg_grade)
        practice_all = np.sum(agg_practice)
        ratio_all =  grade_all / (1.0 * practice_all)
        #ratio_all = np.mean(self.agg_grade_practice_ratio.values())


        # TODO: check wether .values() return things in order
        # weigthed_grade_all = (np.dot(self.agg_grade.values(), self.agg_student.values())) / np.sum(self.agg_student.values())
        # TODO: don't know how to get the sum
        # weighted_practice_all =  ((np.dot(self.agg_practice.values(), self.agg_student.values())) / np.sum(self.agg_student.values()))
        # weighted_ratio_all = (np.dot(self.agg_grade_practice_ratio.values(), self.agg_student.values())) / np.sum(self.agg_student.values())

        self.grade_all = grade_all
        self.practice_all = practice_all
        self.ratio_all = ratio_all

        #print grade_all, practice_all, ratio_all

    def aggregate_all_by_threshold(self):
        pass
#         def calculate(threshold):
#    for kc in kcs:
#         practice += expected_grade(kc, threshold)  -> is it expected_practice(kc, threshold)?
#         grade  += 1/kcs + expected_practice(kc, threshold) -> why there is a 1/kcs? Is it expected_grade?
#         student = ....
#    return practice, grade
#
# def calculate_all():
#       for threshold in thresholds:
#              practice, grade, student  = calculate(threshold)
#              practices.append(practice)
#              grades.append(grade)
#              studens.append(student)
#
#       return wuc(practices) / wuc(students) -

    def aggregate_each_kc(self, type):
        assert type in White.aggregation_types, "Unknown parameter"

        agg_grade_practice_ratio1 = {}
        agg_grade_practice_ratio2 = {}
        for kc in self.policy.grades.keys():
            kc_grades     = self.policy.grades[kc]
            kc_practices  = self.policy.practices[kc]
            kc_students   = self.policy.students[kc]

            self.agg_grades[kc] = (np.array(kc_grades) * np.array(kc_students) / sum(kc_students)).tolist() #
            self.agg_practices[kc] = (np.array(kc_practices) * np.array(kc_students) / sum(kc_students)).tolist() #
            # Following gives scalar
            self.agg_student[kc] = sum(kc_students)
            self.agg_grade[kc] = np.dot(kc_grades, kc_students) / sum(kc_students)
            self.agg_practice[kc] = np.dot(kc_practices, kc_students) / sum(kc_students)

            agg_grade_practice_ratio1[kc] = np.sum(self.agg_grades[kc]) / np.sum(self.agg_practices[kc])
            ind_ratio = np.divide(self.agg_grades[kc], (self.agg_practices[kc]))
            ind_ratio[np.isnan(ind_ratio)] = 0
            ind_ratio[np.isinf(ind_ratio)] = 0
            agg_grade_practice_ratio2[kc] = np.mean(ind_ratio)#np.sum(np.divide(self.agg_grades[kc], (self.agg_practices[kc])))
            #assert(agg_grade_practice_ratio1[kc] == agg_grade_practice_ratio2[kc]), "Are this the same??"

            # This is how you had it before, which I think it's very very complicated, and it looks like it wasn't working
            #kc_grade_practice = np.divide(np.array(kc_grades, dtype=float), np.array(kc_practices + np.finfo(np.float32).eps, dtype=float))
            self.agg_grade_practice_ratio[kc] = agg_grade_practice_ratio1[kc]
        print "agg_grade_practice_ratio2:", pretty(agg_grade_practice_ratio2)


    def __repr__(self):
        return 'thresholds=\t' + pretty(self.policy.thresholds) + \
               '\ngrades=\t' + pretty(self.policy.grades) + \
               '\npractices=\t' + pretty(self.policy.practices) + \
               '\nstudents=\t' + pretty(self.policy.students) + \
               '\nagg_grades=\t' + pretty(self.agg_grades) + \
               '\nagg_practices=\t' + pretty(self.agg_practices) + \
               '\nagg_grade_practice_ratio=\t' + pretty(self.agg_grade_practice_ratio) + \
               '\nagg_grade=\t' + pretty(self.agg_grade) + \
               '\nagg_practice=\t' + pretty(self.agg_practice) + \
               '\nagg_student=\t' + pretty(self.agg_student) + \
               '\ngrade_all=\t' + pretty(self.grade_all) + \
               '\npractice_all=\t' + pretty(self.practice_all) + \
               '\nratio_all=\t' + pretty(self.ratio_all)



class WhiteVisualization():

    def __init__(self, white_obj):
        self.white_obj = white_obj


    # TODO: Fix bug that interpolates thresholds
    def graph_wuc(self, figure_name="images/wuc_{}.png"):
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

    def graph_grade_vs_practice(self, kctype="tdx", figure_name="grade_vs_practice_{}.png"):
        for kc in self.white_obj.policy.grades.keys():
            fig, ax = pl.subplots()
            fig.subplots_adjust(bottom=0.12)

            x = self.white_obj.policy.practices[kc]
            y = self.white_obj.policy.grades[kc]
            pl.scatter(x, y)
            pl.plot(x, y, linewidth=3)
            pl.ylim([0, 1])
            pl.xlabel("expected practice", fontsize=12)
            pl.ylabel("expected grade", fontsize=12)
            pl.savefig("images/" + kctype + "_" + figure_name.format(kc))
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
        return "%4.3f" % x
    else:
        return str(x)

#def main(filename="input/df_2.1.119.tsv", sep="\t"):#df_2.4.278.tsv"):#
def main(filename="example_data/tom_predictions_chapter1.tsv", sep="\t", kctype="tom"):
    df = pd.read_csv(filename, sep=sep)
    w = White(df)
    w.aggregate_each_kc("weighted")
    w.aggregate_all_by_kc()
    print w

    v = WhiteVisualization(w)
    v.graph_wuc()
    v.graph_grade_vs_practice(kctype=kctype)


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

