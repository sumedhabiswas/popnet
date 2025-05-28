"""
popnet/network/duration.py

(SA) Calculates and plots the signal duration

@author:sumedhabiswas
"""
import numpy as np
import matplotlib.pyplot as plt
from bilby.gw.detector import get_safe_signal_duration
import matplotlib as mpl

# Matplotlib settings for publication-quality figures
mpl.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "axes.labelsize": 14,
    "axes.titlesize": 16,
    "legend.fontsize": 12,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "lines.linewidth": 2,
    "lines.markersize": 6
})

# Parameters
flow_values = [5.0, 20.0]
mass_values = [50, 40, 30, 20, 10, 5]
labels = [f"${m}+{m}$" for m in mass_values]
colors = ['#0072B2', '#D55E00']  # Colorblind-friendly: blue, red-orange
markers = ['o', 's']
linestyles = ['-', '--']

# Plot
plt.figure(figsize=(6, 4.5))

for idx, flow in enumerate(flow_values):
    durations = []
    for m in mass_values:
        duration = get_safe_signal_duration(
            mass_1=m,
            mass_2=m,
            a_1=0.1,
            a_2=0.1,
            tilt_1=0.0,
            tilt_2=0.0,
            flow=flow
        )
        durations.append(duration)
    plt.plot(labels, durations, marker=markers[idx], linestyle=linestyles[idx],
             color=colors[idx], label=f"$f_{{\\rm low}} = {flow}\\,\\mathrm{{Hz}}$")

# Axis labels and grid
plt.xlabel("Mass Configuration [$M_\\odot$]", fontsize=14)
plt.ylabel("GW Signal Duration [s]", fontsize=14)
plt.grid(True, which='both', linestyle=':', linewidth=0.8)
plt.legend(frameon=False, loc='upper left')
plt.tight_layout()

# Save and show
plt.savefig("duration.pdf", dpi=300, bbox_inches='tight')
plt.show()

