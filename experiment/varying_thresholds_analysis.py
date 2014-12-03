__author__ = 'ugonzjo'

from sm_evaluation.white import White
from sm_evaluation.policies import *
from sm_evaluation.common import *
from sm_evaluation.standard import *
from sm_evaluation.visualization import *
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

root_path = "/Users/hy/inf/Study/CS/Projects_Codes_Data/Data/Data_white/synthetic_data/"#synthetic_data/" #real_data/"
exp_path = "20kc_20prac_withlearning_g0.6s0.4_2500stu/"#"20kc_10prac_withlearning_2500stu/"

#root_path = "/Users/hy/inf/Study/CS/Projects_Codes_Data/CodingProjects/github/white/example_data/"
#exp_path = ""
#filenames = "obj_predictions_chapter1_white_varying_theshold_back.csv"


def get_synthetic_data_results(path, chapter=228):
    df_all = pd.read_csv(path + "identifiers_obj.txt")
    dfs = []
    names = []
    for chapter in df_all.chapter.unique(): #range(139, 600): #
        df = df_all[df_all["chapter"] == chapter]
        df_chapter = pd.DataFrame()
        for kc in df.kc.unique():
            df_chapter = pd.concat([df_chapter, pd.read_csv(path + kc + "_pcorrect.csv")])
        names.append(str(chapter))
        dfs.append(df_chapter)
    return dfs, names

def get_data(filenames):
    dfs = []
    names = filenames.split(",")
    for input in names:
        print input
        df = pd.read_csv(input, sep=("\t" if "tsv" in input else ","))
        dfs.append(df)
    return dfs, names

#private_data
def main(prefix = "obj_predictions_chapter", synthetic_data=True, plot=True, get_whites=False):
    if synthetic_data:
        dfs, names = get_synthetic_data_results(root_path + exp_path)
        prefix = ""
    else:
        dfs = [1]
        names = [1]
    #for chapter in [1]:
    for pos in range(len(dfs)):
        chapter = names[pos] #chapters
        output = root_path + exp_path + prefix + str(chapter) + "_white_varying_theshold.csv"#"".join(input.split(".tsv"))+ "_white_varying_theshold.csv"
        print output
        if get_whites:
            df = dfs[pos]
            df = df.rename(columns={'pcorrect': 'predicted_outcome'})
            print chapter, "Datapoints:", len(df), "kcs:", df.kc.nunique(), "#stus:", df.student.nunique()
            file = open(output, "w")
            file.write("threshold,score,effort,mean_mastery,mean_mastery_pct\n")

            print "Getting per kc's white varying thresholds..."
            kc_thresholds = {}
            kc_score_students = {}
            kc_effort = {}
            kc_mastery = {}
            kc_mastery_pct = {}
            for kc in df["kc"].unique():
                df_kc = df[df["kc"] == kc]
                thresholds = WhitePolicy.get_thresholds(df_kc)
                kc_thresholds[kc] = thresholds
                kc_score_students[kc] = []
                kc_effort[kc] = []
                kc_mastery[kc] = []
                kc_mastery_pct[kc] = []
                for threshold in thresholds:
                    e = White(SingleKCPolicy(df_kc, threshold=threshold))
                    print pretty(threshold), ":", e
                    kc_score_students[kc].append(e.score_students)
                    kc_effort[kc].append(e.effort)
                    kc_mastery[kc].append(e.mastery)
                    kc_mastery_pct[kc].append(e.mastery_pct)

            thresholds = WhitePolicy.get_thresholds(df)
            print "\nGetting all kcs' threshold, #thresholds = ", len(thresholds)
            score_students_per_thd = []
            effort_per_thd = []
            mastery_per_thd = []
            mastery_pct_per_thd = []
            for threshold in thresholds:
                score_student = 0.0
                effort = 0.0
                mastery = 0.0
                mastery_pct = 0.0
                for kc in df["kc"].unique():
                    threshold_pos = next(i for i, v in enumerate(kc_thresholds[kc]) if v >= threshold)
                    score_student += kc_score_students[kc][threshold_pos] #list or scalar
                    effort += kc_effort[kc][threshold_pos] #list or scalar
                    mastery += kc_mastery[kc][threshold_pos]
                    mastery_pct += kc_mastery_pct[kc][threshold_pos]
                score_student = score_student / (1.0 * df["kc"].nunique())
                mastery = mastery / (1.0 * df["kc"].nunique())
                mastery_pct = mastery_pct / (1.0 * df["kc"].nunique())
                score_students_per_thd.append(score_student)
                effort_per_thd.append(effort)
                mastery_per_thd.append(mastery)
                mastery_pct_per_thd.append(mastery_pct)

                print "threshold: ", pretty(threshold), "overall: score:", pretty(score_student), " effort:", pretty(effort)," mean #stu_mastered:", pretty(mastery)," mean %stu_mastered:", pretty(mastery_pct)
                file.write(",".join([str(threshold), str(score_student), str(effort), str(mastery), str(mastery_pct)]) + "\n")
            file.close()
            df_white = pd.DataFrame({"chapter":chapter, "threshold":thresholds, "score_student":score_students_per_thd, "effort":effort_per_thd, "mean_mastery":mastery_per_thd, "mean_mastery_pct":mastery_pct_per_thd})
            df_white.to_csv(output)

        if plot:
            df = pd.read_csv(output)
            if "score" in df.columns:
                score_str = "score"
            else:
                score_str = "score_student"
            WhiteVisualization.plot_component_relation("all", df["effort"].tolist(), df[score_str].tolist(),
                            root_path + exp_path + "chapter" + str(chapter) + "_", "effort", "score",
                            nb_students=df["mean_mastery"], perkc_stu_thd = 30, ylim=[0.53, 0.68]) #[0, max(practices)], [0,1],

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
