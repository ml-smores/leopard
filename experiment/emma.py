__author__ = 'hy'

import pandas as pd
from sm_evaluation.common import *
from scipy import stats
import numpy as np


# For one kc:
# 1. Given the true parameters (logged when generating synthetic data), all the hypothetical sequences should be generated (Emma doesn't generate and pick one sequence to extend but consider all possible extensions). If we limit sequence length <= 10, then there are at most 2^10 possible sequences. For each sequence, every point's actual correctness, p(know) and p(correct) should be recorded.
# 2. For each sequence, compute score by checking p(know)>=0.6 (etc.), and then weight each sequence's score by its likelihood.
# 3. Compute mean over each sequence score and get the theoretical score of this KC.

verbose = False
path = "/Users/hy/inf/Study/CS/Projects_Codes_Data/Data/Data_white/synthetic_data/data_20kc_perchapter/"
maximum_length = 10
threshold = 0.6
compute_effort = False
use_pL_to_judge_mastery = False
obs_seqs = []
hidden_seqs = []
pcorrect_seqs = []
likelihood = []

def get_kc_parameters(file):
    kc_parameters = {}
    for line in open(file, "r").readlines():
        if "chapter:" in line:
            split_result = line.strip().split(",")
            kc = split_result[3]
            pL0 = float(split_result[5])
            pT = float(split_result[7])
            pG = float(split_result[9])
            pS = float(split_result[11])
            kc_parameters[kc] = [pL0, pT, pG, pS]
    df = pd.DataFrame({kc: kc_parameters})
    df.to_csv(path + "kc_parameters.csv")
    print kc_parameters

    return kc_parameters


def expOppNeed(p_path, pL, pT=0.3, pG=0.1, pS=0.1, d=0.6, eita=0.0000001, length=0, obs=[], hidden=[], pcorrect=[]):#0.0000001):
    if verbose:
        print "\tp_path:", p_path, "pL:", pL
    if p_path < eita or (maximum_length > 0 and length >= maximum_length) or (compute_effort and use_pL_to_judge_mastery and pL >= d):
        if verbose:
            if p_path < eita:
                print "\tp_path < eita(", eita, "), return 0"
            elif (maximum_length > 0 and length >= maximum_length):
                print "\treaching maximum length", maximum_length, ", return 0"
            else:
                print "\tpL(", pL, ") >= ", d, "return 0"
        if not compute_effort:
            obs_seqs.append(obs)
            hidden_seqs.append(hidden)
            likelihood.append(p_path)
            pcorrect_seqs.append(pcorrect)
        return 0
    else:
        length += 1
        p_c_given_pL = pG * (1 - pL) + (1 - pS) * pL
        p_c_pLnext = (1 - pS) * (pL + pT * (1 - pL))
        p_c_pnLnext = pG * (1 - pT) * (1 - pL)
        p_correct = p_c_pLnext + p_c_pnLnext
        if (compute_effort and not use_pL_to_judge_mastery and p_correct >= d):
            if verbose:
                 print "\tp_correct", p_correct, ") >= ", d, "return 1"
            return 1
        p_Lnext_given_c = p_c_pLnext / (p_c_pLnext + p_c_pnLnext)
        p_path_c = p_path * p_c_given_pL
        if not compute_effort:
            EO_c = expOppNeed(pL=p_Lnext_given_c, p_path=p_path_c, length=length, obs=obs+[1], hidden=hidden+[p_Lnext_given_c], pcorrect=pcorrect+[p_correct])
        else:
            EO_c = expOppNeed(pL=p_Lnext_given_c, p_path=p_path_c, length=length)
        p_w_given_pL = (1 - pG) * (1 - pL) + pS * pL
        p_w_pLnext = pS * (pL + pT * (1 - pL))
        p_w_pnLnext = (1 - pG) * (1 - pT) * (1 - pL)
        p_Lnext_given_w = p_w_pLnext /  (p_w_pLnext + p_w_pnLnext)
        p_path_w = p_path * p_w_given_pL
        if not compute_effort:
            EO_w = expOppNeed(pL=p_Lnext_given_w, p_path=p_path_w, length=length, obs=obs+[0], hidden=hidden+[p_Lnext_given_w], pcorrect=pcorrect+[p_correct])
        else:
            EO_w = expOppNeed(pL=p_Lnext_given_w, p_path=p_path_w, length=length)
        return (1 + p_c_given_pL*EO_c + p_w_given_pL * EO_w)

