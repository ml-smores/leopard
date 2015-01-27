__author__ = 'hy'

import pandas as pd
from scipy import stats
import numpy as np

from experiments.visualization import *


# TODO:
# when pG+pS<1, pcorrect should be non-decreasing, double check!

# Compute Score:
# For one kc:
# 1. Given the true parameters (logged when generating synthetic data), all the hypothetical sequences should be generated (Emma doesn't generate and pick one sequence to extend but consider all possible extensions). If we limit sequence length <= 10, then there are at most 2^10 possible sequences. For each sequence, every point's actual correctness, p(know) and p(correct) should be recorded.
# 2. For each sequence, compute score by checking p(know)>=0.6 (etc.), and then weight each sequence's score by its likelihood.
# 3. Compute mean over each sequence score and get the theoretical score of this KC.

verbose = True
maximum_length = 100
output_posterior_pL = False




def expOppNeed(pL, pT, pG, pS, threshold, p_path=1, eita=0.0001, length=0, use_pL_to_judge_mastery=False):#0.0000001):
    length += 1
    p_c_given_pL = pG * (1 - pL) + (1 - pS) * pL #not p(C|K)!

    if verbose:
        print "{}\tp_path: {:.2f},  pL:{:.2f}, pC:{:.2f}".format( length, p_path, pL, p_c_given_pL)

    # Stopping conditions:
    if (p_path < eita) or (maximum_length > 0 and length >= maximum_length):  # simulation has gone too long
        if verbose:
            print length, "\tend 0"
        return 0
    elif (use_pL_to_judge_mastery and pL >= threshold) or ( not use_pL_to_judge_mastery and p_c_given_pL >= threshold): # mastery reached
        if verbose:
            print length, "\tend 1"
        return 1

    # Continue:
    #p_c_pLnext = (1 - pS) * (pL + pT * (1 - pL))
    p_c_pLnext = (1-pL)*pT*pG + (1-pS)*pL
    p_c_pnLnext = pG * (1 - pT) * (1 - pL)
    p_Lnext_given_c = p_c_pLnext / (p_c_pLnext + p_c_pnLnext)
    p_path_c = p_path * p_c_given_pL

    EO_c = expOppNeed(p_Lnext_given_c, pT, pG, pS, threshold, p_path=p_path_c, length=length)

    #JPG
    p_w_given_pL = 1 - p_c_given_pL
    #p_w_given_pL = (1 - pG) * (1 - pL) + pS * pL
    #assert( p_w_given_pL ==  1 - p_c_given_pL)
    #print p_w_given_pL + p_c_given_pL

    #p_w_pLnext = pS * (pL + pT * (1 - pL))
    p_w_pLnext = (1-pL)*pT*(1-pG) + pS*pL
    #p_w_pnLnext = (1 - pG) * (1 - pT) * (1 - pL)
    p_w_pnLnext = (1-pL)*(1-pT)*(1-pG) + 0
    p_Lnext_given_w = p_w_pLnext /  (p_w_pLnext + p_w_pnLnext)
    p_path_w = p_path * p_w_given_pL
    EO_w = expOppNeed(p_Lnext_given_w, pT, pG, pS, threshold, p_path=p_path_w, length=length)

    effort = (1 + p_c_given_pL *EO_c + p_w_given_pL * EO_w)#(1 + p_c_given_pL*EO_c*flag + p_w_given_pL * EO_w* flag)
    if verbose:
        print "*  {}  {:.3f}  {:.3f}".format(length, pL, p_c_given_pL)
    return effort




def main():
    print expOppNeed(pL=0.3, pT=0.25, pG=0.3, pS=0.3, threshold=0.6, use_pL_to_judge_mastery=False)
    #compare(path+"syn_white_kt_on_train.csv", path+"syn_emma_effort_by_pcorrect.csv", "effort")
    # compute_effort = False
    # compute_emma()
    # compute_score()
    #compare(path+"syn_white_kt_on_train.csv", path+"syn_emma_score_by_pcorrect.csv", "score")


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

#threshold=0.6
#0.2 0.3 0.1 0.1, maximum length 10: 5.587356
#0.2 0.3 0.1 0.1, maximum length 20: 6.738366
#0.2 0.3 0.1 0.1, maximum length 30: 6.984749
#0.2 0.3 0.1 0.1, unlimited length: 7.05185265434

#threshold=0.7
#0.2 0.3 0.1 0.1, maximum length 10: 5.587356
#0.2 0.3 0.1 0.1, maximum length 20:
#0.2 0.3 0.1 0.1, maximum length 30:
#0.2 0.3 0.1 0.1, unlimited length:

#threshold=0.8
#0.2 0.3 0.1 0.1, maximum length 10: 6.3517
#0.2 0.3 0.1 0.1, maximum length 20:
#0.2 0.3 0.1 0.1, maximum length 30:
#0.2 0.3 0.1 0.1, unlimited length:

#threshold=0.9
#0.2 0.3 0.1 0.1, maximum length 10: 10
#0.2 0.3 0.1 0.1, maximum length 20:
#0.2 0.3 0.1 0.1, maximum length 30:
#0.2 0.3 0.1 0.1, unlimited length:
