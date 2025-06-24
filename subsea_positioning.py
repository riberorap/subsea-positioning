'''
This Python application calculates the absolute 3D position of an ROV (Remotely Operated Vehicle)
based on the vessel's geodetic position and relative displacements in the local ENU (East-North-Up)
coordinate system, applying corrections from a Sound Velocity Profile (SVP) loaded from a CSV file.

It provides both a 2D visualization using a background image and a 3D interactive visualization
using 3D OBJ models via vedo.

Developed by Heitor Ribeiro | https://www.linkedin.com/in/heitor-ribeiro-geophysics/
'''

import tkinter as tk
from tkinter import ttk, messagebox
from pyproj import Transformer
from PIL import Image, ImageDraw
from vedo import Plotter, load, Line, Box
import math
import csv
import os

# Transformers
transformer_to_ecef = Transformer.from_crs("EPSG:4979", "EPSG:4978")
transformer_to_geodetic = Transformer.from_crs("EPSG:4978", "EPSG:4979")

def load_svp_profile(filename):
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
        [-math.sin(lon_rad), math.cos(lon_rad), 0],
        [-math.sin(lat_rad)*math.cos(lon_rad), -math.sin(lat_rad)*math.sin(lon_rad), math.cos(lat_rad)],
        [math.cos(lat_rad)*math.cos(lon_rad), math.cos(lat_rad)*math.sin(lon_rad), math.sin(lat_rad)]
    ]

    dENU = [delta_e, delta_n, -delta_u]
    dECEF = [sum(R[i][j]*dENU[j] for j in range(3)) for i in range(3)]

    x_new, y_new, z_new = x_base + dECEF[0], y_base + dECEF[1], z_base + dECEF[2]
    lat_new, lon_new, alt_new = transformer_to_geodetic.transform(x_new, y_new, z_new)
    return lat_new, lon_new, alt_new

def calculate_and_display():
    try:
        global displacement_e, displacement_n, corrected_dep, alt_rov  # adicionei alt_rov como global para mostrar na 2D se quiser depois
        script_dir = os.path.dirname(os.path.abspath(__file__))
        svp_profile = load_svp_profile(os.path.join(script_dir, "svp_profile.csv"))
        if not svp_profile:
            return

        lat_base = float(entry_lat.get())
        lon_base = float(entry_lon.get())
        alt_base = 0.0
        delta_e = float(entry_delta_x.get())
        delta_n = float(entry_delta_y.get())
        depth = float(entry_depth.get())

        svp_ref = 1500.0
        sv_at_depth = get_sound_velocity(depth, svp_profile)
        svp_adjustment = (sv_at_depth - svp_ref) * 0.01
        corrected_depth = depth + svp_adjustment

        lat_rov, lon_rov, alt_rov = calculate_3d_position(lat_base, lon_base, alt_base, delta_e, delta_n, corrected_depth)

        result = (
            f"Absolute Position of the ROV:\n"
            f"Latitude: {lat_rov:.7f}°\n"
            f"Longitude: {lon_rov:.7f}°\n"
            f"Sound Velocity at Depth: {sv_at_depth:.1f} m/s\n"
            f"Altitude: {alt_rov:.2f} m\n"
            f"Original Depth: {depth:.2f} m\n"
            f"Corrected Depth: {corrected_depth:.2f} m"
            
        )
        label_result.configure(text=result)

        displacement_e, displacement_n, corrected_dep = delta_e, delta_n, corrected_depth

    except Exception as e:
        messagebox.showerror("Error", f"Calculation error:\n{e}")


def visualize_positioning():
    try:
        from PIL import ImageFont
        global displacement_e, displacement_n, corrected_dep

        def get_font(size):
            try:
                return ImageFont.truetype("DejaVuSans.ttf", size)
            except:
                return ImageFont.load_default()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        bg_img = Image.open(os.path.join(script_dir, "sea_background.png"))
        vessel_img = Image.open(os.path.join(script_dir, "vessel.png")).resize((350, 140))
        rov_img = Image.open(os.path.join(script_dir, "rov.png")).resize((100, 50))

        draw = ImageDraw.Draw(bg_img)
        scale_y = (bg_img.height - vessel_img.height) / 3000
        scale_x = bg_img.width / 1000

        vessel_x = (bg_img.width - vessel_img.width) // 2
        vessel_y = 0

        rov_x = int(vessel_x + (vessel_img.width // 2) + (displacement_e * scale_x) - (rov_img.width // 2))
        rov_y = int(vessel_img.height + (corrected_dep * scale_y))

        bg_img.paste(vessel_img, (vessel_x, vessel_y), vessel_img)
        bg_img.paste(rov_img, (rov_x, rov_y), rov_img)

        draw.line([(vessel_x + vessel_img.width // 2, vessel_img.height),
                   (rov_x + rov_img.width // 2, rov_y)], fill="red", width=5)

        font = get_font(32)

        for depth in range(0, 3050, 50):
            y = int(vessel_img.height + (depth * scale_y))
            if depth % 100 == 0:
                draw.line([(0, y), (30, y)], fill="black", width=2)
                draw.text((35, y - 15), f"{depth} m", fill="black", font=font)
            else:
                draw.line([(0, y), (20, y)], fill="black", width=1)

        for disp in range(-500, 550, 50):
            x = int((bg_img.width / 2) + (disp * scale_x))
            if disp % 100 == 0:
                draw.line([(x, bg_img.height-30), (x, bg_img.height)], fill="black", width=2)
                draw.text((x - 40, bg_img.height-60), f"{disp} m", fill="black", font=font)
            else:
                draw.line([(x, bg_img.height-20), (x, bg_img.height)], fill="black", width=1)

        output_path = os.path.join(script_dir, "output_positioning.png")
        bg_img.save(output_path)
        bg_img.show()

    except Exception as e:
        messagebox.showerror("Error", f"Error in 2D visualization:\n{e}")

def visualize_3d_positioning():
    try:
        from vedo import Plotter, load, Line, Box, Grid, Text2D

        script_dir = os.path.dirname(os.path.abspath(__file__))
        rov_model = load(os.path.join(script_dir, "ROV.obj"))
        vessel_model = load(os.path.join(script_dir, "VESSEL.obj"))

        rov_size = rov_model.diagonal_size()
        vessel_size = vessel_model.diagonal_size()

        vessel_target_size = 50 * 10  # meters
        rov_target_size = 5 * 10      # meters

        vessel_model.scale(vessel_target_size / vessel_size)
        rov_model.scale(rov_target_size / rov_size)

        vessel_model.pos(0, 0, 0)

        rov_model.pos(displacement_e, displacement_n, -corrected_dep)

        line = Line([0, 0, 0], [displacement_e, displacement_n, -corrected_dep], c="red", lw=3)

        surface_grid = Grid(pos=(0, 0, 0), s=(1000, 1000), res=(20, 20)).alpha(0.3).c("deepskyblue")

        box_depth = max(1000, corrected_dep * 1.2)
        background = Box(pos=(0, 0, -box_depth / 2),
                         length=1000, width=1000, height=box_depth,
                         c="lightblue", alpha=0.02).wireframe(True)
        
        instructions = Text2D(
            "Controls:\n"
            "R : reset view\n"
            "Scroll : zoom in/out\n"
            "Esc : close window",
            pos="bottom-left",
            c="white",
            bg="black",
            alpha=0.6,
            font="Calco",
            s=0.5
        )

        vp = Plotter(title="3D Subsea Positioning",
                     axes=dict(xtitle="East (m)", ytitle="North (m)", ztitle="Depth (m)"),
                     bg="black")
        
        vp.show(background, surface_grid, vessel_model, rov_model, line, instructions,
                interactive=True, zoom=1.2, viewup="z")

    except Exception as e:
        messagebox.showerror("Error", f"3D visualization error:\n{e}")

# Interface
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("3D Subsea Positioning")
root.geometry("370x530")
root.resizable(False, False)

frame = ctk.CTkFrame(master=root, corner_radius=15)
frame.pack(padx=11, pady=11, fill="both", expand=True)

labels_text = ["Vessel Latitude (°):", "Vessel Longitude (°):",
               "Displacement X (m):", "Displacement Y (m):", "Depth (m):"]

entries = []
for i, text in enumerate(labels_text):
    ctk.CTkLabel(frame, text=text, font=("Segoe UI", 16)).grid(row=i, column=0, sticky="w", pady=6, padx=10)
    entry = ctk.CTkEntry(frame, width=160, corner_radius=10)
    entry.grid(row=i, column=1, sticky="e", pady=6, padx=10)
    entries.append(entry)

entry_lat, entry_lon, entry_delta_x, entry_delta_y, entry_depth = entries

ctk.CTkButton(frame, text="Calculate Position", command=calculate_and_display, corner_radius=12).grid(
    row=6, column=0, columnspan=2, padx=10, pady=6, sticky="ew")

ctk.CTkButton(frame, text="2D Visualization", command=visualize_positioning, corner_radius=12).grid(
    row=7, column=0, columnspan=2, padx=10, pady=6, sticky="ew")

ctk.CTkButton(frame, text="3D Visualization", command=visualize_3d_positioning, corner_radius=12).grid(
    row=8, column=0, columnspan=2, padx=10, pady=6, sticky="ew")

label_result = ctk.CTkLabel(frame, text="", justify="left", wraplength=300, font=("Segoe UI", 16))
label_result.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

root.mainloop()

