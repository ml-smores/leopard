__author__ = 'ugonzjo'

from matplotlib import pyplot as pl, pyplot, cm, colors
from scipy import stats
import pandas as pd
from common import *
import numpy as np


class WhiteVisualization():

    def __init__(self, white_obj):
        self.white_obj = white_obj

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


    @staticmethod
    def plot_auc_vs_white(white_objs, aucs, outfile, infile="", ylim=None):
        if white_objs is not None and aucs is not None:
            auc_list = []
            score_students_list = []
            effort_list = []
            #ratio_list = []
            kc_list = []
            for pos in range(len(white_objs)):
                white_obj = white_objs[pos]
                auc_list.append(aucs[pos])#white_obj.standard_metrics["auc"])
                score_students_list.append(white_obj.score_students)#white_obj.ratio_all)
                effort_list.append(white_obj.effort)
                #ratio_list.append(white_obj.ratio)
                kc_list.append("_".join(white_obj.detail.keys()))#white_obj.kcs))
        else:
            df = pd.read_csv(infile)
            if "score" in df.columns:
                score_students_list = df["score"].tolist()
            else:
                score_students_list = df["score_student"].tolist()
            effort_list = df["effort"].tolist()
            auc_list = df["auc"].tolist()
        xs = [score_students_list, effort_list]#, ratio_list]
        ys = [auc_list] * 2
        titles = ["score", "effort"]#, "ratio"]

        for pos in range(len(xs)):
            x = xs[pos]
            y = ys[pos]
            title = titles[pos]
            #print pretty(x), pretty(y), "\n"

            correlation, correlation_pval = stats.spearmanr(x, y)
            correlation_str = "Spearman correlation : {:4.2f}".format(correlation) + ", p-value:{:5.3f}".format(correlation_pval)

            plot_scatterplot(x, y, title, "AUC",
                      file=outfile.format(title),
                      title="Spearman correlation=" + pretty(correlation) + " (p-value=" + pretty(correlation_pval) + ")", ylim=ylim)

    @staticmethod
    def plot_histogram(white_objs, aucs, outfile):
        auc_list = []
        score_students_list = []
        effort_list = []
        kc_list = []
        for pos in range(len(white_objs)):
            white_obj = white_objs[pos]
            auc_list.append(aucs[pos])#white_obj.standard_metrics["auc"])
            score_students_list.append(white_obj.score_students)#white_obj.ratio_all)
            effort_list.append(white_obj.effort)
            #ratio_list.append(white_obj.ratio)
            kc_list.append("_".join(white_obj.detail.keys()))#white_obj.kcs))
        xs = [score_students_list, effort_list, auc_list]
        titles = ["score", "effort", "auc"]#, "ratio"]

        for pos in range(len(xs)):
            list_values = xs[pos]
            title = titles[pos]
            df = pd.DataFrame({"kcs":kc_list, title:list_values}) #"sm_evaluation":white_list
            df.to_csv("../example_data/synthetic_data_" + title + ".csv")

            print "*** Plotting histagram for", title, " *** "
            fig, ax = pl.subplots()
            max_ = max(list_values)
            min_ = min(list_values)
            nb_bins = 20
            bin_size = ( max_ - min_ ) / nb_bins
            print "max=", max_, "\tmin=", min_, "\t#bins=", nb_bins, "\tbin_size=", bin_size
            fig.subplots_adjust(bottom=0.1)
            bins=np.arange(int(min_), max_+bin_size, bin_size)
            ax.hist(list_values, bins=bins)  #, align='left')
            pl.xlim([min_, max_])
            pl.xticks(bins, rotation=30)#, fontsize=xtick_size)
            pl.title(title, fontsize=18)
            pl.xlabel(title, fontsize=18)
            pl.ylabel("#datasets", fontsize=18)
            pl.savefig(outfile.format(title))
            pl.close("all")

    @staticmethod
    def plot_barchart(names, values, xlabel, ylabel, file=None, figure_size=None, xtick_step=None, ytick_size=6.5, comparison_line=None, to_sort=False, nstu=None):
        #for sorting
        if to_sort:
            sorted_points = sorted(zip(values, names))
            values = [point[0] for point in sorted_points]
            names = [point[1] for point in sorted_points]
        fig, ax = pl.subplots()
        fig = pl.gcf()
        if figure_size is not None:
            fig.set_size_inches(figure_size[0],figure_size[1])
        # Move the edge of an axes to make room for tick labels
        #fig.subplots_adjust(bottom=0.2)
        #fig.subplots_adjust(left=0.37)
        #fig.subplots_adjust(right=0.005)
        name_pos = np.arange(len(names))
        if comparison_line is None:
            comparison_line = np.mean(values)
        pl.axvline(x=comparison_line, color="red", linewidth=1)#, ymin, ymax
        if nstu is not None:
            ycolor_list = ["blue"] * len(values)
            for pos in range(len(values)):
                if nstu[pos] < 30:
                    ycolor_list[pos] = "lightgrey"
            barlist = ax.barh(name_pos, values, align="center", color=ycolor_list, edgecolor=ycolor_list)
        else:
            barlist = ax.barh(name_pos, values, align="center", color="blue", edgecolor="blue")
        pl.ylim([-1, len(names)])
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_xlabel(xlabel, fontsize=12)
        if xtick_step is not None:
            pl.xticks(np.arange(0, max(values) + xtick_step, xtick_step), fontsize=10, rotation=30)
        pl.yticks(name_pos, names, fontsize=ytick_size)
        ax.xaxis.grid(True, linestyle='-', which='major', color='lightgrey',alpha=0.5)
        pl.savefig(file)
        pl.close('all')

    @staticmethod
    def plot_white_distribution_across_kcs(white_obj, file):
        kc_list = []
        score_student_list = []
        effort_list = []
        for k, v in white_obj.detail.items():
            kc_list.append(k)
            score_student_list.append(v["score_student"]["mean"])
            effort_list.append(v["effort"]["mean"])
        WhiteVisualization.plot_barchart(kc_list, score_student_list, "score", "KC", "../images/" + file.format("score"), ytick_size=8.5)
        WhiteVisualization.plot_barchart(kc_list, effort_list, "effort", "KC", "../images/" + file.format("effort"), ytick_size=8.5)

    @staticmethod
    def plot_component_relation(kc, x, y, figure_path, xlabel, ylabel,
                                xlim=None, ylim=None, linewidth=3, ycolor="black", label=None, dotsize=20,
                                figure=None, axis=None, nb_students=None, perkc_stu_thd = 30,
                                nb_kcs=None, tick_size=20, label_size=25, regress=False, legend=""):
        if figure is None:
            fig, ax = pl.subplots()
        else:
            fig = figure
        dot_color = None
        if nb_students is not None:
            x = [x[i] for i, v in enumerate(nb_students) if v > 0]#30 #250
            y = [y[i] for i, v in enumerate(nb_students) if v > 0]#30 #250
            dot_color = [ycolor] * len(y)
            dotsize = [dotsize] * len(y)
            if nb_kcs is not None:
                perkc_stu_thd *= nb_kcs
            for pos in range(len(y)):
                if nb_students[pos] < perkc_stu_thd:
                    dot_color[pos] = "lightgrey"
                    dotsize[pos] = 0.3 * dotsize[pos]
            #todo: add sizes correspond to #students
        fig.subplots_adjust(left=0.15, bottom=0.15)

        if regress:
            slope, intercept, r_value, slope_pval, std_err = stats.linregress(x, y)
            fit_fn = np.poly1d([slope, intercept])
            legend = legend + ", slope=" + "{:4.3f}".format(slope) + "(p=" + pretty(slope_pval) + ")"
            pl.plot(x, fit_fn(x), color="grey", linestyle="-", linewidth=1) #color='k', linestyle='--', linewidth=0.01
        if dot_color is not None:
            pl.scatter(x, y, color=dot_color, s=dotsize, alpha = 0.5, label=legend)
        else:
            pl.scatter(x, y, s=dotsize, color=ycolor, alpha = 0.5, label=legend)
        pl.legend(loc='upper left', prop={'size':12})

            #current_slope = {pct : ["{:4.2f}".format(slope), "{:5.3f}".format(slope_pval)]}
        # if label is None:
        #     pl.step(x, y, color=dot_color, linewidth=linewidth)
        # else:
        #     pl.step(x, y, color=dot_color, linewidth=linewidth, label=label)
        #     pl.legend(loc="lower right", prop={'size':9}) #ncol=4,

        pl.ylabel(ylabel, fontsize=label_size)#ycolor
        pl.xlabel(xlabel, fontsize=label_size)
        pl.yticks(fontsize=tick_size)
        pl.xticks(fontsize=tick_size, rotation=30)

        if xlim is not None:
            pl.xlim(xlim)
        elif xlabel == "effort":
            pl.xlim([-1, max(x)+1])
        if ylim is not None:
            pl.ylim(ylim)
        elif ylabel == "score":
            pl.ylim([min(y)-0.001, max(y)+0.002])

        if figure is None:
            out_file = figure_path + (ylabel.replace("/", "_over_") + "_" + xlabel + "_{}.pdf").format(kc)
            print "outputting to ", out_file
            pl.savefig(out_file)
            pl.close(fig)
        return fig

    def plot_by_threshold(self, type, figure_path="images/"):
        if type == "single" and self.white_obj.policy is not None: #plot each KC
            for kc in self.white_obj.policy.scores.keys():
                thresholds, scores, practices, _, _ = self.get_after_integral_lower_bound(self.white_obj.policy.thresholds[kc], self.white_obj.policy.scores[kc], self.white_obj.policy.practices[kc])
                plot_component_relation(kc, thresholds, scores, figure_path, "threshold", "score", [0, 1], [0, 1])
                plot_component_relation(kc, thresholds, practices, figure_path, "threshold", "effort", [0, 1], [0, max(practices)])
                plot_component_relation(kc, practices, scores, figure_path, "effort", "score", [0, max(practices)], [0,1])
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
                fig1 = plot_component_relation(kc, thresholds, scores, figure_path, "threshold", "score", [self.white_obj.integral_lower_bound, 1], [0, 1], linewidth=1, ycolor=color, label=legend, dotsize=10, figure=fig1)
                pl.figure(2)
                fig2 = plot_component_relation(kc, thresholds, practices, figure_path, "threshold", "effort", [self.white_obj.integral_lower_bound, 1], [0, max(practices)], linewidth=1, ycolor=color, label=legend, dotsize=10, figure=fig2)
                pl.figure(3)
                fig3 = plot_component_relation(kc, practices, scores, figure_path, "effort", "score", [0, max(practices)], [0,1], linewidth=1, ycolor=color, label=legend, dotsize=10, figure=fig3)
            pl.figure(1)
            pl.savefig(figure_path + "score_threshold_multiple.png")
            pl.figure(2)
            pl.savefig(figure_path + "effort_threshold_multiple.png")
            pl.figure(3)
            pl.savefig(figure_path + "score_effort_multiple.png")
        elif type == "all" and self.white_obj.thresholds is not None: #plot for all KCs
            thresholds, scores, practices, ratios, students = self.get_after_integral_lower_bound(self.white_obj.thresholds, self.white_obj.scores, self.white_obj.practices, self.white_obj.ratios, self.white_obj.students)
            nb_kcs = len(self.white_obj.kcs)
            plot_component_relation("all", practices, scores, figure_path, "effort", "score", nb_students=students, nb_kcs=nb_kcs) #[0, max(practices)], [0,1],
            plot_component_relation("all", thresholds, scores, figure_path, "threshold", "score", [self.white_obj.integral_lower_bound, 1], nb_students=students, nb_kcs=nb_kcs) #[0, 1],
            plot_component_relation("all", thresholds, practices, figure_path, "threshold", "effort", [self.white_obj.integral_lower_bound, 1], nb_students=students, nb_kcs=nb_kcs) #[0, max(practices)],
            plot_component_relation("all", thresholds, ratios, figure_path, "threshold", "score/effort", [self.white_obj.integral_lower_bound, 1], [0, max(ratios)], nb_students=students, nb_kcs=nb_kcs) #
            plot_component_relation("all", thresholds, students, figure_path, "threshold", "students", [self.white_obj.integral_lower_bound, 1], nb_students=students, nb_kcs=nb_kcs) #
        else:
            print "ERROR: Please reconfigure!"
            exit(-1)
    #
    # def get_after_integral_lower_bound(self, thresholds, scores, practices, ratios=None, students=None):
    #     if self.white_obj.integral_lower_bound > 0.0:
    #         threshold_pos = next(i for i, v in enumerate(thresholds) if v > self.white_obj.integral_lower_bound)
    #         thresholds = thresholds[threshold_pos:]
    #         scores = scores[threshold_pos:]
    #         practices = practices[threshold_pos:]
    #         if ratios is not None:
    #             ratios = ratios[threshold_pos:]
    #         if students is not None:
    #             students = students[threshold_pos:]
    #     return thresholds, scores, practices, ratios, students


