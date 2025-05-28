"""
popnet/galaxycatalogue/nedlvs.py

(M) Loads the NED-LVS galaxy catalogue

@author: sumedhabiswas 

"""

from astropy.coordinates import SkyCoord
from astropy import units as u
import astropy.io.fits as fits
import numpy as np
import pandas as pd
from tqdm import tqdm
from astropy.table import Table
import matplotlib.pyplot as plt
from matplotlib import rcParams

LVS_CAT = "/home/sumedha/Documents/Projects/BBH_hosts/galaxy_counting/ned/NEDLVS_2025.fits"

# Details of columns can be found here: https://ned.ipac.caltech.edu/NED::LVS/
COLS = [
    'objname',
    'ra', 'dec',
    'z', 'z_unc',
    'z_tech',
    'z_qual',
    'ziDist', 'ziDist_unc',
    'ziDist_method',
    'DistMpc', 'DistMpc_unc',
    'DistMpc_method',
    'ebv',
    'm_FUV', 'm_FUV_unc',
    'm_NUV', 'm_NUV_unc',
    'Lum_FUV', 'Lum_FUV_unc',
    'Lum_NUV', 'Lum_NUV_unc',
    'm_J', 'm_J_unc',
    'm_H', 'm_H_unc',
    'm_Ks', 'm_Ks_unc',
    'Lum_J', 'Lum_J_unc',
    'Lum_H', 'Lum_H_unc',
    'Lum_Ks', 'Lum_Ks_unc',
    'm_W1', 'm_W1_unc',
    'm_W2', 'm_W2_unc',
    'm_W3', 'm_W3_unc',
    'm_W4', 'm_W4_unc',
    'Lum_W1', 'Lum_W1_unc',
    'Lum_W2', 'Lum_W2_unc',
    'Lum_W3', 'Lum_W3_unc',
    'Lum_W4', 'Lum_W4_unc',
    'SFR_W4', 'SFR_W4_unc',
    'SFR_hybrid', 'SFR_hybrid_unc',
    'SFR_flag',
    'Mstar', 'Mstar_unc'
]

def load_ned_lvs(fits_path):
    """Load NED-LVS catalog with optimized FITS handling"""
    with fits.open(fits_path, memmap=True) as hdul:
        # Convert FITS to Astropy Table with byte order conversion
        table = Table.read(hdul[1])

        # Convert columns to native byte order
        for col in table.colnames:
            if table[col].dtype.byteorder not in ('=', '|'):
                table[col] = table[col].byteswap().newbyteorder()

        # Create DataFrame with selected columns
        df = pd.DataFrame()
        for col in COLS:
            if col in table.colnames:
                df[col] = table[col].value
            else:
                print(f"Warning: Column {col} not found - filling with NaN")
                df[col] = np.nan

        # Create SkyCoord array from cleaned data
        catalog_coords = SkyCoord(
            ra=df['ra'].values*u.deg,
            dec=df['dec'].values*u.deg,
            frame='icrs'
        )

    return df, catalog_coords

#global ned_df
#global ned_coords

def get_ned_catalog():
    return load_ned_lvs(LVS_CAT)
