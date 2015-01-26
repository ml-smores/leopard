__author__ = 'hy'

import os
import os.path

from sm_evaluation.white import White
from sm_evaluation.policies import *
from sm_evaluation.conventional_metrics import *
from sm_evaluation.visualization import *
from get_synthetic_data import *
from split_data import *


pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def load_intermediate_data(kc_id, index):
    data  = IntermediateData.load(kc_id, "obj", index)
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


def get_index_kcs(path, index):
    df_index_to_kc = pd.read_csv(path + "identifiers_obj.txt").sort(columns=[index])#, header=None)
    print df_index_to_kc
    if "index" not in df_index_to_kc.columns:
        index = "chapter"
    else:
        index = "index"
    indexes = df_index_to_kc[index].unique().tolist()
    return indexes, df_index_to_kc

def get_intermidate_data(generate_synthetic_data=False, nb_students=[100]+range(500, 1000+500, 500), seq_lens=[10, 20],
                         chapters=[100], path="", k=0.2, l=0.3, g=0.1, s=0.1, verbose=False):
    if generate_synthetic_data:
        run_experiment(nb_students, seq_lens, chapters, in_path, k, l, g, s, verbose)
    #inter = IntermediateData(-1, "", None, None, None, None)
    IntermediateData.output_path = path
    file_identifier = open(os.path.join(IntermediateData.output_path, "identifiers_" + "obj" +  ".txt"), "w")
    file_identifier.write("chapter,kc,index\n")
    for i in range(len(nb_students)):
        nb_stu = nb_students[i]
        for seq_len in seq_lens:
            index = str(seq_len) + "prac_" + str(nb_stu) + "stu"
            IntermediateData.input_path = in_path + index + "/"
            for chapter_id in chapters:
                print "-----------------"
                print "obj", chapter_id, index
                print "-----------------"
                IntermediateData.create(chapter_id, "obj",
                                        file_identifier,
                                        index=index, train_pct=1.0, dev_pct=0.0)


def run_os_system_command(command):
    print "command: ", command
    os.system(command)

def generate_kt_input(a_index_kcs, file_prefix, index):
    df_train_all = pd.DataFrame(columns=columns)
    df_test_all = pd.DataFrame(columns=columns)
    if not combine_train_dev:
        df_dev_all = pd.DataFrame(columns=columns)
    for kc in a_index_kcs:
        print kc
        df_train, df_dev, df_test = load_intermediate_data(kc, index)
        df_train_all = pd.concat([df_train_all, df_train])
        df_test_all = pd.concat([df_test_all, df_test])
        if combine_train_dev:
            df_train_all = pd.concat([df_train_all, df_dev])
        else:
            df_dev_all = pd.concat([df_dev_all, df_dev])
    print "#datapoints: train:", len(df_train_all), ", test:", len(df_test_all),
    if not combine_train_dev:
        print ", dev:", len(df_dev_all)
    else:
        print ""

    df_train_all.to_csv(out_path + file_prefix + "train0.txt", index=False, header=False, sep="\t", columns=columns)
    df_test_all.to_csv(out_path + file_prefix + "test0.txt", index=False, header=False, sep="\t", columns=columns)#, columns=columns)
    if not combine_train_dev:
        df_dev_all.to_csv(out_path + file_prefix + "dev0.txt", index=False, header=False, sep="\t", columns=columns)#, columns=columns)

def run_mibkt(file_prefix, predict_on_train=True):
    # ./trainhmm: cannot execute binary file: Exec format error
    run_os_system_command("/".join(out_path.split("/")[:-2]) + "/" + "trainhmm -s 1.1 -m 1 -p 1 " + out_path + file_prefix + "train0.txt " + out_path + file_prefix + "model.txt " + out_path + file_prefix + "predict_train.txt")
    run_os_system_command("/".join(out_path.split("/")[:-2]) + "/" + "predicthmm -p 1 " + out_path + file_prefix + "test0.txt " +
                          out_path + file_prefix + "model.txt " +
                          out_path + file_prefix + "predict_test.txt")

    if predict_on_train:
        df_predict = pd.read_csv(out_path + file_prefix + "predict_train.txt", sep="\t", header=None)
        df_test = pd.read_csv(out_path + file_prefix + "train0.txt", sep="\t", header=None)
    else:
        df_predict = pd.read_csv(out_path + file_prefix + "predict_test.txt", sep="\t", header=None)
        df_test = pd.read_csv(out_path + file_prefix + "test0.txt", sep="\t", header=None)
        
    df_predict = df_predict.rename(columns={0:"predicted_outcome", 1:"pwrong"})
    df_test = df_test.rename(columns={0:"outcome", 1:"student", 3:"kc", 2:"problem"})
    df_test["outcome"] = df_test["outcome"].apply(lambda x: 1 if x== 1 else 0)
    df_test["predicted_outcome"] = df_predict["predicted_outcome"]
    df_test.to_csv(out_path + file_prefix + "kt.tsv", sep="\t")
    return df_test

