from astropy.coordinates import SkyCoord
from astropy import units as u
import pandas as pd

def crossmatch_galaxies_2d(gw_coords, ned_df, max_distance_deg=0.5, output_file=None):
    """
    Crossmatch GW coordinates with NED-LVS catalog based on RA, Dec.

    Parameters
    ----------
    gw_coords : pd.DataFrame or SkyCoord
        DataFrame with 'ra' and 'dec' in degrees, or SkyCoord object.
    ned_df : pd.DataFrame
        NED-LVS catalog with columns 'ra', 'dec'.
    max_distance_deg : float
        Matching radius in degrees.
    output_file : str or None
        Optional path to save the matched subset.

    Returns
    -------
    pd.DataFrame
        Matched galaxy subset from NED-LVS.
    """
    if isinstance(gw_coords, pd.DataFrame):
        gw_coords = SkyCoord(ra=gw_coords['ra'].values * u.deg,
                             dec=gw_coords['dec'].values * u.deg)

    ned_coords = SkyCoord(ra=ned_df['ra'].values * u.deg,
                          dec=ned_df['dec'].values * u.deg)
    
    idx, d2d, _ = gw_coords.match_to_catalog_sky(ned_coords)
    matched = d2d < max_distance_deg * u.deg
    matched_galaxies = ned_df.iloc[idx[matched]].drop_duplicates(subset=['ra', 'dec'])

    if output_file:
        matched_galaxies.to_csv(output_file, index=False)
        print(f"Matched galaxies saved to {output_file}")
    
    return matched_galaxies

