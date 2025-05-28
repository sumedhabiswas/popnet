# ===================================================================
# Setting the same publication style
# ===================================================================
def set_pub_style():
    import matplotlib.pyplot as plt
    import seaborn as sns
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        #"font.serif": ["Computer Modern Roman"],
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.dpi": 300
    })
    sns.set_context("paper")
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.4)
    sns.set_style("whitegrid")
    plt.rc("axes", titlesize=14)
    plt.rc("axes", labelsize=12)
    plt.rc("legend", fontsize=10)
    plt.rc("xtick", labelsize=10)
    plt.rc("ytick", labelsize=10)
    plt.rc("savefig", dpi=300)
