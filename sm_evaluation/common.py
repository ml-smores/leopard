__author__ = 'ugonzjo'

import sklearn.metrics as metrics
#import scikits.bootstrap as bootstrap
import pandas as pd
import scipy
import matplotlib.pyplot as pl


def pretty(x):
    if isinstance(x, dict):
        ans = []
        for (k, v) in x.items():
            ans.append("{}:{}".format(k, pretty(v)))
        return "{" + ",".join(ans) + "}"
    elif isinstance(x, list):
        return "[" + ", ".join([pretty(e) for e in x]) + "]"
    elif isinstance(x, float):
        return "%4.3f" % x
    else:
        return str(x)

def intstr(x):
    return str(int(x))


def bootstrap_ci():
    df_bootstrap = pd.read_csv("../example_data/obj_bootstrap_input.csv")
    #compute confidence intervals around the mean, default  95% , 10000 samples
    cis = bootstrap.ci(data=df_bootstrap["score"], statfunction=scipy.mean) #, alpha=0.2, n_samples=20000)
    print "mean", df_bootstrap["score"].mean(), "Bootstrapped 95% confidence intervals Low:", cis[0], "High:", cis[1]
    cis_effort = bootstrap.ci(data=df_bootstrap["effort"], statfunction=scipy.mean) #, alpha=0.2, n_samples=20000)
    print "mean", df_bootstrap["effort"].mean(), "Bootstrapped 95% confidence intervals Low:", cis_effort[0], "High:", cis_effort[1]
    cis_effort_filled = bootstrap.ci(data=df_bootstrap["effort_filled"], statfunction=scipy.mean) #, alpha=0.2, n_samples=20000)
    print "mean", df_bootstrap["effort_filled"].mean(), "Bootstrapped 95% confidence intervals Low:", cis_effort_filled[0], "High:", cis_effort_filled[1]

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


def plot_scatterplot(x, y, xlabel, ylabel, file, legend):
    fig, ax = pl.subplots()
    pl.scatter(x, y, label=legend)
    pl.legend(loc='upper left', prop={'size':10})
    pl.ylabel(ylabel, fontsize=13)#ycolor
    pl.xlabel(xlabel, fontsize=13)
    # if not os.path.isdir(file):
    #     os.makedirs(file)
    pl.savefig(file)
    pl.close(fig)


def main():
    bootstrap_ci()

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