def plot_histogram_from_file():
    outfile = "../images/" + exp_path + "synthetic_data_histogram_{}.pdf"
    df = pd.read_csv("../example_data/" + exp_path + "synthetic_data_auc_vs_score.csv")
    auc_list = df["auc"].tolist()
    score_students_list = df["score"].tolist()
    effort_list = df["effort"].tolist()
    xs = [score_students_list, effort_list, auc_list]
    titles = ["score", "effort", "auc"]#, "ratio"]

    for pos in range(len(xs)):
        list_values = xs[pos]
        title = titles[pos]

        print "*** Plotting histagram for", title, " *** "
        fig, ax = pl.subplots()
        max_ = max(list_values)
        min_ = min(list_values)
        nb_bins = 10
        bin_size = ( max_ - min_ ) / nb_bins
        print "max=", max_, "\tmin=", min_, "\t#bins=", nb_bins, "\tbin_size=", bin_size

        if title == "auc" or title == "score":
            min_ = round(min_, 2)
            max_ = round(max_, 2)
            bin_size = round(bin_size, 2)
        else:
            min_ = int(math.floor(min_))
            max_ = int(math.ceil(max_))
            bin_size = int(bin_size)

        print "max=", max_, "\tmin=", min_, "\t#bins=", nb_bins, "\tbin_size=", bin_size
        pl.xlim([min_, max_])
        fig.subplots_adjust(bottom=0.2)
        bins=np.arange(min_, max_+bin_size*1.1, bin_size)
        ax.hist(list_values, bins=bins)  #, align='left')
        pl.xticks(bins, rotation=30)#, fontsize=xtick_size)
        #pl.title(title, fontsize=18)
        pl.xlabel(title, fontsize=18)
        pl.ylabel("#datasets", fontsize=18)
        pl.savefig(outfile.format(title))
        pl.close("all")


