
import matplotlib.pyplot as plt
import seaborn as sns
import os
import corner
import healpy as hp
import numpy as np

def set_pub_style():
    import matplotlib.pyplot as plt
    import seaborn as sns
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman"],
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

def plot_radec_posterior(df_samples, injection_parameters, outdir, label, mass1, mass2):
    set_pub_style()
    ra_samples = df_samples['ra']
    dec_samples = df_samples['dec']
    ra_inj = injection_parameters['ra']
    dec_inj = injection_parameters['dec']

    plt.figure(figsize=(8, 6))
    sns.kdeplot(x=ra_samples, y=dec_samples, cmap="Blues", fill=True, thresh=0.05, alpha=0.7)
    plt.axvline(ra_inj, color='red', linestyle='--', label=f'Injected RA = {ra_inj:.2f}')
    plt.axhline(dec_inj, color='green', linestyle='--', label=f'Injected Dec = {dec_inj:.2f}')
    plt.scatter([ra_inj], [dec_inj], color='black', s=40, zorder=5, label="Injection")

    plt.xlabel(r"$\mathrm{RA}\ (\mathrm{rad})$")
    plt.ylabel(r"$\mathrm{Dec}\ (\mathrm{rad})$")
    plt.title(f"Sky Localization Posterior: m1={mass1}, m2={mass2}")
    plt.legend(loc="upper right")
    plt.tight_layout()

    path = os.path.join(outdir, f"{label}_radec_posterior.png")
    plt.savefig(path)
    plt.close()
    print(f"✅ RA/Dec posterior plot saved to {path}")

def plot_full_posterior(df_samples, parameter_list, outdir, label):
    set_pub_style()
    fig = corner.corner(df_samples[parameter_list], labels=parameter_list,
                        show_titles=True, title_fmt=".2f",
                        title_kwargs={"fontsize": 12}, label_kwargs={"fontsize": 12})
    fig.suptitle("Fisher Posterior Samples", fontsize=16, y=1.05)
    path = os.path.join(outdir, f"{label}_corner.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"✅ Full posterior corner plot saved to {path}")

def plot_1d_marginals(df_samples, parameter_list, outdir, label):
    set_pub_style()
    plt.figure(figsize=(10, len(parameter_list) * 2))
    for i, param in enumerate(parameter_list):
        plt.subplot(len(parameter_list), 1, i + 1)
        sns.kdeplot(df_samples[param], fill=True, color="skyblue")
        plt.title(f"{param} posterior")
        plt.xlabel(param)
        plt.grid(True)
    plt.tight_layout()
    path = os.path.join(outdir, f"{label}_1d_marginals.png")
    plt.savefig(path)
    plt.close()
    print(f"✅ 1D marginal plots saved to {path}")

def plot_distance_vs_inclination(df_samples, outdir, label):
    set_pub_style()
    plt.figure(figsize=(8, 6))
    sns.kdeplot(
        x=df_samples['luminosity_distance'],
        y=df_samples['theta_jn'],
        cmap="Purples", fill=True, thresh=0.05, alpha=0.6
    )
    plt.xlabel(r"$d_L\ (\mathrm{Mpc})$")
    plt.ylabel(r"$\theta_{\mathrm{JN}}\ (\mathrm{rad})$")
    plt.title(r"Distance vs Inclination: $d_L$ vs $\theta_{\mathrm{JN}}$")
    plt.tight_layout()
    path = os.path.join(outdir, f"{label}_distance_theta_posterior.png")
    plt.savefig(path)
    plt.close()
    print(f"✅ Distance vs Inclination plot saved to {path}")

def plot_healpix_skymap(df_samples, outdir, label, nside=64):
    set_pub_style()
    ra = df_samples["ra"].values
    dec = df_samples["dec"].values
    theta = 0.5 * np.pi - dec
    phi = ra
    npix = hp.nside2npix(nside)
    skymap = np.zeros(npix)
    pixels = hp.ang2pix(nside, theta, phi)
    for pix in pixels:
        skymap[pix] += 1
    skymap /= np.sum(skymap)

    fig = plt.figure(figsize=(10, 6))
    hp.mollview(skymap, title=f"Sky Localization: {label}", unit="Probability", cmap="Blues", cbar=True)
    path = os.path.join(outdir, f"{label}_skymap.png")
    plt.savefig(path)
    plt.close()
    print(f"✅ HEALPix skymap saved to {path}")


def plot_fisher_matrix(fisher_matrix, parameter_list, outdir, label, log_scale=True):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    set_pub_style()

    fig, ax = plt.subplots(figsize=(10, 8))
    matrix_to_plot = np.log10(np.abs(fisher_matrix)) if log_scale else np.abs(fisher_matrix)

    sns.heatmap(matrix_to_plot, xticklabels=parameter_list, yticklabels=parameter_list,
                cmap="viridis", square=True, annot=True, fmt=".2f",
                cbar_kws={"label": r"$\log_{10}|\mathcal{I}_{ij}|$" if log_scale else r"$|\mathcal{I}_{ij}|$"})

    ax.set_title(r"Fisher Information Matrix", fontsize=16)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    path = os.path.join(outdir, f"{label}_fisher_matrix.png")
    plt.savefig(path)
    plt.close()
    print(f"✅ Fisher matrix heatmap saved to {path}")

def plot_covariance_matrix(covariance_matrix, parameter_list, outdir, label):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    set_pub_style()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(np.abs(covariance_matrix), xticklabels=parameter_list, yticklabels=parameter_list,
                cmap="magma", square=True, annot=True, fmt=".2e",
                cbar_kws={"label": r"$\mathrm{Cov}(\theta_i, \theta_j)$"})

    ax.set_title(r"Covariance Matrix", fontsize=16)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    path = os.path.join(outdir, f"{label}_covariance_matrix.png")
    plt.savefig(path)
    plt.close()
    print(f"✅ Covariance matrix heatmap saved to {path}")

def print_condition_number(matrix):
    import numpy as np
    try:
        cond_number = np.linalg.cond(matrix)
        print(f"🔍 Condition number of matrix: {cond_number:.2e}")
    except Exception as e:
        print(f"❌ Could not compute condition number: {e}")
