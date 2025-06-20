# Developed by Heitor Ribeiro | https://www.linkedin.com/in/heitor-ribeiro-geophysics/

'''
This Python application calculates the absolute 3D position of an ROV (Remotely Operated Vehicle)
based on the vessel's geodetic position and relative displacements in the local ENU (East-North-Up)
coordinate system, applying corrections from a Sound Velocity Profile (SVP) loaded from a CSV file.

The program uses pyproj for Geodetic <-> ECEF transformations and Tkinter for a custom dark-themed GUI.
'''

import tkinter as tk
from tkinter import ttk, messagebox
from pyproj import Transformer
import math
import csv
import os

# Transformers
transformer_to_ecef = Transformer.from_crs("EPSG:4979", "EPSG:4978")
transformer_to_geodetic = Transformer.from_crs("EPSG:4978", "EPSG:4979")

def load_svp_profile(filename):
    """Loads the SVP profile from a CSV file."""
    svp = []
    try:
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                svp.append((float(row['Depth']), float(row['Velocity'])))
        return sorted(svp, key=lambda x: x[0])
    except Exception as e:
        messagebox.showerror("Error", f"Error reading SVP file:\n{e}")
        return None

def get_sound_velocity(depth, svp_profile):
    """Interpolates the sound velocity at a given depth."""
    if depth <= svp_profile[0][0]:
        return svp_profile[0][1]
    if depth >= svp_profile[-1][0]:
        return svp_profile[-1][1]

    for i in range(len(svp_profile) - 1):
        d0, sv0 = svp_profile[i]
        d1, sv1 = svp_profile[i + 1]
        if d0 <= depth <= d1:
            return sv0 + (sv1 - sv0) * (depth - d0) / (d1 - d0)

def calculate_3d_position(lat_base, lon_base, alt_base, delta_e, delta_n, delta_u):
    lat_rad = math.radians(lat_base)
    lon_rad = math.radians(lon_base)

    x_base, y_base, z_base = transformer_to_ecef.transform(lat_base, lon_base, alt_base)

    R = [
        [-math.sin(lon_rad),               math.cos(lon_rad),               0],
        [-math.sin(lat_rad)*math.cos(lon_rad), -math.sin(lat_rad)*math.sin(lon_rad), math.cos(lat_rad)],
        [math.cos(lat_rad)*math.cos(lon_rad),  math.cos(lat_rad)*math.sin(lon_rad),  math.sin(lat_rad)]
    ]

    dENU = [delta_e, delta_n, -delta_u]

    dECEF = [
        R[0][0]*dENU[0] + R[0][1]*dENU[1] + R[0][2]*dENU[2],
        R[1][0]*dENU[0] + R[1][1]*dENU[1] + R[1][2]*dENU[2],
        R[2][0]*dENU[0] + R[2][1]*dENU[1] + R[2][2]*dENU[2]
    ]

    x_new = x_base + dECEF[0]
    y_new = y_base + dECEF[1]
    z_new = z_base + dECEF[2]

    lat_new, lon_new, alt_new = transformer_to_geodetic.transform(x_new, y_new, z_new)
    return lat_new, lon_new, alt_new

def calculate_and_display():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        svp_path = os.path.join(script_dir, "svp_profile.csv")
        svp_profile = load_svp_profile(svp_path)

        if not svp_profile:
            return

        lat_base = float(entry_lat.get())
        lon_base = float(entry_lon.get())
        alt_base = 0.0

        delta_e = float(entry_delta_x.get())
        delta_n = float(entry_delta_y.get())
        depth = float(entry_depth.get())

        svp_ref = 1500.0  # m/s reference
        sv_at_depth = get_sound_velocity(depth, svp_profile)
        svp_correction_factor = 0.01  # m offset per m/s deviation
        svp_adjustment = (sv_at_depth - svp_ref) * svp_correction_factor
        corrected_depth = depth + svp_adjustment

        delta_u = corrected_depth

        lat_rov, lon_rov, alt_rov = calculate_3d_position(lat_base, lon_base, alt_base, delta_e, delta_n, delta_u)

        result = (
            f"Absolute Position of the ROV:\n"
            f"Latitude: {lat_rov:.7f}°\n"
            f"Longitude: {lon_rov:.7f}°\n"
            f"Original Depth: {depth:.2f} m\n"
            f"Sound Velocity at Depth: {sv_at_depth:.1f} m/s\n"
            f"Corrected Depth (SVP): {corrected_depth:.2f} m\n"
            f"Altitude: {alt_rov:.2f} m\n"
            f"SVP Correction: {svp_adjustment:.2f} m"
        )

        label_result.config(text=result)

    except Exception as e:
        messagebox.showerror("Error", f"Invalid input or calculation error:\n{e}")

# GUI setup
root = tk.Tk()
root.title("3D Absolute Positioning of the ROV with SVP Correction")
root.geometry("500x520")
root.resizable(False, False)

style = ttk.Style(root)
style.theme_use('clam')

bg_color = '#2e2e2e'
fg_color = '#f0f0f0'
entry_bg = '#3c3f41'
btn_bg = '#007acc'
btn_bg_active = '#005a9e'
label_result_bg = '#1e1e1e'

style.configure("TFrame", background=bg_color)
style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 11))
style.configure("TEntry", fieldbackground=entry_bg, foreground=fg_color, font=("Segoe UI", 11))
style.configure("TButton", font=("Segoe UI Semibold", 12), padding=6, background=btn_bg, foreground=fg_color)
style.map("TButton", foreground=[('pressed', fg_color), ('active', fg_color)], background=[('pressed', btn_bg_active), ('active', btn_bg_active)])

frame = ttk.Frame(root, padding=25)
frame.pack(fill="both", expand=True)

labels_text = [
    "Vessel Latitude (°):",
    "Vessel Longitude (°):",
    "ROV Displacement X (E) (m):",
    "ROV Displacement Y (N) (m):",
    "ROV Depth (m):"
]

entries = []

for i, text in enumerate(labels_text):
    ttk.Label(frame, text=text).grid(row=i, column=0, sticky="w", pady=8)
    entry = ttk.Entry(frame, width=25)
    entry.grid(row=i, column=1, sticky="e", padx=10, pady=8)
    entries.append(entry)

entry_lat, entry_lon, entry_delta_x, entry_delta_y, entry_depth = entries

button_calculate = ttk.Button(frame, text="Calculate Absolute Position", command=calculate_and_display)
button_calculate.grid(row=6, column=0, columnspan=2, pady=(20, 10), sticky="ew")

label_result = ttk.Label(frame, text="", justify="left",
                         font=("Segoe UI Semibold", 12),
                         background=label_result_bg,
                         foreground=fg_color,
                         padding=12,
                         relief="ridge")
label_result.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(5, 0))

frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=2)

root.configure(bg=bg_color)
root.mainloop()
