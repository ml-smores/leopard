import numpy as np
import scipy
#import scikits.bootstrap as bootstrap
import pandas as pd

# boostrap confidence interval:
# https://scikits.appspot.com/bootstrap (homepage: https://github.com/cgevans/scikits-bootstrap/blob/master/scikits/bootstrap/bootstrap.py)
# example: http://www.randalolson.com/2012/08/06/statistical-analysis-made-easy-in-python/
# Currently hy uses per student on all kcs' effort (score) as a datapoint to do bootstrap for mean estimation;
# TODO: think about how to keep per kc perspective to do bootstrap

class White:
    def __init__(self, policy, compute_ci=False):
        self.policy = policy
        self.detail = {}
        self.effort = 0
        self.score_students = 0
        self.mastery = 0.0
        self.mastery_pct = 0.0

        self.compute_ci = compute_ci
        self.score_kcs = 0
        self.effort_filled = 0
        if compute_ci:
            self.score_ci = [float('nan')] * 2
            self.effort_ci = [float('nan')] * 2
            self.effort_filled_ci = [float('nan')] * 2
            self.evaluate_by_stu()
        else:
            self.evaluate()
        #self.ratio = 0


    def __repr__(self):
        ans = ""
        for k, v in self.detail.items():
            mastery_pct =  v["mastery%"]
            score =  v["score"]
            if not self.compute_ci:#"score_student" in v.keys():
                score_student = v["score_student"]["mean"]
                effort =  v["effort"]["mean"]
                ans += "{} : {:.2f} ({:.2f}) {:2f}   {:.2f}\n".format(k, score_student, score, effort, mastery_pct)
            else:
                score_kc =  v["score_kc"]["mean"]
                effort =  v["effort"]
                effort_filled = v["effort_filled"]
                ans += "{} : {:.2f} ({:.2f}) {:2f} ({:.2f})  {:.2f}\n".format(k, score_kc, score, effort, effort_filled,  mastery_pct)
        if not self.compute_ci:#"score_student" in v.keys():
            ans += "overall score: {:.2f} ".format(self.score_students) + "\noverall effort: {:.2f} ".format(self.effort)
        else:
            ans += "overall score: {:.3f} ".format(self.score_kcs) + ("95% CI: [{:.3f}, {:.3f}]".format(self.score_ci[0], self.score_ci[1])) +\
                 "\noverall effort: {:.3f} ".format(self.effort) + ("95% CI: [{:.3f}, {:.3f}]".format(self.effort_ci[0], self.effort_ci[1])) +\
                 "\noverall effort(filled): {:.3f} ".format(self.effort_filled) + ("95% CI: [{:.3f}, {:.3f}]".format(self.effort_filled_ci[0], self.effort_filled_ci[1]))# if self.compute_ci else "")
        return ans

    def evaluate(self):
        df = self.policy.simulate()
        df_kcs = df.groupby("id")

        # score_student_list = []
        # effort_list = []
        for g, df_kc in df_kcs: #g is a kc
            self.detail[g] = {}

            # Fill missing values (that occur when a student doesn't have transitions)
            for c in df_kc.columns:
                if "_pre" in c:
                    opposite = c.replace("_pre", "_pos")
                else:
                    opposite = c.replace("_pos", "_pre")
                df_kc[c] = df_kc[c].fillna(value= df_kc[opposite])

            # Store individual values:
            #print df_kc
            self.detail[g]["mastery"]  = sum(df_kc["mastered"] == True)
            self.detail[g]["mastery%"] = sum(df_kc["mastered"] == True) / (len(df_kc) + .0)
            self.detail[g]["effort"] =  df_kc["effort_pos"].describe()
            self.detail[g]["score_student"] =  (df_kc["correct_pos"] / df_kc["n_pos"]).describe()
            self.detail[g]["score"] =  df_kc["correct_pos"].sum() / df_kc["n_pos"].sum()
            #score_student_list = (df_kc["correct_pos"] / df_kc["n_pos"]).tolist()
            #effort_list = df_kc["effort_pos"].tolist()

            # Store aggregate values:
            self.score_students += self.detail[g]["score_student"]["mean"]
            self.effort += self.detail[g]["effort"]["mean"]
            self.mastery += self.detail[g]["mastery"]
            self.mastery_pct += self.detail[g]["mastery%"]

        self.score_students /= len(df_kcs)
        self.mastery /= len(df_kcs)
        self.mastery_pct /= len(df_kcs)
        #self.ratio = self.effort / self.score_students

        #print score_student_list, effort_list
        # compute confidence intervals around the mean, default  95% , 10000 samples
        # cis = bootstrap.ci(data=score_student_list, statfunction=scipy.mean) #, alpha=0.2, n_samples=20000)
        # self.score_ci  = cis
        # print "Bootstrapped 95% confidence intervals\nLow:", cis[0], "\nHigh:", cis[1]
        # cis = bootstrap.ci(data=effort_list, statfunction=scipy.mean) #, alpha=0.2, n_samples=20000)
        # self.effort_ci  = cis
        # print "Bootstrapped 95% confidence intervals\nLow:", ci[0], "\nHigh:", ci[1]

    def evaluate_by_stu(self):
        df = self.policy.simulate()
        df["kc"] = df.index
        df_stus = df.groupby("id")

        score_list = []
        effort_list = []
        effort_filled_list = []
        for g, df_stu in df_stus:
            self.detail[g] = {}

            # Fill missing values (that occur when a student doesn't have transitions)
            for c in df_stu.columns:
                if "_pre" in c:
                    opposite = c.replace("_pre", "_pos")
                else:
                    opposite = c.replace("_pos", "_pre")
                df_stu[c] = df_stu[c].fillna(value= df_stu[opposite])

            #print g, "\n", df_stu
            # Store individual values:
            self.detail[g]["mastery"]  = sum(df_stu["mastered"] == True)
            self.detail[g]["mastery%"] = sum(df_stu["mastered"] == True) / (len(df_stu) + .0)
            #TODO: describe
            self.detail[g]["effort"] =  df_stu["effort_pos"].sum() #TODO: only one number to be described. another format of __repr__?
            self.detail[g]["effort_filled"] =  (self.detail[g]["effort"] / (df_stu["kc"].nunique() * 1.0)) * df["kc"].nunique()
            self.detail[g]["score_kc"] =  (df_stu["correct_pos"] / df_stu["n_pos"]).describe()
            self.detail[g]["score"] =  df_stu["correct_pos"].sum() / df_stu["n_pos"].sum() #TODO: consider change name; now this one is consistent with effort

            # Store aggregate values:
            self.score_kcs += self.detail[g]["score_kc"]["mean"]#TODO: only one number to be described. consider using score_kcs
            self.effort += self.detail[g]["effort"] #TODO: only one number to be described.
            self.effort_filled += self.detail[g]["effort_filled"]
            score_list.append(self.detail[g]["score_kc"]["mean"])
            effort_list.append(self.detail[g]["effort"])
            effort_filled_list.append(self.detail[g]["effort_filled"])

        self.score_kcs /= len(df_stus) #TODO: consider using score_kcs
        self.effort /= len(df_stus)
        self.effort_filled /= len(df_stus)

        df_bootstrap = pd.DataFrame({"score":score_list, "effort":effort_list, "effort_filled": effort_filled_list})
        df_bootstrap.to_csv("../example_data/tdx_bootstrap_input.csv")
        #compute confidence intervals around the mean, default  95% , 10000 samples
        cis = bootstrap.ci(data=score_list, statfunction=scipy.mean) #, alpha=0.2, n_samples=20000)
        self.score_ci  = cis
        print "Bootstrapped 95% confidence intervals\nLow:", cis[0], "\nHigh:", cis[1]
        cis_effort = bootstrap.ci(data=effort_list, statfunction=scipy.mean) #, alpha=0.2, n_samples=20000)
        self.effort_ci  = cis_effort
        print "Bootstrapped 95% confidence intervals\nLow:", cis_effort[0], "\nHigh:", cis_effort[1]
        cis_effort_filled = bootstrap.ci(data=effort_filled_list, statfunction=scipy.mean) #, alpha=0.2, n_samples=20000)
        self.effort_filled_ci  = cis_effort_filled
        print "Bootstrapped 95% confidence intervals\nLow:", cis_effort_filled[0], "\nHigh:", cis_effort_filled[1]








