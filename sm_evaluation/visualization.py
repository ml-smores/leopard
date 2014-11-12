__author__ = 'ugonzjo'

from matplotlib import pyplot as pl, pyplot, cm, colors
from scipy import stats
import pandas as pd
from common import *


class WhiteVisualization():

    def __init__(self, white_obj):
        self.white_obj = white_obj

    def plot_by_threshold(self, type, figure_path="images/"):
        if type == "single" and self.white_obj.policy is not None: #plot each KC
            for kc in self.white_obj.policy.scores.keys():
                thresholds, scores, practices, _, _ = self.get_after_integral_lower_bound(self.white_obj.policy.thresholds[kc], self.white_obj.policy.scores[kc], self.white_obj.policy.practices[kc])
                self.plot_component_relation(kc, thresholds, scores, figure_path, "threshold", "score", [0, 1], [0, 1])
                self.plot_component_relation(kc, thresholds, practices, figure_path, "threshold", "effort", [0, 1], [0, max(practices)])
                self.plot_component_relation(kc, practices, scores, figure_path, "effort", "score", [0, max(practices)], [0,1])
        elif type == "multiple" and self.white_obj.policy is not None: #plot multiple kcs in one figure
            fig1 = pl.figure(1)
            fig2 = pl.figure(2)
            fig3 = pl.figure(3)
            labels = []
            for kc in self.white_obj.policy.scores.keys():
                thresholds, scores, practices, _, _ = self.get_after_integral_lower_bound(self.white_obj.policy.thresholds[kc], self.white_obj.policy.scores[kc], self.white_obj.policy.practices[kc])
                color = "green" if "easy" in kc else ("yellow" if "medium" in kc else "red")
                legend = ""
                label = "easy" if "easy" in kc else ("medium" if "medium" in kc else "hard")
                if label not in labels:
                    legend = label
                    labels.append(legend)
                pl.figure(1)
                fig1 = self.plot_component_relation(kc, thresholds, scores, figure_path, "threshold", "score", [self.white_obj.integral_lower_bound, 1], [0, 1], linewidth=1, ycolor=color, label=legend, dotsize=10, figure=fig1)
                pl.figure(2)
                fig2 = self.plot_component_relation(kc, thresholds, practices, figure_path, "threshold", "effort", [self.white_obj.integral_lower_bound, 1], [0, max(practices)], linewidth=1, ycolor=color, label=legend, dotsize=10, figure=fig2)
                pl.figure(3)
                fig3 = self.plot_component_relation(kc, practices, scores, figure_path, "effort", "score", [0, max(practices)], [0,1], linewidth=1, ycolor=color, label=legend, dotsize=10, figure=fig3)
            pl.figure(1)
            pl.savefig(figure_path + "score_threshold_multiple.png")
            pl.figure(2)
            pl.savefig(figure_path + "effort_threshold_multiple.png")
            pl.figure(3)
            pl.savefig(figure_path + "score_effort_multiple.png")
        elif type == "all" and self.white_obj.thresholds is not None: #plot for all KCs
            thresholds, scores, practices, ratios, students = self.get_after_integral_lower_bound(self.white_obj.thresholds, self.white_obj.scores, self.white_obj.practices, self.white_obj.ratios, self.white_obj.students)
            nb_kcs = len(self.white_obj.kcs)
            self.plot_component_relation("all", thresholds, scores, figure_path, "threshold", "score", [self.white_obj.integral_lower_bound, 1], nb_students=students, nb_kcs=nb_kcs) #[0, 1],
            self.plot_component_relation("all", thresholds, practices, figure_path, "threshold", "effort", [self.white_obj.integral_lower_bound, 1], nb_students=students, nb_kcs=nb_kcs) #[0, max(practices)],
            self.plot_component_relation("all", practices, scores, figure_path, "effort", "score", nb_students=students, nb_kcs=nb_kcs) #[0, max(practices)], [0,1],
            self.plot_component_relation("all", thresholds, ratios, figure_path, "threshold", "score/effort", [self.white_obj.integral_lower_bound, 1], [0, max(ratios)], nb_students=students, nb_kcs=nb_kcs) #
            self.plot_component_relation("all", thresholds, students, figure_path, "threshold", "students", [self.white_obj.integral_lower_bound, 1], nb_students=students, nb_kcs=nb_kcs) #
        else:
            print "ERROR: Please reconfigure!"
            exit(-1)

    # def graph_path(self, white_objs, threshold=None):
    def plot_by_practice(self, white_objs, threshold=None):
        ''' white_objs is a list of sm_evaluation objects... it may only have a single object
           x=kc, y=practice, dot size=students, dot color=score
           this should save the image to file
        '''
        if threshold == None:
            # draw path for aggregated
            for white in white_objs:
                pass
        else:
            # draw a single path
            pass


    def plot_component_relation(self, kc, x, y, figure_path, xlabel, ylabel,
                                xlim=None, ylim=None, linewidth=3, ycolor="black", label=None, dotsize=20,
                                figure=None, axis=None, nb_students=None, perkc_stu_thd = 30, nb_kcs=None):
        if figure is None:
            fig, ax = pl.subplots()
        else:
            fig = figure
        if nb_students is not None:
            x = [x[i] for i, v in enumerate(nb_students) if v > 0]#30 #250
            y = [y[i] for i, v in enumerate(nb_students) if v > 0]#30 #250
            dot_color = [ycolor] * len(y)
            if nb_kcs is not None:
                perkc_stu_thd *= nb_kcs
            for pos in range(len(y)):
                if nb_students[pos] < perkc_stu_thd:
                    dot_color[pos] = "lightgrey"
            #todo: add sizes correspond to #students
        fig.subplots_adjust(bottom=0.15)
        pl.scatter(x, y, color=dot_color, s=dotsize)
        # if label is None:
        #     pl.step(x, y, color=dot_color, linewidth=linewidth)
        # else:
        #     pl.step(x, y, color=dot_color, linewidth=linewidth, label=label)
        #     pl.legend(loc="lower right", prop={'size':9}) #ncol=4,

        pl.ylabel(ylabel, fontsize=20)#ycolor
        pl.xlabel(xlabel, fontsize=20)
        pl.yticks(fontsize=18)
        pl.xticks(fontsize=18)
        if ylim is not None:
            pl.ylim(ylim)
        if xlim is not None:
            pl.xlim(xlim)
        if figure is None:
            pl.savefig(figure_path + (ylabel.replace("/", "_over_") + "_" + xlabel + "_{}.pdf").format(kc))
            pl.close(fig)
        return fig


    @staticmethod
    def plot_auc_vs_white(white_objs, aucs, outfile):
        auc_list = []
        score_students_list = []
        effort_list = []
        ratio_list = []
        kc_list = []
        for pos in range(len(white_objs)):
            white_obj = white_objs[pos]
            auc_list.append(aucs[pos])#white_obj.standard_metrics["auc"])
            score_students_list.append(white_obj.score_students)#white_obj.ratio_all)
            effort_list.append(white_obj.effort)
            ratio_list.append(white_obj.ratio)
            kc_list.append("_".join(white_obj.detail.keys()))#white_obj.kcs))
        xs = [score_students_list, effort_list, ratio_list]
        ys = [auc_list] * 3
        titles = ["score", "effort", "ratio"]

        for pos in range(len(xs)):
            x = xs[pos]
            y = ys[pos]
            title = titles[pos]
            print pretty(x), pretty(y), "\n"
            df = pd.DataFrame({"kcs":kc_list, title:x, "auc":y}) #"sm_evaluation":white_list
            df.to_csv("example_data/synthetic_data_auc_vs_" + title + ".csv")

            correlation, correlation_pval = stats.spearmanr(x, y)
            correlation_str = "Spearman correlation : {:4.2f}".format(correlation) + ", p-value:{:5.3f}".format(correlation_pval)

            fig, ax = pl.subplots()
            fig.subplots_adjust(bottom=0.15)
            pl.scatter(x, y, s=20)#, label=correlation_str)
            #pl.plot(x, y, linewidth=3, label=correlation_str)
            #pl.legend(loc="upper right", prop={'size':15}) #ncol=4,
            pl.title(correlation_str, fontsize=20)
            pl.ylabel("AUC", fontsize=20)#ycolor
            pl.xlabel(title, fontsize=20)
            pl.yticks(fontsize=18)
            pl.xticks(fontsize=18)
            pl.savefig(outfile.format(title))
            pl.close(fig)


    def get_after_integral_lower_bound(self, thresholds, scores, practices, ratios=None, students=None):
        if self.white_obj.integral_lower_bound > 0.0:
            threshold_pos = next(i for i, v in enumerate(thresholds) if v > self.white_obj.integral_lower_bound)
            thresholds = thresholds[threshold_pos:]
            scores = scores[threshold_pos:]
            practices = practices[threshold_pos:]
            if ratios is not None:
                ratios = ratios[threshold_pos:]
            if students is not None:
                students = students[threshold_pos:]
        return thresholds, scores, practices, ratios, students