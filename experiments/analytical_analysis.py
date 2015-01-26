
# In[1]:

from sklearn import hmm
import matplotlib.pyplot as pl
import pandas as pd

from experiments.visualization import *

#get_ipython().magic(u'matplotlib inline')


# In[2]:

states = ["novice", "master"]
observations = ["incorrect", "correct"]

def kt(k0, learning_rate, guess, slip, forget= 0):
    global states, observations
    startprob = np.array([.0, .0])
    transmat = np.array([[.0, .0], [.0, .0]])
    emissionprob = np.array([[.0, .0], [.0, .0]])
    
    # Forget is 0
    transmat[ states.index("master"), states.index("novice") ] = forget
    transmat[ states.index("master"), states.index("master") ] = 1-forget
    
    # Learning rate
    transmat[ states.index("novice"), states.index("master") ]    = learning_rate
    transmat[ states.index("novice"), states.index("novice") ]    = 1- learning_rate
    
    #Guess
    emissionprob[ states.index("novice"), observations.index("correct") ]    = guess
    emissionprob[ states.index("novice"), observations.index("incorrect") ]  = 1-guess

    #Slip    
    emissionprob[ states.index("master"), observations.index("incorrect") ]  = slip
    emissionprob[ states.index("master"), observations.index("correct") ]    = 1-slip
    
    #K0
    startprob[states.index("master")] = k0
    startprob[states.index("novice")] = 1 - k0
    
    
    model = hmm.MultinomialHMM(n_components=2)
    model.startprob_ = startprob
    model.transmat_ = transmat
    model.emissionprob_ = emissionprob

    #model._set_startprob(startprob)
    #model._set_transmat(transmat)
    #model._set_emissionprob(emissionprob)


    #print "Start prob"
    #print model._get_startprob()
    #print "Transition"
    #print model._get_transmat()
    #print "Emission"
    #print model._get_emissionprob()


    return model


def get_fit(model, data):
    ll = 0
    for seq in data:
        ll += model.score(seq)
    return ll
        
    
    


# $$ 
# A =  (1 - s - g) \cdot (1-k_0)  \\
# p(k) = 1 - s -  A  (1 - L) ^ j  $$ 
# 

# In[3]:

def theoretical_pcorrect(k0, learning_rate, guess, slip, j):
    A = (1 - slip - guess) * (1 - k0)
    base = ( 1 - learning_rate )
    return 1 - slip - ( A * np.power(base,  j) )

    
    


# $$ p(k) = 1 -  \left ( (1-k_0) \cdot (1 - L) ^ j  \right) $$ 

# In[4]:


def theoretical_mastery(k0, learning_rate,  j):
    A = (1 - k0)
    base = ( 1 - learning_rate )
    return 1  - ( A * np.power(base,  j) )


# In[5]:

def synthetic_data_analysis(k0, learning_rate, guess, slip, sequence_length, sequences):
    gold_model = kt(k0=k0, learning_rate=l, guess=g, slip=s)
    gold_model.predict_proba(rows[0:i+1])
    obs = None
    sts = None
    for i in range(0,sequences):
        sample = gold_model.sample(sequence_length)
        row_o =sample[0]
        row_s =sample[1]

        if obs == None:
            obs = row_o
            sts = row_s
        else:
            obs = np.vstack( (obs, row_o) )
            sts = np.vstack( (sts, row_s)   )


    # In[6]:

    print obs
    print sts


    # Out[6]:

    #     [[1 0 1 ..., 1 1 1]
    #      [1 0 0 ..., 1 1 0]
    #      [0 0 0 ..., 0 1 1]
    #      ...,
    #      [0 1 1 ..., 1 1 1]
    #      [0 0 1 ..., 1 1 0]
    #      [0 1 0 ..., 1 1 1]]
    #     [[0 0 1 ..., 1 1 1]
    #      [0 0 0 ..., 1 1 1]
    #      [1 1 1 ..., 1 1 1]
    #      ...,
    #      [0 1 1 ..., 1 1 1]
    #      [0 0 1 ..., 1 1 1]
    #      [0 0 0 ..., 1 1 1]]
    #

    # In[7]:

    ecorrect = np.sum(obs, axis = 0) / float(sequences)
    # emastery = np.sum(sts, axis = 0) / float(sequences)
    #
    #
    # # In[8]:
    #
    # xs = np.arange(0,  sequence_length)
    # tcorrect = theoretical_pcorrect(k0=k0, learning_rate=l, guess=g, slip=s, j=xs)
    # tmastery = theoretical_mastery(k0=k0, learning_rate=l, j=xs)
    for pos in len(ecorrect):
        if ecorrect[pos] >= 0.6:
            effort = pos
            score = np.mean(ecorrect[pos:])

    return ecorrect, pos, score


    # In[9]:



    pl.plot(xs, ecorrect, ':b',  xs, tcorrect, 'b', xs, emastery, ':r', xs, tmastery, 'r'   )
    #pl.ylim([0.7, 1])
    pl.legend(["empirical p(c)", "theoretical p(c)", "empirical p(k)", "theoretical p(k)"], loc='upper center', bbox_to_anchor=(0.5, -0.05),  ncol=2)


# Out[9]:

#     <matplotlib.legend.Legend at 0x1095c5590>

# image file:

#   $$ \frac {  \log  \left[ \frac{ 1 - s - c  } { A} \right] } { \log  1 - L]} $$

# In[17]:

def theoretical_effort (k0, learning_rate, guess, slip, pcorrect):
    A = (1 - slip - guess) * (1 - k0)
    if (1 - slip - pcorrect) == 0:
        pcorrect = pcorrect - 0.0000001
    return np.log( (1 - slip - pcorrect) /  A  ) / np.log( 1 - learning_rate )


def score_vs_effort():
    thresholds = np.arange(0, 1, 0.01)
    efforts = theoretical_effort (k0=k0, learning_rate=l, guess=g, slip=s, pcorrect=thresholds)


    pl.plot (efforts, thresholds)
    pl.xlim([0, 12])
    pl.xlabel("effort")
    pl.ylabel("score")



def plot(tefforts, path):
    df = pd.read_csv(path + "white.csv")
    print df
    #effort
    for threshold in df["threshold"].unique():
        df_thd = df[df["threshold"] == threshold]
        df_npracs = []
        legends = []
        for nb_prac in df["#practice"].unique():
            df_npracs.append(df_thd[df_thd["#practice"] == nb_prac].reset_index())
            legends.append(str(nb_prac) + " practices")
        plot_multiple_scatterplot(df_npracs,
                          legends=legends,
                          colors=["black", "blue", "green"],#, "magenta", "red"],
                          out_figure_path=path + "threshold" + str(threshold) + "_",
                          regress=True, xlabel="#students", ylabel="effort", yconstant=tefforts[threshold])#, title="threshold " + str(threshold))
        plot_multiple_scatterplot(df_npracs,
                          legends=legends,
                          colors=["black", "blue", "green"],#, "magenta", "red"],
                          out_figure_path=path + "threshold" + str(threshold) + "_",
                          regress=True, xlabel="#students", ylabel="score", yconstant=threshold)#, title="threshold " + str(threshold))



def main():
    path = "/Users/hy/inf/Study/CS/Projects_Codes_Data/Data/Data_white/synthetic_data/1kc_k0.2l0.3g0.6s0.4/"

    # Parameters of the model:
    # k0 = 0.2
    # l = 0.3
    # g = 0.1
    # s = 0.1
    # 0.2 0.3 0.1 0.1 0.6
    # 2.12430313532
    # 0.2 0.3 0.1 0.1 0.7
    # 3.26109481356
    # 0.2 0.3 0.1 0.1 0.8
    # 5.20445302344
    # 0.2 0.3 0.1 0.1 0.9
    # inf

    k0 = 0.2
    l = 0.3
    g = 0
    s = 0
    pcorrects = [0.6, 0.7, 0.8, 0.9]
    tefforts = {}



    # /Users/hy/inf/Study/CS/Projects_Codes_Data/CodingProjects/github/white/experiments/analytical_analysis.py:180: RuntimeWarning: divide by zero encountered in log
    #   return np.log( (1 - slip - pcorrect) /  A  ) / np.log( 1 - learning_rate )

    #sequences = 1000
    # k0 = 0.3
    # l = 0.3
    # g = 0.3
    # s = 0.3
    # sequence_length = 20
    # sequences = 1000
    # pcorrect = 0.6

    for pcorrect in pcorrects:
        print k0, l, g, s, pcorrect
        teffort = theoretical_effort(k0=k0, learning_rate=l, guess=g, slip=s, pcorrect = pcorrect)
        print teffort
        tefforts[pcorrect] = teffort
    plot(tefforts, path)
#score


# get white


# Out[18]:

#     2.8867164197494635

# In[ ]:

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