def plot_scatterplot(x, y, xlabel, ylabel, file, title, ylim=None, label_size = 25, tick_size=20):
    fig, ax = pl.subplots()
    pl.scatter(x, y, color='black',alpha=0.6)#, label=legend)
    #pl.legend(loc='upper left', prop={'size':10})
    fig.subplots_adjust(bottom=0.18, left=0.15)
    pl.ylabel(ylabel, fontsize=label_size)#ycolor
    pl.xlabel(xlabel, fontsize=label_size)
    pl.title(title, fontsize=label_size)
    pl.xticks(fontsize=tick_size, rotation=30)
    pl.yticks(fontsize=tick_size)
    if ylim is not None:
        pl.ylim(ylim)

    # if not os.path.isdir(file):
    #     os.makedirs(file)
    pl.savefig(file)
    pl.close(fig)


#pl.legend(["empirical p(c)", "theoretical p(c)", "empirical p(k)", "theoretical p(k)"], loc='upper center', bbox_to_anchor=(0.5, -0.05),  ncol=2)
def plot_multiple_scatterplot_from_files(files, legends, colors, out_figure_path, chapter=100, linewidth=2, dotsize=20.0,
                              perkc_stu_thd = 30, tick_size=20, label_size=25, regress=False, ylim=None, xlim=None): #ylim=[0.38, 1.02], xlim=[0, 100]):
    fig, ax = pl.subplots()
    fig.subplots_adjust(left=0.15, bottom=0.20)
    if xlim is not None:
        pl.xlim(xlim)
    if ylim is not None:
        pl.ylim(ylim)
    xlabel = "effort"
    ylabel = "score"
    pl.ylabel(ylabel, fontsize=label_size)#ycolor
    pl.xlabel(xlabel, fontsize=label_size)
    pl.yticks(fontsize=tick_size)
    pl.xticks(fontsize=tick_size, rotation=30)
    for id in range(len(files)):
        file = files[id]
        legend = legends[id]
        ycolor = colors[id]
        df = pd.read_csv(file)
        if "score" in df.columns:
            score_str = "score"
        else:
            score_str = "score_student"
        # WhiteVisualization.plot_component_relation("all", df["effort"].tolist(), df[score_str].tolist(),
        #                     root_path + exp_path + "chapter" + str(chapter) + "_", "effort", "score",
        #                     nb_students=df["mean_mastery"], perkc_stu_thd = 30, ylim=[0.53, 0.68])
        kc = "all"
        x = df["effort"].tolist()
        y = df[score_str].tolist()
        dot_color = None
        perkc_stu_thd = 30
        if "mean_mastery" in df.columns:
            nb_students = df["mean_mastery"]
            x = [x[i] for i, v in enumerate(nb_students) if v > 0]#30 #250
            y = [y[i] for i, v in enumerate(nb_students) if v > 0]#30 #250
            dot_color = [ycolor] * len(y)
            dotsize_list = [dotsize] * len(y)
            for pos in range(len(y)):
                if nb_students[pos] < perkc_stu_thd:
                    dot_color[pos] = "lightgrey"
                    dotsize_list[pos] = 0.3 * dotsize_list[pos]
            #todo: add sizes correspond to #students
        if regress:
            slope, intercept, r_value, slope_pval, std_err = stats.linregress(x, y)
            fit_fn = np.poly1d([slope, intercept])
            #legend = legend + ", slope=" + "{:4.3f}".format(slope) + "(p=" + pretty(slope_pval) + ")"
            pl.plot(x, fit_fn(x), color="grey", linestyle="--", linewidth=linewidth) #color='k', linestyle='--', linewidth=0.01
        if dot_color is not None:
            pl.scatter(x, y, color=dot_color, s=dotsize, alpha = 0.4, label=legend)
        else:
            pl.scatter(x, y, s=dotsize, color=ycolor, alpha = 0.4, label=legend)
        pl.legend(prop={'size':12}, bbox_to_anchor=(1, 0.5))
        #pl.legend(["empirical p(c)", "theoretical p(c)", "empirical p(k)", "theoretical p(k)"],
        # loc='upper center', bbox_to_anchor=(0.5, -0.05),  ncol=2)

    out_file = out_figure_path + (ylabel.replace("/", "_over_") + "_" + xlabel + "_{}.pdf").format(kc)
    print "outputting to ", out_file
    pl.savefig(out_file)
    pl.close(fig)


