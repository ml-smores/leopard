__author__ = 'hy'

import pandas as pd
import pickle
import os
from sm_evaluation.white import White
from sm_evaluation.policies import *
from sm_evaluation.common import *
from sm_evaluation.standard import *
from sm_evaluation.visualization import *

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)



#out_path = "/data/research/white/kt/"
out_path = "/Users/hy/inf/Study/CS/Projects_Codes_Data/CodingProjects/BKT_Michael/standard-bkt-public-standard-bkt/white_data/" #"/Users/hy/inf/Study/CS/Projects_Codes_Data/CodingProjects/github/fast/input/"
#in_path = "/data/research/white/adaptivelearningservice/als/pfa/intermediate/"
in_path = "/Users/hy/inf/Study/CS/Projects_Codes_Data/Data/Data_white/synthetic_data/data_20kc_perchapter/"
format = "mibkt"
columns = []
combine_train_dev = True

class IntermediateData():
    input_path = "./data/"
    output_path= in_path

    def __init__(self, chapter, kc, df, train_rows, dev_rows, test_rows):
        self.chapter_id = chapter
        self.kc_id = kc
        self.df_features = df
        self.train_rows = train_rows
        self.dev_rows = dev_rows
        self.test_rows = test_rows

    @staticmethod
    def load(kc_id, kctype):
        path = IntermediateData.output_path + IntermediateData.get_filename(kctype, kc_id)
        try:
            f_output = open(path, "r")
            ans = pickle.load(f_output)
            f_output.close()
        except IOError:
            print "Can't load model ", path
            raise
        return ans

    @staticmethod
    def get_filename(kctype, kc):
        return kctype +  "_" + str(kc)

def get_data(kc_id):
    data  = IntermediateData.load(kc_id, "obj")
    if format == "fast":
        columns = ["user_id", "kc", "outcome"]
        df_features = data.df_features[columns]
        df_features = df_features.rename(columns={"user_id":"student", "kc":"KCs"})
        df_features["outcome"] = df_features["outcome"].apply(lambda x: "correct" if x == 1 else "incorrect")
    elif format == "mibkt":
        columns = ["outcome", "user_id", "xml_qno",  "kc"]
        df_features = data.df_features[columns]
        df_features["outcome"] = df_features["outcome"].apply(lambda x: "1" if x == 1 else "2")
        df_features["xml_qno"] = df_features["xml_qno"].astype(np.uint8)
        df_features["user_id"] = df_features["user_id"].astype(str)
    train = data.train_rows
    dev   = data.dev_rows
    test  = data.test_rows
    df_train = df_features[train]
    df_dev = df_features[dev]
    df_test = df_features[test]
    return df_train, df_dev, df_test


def get_chapters_kcs(path):
    df_chapter_kc = pd.read_csv(path + "identifiers_obj.txt", header=None)
    df_chapter_kc = df_chapter_kc.rename(columns={0:"chapter", 1:"kc"})
    df_chapter_kc = df_chapter_kc.sort(columns=["kc"])
    kcs = df_chapter_kc["kc"].tolist()
    chapters = df_chapter_kc["chapter"].unique().tolist()
    return kcs, chapters, df_chapter_kc



def run_os_system_command(command):
    print "command: ", command
    os.system(command)

