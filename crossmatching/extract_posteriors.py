import numpy as np
import bilby
from scipy.stats import gaussian_kde
from astropy.coordinates import SkyCoord
from astropy import units as u
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def extract_and_sample_posterior(run_file, bandwidth=0.5, n_samples=8000, injected_coords=None,
                                 plot=False, save_path=None, style_func=None):
    """
    Extract RA/Dec samples from a Bilby result, compute KDE-based posterior, and resample within 50% and 90% contours.

    Parameters
    ----------
    run_file : str
        Path to the Bilby result file (.json or .h5).
    bandwidth : float, optional
        Bandwidth for Gaussian KDE. Default is 0.5.
    n_samples : int, optional
        Number of resampled points per contour region.
    injected_coords : tuple (ra_deg, dec_deg), optional
        Injected RA/Dec in degrees, for plotting (default: None).
    plot : bool, optional
        If True, produce the skymap plot.
    save_path : str, optional
        If provided, path to save the figure (e.g., 'output/skymap.pdf').
    style_func : callable, optional
        Function to apply publication styling (e.g., `set_pub_style()`).

    Returns
    -------
    dict
        Dictionary with posterior samples, KDE grid, thresholds, and resampled contour points.
    """
    result = bilby.result.read_in_result(run_file)
    ra_samples = result.samples['ra'].dropna().values
    dec_samples = result.samples['dec'].dropna().values

    # Convert radians to degrees
    sky_coord = SkyCoord(ra=ra_samples, dec=dec_samples, unit=(u.rad, u.rad))
    ra_samples = sky_coord.ra.deg
    dec_samples = sky_coord.dec.deg

    # KDE calculation
    kde = gaussian_kde([ra_samples, dec_samples], bw_method=bandwidth)
    ra_grid, dec_grid = np.mgrid[
        np.min(ra_samples):np.max(ra_samples):100j,
        np.min(dec_samples):np.max(dec_samples):100j
    ]
    kde_values = kde(np.vstack([ra_grid.ravel(), dec_grid.ravel()])).reshape(ra_grid.shape)

    # Normalize + thresholds
    kde_values_norm = kde_values / np.sum(kde_values)
    kde_cumulative = np.cumsum(kde_values_norm.ravel())
    threshold_50 = np.interp(0.50, kde_cumulative, kde_values.ravel())
    threshold_90 = np.interp(0.90, kde_cumulative, kde_values.ravel())

    # Identify contour regions
    ra_90, dec_90 = ra_grid[kde_values > threshold_90], dec_grid[kde_values > threshold_90]
    ra_50, dec_50 = ra_grid[kde_values > threshold_50], dec_grid[kde_values > threshold_50]

    def sample_inside_contour(ra_in, dec_in, threshold):
        ra_min, ra_max = np.min(ra_in), np.max(ra_in)
        dec_min, dec_max = np.min(dec_in), np.max(dec_in)
        ra_rand = np.random.uniform(ra_min, ra_max, size=n_samples)
        dec_rand = np.random.uniform(dec_min, dec_max, size=n_samples)
        mask = kde([ra_rand, dec_rand]) > threshold
        return ra_rand[mask], dec_rand[mask]

    ra_new, dec_new = sample_inside_contour(ra_90, dec_90, threshold_90)
    ra_new_50, dec_new_50 = sample_inside_contour(ra_50, dec_50, threshold_50)

    # Optional plotting
    if plot:
        if style_func:
            style_func()
        fig, ax = plt.subplots(figsize=(8, 6))
        posterior_handle = ax.scatter(
            ra_samples, dec_samples, s=25, color='#6CA6CD',
            alpha=0.18, edgecolor='black', lw=0.2, label='Posterior Samples'
        )

        inj_handle = None
        if injected_coords:
            inj_handle = ax.scatter(
                injected_coords[0], injected_coords[1], marker='*', color='black',
                s=120, lw=1, label='Injection'
            )

        ax.contour(ra_grid, dec_grid, kde_values, levels=[threshold_50], colors='#4B0082', linewidths=2.5, linestyles='--')
        ax.contour(ra_grid, dec_grid, kde_values, levels=[threshold_90], colors='#9370DB', linewidths=2.5, linestyles='--')

        legend_elements = [
            Line2D([0], [0], color='#4B0082', lw=2.5, linestyle='--', label="50% Contour"),
            Line2D([0], [0], color='#9370DB', lw=2.5, linestyle='--', label="90% Contour")
        ]

        handles = [posterior_handle] + ([inj_handle] if inj_handle else []) + legend_elements
        ax.set_xlabel(r"$\mathrm{RA\ (deg)}$")
        ax.set_ylabel(r"$\mathrm{Dec\ (deg)}$")
        ax.legend(handles=handles, loc='best', frameon=False)
        ax.grid(True, linestyle='--', color='#D3D3D3', alpha=0.6)

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path)
        plt.show()

    return {
        'ra_samples': ra_samples,
        'dec_samples': dec_samples,
        'ra_grid': ra_grid,
        'dec_grid': dec_grid,
        'kde_values': kde_values,
        'threshold_50': threshold_50,
        'threshold_90': threshold_90,
        'ra_new': ra_new,
        'dec_new': dec_new,
        'ra_new_50': ra_new_50,
        'dec_new_50': dec_new_50
    }

