import numpy as np



class White:
    def __init__(self, policy):
        self.policy = policy

    def evaluate(self, minimum=0):
        df = self.policy.simulate()
        df_kcs = df.groupby("id")

        white = {}
        for g, df_kc in df_kcs:
            #print df_kc
            #print df_kc["pre_effort"].describe()
            #print df_kc["pos_effort"].describe()

            white[g] = {}

            pre_score =  (df_kc["pre_correct"] / df_kc["pre_n"]).describe()
            white[g]["pre_score"]  = pre_score["mean"]

            pos_score = (df_kc["pos_correct"] / df_kc["pos_n"]).describe()
            if pos_score["count"] >= minimum:
                white[g]["pos_score"]  = pos_score["mean"]
            else:
                white[g]["pos_score"] = pre_score["mean"]


            pos_effort = df_kc["pos_effort"].describe()
            white[g]["pos_effort"] = pos_effort["mean"]



        return white





