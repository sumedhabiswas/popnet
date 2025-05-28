import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
import bilby
from astropy.coordinates import SkyCoord
import astropy.units as u


def load_bilby_result(result_path):
    """
    Load a BILBY result file and extract posterior samples for RA and Dec.

    Parameters:
    -----------
    result_path : str
        Path to the BILBY result `.json` file.

    Returns:
    --------
    ra_samples_deg : np.ndarray
        Right Ascension samples in degrees.
    dec_samples_deg : np.ndarray
        Declination samples in degrees.
    result : bilby.core.result.Result
        Full BILBY result object.
    """
    result = bilby.result.read_in_result(result_path)
    ra_samples = result.samples['ra'].dropna().values
    dec_samples = result.samples['dec'].dropna().values

    # Convert from radians to degrees
    coords = SkyCoord(ra=ra_samples * u.rad, dec=dec_samples * u.rad)
    return coords.ra.deg, coords.dec.deg, result


def compute_kde_contours(ra_samples, dec_samples, bandwidth=0.5, resolution=100):
    """
    Compute 2D KDE contours for the GW posterior RA/Dec samples.

    Parameters:
    -----------
    ra_samples : np.ndarray
        Right Ascension samples in degrees.
    dec_samples : np.ndarray
        Declination samples in degrees.
    bandwidth : float
        KDE bandwidth (affects smoothness). Default is 0.5.
    resolution : int
        Grid resolution for evaluating KDE.

    Returns:
    --------
    kde : gaussian_kde
        The KDE object itself for later reuse.
    ra_grid, dec_grid : np.ndarray
        Meshgrid arrays over the RA/Dec region.
    kde_values : np.ndarray
        KDE evaluated on the grid.
    threshold_50, threshold_90 : float
        KDE density values corresponding to 50% and 90% credible regions.
    """
    kde = gaussian_kde([ra_samples, dec_samples], bw_method=bandwidth)

    # Create grid over posterior samples
    ra_grid, dec_grid = np.mgrid[
        np.min(ra_samples):np.max(ra_samples):complex(resolution),
        np.min(dec_samples):np.max(dec_samples):complex(resolution)
    ]
    positions = np.vstack([ra_grid.ravel(), dec_grid.ravel()])
    kde_values = kde(positions).reshape(ra_grid.shape)

    # Normalize KDE for total probability mass
    kde_normalized = kde_values / np.sum(kde_values)
    kde_cumulative = np.cumsum(np.sort(kde_normalized.ravel()))

    # Estimate 50% and 90% thresholds by interpolation
    sorted_vals = np.sort(kde_values.ravel())
    threshold_50 = np.interp(0.5, kde_cumulative, sorted_vals)
    threshold_90 = np.interp(0.9, kde_cumulative, sorted_vals)

    return kde, ra_grid, dec_grid, kde_values, threshold_50, threshold_90


def reject_sample_within_contour(kde, ra_bounds, dec_bounds, threshold, n_samples=8000):
    """
    Perform rejection sampling to draw points within a given KDE contour region.

    Parameters:
    -----------
    kde : gaussian_kde
        Trained KDE model from RA/Dec samples.
    ra_bounds : tuple
        (min_ra, max_ra) range for sampling.
    dec_bounds : tuple
        (min_dec, max_dec) range for sampling.
    threshold : float
        KDE density threshold to define the region.
    n_samples : int
        Number of trial points to draw.

    Returns:
    --------
    ra_new : np.ndarray
        Sampled RA points within the contour.
    dec_new : np.ndarray
        Sampled Dec points within the contour.
    """
    ra_trial = np.random.uniform(ra_bounds[0], ra_bounds[1], size=n_samples)
    dec_trial = np.random.uniform(dec_bounds[0], dec_bounds[1], size=n_samples)
    mask = kde([ra_trial, dec_trial]) > threshold
    return ra_trial[mask], dec_trial[mask]

