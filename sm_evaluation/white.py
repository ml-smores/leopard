import numpy as np



class White:
    def __init__(self, policy):
        self.policy = policy
        self.detail = {}
        self.effort = 0
        self.score_students = 0
        self.ratio = 0
        self.evaluate()



    def __repr__(self):
        ans = ""
        for k, v in self.detail.items():
            score_student = v["score_student"]["mean"]
            effort =  v["effort"]["mean"]
            mastery_pct =  v["mastery%"]
            score =  v["score"]
            ans += "{} : {:.2f}  ({:.2f}) {:2f}   {:.2f}\n".format(k, score_student, score, effort, mastery_pct)
        ans += "{:.2f}  {:.2f}".format(self.score_students, self.effort)
        return ans

    def evaluate(self):
        df = self.policy.simulate()
        df_kcs = df.groupby("id")


        for g, df_kc in df_kcs:
            self.detail[g] = {}

            # Fill missing values (that occur when a student doesn't have transitions)
            for c in df_kc.columns:
                if "_pre" in c:
                    opposite = c.replace("_pre", "_pos")
                else:
                    opposite = c.replace("_pos", "_pre")
                df_kc[c] = df_kc[c].fillna(value= df_kc[opposite])


            # Store individual values:
            self.detail[g]["mastery"]  = sum(df_kc["mastered"] == True)
            self.detail[g]["mastery%"] = sum(df_kc["mastered"] == True) / (len(df_kc) + .0)
            self.detail[g]["effort"] =  df_kc["effort_pos"].describe()
            self.detail[g]["score_student"] =  (df_kc["correct_pos"] / df_kc["n_pos"]).describe()
            self.detail[g]["score"] =  df_kc["correct_pos"].sum() / df_kc["n_pos"].sum()

            # Store aggregate values:
            self.score_students += self.detail[g]["score_student"]["mean"]
            self.effort += self.detail[g]["effort"]["mean"]

        self.score_students /= len(df_kcs)
        self.ratio = self.effort / self.score_students













