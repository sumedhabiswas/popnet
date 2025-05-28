"""
popnet/network/building_gw_network.py

(stand-alone) Script to build a 7-detector GW network (HLVKIEC), and save as a pickle file

@author: sumedhabiswas
"""

import numpy as np
import bilby
import pickle
import matplotlib.pyplot as plt
import os
from bilby.gw.detector import InterferometerList, PowerSpectralDensity, get_safe_signal_duration, get_empty_interferometer
from bilby.gw.detector.networks import TriangularInterferometer
import healpy as hp

sampling_frequency = 4096

PSD_PATH = {
    'I1': 'aligo_O4high.txt' # ASD
}

DETECTOR_COORDS = {
    'I1': (19.09, 74.05, 200)
}

DETECTOR_CONFIG = {
    'I1': {'min': 20, 'max': 2048}
}

def load_psd(detector_name):
    """Load and validate PSD/ASD data correctly based on detector type."""
    path = PSD_PATH[detector_name]
    if not os.path.exists(path):
        raise FileNotFoundError(f"PSD file for {detector_name} not found at {path}")

    data = np.loadtxt(path)

    if detector_name == 'I1':
        freq = data[:, 0]
        asd_vals = data[:, 1]
        psd = asd_vals**2

    return PowerSpectralDensity(
        frequency_array=freq,
        psd_array=psd
    )

def create_interferometer(name):
    lat, lon, elev = DETECTOR_COORDS[name]
    lat = np.deg2rad(lat)
    lon = np.deg2rad(lon)
    psd = load_psd(name)

    if name == 'I1':
        ifo = get_empty_interferometer('H1')
        ifo.name = name
        ifo.latitude = lat
        ifo.longitude = lon
        ifo.elevation = elev
        ifo.power_spectral_density = psd
        ifo.minimum_frequency = DETECTOR_CONFIG[name]['min']
        ifo.maximum_frequency = DETECTOR_CONFIG[name]['max']
        if name == 'I1':
            ifo.xarm_azimuth = np.deg2rad(45)
            ifo.yarm_azimuth = np.deg2rad(135)
        return ifo

create_interferometer('I1')

ifos = bilby.gw.detector.InterferometerList(['H1', 'L1', 'V1', 'K1', 'CE', 'ET'])

ifo_i1 = create_interferometer('I1')

ifos.append(ifo_i1)

with open('HLVKIEC.pkl', 'wb') as f:
    pickle.dump(ifos, f, protocol=pickle.HIGHEST_PROTOCOL)

