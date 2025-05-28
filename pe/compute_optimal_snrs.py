
import pickle
import bilby
import numpy as np
import os
from bilby.gw.detector import InterferometerList, get_safe_signal_duration
from astropy.coordinates import Angle
import astropy.units as u

# Load detector network
with open('/home/sumedhabiswas/ligo_related/detector_network/HLVKIEC.pkl', 'rb') as f:
    detector_list = pickle.load(f)
detectors = InterferometerList(detector_list)

# Define distances and mass grid
distances = [500, 750, 1000]
mass_grid = [10, 20, 30, 40, 50]
injected_coords = {
    1000: (313.395908, 1.0067769, 999.938),
    750: (216.638478, 33.9201492, 750.08105),
    500: (258.9317702, 29.2868707, 499.92175)
}

sampling_frequency = 4096
snr_dict = {d: {ifo.name: [] for ifo in detectors} for d in distances}

for dist in distances:
    ra_deg, dec_deg, lum_dist = injected_coords[dist]
    ra_rad = Angle(ra_deg, unit=u.degree).rad
    dec_rad = Angle(dec_deg, unit=u.degree).rad

    for m in mass_grid:
        injection_parameters = dict(
            mass_1=m,
            mass_2=m,
            a_1=0.1,
            a_2=0.1,
            tilt_1=0.0,
            tilt_2=0.0,
            phi_12=0.0,
            phi_jl=0.0,
            luminosity_distance=lum_dist,
            theta_jn=0.4,
            psi=0.0,
            phase=0.0,
            geocent_time=0.0,
            ra=ra_rad,
            dec=dec_rad
        )

        duration = get_safe_signal_duration(
            m, m, 0.1, 0.1, 0.0, 0.0, flow=5.0
        )

        # Explicitly define a consistent frequency array
        delta_f = 1.0 / duration
        frequency_array = np.linspace(0, sampling_frequency / 2, int(duration * sampling_frequency / 2) + 1)

        waveform_arguments = dict(
            waveform_approximant='IMRPhenomXPHM',
            reference_frequency=20.0,
            minimum_frequency=5.0,
            maximum_frequency=10000.0,
            catch_waveform_errors=True
        )

        waveform_generator = bilby.gw.WaveformGenerator(
            duration=duration,
            sampling_frequency=sampling_frequency,
            frequency_domain_source_model=bilby.gw.source.lal_binary_black_hole,
            parameter_conversion=bilby.gw.conversion.convert_to_lal_binary_black_hole_parameters,
            waveform_arguments=waveform_arguments
        )
        waveform_generator.frequency_array = frequency_array

        for ifo in detectors:
            ifo.frequency_array = frequency_array

        # Inject signal
        for ifo in detectors:
            ifo.set_strain_data_from_power_spectral_density(
                sampling_frequency=sampling_frequency,
                duration=duration,
                start_time=injection_parameters['geocent_time'] - duration + 2.0
            )

        waveform = waveform_generator.frequency_domain_strain(injection_parameters)

        for ifo in detectors:
            try:
                snr_sq = ifo.optimal_snr_squared(waveform[ifo.name])
                snr_dict[dist][ifo.name].append(np.sqrt(snr_sq.real))
            except Exception as e:
                snr_dict[dist][ifo.name].append(np.nan)
                print(f"Error computing SNR for {ifo.name} at {m} M_sun, {dist} Mpc: {e}")

# Save SNR results
with open("snr_vs_mass_vs_distance.pkl", "wb") as f:
    pickle.dump(snr_dict, f)
