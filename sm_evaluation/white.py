
class White:
    def __init__(self, policy):
        self.policy = policy
        self.detail = {}
        self.effort = 0
        self.score_students = 0
        self.mastery = 0.0
        self.mastery_pct = 0.0

        self.score_kcs = 0
        self.effort_filled = 0
        self.evaluate()
        #self.ratio = 0


    def __repr__(self):
        ans = ""
        for k, v in self.detail.items():
            mastery_pct =  v["mastery%"]
            score =  v["score"]

            score_student = v["score_student"]["mean"]
            effort =  v["effort"]["mean"]
            ans += "{} : {:.2f} ({:.2f}) {:2f}   {:.2f}\n".format(k, score_student, score, effort, mastery_pct)

        ans += "overall score: {:.2f} ".format(self.score_students) + "\noverall effort: {:.2f} ".format(self.effort)
        return ans

    def evaluate(self, fill_missing=True):
        df = self.policy.simulate()
        df_kcs = df.groupby("id")

        # score_student_list = []
        # effort_list = []
        for g, df_kc in df_kcs: #g is a kc
            self.detail[g] = {}

            # Fill missing values (that occur when a student doesn't have transitions)
            if fill_missing:
                # On NIPS paper we did this:
                for c in df_kc.columns:
                    if "_pre" in c:
                        opposite = c.replace("_pre", "_pos")
                    else:
                        opposite = c.replace("_pos", "_pre")
                    df_kc[c] = df_kc[c].fillna(value= df_kc[opposite])
                #Alternative way for filling missing values
                #df_kc["effort_pos"] = df_kc["effort_pos"].fillna(df_kc["effort_pre"])
                #df_kc["correct_pos"] = df_kc["correct_pos"].fillna(0)
                #df_kc["n_pos"] = df_kc["n_pos"].fillna(0)


            # Store individual values:
            self.detail[g]["mastery"]  = sum(df_kc["mastered"] == True)
            self.detail[g]["mastery%"] = sum(df_kc["mastered"] == True) / (len(df_kc) + .0)
            self.detail[g]["effort"] =  df_kc["effort_pos"].describe()
            self.detail[g]["score_student"] =  (df_kc["correct_pos"] / df_kc["n_pos"]).describe()

            self.detail[g]["score"] =  df_kc["correct_pos"].sum() / df_kc["n_pos"].sum()

            # Store aggregate values:
            self.score_students += self.detail[g]["score_student"]["mean"]
            self.effort += self.detail[g]["effort"]["mean"]
            self.mastery += self.detail[g]["mastery"]
            self.mastery_pct += self.detail[g]["mastery%"]

        self.score_students /= len(df_kcs)
        self.mastery /= len(df_kcs)
        self.mastery_pct /= len(df_kcs)