def get_white(df, index, df_white, threshold=0.6):
    print "df from formated pred file:\n", df.head(50)
    print "Datapoints:", len(df), "#kcs:", df.kc.nunique(), "#students:", df.student.nunique(), "threshold:", threshold
    policy = SingleKCPolicy(df, threshold=threshold)
    e = White(policy)
    print e
    auc, pct_correct, accuracy, fmeasure, log_loss,  rmse, r2, mean_auc_by_kc, mean_auc_by_user = compute_standard_metrics(df, detail=False)
    print "auc=", pretty(auc), "pct_correct=", pretty(pct_correct)
    df_white = pd.concat([df_white, pd.DataFrame({"index":index, "score":e.score_students, "effort":e.effort,
                                                  "mean_mastery":e.mastery, "mean_%mastery":e.mastery_pct,
                                                  "auc":auc,"correct%":pct_correct, "#datapoints":len(df),"#kcs":df.kc.nunique(),
                                                  "#students":df.student.nunique(),"#practice":len(df)/(1.0 * df.kc.nunique() *df.student.nunique()),
                                                  "threshold":threshold}, index=[len(df_white)])])
    return df_white





#out_path = "/data/research/white/kt/"
out_path = "/Users/hy/inf/Study/CS/Projects_Codes_Data/CodingProjects/BKT_Michael/standard-bkt-public-standard-bkt/mibkt_white_data/1kc_k0.2l0.3g0.1s0.1/" #"/Users/hy/inf/Study/CS/Projects_Codes_Data/CodingProjects/github/fast/input/"
#in_path = "/data/research/white/adaptivelearningservice/als/pfa/intermediate/"
in_path = "/Users/hy/inf/Study/CS/Projects_Codes_Data/Data/Data_white/synthetic_data/1kc_k0.2l0.3g0.1s0.1/"
format = "mibkt"
columns = []
combine_train_dev = True
def main(generate_synthetic_data=False, get_intermediate=True, gen_kt_input=True, run_kt=True, predict_on_train=True, compute_white=True,
         index="index", thresholds=[0.6,0.7,0.8,0.9], verbose=False): #syn_ #obj_chapter1_
    global columns
    columns = ["outcome", "user_id", "xml_qno",  "kc"] if format == "mibkt" else ["user_id", "kc", "outcome"]

    if get_intermediate:
        get_intermidate_data(generate_synthetic_data=generate_synthetic_data,
                             nb_students=[100]+range(500, 10000+500, 500),
                             seq_lens=[10, 20, 30],
                             path=in_path,
                             k=0.2, l=0.3, g=0.1, s=0.1,
                             verbose=verbose)

    indexes, df_index_to_kc = get_index_kcs(in_path, index)
    print "indexes:", indexes
    if not os.path.isdir(out_path):
        os.makedirs(out_path)

    df_white = pd.DataFrame()
    for id in df_index_to_kc["index"].tolist():
        file_prefix = str(id) + "_"
        print "\n", "id:", id, "file_prefix:", file_prefix

        if gen_kt_input:
            generate_kt_input(df_index_to_kc[df_index_to_kc[index] == id].kc.unique().tolist(), file_prefix, id)

        if run_kt:
            df_test = run_mibkt(file_prefix, predict_on_train=predict_on_train)
        else:
            df_test = pd.read_csv(out_path + file_prefix + "kt.tsv", sep="\t")
        if compute_white:
            for threshold in thresholds:
                df_white = get_white(df_test, id, df_white, threshold)

    if compute_white:
        df_white = df_white.sort(columns=["#practice", "#students"])
        print df_white
        df_white.to_csv(in_path + "white.csv")

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