#pl.legend(["empirical p(c)", "theoretical p(c)", "empirical p(k)", "theoretical p(k)"], loc='upper center', bbox_to_anchor=(0.5, -0.05),  ncol=2)
def plot_multiple_scatterplot(data, legends, colors, out_figure_path, chapter=100, linewidth=2, dotsize=20.0,
                              perkc_stu_thd = 30, tick_size=15, label_size=25, regress=False,
                              xlabel = "effort", ylabel = "score", yconstant=None, use_alpha=False, ylim=None, xlim=[0,10500]): #ylim=[0.38, 1.02], xlim=[0, 100],
    fig, ax = pl.subplots()
    fig.subplots_adjust(left=0.15, bottom=0.15)
    if xlim is not None:
        pl.xlim(xlim)
    if ylim is not None:
        pl.ylim(ylim)
    pl.ylabel(ylabel, fontsize=label_size)#ycolor
    pl.xlabel(xlabel, fontsize=label_size)
    pl.yticks(fontsize=tick_size)
    pl.xticks(fontsize=tick_size, rotation=15)
    for id in range(len(data)):
        legend = legends[id]
        ycolor = colors[id]
        df = data[id]
        if "score" in xlabel or "score" in ylabel:
            score_str = "score" if "score" in df.columns else "score_student"
        # WhiteVisualization.plot_component_relation("all", df["effort"].tolist(), df[score_str].tolist(),
        #                     root_path + exp_path + "chapter" + str(chapter) + "_", "effort", "score",
        #                     nb_students=df["mean_mastery"], perkc_stu_thd = 30, ylim=[0.53, 0.68])
        kc = "all"
        x = df[xlabel].tolist()
        y = df[ylabel].tolist()
        dot_color = None
        perkc_stu_thd = 30
        if "mean_mastery" in df.columns:
            nb_students = df["mean_mastery"]
            x = [x[i] for i, v in enumerate(nb_students) if v >= 0]#30 #250
            y = [y[i] for i, v in enumerate(nb_students) if v >= 0]#30 #250
            dot_color = [ycolor] * len(y)
            dotsize_list = [dotsize] * len(y)
            for pos in range(len(y)):
                if nb_students[pos] < perkc_stu_thd:
                    #dot_color[pos] = "lightgrey"
                    dotsize_list[pos] = 0.2 * dotsize_list[pos]
            #todo: add sizes correspond to #students
        if regress:
            slope, intercept, r_value, slope_pval, std_err = stats.linregress(x, y)
            fit_fn = np.poly1d([slope, intercept])
            #legend = legend + ", slope=" + "{:4.3f}".format(slope) + "(p=" + pretty(slope_pval) + ")"
            pl.plot(x, fit_fn(x), color=ycolor, linestyle="--", alpha=0.4, linewidth=linewidth) #color='k', linestyle='--', linewidth=0.01
        if dot_color is not None:
            pl.scatter(x, y, color=dot_color, s=dotsize_list, alpha = (0.4 if use_alpha else 1) , label=legend)
        else:
            pl.scatter(x, y, s=dotsize_list, color=ycolor, alpha = (0.4 if use_alpha else 1), label=legend)
        pl.legend(prop={'size':8}, loc="upper center", bbox_to_anchor=(0.5, 1.08), ncol=3)
        #pl.legend(["empirical p(c)", "theoretical p(c)", "empirical p(k)", "theoretical p(k)"],
        # loc='upper center', bbox_to_anchor=(0.5, -0.05),  ncol=2)
    if yconstant is not None:
        pl.axhline(y=yconstant, color="red", linewidth=1)#, ymin, ymax

    out_file = out_figure_path + (ylabel.replace("/", "_over_") + "_" + xlabel + "_{}.pdf").format(kc)
    print "outputting to ", out_file
    pl.savefig(out_file)
    pl.close(fig)


def main():
    path = "/Users/hy/inf/Study/CS/Projects_Codes_Data/Data/Data_white/"
    plot_multiple_scatterplot_from_files([path+"real_data/backup/obj_predictions_chapter1_white_varying_theshold.csv",
                               path+"synthetic_data/20kc_10prac_withlearning_GS0_2500stu/100_white_varying_theshold.csv",
                               path+"synthetic_data/20kc_20prac_withlearning_GS0_2500stu/100_white_varying_theshold.csv"],
                              legends=["real data", "with learning, short", "with learning, long"],
                              colors=["black", "blue", "green"],#, "magenta", "red"],
                              out_figure_path=path + "synthetic_data/",
                              regress=False)
    #path+"synthetic_data/20kc_10prac_withlearning_g0.6s0.4_2500stu/100_white_varying_theshold.csv", path+"synthetic_data/20kc_20prac_withlearning_g0.6s0.4_2500stu/100_white_varying_theshold.csv",
    #"high G+S short sequence", "high G+S long sequence",

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

