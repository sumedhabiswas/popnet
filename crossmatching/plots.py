import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

def plot_2d_crossmatch_results(ra_samples, dec_samples, matched_50, matched_90, matched_all,
                                injected_ra, injected_dec, ra_grid, dec_grid, kde_values,
                                threshold_50, threshold_90, save_path=None, title=None):
    """
    Plot 2D posterior samples and crossmatched galaxies with KDE contours.

    Parameters
    ----------
    ra_samples, dec_samples : array-like
        Full posterior RA and Dec samples (in degrees).
    matched_50, matched_90, matched_all : pd.DataFrame
        DataFrames with RA/Dec of matched galaxies in 50%, 90%, and all posteriors.
    injected_ra, injected_dec : float
        Injected coordinates in degrees.
    ra_grid, dec_grid : 2D arrays
        Grid used to compute KDE.
    kde_values : 2D array
        KDE density values on the grid.
    threshold_50, threshold_90 : float
        Density values for the 50% and 90% contours.
    save_path : str or None
        File path to save the plot.
    title : str or None
        Title for the plot.
    """
    from pubstyle import set_pub_style
    set_pub_style()

    fig, ax = plt.subplots(figsize=(8, 6))

    # Posterior samples
    posterior_handle = ax.scatter(ra_samples, dec_samples, s=25, color='#6CA6CD', alpha=0.18,
                                   edgecolor='black', lw=0.2, label='Posterior Samples')
    
    # Matched galaxies
    handle_50 = ax.scatter(matched_50['ra'], matched_50['dec'], s=40, color='#B8860B',
                           alpha=0.9, edgecolor='black', lw=0.2, label="Matched Galaxies (50%)")
    handle_90 = ax.scatter(matched_90['ra'], matched_90['dec'], s=30, color='#CD5C5C',
                           alpha=0.85, edgecolor='black', lw=0.2, label="Matched Galaxies (90%)")
    handle_all = ax.scatter(matched_all['ra'], matched_all['dec'], s=25, color='#8A2BE2',
                            alpha=0.9, edgecolor='black', lw=0.2, label="Matched Galaxies (All)")

    # Injection
    inj_handle = ax.scatter(injected_ra, injected_dec, s=110, facecolors='none',
                            edgecolors='black', lw=1.5, label='Injection')

    # KDE contours
    ax.contour(ra_grid, dec_grid, kde_values, levels=[threshold_50],
               colors='#4B0082', linewidths=2.5, linestyles='--')
    ax.contour(ra_grid, dec_grid, kde_values, levels=[threshold_90],
               colors='#9370DB', linewidths=2.5, linestyles='--')

    # Legend
    legend_elements = [
        Line2D([0], [0], color='#4B0082', lw=2.5, linestyle='--', label="50% Contour"),
        Line2D([0], [0], color='#9370DB', lw=2.5, linestyle='--', label="90% Contour")
    ]

    ax.set_xlabel(r"$\mathrm{RA\ (deg)}$")
    ax.set_ylabel(r"$\mathrm{Dec\ (deg)}$")
    ax.set_title(title or "Crossmatched Galaxies vs. GW Posterior Regions", pad=10)
    ax.legend(handles=[posterior_handle, handle_50, handle_90, handle_all, inj_handle] + legend_elements,
              loc='best', frameon=False)
    ax.grid(True, linestyle='--', color='#D3D3D3', alpha=0.6)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()