def main(prefix="syn_"): #syn_ #obj_chapter1_
    global columns
    if format == "fast":
        columns = ["user_id", "kc", "outcome"]
    elif format == "mibkt":
        columns = ["outcome", "user_id", "xml_qno",  "kc"]
    kcs, chapters, df_chapter_kc = get_chapters_kcs(in_path)
    print chapters
    chapter_white = {}
    outfile = open(out_path + prefix + "white.csv", "w")
    outfile.write("chapter,score,effort,mean_mastery,mean_%mastery,auc,correct%\n")
    for chapter in chapters:
        print "chapter", chapter
        a_chapter_kcs = df_chapter_kc[df_chapter_kc["chapter"] == chapter].kc.unique().tolist()
        df_train_all = pd.DataFrame(columns=columns)
        df_test_all = pd.DataFrame(columns=columns)
        if not combine_train_dev:
            df_dev_all = pd.DataFrame(columns=columns)
        for kc in a_chapter_kcs:
            print kc
            df_train, df_dev, df_test = get_data(kc)
            df_train_all = pd.concat([df_train_all, df_train])
            df_test_all = pd.concat([df_test_all, df_test])
            if combine_train_dev:
                df_train_all = pd.concat([df_train_all, df_dev])
            else:
                df_dev_all = pd.concat([df_dev_all, df_dev])
        print "chapter", chapter, "#datapoints: train:", len(df_train_all), ", test:", len(df_test_all),
        if not combine_train_dev:
            print ", dev:", len(df_dev_all)
        else:
            print ""

        file_prefix = prefix + "chapter" + str(chapter) + "_"
        df_train_all.to_csv(out_path + file_prefix + "train0.txt", index=False, header=False, sep="\t", columns=columns)
        df_test_all.to_csv(out_path + file_prefix + "test0.txt", index=False, header=False, sep="\t", columns=columns)#, columns=columns)
        if not combine_train_dev:
            df_dev_all.to_csv(out_path + file_prefix + "dev0.txt", index=False, header=False, sep="\t", columns=columns)#, columns=columns)

        # ./trainhmm: cannot execute binary file: Exec format error
        run_os_system_command(out_path + "trainhmm -s 1.1 -m 1 -p 1 " + out_path + file_prefix + "train0.txt " + out_path + file_prefix + "model.txt " + out_path + file_prefix + "predict_train.txt")
        run_os_system_command(out_path + "predicthmm -p 1 " + out_path + file_prefix + "test0.txt " +
                              out_path + file_prefix + "model.txt " +
                              out_path + file_prefix + "predict_test.txt")

        df_predict = pd.read_csv(out_path + file_prefix + "predict_test.txt", sep="\t", header=None)
        df_predict = df_predict.rename(columns={0:"predicted_outcome", 1:"pwrong"})
        df_test = pd.read_csv(out_path + file_prefix + "test0.txt", sep="\t", header=None)
        df_test = df_test.rename(columns={0:"outcome", 1:"student", 3:"kc", 2:"problem"})
        df_test["outcome"] = df_test["outcome"].apply(lambda x: 1 if x== 1 else 0)
        df_test["predicted_outcome"] = df_predict["predicted_outcome"]
        df_test.to_csv(out_path + file_prefix + "kt.tsv", sep="\t")

        df = df_test
        print "df from formated pred file:\n", df.head()
        threshold = 0.6
        print "Datapoints:", len(df), "#kcs:", df.kc.nunique(), "threshold:", threshold, "#students:", df.student.nunique()
        policy = SingleKCPolicy(df, threshold=threshold)
        e = White(policy)
        print e
        auc, pct_correct = compute_standard_metrics(df)
        print "auc=", pretty(auc), "pct_correct=", pretty(pct_correct)
        chapter_white[chapter] = [e.score_students, e.effort, e.mastery, e.mastery_pct, auc, pct_correct]
        outfile.write(str(chapter)+","+",".join([str(e.score_students), str(e.effort), str(e.mastery), str(e.mastery_pct), str(auc), str(pct_correct)]) + "\n")
    print pretty(chapter_white)
    print "Done"


if __name__ == "__main__":
    import sys
    args = sys.argv
    print args
    cl = {}
    for i in range(1, len(args)): # index 0 is the filename
        pair  =  args[i].split('=')
        if pair[1].isdigit():
            cl[pair[0]] = int(pair[1])
        elif pair[1].lower() in ("true", "false"):
            cl[pair[0]] = (pair[1].lower() == 'true')
        else:
            cl[pair[0]] = pair[1]

    main(**cl)

