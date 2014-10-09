__author__ = 'ugonzjo'

from matplotlib import pyplot as pl, pyplot, cm, colors


class WhiteVisualization():

    def __init__(self, white_obj):
        self.white_obj = white_obj

    def plot_by_threshold(self, type, figure_path="images/"):
        if type == "single" and self.white_obj.policy is not None: #plot each KC
            for kc in self.white_obj.policy.grades.keys():
                thresholds = self.white_obj.policy.thresholds[kc]
                grades = self.white_obj.policy.grades[kc]
                practices = self.white_obj.policy.practices[kc]
                self.plot_component_relation(kc, thresholds, grades, figure_path, "threshold", "grade", [0, 1], [0, 1])
                self.plot_component_relation(kc, thresholds, practices, figure_path, "threshold", "practice", [0, 1], [0, max(practices)])
                self.plot_component_relation(kc, practices, grades, figure_path, "practice", "grade", [0, max(practices)], [0,1])
        elif type == "multiple" and self.white_obj.policy is not None: #plot multiple kcs in one figure
            fig1 = pl.figure(1)
            fig2 = pl.figure(2)
            fig3 = pl.figure(3)
            labels = []
            for kc in self.white_obj.policy.grades.keys():
                thresholds = self.white_obj.policy.thresholds[kc]
                grades = self.white_obj.policy.grades[kc]
                practices = self.white_obj.policy.practices[kc]
                color = "green" if "easy" in kc else ("yellow" if "medium" in kc else "red")
                legend = ""
                label = "easy" if "easy" in kc else ("medium" if "medium" in kc else "hard")
                if label not in labels:
                    legend = label
                    labels.append(legend)
                pl.figure(1)
                fig1 = self.plot_component_relation(kc, thresholds, grades, figure_path, "threshold", "grade", [0, 1], [0, 1], linewidth=1, ycolor=color, label=legend, dotsize=10, figure=fig1)
                pl.figure(2)
                fig2 = self.plot_component_relation(kc, thresholds, practices, figure_path, "threshold", "practices", [0, 1], [0, max(practices)], linewidth=1, ycolor=color, label=legend, dotsize=10, figure=fig2)
                pl.figure(3)
                fig3 = self.plot_component_relation(kc, practices, grades, figure_path, "practice", "grade", [0, max(practices)], [0,1], linewidth=1, ycolor=color, label=legend, dotsize=10, figure=fig3)
            pl.figure(1)
            pl.savefig(figure_path + "grade_threshold_multiple.png")
            pl.figure(2)
            pl.savefig(figure_path + "practice_threshold_multiple.png")
            pl.figure(3)
            pl.savefig(figure_path + "grade_practice_multiple.png")
        elif type == "all" and self.white_obj.thresholds is not None: #plot for all KCs
            thresholds = self.white_obj.thresholds
            grades = self.white_obj.grades
            practices = self.white_obj.practices
            self.plot_component_relation("all", thresholds, grades, figure_path, "threshold", "grade", [0,1], [0, 1])
            self.plot_component_relation("all", thresholds, practices, figure_path, "threshold", "practice", [0, 1], [0, max(practices)])
            self.plot_component_relation("all", practices, grades, figure_path, "practice", "grade", [0, max(practices)], [0,1])
        else:
            print "ERROR: Please reconfigure!"
            exit(-1)

    # def graph_path(self, white_objs, threshold=None):
    def plot_by_practice(self, white_objs, threshold=None):
        ''' white_objs is a list of white objects... it may only have a single object
           x=kc, y=practice, dot size=students, dot color=grade
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
                                figure=None, axis=None):
        if figure is None:
            fig, ax = pl.subplots()
        else:
            fig = figure

        pl.scatter(x, y, color=ycolor, s=dotsize)
        if label is None:
            pl.step(x, y, color=ycolor, linewidth=linewidth)
        else:
            pl.step(x, y, color=ycolor, linewidth=linewidth, label=label)
            pl.legend(loc="lower right", prop={'size':9}) #ncol=4,

        pl.ylabel(ylabel, fontsize=12)#ycolor
        pl.xlabel(xlabel, fontsize=12)
        if ylim is not None:
            pl.ylim(ylim)
        if xlim is not None:
            pl.xlim(xlim)
        if figure is None:
            pl.savefig(figure_path + (ylabel + "_" + xlabel + "_{}.png").format(kc))
            pl.close(fig)
        return fig
