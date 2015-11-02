__author__ = 'hy'
import numpy as np
from collections import OrderedDict
import warnings

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

    print("init=", initial)
    print("emit=", emission)
    print("trans=", transition)
    print("alphabet=", outputs)

    forward_synthetic_aux.memo = {}

    # Calculate forward probs, while exhaustively generating synthetic data
    a = []
    for k1 in states:
        for o1 in outputs:
            result = forward_synthetic_aux(t,k1, o1, initial, emission, transition)
            a.append(result)
            print("*", k1, o1, result)
    print(sum(a))
    pc = [0] * (t+1)
    pk = [0] * (t+1)
    for ((t1, s1, e1), p) in forward_synthetic_aux.memo.iteritems():
        if s1 == master:
            pk[t1] += p
        if e1 == correct:
            pc[t1] += p

    print(pc)
    print(pk)


def theoretical_pcorrect(k0, learning_rate, guess, slip, j):
    A = (1 - slip - guess) * (1 - k0)
    base = ( 1 - learning_rate )
    return 1 - slip - ( A * np.power(base,  j) )

def theoretical_mastery(k0, learning_rate,  j):
    A = (1 - k0)
    base = ( 1 - learning_rate )
    return 1  - ( A * np.power(base,  j) )



def theoretical_pcorrect1(k0, learning_rate, guess, slip, t):
     return 0.5


def generate_all_sequences(k0, learning_rate, guess, slip, threshold, T, t=0, p_sequence=1, already_stop=False, effort=0, outcome=0,n=0, dummy=""):
    if t ==0 and np.isnan(effort_threshold(k0, learning_rate, guess, slip, threshold)):
        warnings.warn("The effort may be infinite",  RuntimeWarning)

    # correct:
    p_c_given_pk = guess * (1 - k0) + (1 - slip) * k0
    p_c_pLnext = (1 - k0) * learning_rate * guess + (1 - slip) * k0
    p_c_pnLnext = guess * (1 - learning_rate) * (1 - k0)
    ck0 = p_c_pLnext / (p_c_pLnext + p_c_pnLnext)

    # incorrect:
    p_w_pLnext = (1 - k0) * learning_rate * (1 - guess) + slip * k0
    p_w_pnLnext = (1 - k0) * (1 - learning_rate) * (1 - guess) + 0
    wk0 = p_w_pLnext / (p_w_pLnext + p_w_pnLnext)

    if t > T:
        if n == 0: #not already_stop:
            out = 0
            students = 0
            effort = T
        else:
            out = outcome * p_sequence/n

            students = p_sequence
        return (effort * p_sequence, out, students)
    elif already_stop or p_c_given_pk > threshold:
        if  already_stop: #instruction would have been stopped
            outcome += 0 if (dummy == "") else (dummy[-1] == "1") # outcome += 1 <-- should add to T
            n += 1
        else: # first time instruction is stopped
            effort = t
            already_stop = True



    (ec, oc, sc) = generate_all_sequences(ck0, learning_rate, guess, slip, threshold, T, t + 1, p_c_given_pk * p_sequence, already_stop, effort, outcome, n,dummy + "1")
    (ew, ow, sw) = generate_all_sequences(wk0, learning_rate, guess, slip, threshold, T, t + 1, (1 - p_c_given_pk) * p_sequence, already_stop, effort, outcome, n, dummy + "0")
    return (ec+ew, oc+ow, sc+sw)




def expOppNeed(pL, pT, pG, pS, threshold, p_path=1, eita=0.0001, length=0, use_pL_to_judge_mastery=False):#0.0000001):
    verbose=True
    maximum_length = 50

    length += 1
    p_c_given_pL = pG * (1 - pL) + (1 - pS) * pL #not p(C|K)!

    if verbose:
        print("{}\tp_path: {:.2f},  pL:{:.2f}, pC:{:.2f}".format( length, p_path, pL, p_c_given_pL))

    # Stopping conditions:
    if (p_path < eita) or (maximum_length > 0 and length >= maximum_length):  # simulation has gone too long
        if verbose:
            print(length, "\tend 0")
        return 0
    elif (use_pL_to_judge_mastery and pL >= threshold) or ( not use_pL_to_judge_mastery and p_c_given_pL >= threshold): # mastery reached
        if verbose:
            print(length, "\tend 1")
        return 1

    # Continue:
    #p_c_pLnext = (1 - pS) * (pL + pT * (1 - pL))
    p_c_pLnext = (1-pL)*pT*pG + (1-pS)*pL
    p_c_pnLnext = pG * (1 - pT) * (1 - pL)
    p_Lnext_given_c = p_c_pLnext / (p_c_pLnext + p_c_pnLnext)
    p_path_c = p_path * p_c_given_pL
    #p_path_c =  p_c_given_pL

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
    #p_path_w =   p_w_given_pL
    EO_w = expOppNeed(p_Lnext_given_w, pT, pG, pS, threshold, p_path=p_path_w, length=length)

    effort = (1 + p_c_given_pL *EO_c + p_w_given_pL * EO_w)#(1 + p_c_given_pL*EO_c*flag + p_w_given_pL * EO_w* flag)
    if verbose:
        print("*  {}  {:.3f}  {:.3f}  | {}".format(length, pL, p_c_given_pL, effort))
    return effort

def prepare_arrays(k0, learning_rate, guess, slip, forget):

    transmat     = OrderedDict()
    emissionprob = OrderedDict()
    startprob    = OrderedDict()

    transmat[novice] = OrderedDict()
    transmat[master] = OrderedDict()
    transmat[novice][novice]    = 1- learning_rate
    transmat[novice][master]     = learning_rate
    transmat[master][novice] = forget
    transmat[master][master]  = 1-forget

    emissionprob[novice] = OrderedDict()
    emissionprob[master] = OrderedDict()
    emissionprob[novice][incorrect]  = 1-guess
    emissionprob[novice][correct]    = guess
    emissionprob[master][incorrect]  = slip
    emissionprob[master][correct]    = 1-slip

    startprob[novice] = 1 - k0
    startprob[master] = k0


    return transmat, emissionprob, startprob


def effort_threshold (k0, learning_rate, guess, slip, pcorrect):
    A = (1 - slip - guess) * (1 - k0)
    base = ( 1 - learning_rate  )

    eps = 1e-5

    if abs(A)  <= eps:
        return float('NaN')
    elif abs(base) <= eps:
        return float('NaN')

    numerator = (- pcorrect + 1 - slip ) /  A

    if numerator <0 + eps:
        return float('NaN')

    return np.log( numerator  ) / np.log( base )


def main():
    sequence_length = 5

    k0 = 0.3
    l = 0.25
    g = 0.3
    s = 0.3
    # theoretical_effort(k0=k0, learning_rate=l, guess=g, slip=s, threshold= 0.6)
    print(generate_all_sequences(k0=k0, learning_rate=l, guess=g, slip=s, threshold=0.9, T=10))



    #expOppNeed(pL=k0, pT=l, pG=g, pS=s, threshold=0.6)
    #print effort(k0, learning_rate=l, guess=g, slip=s, threshold=0.6)

    #forward_synthetic(t=5, k0=k0, learning_rate=l, guess=g, slip=s)

    #xs = np.arange(0,  sequence_length)
    #tcorrect = theoretical_pcorrect(k0=k0, learning_rate=l, guess=g, slip=s, j=xs)
    #tmastery = theoretical_mastery(k0=k0, learning_rate=l, j=xs)

    #print tcorrect


if __name__ == "__main__":
    import sys

    args = sys.argv
    print(args)
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

