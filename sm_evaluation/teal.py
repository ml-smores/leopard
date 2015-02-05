__author__ = 'hy'
import numpy as np


novice = "novice"
master = "master"
incorrect = "w"
correct = "c"

class Memoize:
    def __init__(self, f, n):
        self.f = f
        self.n = n
        self.memo = {}
    def __call__(self, *args):
        keys = args[:self.n]
        if not keys in self.memo:
            self.memo[keys] = self.f(*args)
        return self.memo[keys]

# Needs a call to forward_synthetic_aux.memo = {}
def forward_synthetic_aux(t, k, o, initial, emission, transition):
    if t == 0:
        return initial[k] * emission[k][o]
    elif t < 1:
        raise RuntimeError ("Invalid argument t ({:0.2f}) should be >= 0".format(t))
    else:
        outputs= emission.items()[0][1].keys()
        states = emission.keys()
        ans = 0
        for k1 in states:
            for o1 in outputs:
                ans += forward_synthetic_aux(t-1, k1, o1, initial, emission, transition) * transition[k1][k]
        return ans * emission[k][o]

forward_synthetic_aux = Memoize(forward_synthetic_aux, 3)

def forward_synthetic(t, k0, learning_rate, guess, slip, forget=0):
    # Setup helpful variables / memoization:
    transition, emission, initial = prepare_arrays(k0, learning_rate, guess, slip, forget) # convenience method
    outputs= emission.items()[0][1].keys()
    states = emission.keys()

    print "init=", initial
    print "emit=", emission
    print "trans=", transition
    print "alphabet=", outputs

    forward_synthetic_aux.memo = {}

    # Calculate forward probs, while exhaustively generating synthetic data
    a = []
    for k1 in states:
        for o1 in outputs:
            result = forward_synthetic_aux(t,k1, o1, initial, emission, transition)
            a.append(result)
            print "*", k1, o1, result
    print sum(a)
    pc = [0] * (t+1)
    pk = [0] * (t+1)
    for ((t1, s1, e1), p) in forward_synthetic_aux.memo.iteritems():
        if s1 == master:
            pk[t1] += p
        if e1 == correct:
            pc[t1] += p

    print pc
    print pk


def theoretical_pcorrect(k0, learning_rate, guess, slip, j):
    A = (1 - slip - guess) * (1 - k0)
    base = ( 1 - learning_rate )
    return 1 - slip - ( A * np.power(base,  j) )

def theoretical_mastery(k0, learning_rate,  j):
    A = (1 - k0)
    base = ( 1 - learning_rate )
    return 1  - ( A * np.power(base,  j) )


def prepare_arrays(k0, learning_rate, guess, slip, forget):
    transmat     = {master:{master:-1, novice:-1}, novice:{master:-1, novice:-1}}
    emissionprob = {master:{incorrect:-1, correct:-1}, novice:{incorrect:-1, correct:-1}}
    startprob    = {master:-1, novice:-1}

    transmat[master][novice] = forget
    transmat[master][master]  = 1-forget
    transmat[novice][master]     = learning_rate
    transmat[novice][novice]    = 1- learning_rate
    emissionprob[novice][correct]    = guess
    emissionprob[novice][incorrect]  = 1-guess
    emissionprob[master][incorrect]  = slip
    emissionprob[master][correct]    = 1-slip
    startprob[master] = k0
    startprob[novice] = 1 - k0

    return transmat, emissionprob, startprob


def theoretical_effort (k0, learning_rate, guess, slip, pcorrect):
    A = (1 - slip - guess) * (1 - k0)
    base = ( 1 - learning_rate  )
    return np.log( (- pcorrect + 1 - slip ) /  A  ) / np.log( 1 - learning_rate )


def main():
    sequence_length = 5

    k0=0.3
    l=0.25
    g=0.3
    s=0.3

    forward_synthetic(t=5, k0=k0, learning_rate=l, guess=g, slip=s)

    xs = np.arange(0,  sequence_length)
    tcorrect = theoretical_pcorrect(k0=k0, learning_rate=l, guess=g, slip=s, j=xs)
    tmastery = theoretical_mastery(k0=k0, learning_rate=l, j=xs)

    print tcorrect


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

