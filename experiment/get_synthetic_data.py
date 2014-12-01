
# In[1]:

import numpy as np
from sklearn import hmm
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
#get_ipython().magic(u'matplotlib inline')
import random
import numpy as np
import csv


# In[2]:

# Functions and constants
states = ["novice","master"]
observations = ["incorrect", "correct"]

def kt(k0, learning_rate, guess, slip, forget= 0, random_state=None):
    global states, observations
    startprob = np.array([.0, .0])
    transmat = np.array([[.0, .0], [.0, .0]])
    emissionprob = np.array([[.0, .0], [.0, .0]])

    # Forget
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


    model = hmm.MultinomialHMM(n_components=2, random_state=random_state)
    model.startprob_ = startprob
    model.transmat_ = transmat
    model.emissionprob_ = emissionprob

    return model


def get_fit(model, data):
    ll = 0
    for seq in data:
        ll += model.score(seq)
    return ll


prng =np.random.RandomState(898898)
initialize_type = "uniform" #with learning
dataset_type = "exp2"
path = "./data_20kc_perchapter/"

if dataset_type == "exp1":
    datasets = 500
    kcs = 5
    sequence_length = 10
    students = 500 #1000
elif dataset_type == "exp2":
    datasets = 500
    kcs = 20
    sequence_length = 10
    students = 500 #1000

id_out = csv.writer(open(path + "identifiers_obj.txt", "w"))
log = open(path + "log.txt", "w")
for d in range(100, 100+datasets):
    out = csv.writer(open(path + "homework_xref_{:03d}_decompressed.csv".format(d), "w"))
    out.writerow(["user_id", "objective_id", "xml_qno","xml_correct_first",      "homework_id", "isTeacher", "xml_state","chapter_id", "section_id", "exercise_id", "handedin", "numberCorrect", "numberAttempts", "duration"])

    avg_ones_per_kc = []
    for kc in range(9000, 9000+kcs):
        if initialize_type == "uniform":
            k0 = prng.uniform(0.001, 1)
            lr = prng.uniform(0.001, 1)
            guess  = prng.uniform(0.001, 1)
            slip  = prng.uniform(0.001, 1)
        elif initialize_type == "with_learning":
            k0 = prng.uniform(0.001, 0.5) #Samples are uniformly distributed over the half-open interval [low, high) (includes low, but excludes high).
            lr = prng.uniform(0.2, 1)
            guess  = 0.1 #prng.uniform(0, 1)
            slip  = 0.1 #prng.uniform(0, 1)

        kc_ = str(d) + ".1." + str(kc)
        id_out.writerow([d, kc_])
        print "chapter:", d, "kc:", kc_, "k0:", k0, "lr:", lr, "g:", guess, "s:", slip
        log.write(",".join(["chapter:", str(d), "kc:", kc_, "k0:", str(k0), "lr:", str(lr), "g:", str(guess), "s:", str(slip)])+"\n")

        model = kt(k0=k0, learning_rate=lr, guess=guess, slip=slip)
        total_nb_ones = 0
        for s in range(0,students):
            nb_ones = 0
            obs, hidden = model.sample(sequence_length, random_state=prng)
            for ix, o in enumerate (obs):
                nb_ones += 1 if o == 1 else 0
                out.writerow([s, kc, ix + ((kc-9000) * sequence_length), o,      1, 0, "complete", d, 1, 1,  "2013-09-26 11:36:00,", 0, 0, 50])
            print "\t\tstu:",s, "hidden:", str(hidden), "obs:",  str(obs), "#1:", nb_ones
            log.write( "\t\t" + "\t".join(["stu:", str(s), "hidden:", str(hidden), "obs:",  str(obs), "#1:", str(nb_ones)])+"\n")
            total_nb_ones += nb_ones
        avg_ones = total_nb_ones / (1.0 * students)
        print "\t\tavg #1:", avg_ones
        log.write( "\t\t"+ ",".join(["avg #1:", str(avg_ones)])+"\n")
        avg_ones_per_kc.append(avg_ones)
    print "chapter", d, "per kc avg #1:", np.mean(avg_ones_per_kc), avg_ones_per_kc
    log.write( "\t\t" + "\t".join(["chapter"+str(d), "per kc avg #1:", str(np.mean(avg_ones_per_kc)), str(avg_ones_per_kc)])+"\n")


'''Testing code'''
# In[3]:

# model1 = kt(k0=0.1, learning_rate=0.1, guess=0.0, slip=0.05)
# model2 = kt(k0=0.1, learning_rate=0.1, guess=0.53, slip=0.05)


# data =  np.array([0, 1,1,1,1,0])
#
# logprob1, k1 = model1.decode(data, algorithm="viterbi")
# logprob2, k2 = model2.decode(data, algorithm="viterbi")
#
# print "Data:", ", ".join(map(lambda x: observations[x], data))
# print "States:", ", ".join(map(lambda x: states[x], k1)), logprob1
# print "States:", ", ".join(map(lambda x: states[x], k2)), logprob2
#
# print model1.score(data), model2.score(data)
#

# Out[3]:

#     Data: correct, incorrect, incorrect, incorrect, incorrect, correct
#     States: master, master, master, master, master, master -14.388100776
#     States: novice, novice, novice, novice, novice, novice -4.92200997593
#     -14.388100776 -4.71830951083
#

# In[25]:


