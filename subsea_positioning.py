'''
* Developed by Heitor Ribeiro | https://www.linkedin.com/in/heitor-ribeiro-geophysics/* 

 This Python application calculates the absolute 3D position of a ROV (Remotely Operated Vehicle)
 based on the vessel's geodetic position (latitude, longitude, altitude) and relative displacements
 in the local ENU (East-North-Up) coordinate system.

 It uses pyproj to perform transformations between Geodetic and ECEF (Earth-Centered, Earth-Fixed)
 coordinate systems, converting relative movements to new absolute positions.

 The application features a custom dark-themed graphical interface built with Tkinter.

 Enjoy it and feel free to improve and contribute!
'''

import tkinter as tk
from tkinter import ttk, messagebox
from pyproj import Transformer
import math
import os
import sys

# Geodetic <-> ECEF transformers
transformer_to_ecef = Transformer.from_crs("EPSG:4979", "EPSG:4978")
transformer_to_geodetic = Transformer.from_crs("EPSG:4978", "EPSG:4979")

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
        lat_base = float(entry_lat.get())
        lon_base = float(entry_lon.get())
        alt_base = 0.0

        delta_e = float(entry_delta_x.get())
        delta_n = float(entry_delta_y.get())
        depth = float(entry_depth.get())

        delta_u = depth

        lat_rov, lon_rov, alt_rov = calculate_3d_position(lat_base, lon_base, alt_base, delta_e, delta_n, delta_u)

        subsea_depth = delta_u

        result = (
            f"Absolute Position of the ROV:\n"
            f"Latitude: {lat_rov:.7f}°\n"
            f"Longitude: {lon_rov:.7f}°\n"
            f"Subsea Depth: {subsea_depth:.2f} m\n"
            f"Altitude: {alt_rov:.2f} m"
        )

        label_result.config(text=result)
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input or calculation error:\n{e}")

# GUI setup
root = tk.Tk()
root.title("3D Absolute Positioning of the ROV")
root.geometry("460x460")
root.resizable(False, False)

# Manual dark theme (no dependency on azure.tcl)
style = ttk.Style(root)
style.theme_use('clam')  # good for customization

# Dark color palette
bg_color = '#2e2e2e'        # dark gray
fg_color = '#f0f0f0'        # almost white
entry_bg = '#3c3f41'        # slightly lighter gray
entry_fg = fg_color
btn_bg = '#007acc'          # vibrant blue
btn_bg_active = '#005a9e'   # dark blue
label_result_bg = '#1e1e1e' # background for result label
label_result_fg = fg_color

# Style configurations
style.configure("TFrame", background=bg_color)
style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 11))
style.configure("TEntry",
                fieldbackground=entry_bg,
                foreground=entry_fg,
                font=("Segoe UI", 11))
style.configure("TButton",
                font=("Segoe UI Semibold", 12),
                padding=6,
                background=btn_bg,
                foreground=fg_color)
style.map("TButton",
          foreground=[('pressed', fg_color), ('active', fg_color)],
          background=[('pressed', btn_bg_active), ('active', btn_bg_active)])

# Main frame
frame = ttk.Frame(root, padding=25, style="TFrame")
frame.pack(fill="both", expand=True)

# Labels and entry fields
labels_text = [
    "Vessel Latitude (°):",
    "Vessel Longitude (°):",
    "ROV Displacement X (E) (m):",
    "ROV Displacement Y (N) (m):",
    "ROV Depth (m):"
]

entries = []

for i, text in enumerate(labels_text):
    ttk.Label(frame, text=text, style="TLabel").grid(row=i, column=0, sticky="w", pady=8)
    entry = ttk.Entry(frame, width=25, style="TEntry")
    entry.grid(row=i, column=1, sticky="e", padx=10, pady=8)
    entries.append(entry)

entry_lat, entry_lon, entry_delta_x, entry_delta_y, entry_depth = entries

# Calculate button
button_calculate = ttk.Button(frame, text="Calculate Absolute Position", command=calculate_and_display, style="TButton")
button_calculate.grid(row=6, column=0, columnspan=2, pady=(20, 10), sticky="ew")

# Result label with dark background and light text
label_result = ttk.Label(frame, text="", justify="left",
                         font=("Segoe UI Semibold", 12),
                         background=label_result_bg,
                         foreground=label_result_fg,
                         padding=12,
                         relief="ridge")
label_result.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(5, 0))

# Layout adjustment
frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=2)

# Set main window background color
root.configure(bg=bg_color)

# Start the app
root.mainloop()
