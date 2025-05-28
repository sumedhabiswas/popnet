"""
popnet/galaxycatalogue/mstar_galaxy_ned.py

(CL) Obtain list of M* NED-LVS catalogue galaxies at a specified distance.

Steps:
1. Prompts the user for distance (Mpc)
2. Converts distance to redshift, assuming H0=70. 
3. Maps the redshift to M* values, based on observations (taken from refs)
4. Loads the NED-LVS galaxy catalogue. 
5. Returns a list of M* galaxies at the specified distances, and saves it to a CSV file. 

@author: sumedhabiswas

"""

from astropy.io import fits
import numpy as np
import pandas as pd

LVS_CAT = "NEDLVS_2025.fits"

# Constants
H0 = 70  # Hubble constant in km/s/Mpc (assumed)
c = 3e5  # Speed of light in km/s

# Redshift-Mstar mapping from the table
redshift_mstar_mapping = [
    {"z_min": 0, "z_max": 0.06, "log_mstar": 10.66},  # B12
    {"z_min": 0.02, "z_max": 0.06, "log_mstar": 10.79},  # W16
    {"z_min": 0.06, "z_max": 0.25, "log_mstar": 10.79},  # ASSUMPTION !!!
    {"z_min": 0.25, "z_max": 0.75, "log_mstar": 10.64},  # M21
    {"z_min": 0.75, "z_max": 1.25, "log_mstar": 10.51},
    {"z_min": 1.25, "z_max": 1.75, "log_mstar": 10.54},
    {"z_min": 1.75, "z_max": 2.25, "log_mstar": 10.56},
    {"z_min": 2.25, "z_max": 2.75, "log_mstar": 10.55},
    {"z_min": 2.75, "z_max": 3.75, "log_mstar": 10.64},
]

# Function to calculate redshift from distance
def calculate_redshift(distance_mpc):
    return distance_mpc * H0 / c

# Function to get log(M*) based on redshift
def get_log_mstar(redshift):
    for entry in redshift_mstar_mapping:
        if entry["z_min"] <= redshift < entry["z_max"]:
            return entry["log_mstar"]
    return None

# Constants
H0 = 70  # Hubble constant in km/s/Mpc
c = 3e5  # Speed of light in km/s

# Modified log(M*) calculation with adaptive width
def get_mass_range(log_mstar, distance):
    # Base width for nearby galaxies (conservative)
    base_delta = 0.01  # ±1% in log-space (~2% linear mass range)
    
    # Wider window for >750 Mpc to account for:
    # - Increased stellar mass uncertainties at larger distances
    # - Sparse sampling in deep surveys
    # - Evolution of M* with redshift (passive aging vs mergers)
    if distance > 750:
        delta = 0.1 
    else:
        delta = base_delta
    
    return (10**(log_mstar - delta), 10**(log_mstar + delta))



# Load FITS file
with fits.open(LVS_CAT) as hdul:
    data = hdul[1].data

# Get user input for distance
target_distance = float(input("Enter target distance in Mpc: "))

# Calculate redshift and find corresponding log(M*)
redshift = calculate_redshift(target_distance)
log_mstar = get_log_mstar(redshift)

if log_mstar is None:
    print(f"\nNo matching log(M*) found for redshift {redshift:.2f}.")
else:
    print(f"\nCalculated redshift: {redshift:.2f}")
    print(f"Using log(M*) = {log_mstar:.2f}")

    # Convert log(M*) to linear scale and define mass range
    #mass_lower = 10**(log_mstar - 0.01)  # Slightly below log(M*)
    #mass_upper = 10**(log_mstar + 0.01)  # Slightly above log(M*)
    print(max(data['DistMpc']))
    mass_lower, mass_upper = get_mass_range(log_mstar, target_distance)
    
    # Create masks
    distance_mask = np.isclose(data['DistMpc'], target_distance, atol=0.1)
    mass_mask = (data['Mstar'] >= mass_lower) & (data['Mstar'] <= mass_upper)

    # Combine masks and filter
    combined_mask = distance_mask & mass_mask
    matches = data[combined_mask]

    # Print results
    if len(matches) > 0:
        print(f"\nFound {len(matches)} galaxies at {target_distance} Mpc")
        print(f"within mass range {mass_lower:.2e}-{mass_upper:.2e} M☉:")
        print("\nMatching rows:")
        for row in matches:
            print(row)  # Print entire row with all columns

        # Save matches to CSV file
        df = pd.DataFrame(matches)  # Convert FITS rows to a pandas DataFrame
        output_filename = f"matched_galaxies_{int(target_distance)}Mpc.csv"
        df.to_csv(output_filename, index=False)
        print(f"\nMatching rows saved to '{output_filename}'")
    else:
        print("\nNo galaxies found in specified range.")



