## 📖 README.md

# 🌊 Subsea 3D Absolute Positioning Calculator

A Python-based application with a graphical interface (Tkinter) for calculating the **absolute geodetic position** of a subsea ROV based on its relative displacement from a vessel's known position.

## 📌 Overview

In offshore and subsea operations, it's common to track ROV (Remotely Operated Vehicle) positions relative to a surface vessel using **East-North-Up (ENU)** displacements. This tool converts those **relative coordinates** into **absolute global positions** (Latitude, Longitude, Altitude) using precise geodetic transformations.


## 📊 Features

- ✅ Clean, dark mode user interface  
- ✅ Input fields for vessel position and ROV displacements  
- ✅ Real-time calculation of absolute subsea position  
- ✅ Displays both subsea depth and absolute altitude  
- ✅ Uses **pyproj** for WGS84 and ECEF transformations  


## 🌍 Application Scenario

In subsea environments, where **GNSS signals are unavailable underwater**, ROVs are tracked relative to a vessel equipped with GNSS. This tool integrates those relative displacements with the vessel's position, generating absolute coordinates for:

- Subsea surveys  
- ROV inspections  
- Offshore construction support  
- GIS database updates  


## 📸 Interface Preview

![image](https://github.com/user-attachments/assets/d982b6c3-e13a-4c0b-a73a-677260f3d92a)


## 🛠️ Technologies Used

- **Python 3**  
- **Tkinter** — for GUI  
- **pyproj** — for geodetic ↔ ECEF transformations  


## 🚀 How to Run

1. Install dependencies:
   ```bash
   pip install pyproj
````

2. Run the application:

   ```bash
   python subsea_positioning.py
   ```
````
## 📚 Coordinate Concepts

* **Absolute Position (Global):**
  Latitude, Longitude, and Altitude in a geodetic system (WGS84).

* **Relative Position:**
  Displacements in **East, North, Up (ENU)** directions relative to a fixed origin (usually a vessel on the surface).


## 📖 License

MIT License


## 👨‍💻 Author

[Heitor Ribeiro](https://www.linkedin.com/in/heitor-ribeiro-geophysics/)
 | Surveyor | Offshore & Subsea Positioning Solutions 🚢🌊