def compute_emma():
    global obs_seqs, hidden_seqs, likelihood, pcorrect_seqs
    kc_parameters = get_kc_parameters(path + "log.txt")
    df_chapter_kcs = pd.read_csv(path + "identifiers_obj.txt")
    chapter_effort = {}
    for chapter in df_chapter_kcs.chapter.unique():
        effort = 0.0
        df_a_chapter = df_chapter_kcs[df_chapter_kcs["chapter"] == chapter]
        df_a_chapter_seqs = pd.DataFrame()
        for kc in df_a_chapter.kc.unique():
            if kc not in kc_parameters.keys():
                print "Can't retrieve paramters for kc ", kc
                continue
            print kc
            pL0, pT, pG, pS =  kc_parameters[kc]
            if verbose:
                print "\t", pL0, pT, pG, pS
            effort += expOppNeed(p_path=1, pL=pL0, pT=pT, pG=pG, pS=pS, d=threshold)
            if verbose:
                print "\teffort:", effort
            df_a_chapter_seqs = pd.concat([df_a_chapter_seqs,
                      pd.DataFrame({"kc":[kc]*len(obs_seqs), "obs":obs_seqs, "hidden":hidden_seqs, "likelihood":likelihood, "pcorrect":pcorrect_seqs})])
            obs_seqs = []
            hidden_seqs = []
            likelihood = []
            pcorrect_seqs = []
        if compute_effort:
            print "chapter", chapter, "effort:", effort
            chapter_effort[chapter] = effort
        df_a_chapter_seqs.to_csv(path + "chapter" + str(chapter) + "_seq.csv")
    if compute_effort:
        df_chapter_effort = pd.DataFrame(chapter_effort.items(), columns=['chapter', 'effort'])
        print df_chapter_effort
        df_chapter_effort.to_csv(path + "syn_emma_effort_by_pcorrect.csv")

def compute_score():
    chapter_score = {}
    for chapter in range(100, 600):
        df = pd.read_csv(path + "chapter" + str(chapter) + "_seq.csv")
        sum_likelihood = 0.0
        mean_score_per_chapter = 0.0
        for kc in df.kc.unique(): #per kc
            df_kc = df[df["kc"] == kc]
            df_kc = df_kc.reset_index(drop=True)
            mean_score_per_kc = 0.0
            sum_likelihood = 0.0
            for pos in range(len(df_kc)): #per sequence
                decision_seq = df_kc.loc[pos, "hidden"] if use_pL_to_judge_mastery else df_kc.loc[pos, "pcorrect"]
                obs = df_kc.loc[pos, "obs"]
                obs = [int(x) for x in obs[1:-1].split(",")]
                likelihood = float(df_kc.loc[pos, "likelihood"])
                # print obs
                # print decision_seq
                # print likelihood
                threshold_pos = -1
                for ds_pos in range(len(decision_seq)):
                    if decision_seq[ds_pos] >= threshold:
                        threshold_pos = ds_pos
                        break
                if threshold_pos == -1:
                    score = np.sum(obs) / (1.0 * len(obs))
                else:
                    obs_after = obs[ds_pos:]
                    score = np.sum(obs_after) / (1.0 * len(obs_after))
                #print score
                mean_score_per_kc += score * likelihood #for a sequence
                sum_likelihood += likelihood
            mean_score_per_kc = mean_score_per_kc / sum_likelihood #weighed score per kc
            mean_score_per_chapter += mean_score_per_kc
        mean_score_per_chapter = mean_score_per_chapter / df.kc.nunique()
        chapter_score[chapter] = mean_score_per_chapter
        print "chapter:", chapter, "score:", mean_score_per_chapter
    df_chapter_score = pd.DataFrame(chapter_score.items(), columns=['chapter', 'score'])
    print df_chapter_score
    df_chapter_score.to_csv(path + "syn_emma_score_by_pcorrect.csv")


def compare(file1, file2, type="effort"):
    df_white = pd.read_csv(file1)
    df_emma = pd.read_csv(file2)
    rho, rho_pval = stats.spearmanr(df_white[type],df_emma[type])
    plot_scatterplot(df_white[type].tolist(),
                        df_emma[type].tolist(),
                       "white " + type,
                       "theoretical " + type,
                      file=path+ "theoretical_vs_white_" + type + ".png",
                      legend="Spearman correlation=" + pretty(rho) + "(pvalue=" + pretty(rho_pval) + ")")


def main():
    #compute_emma()
    #compare(path+"syn_white.csv", path+"emma_effort_by_pcorrect_no_seqlen_limit.csv")
    #compute_score()
    compare(path+"syn_white.csv", path+"syn_emma_score_by_pcorrect.csv", "score")


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