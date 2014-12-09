__author__ = 'hy'

from sm_evaluation.white import *
from sm_evaluation.visualization import *
from sm_evaluation.policies import *
from sm_evaluation.standard import *
import pandas as pd


root_path = "/Users/hy/inf/Study/CS/Projects_Codes_Data/Data/Data_white/synthetic_data/"#real_data/"
exp_path = "20kc_10prac_uniform_500stu/" #"20kc_20prac_withlearning_2500stu/"

def get_synthetic_data_results(path):
    df = pd.read_csv(path + "identifiers_obj.txt")
    df_grouped = df.groupby("chapter", as_index=False).agg({"kc": ",".join})
    dfs = []
    chapters = []
    for pos in range(len(df_grouped)):
        #print df_grouped.loc[pos, "chapter"]
        kcs = df_grouped.loc[pos, "kc"].split(",")
        chapter = df_grouped.loc[pos, "chapter"]
        df_chapter = pd.DataFrame()
        for kc in kcs:
            #print kc
            df_chapter = pd.concat([df_chapter, pd.read_csv(path + kc + "_pcorrect.csv")])
        dfs.append(df_chapter)
        chapters.append(chapter)
    return dfs, chapters

# def main(filenames="input/df_2.1.119.tsv", sep="\t"):#df_2.4.278.tsv"):#tom_predictions_chapter1.tsv #tdx_1.3.2.61_16.csv #obj_predictions_chapter1_tries_model_linear
def main(threshold=0.6, generate_whites=True, metrics_correlation=True, plot=False): #example_data/example1.csv"
    if generate_whites:
        dfs, chapters = get_synthetic_data_results(root_path + exp_path) #"../synthetic_data/")
        # dfs = [pd.read_csv(root_path + exp_path + "100.1.9000_pcorrect.csv"), pd.read_csv(root_path + exp_path + "100.1.9001_pcorrect.csv")]
        # chapters = [100, 101]
        whites = []
        aucs = []
        metric_columns = ["score","effort","auc","accuracy","fmeasure","log_loss","rmse","r2","mean_auc_by_kc", "mean_auc_by_stu"]
        standard_metrics = {}
        for metric in metric_columns:
            standard_metrics[metric] = []
        for df in dfs:
            df = df.rename(columns={'pcorrect': 'predicted_outcome'})
            print "Datapoints:", len(df)
            policy = SingleKCPolicy(df, threshold=threshold)
            e = White(policy)
            print e
            whites.append(e)
            auc, pct_correct, accuracy, fmeasure, log_loss,  rmse, r2, mean_auc_by_kc, mean_auc_by_stu = compute_standard_metrics(df)
            aucs.append(auc)
            print "auc:", auc, "correct%:", pct_correct
            standard_metrics["auc"].append(auc)
            standard_metrics["score"].append(e.score_students)
            standard_metrics["effort"].append(e.effort)
            standard_metrics["accuracy"].append(accuracy)
            standard_metrics["fmeasure"].append(fmeasure)
            standard_metrics["log_loss"].append(log_loss)
            standard_metrics["rmse"].append(rmse)
            standard_metrics["r2"].append(r2)
            standard_metrics["mean_auc_by_kc"].append(mean_auc_by_kc)
            standard_metrics["mean_auc_by_stu"].append(mean_auc_by_stu)
        df_metrics = pd.DataFrame({"chapter":chapters, "score":standard_metrics["score"], "effort":standard_metrics["effort"], "auc":standard_metrics["auc"],
                                   "accuracy":standard_metrics["accuracy"], "fmeasure":standard_metrics["fmeasure"], "log_loss":standard_metrics["log_loss"],
                                   "rmse": standard_metrics["rmse"], "r2": standard_metrics["r2"],
                                   "mean_auc_by_kc": standard_metrics["mean_auc_by_kc"],"mean_auc_by_stu": standard_metrics["mean_auc_by_stu"]},
                                  columns=["chapter"] + metric_columns)
        df_metrics.to_csv(root_path + exp_path + "metrics_pfa.csv", index=False)#, columns=["chapter","score","effort","auc","accuracy","fmeasure","log_loss","rmse","r2"])
    else:
        whites=None
        aucs=None

    if metrics_correlation:
        df_metrics = pd.read_csv(root_path + exp_path + "metrics_pfa.csv")
        del df_metrics["chapter"]
        df_metric_correlation = df_metrics.corr(method='spearman') #spearman
        print df_metric_correlation
        df_metric_correlation.to_csv(root_path + exp_path + "metrics_correlation_pfa.csv")
        # metric_correlation = open(root_path + exp_path + "metrics_correlation.csv", "w")
        # metric_correlation.write("metric1,metric2,correlation,p_value\n")
        # for metric in standard_metrics.keys():
        #     cor, pvalue = analyze_correlation(standard_metrics["score"], standard_metrics[metric])
        #     metric_correlation.write("score," + metric + "," + str(cor) + "," + str(pvalue)+"\n")
        #     cor, pvalue = analyze_correlation(standard_metrics["effort"], standard_metrics[metric])
        #     metric_correlation.write("effort," + metric + "," + str(cor) + "," + str(pvalue)+"\n")
        #     cor, pvalue = analyze_correlation(aucs, standard_metrics[metric])
        #     metric_correlation.write("auc," + metric + "," + str(cor) + "," + str(pvalue)+"\n")

    if plot:
        #WhiteVisualization.plot_auc_vs_white(whites, aucs, "../images/" + exp_path + "synthetic_data_auc_vs_{}.pdf")
        #WhiteVisualization.plot_histogram(whites, aucs, "../images/" + exp_path + "synthetic_data_histogram_{}.pdf")
        WhiteVisualization.plot_auc_vs_white(whites, aucs, root_path + exp_path +  "synthetic_data_auc_vs_{}.pdf",
                                             root_path + exp_path + "obj_predictions_chapter1_white_varying_theshold_back.csv", ylim=[0.4,1])
    print "Done"

    #If you need to do multi-dataset comparison do them here:
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
