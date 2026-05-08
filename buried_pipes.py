import math
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk

class PipePressures:
    def __init__(self):
        self.lib_load_points = {}
    
    def mesh(self, x, y, z, xdivs, ydivs, zdivs, zmin=0.5):
        # generate 3d spatial mesh for calculation of pressures
        xinc = x / xdivs
        yinc = y / ydivs
        zinc = z / zdivs
        xmin = - x/2 + xinc/2
        ymin = - y/2 + yinc/2
        self.x_arr = np.linspace(xmin, -xmin, xdivs)
        self.y_arr = np.linspace(ymin, -ymin, ydivs)
        self.z_arr = np.linspace(zmin, z, zdivs)
        return

    def load_points(self, name, wheel_loads):
        # define wheel loads along axle as point loads
        self.lib_load_points[name] = wheel_loads
        return

    def load_patches(self):
        return

    def boussinesq_pressure(self, loadname):
        # calculate boussinesq pressures on grid
        # z, x, y, p

        for iz in self.z_arr:
            for iy in self.y_arr:
                for ix in self.x_arr:
                    sig_z = 0
                    for wheel in self.lib_load_points[loadname]:
                        rad = ((ix - wheel[0])**2 + (iy - wheel[1])**2) ** 0.5
                        sig_z += (3 * wheel[2] / (2 * math.pi * iz**2) * 
                                  (1 / (1 + (rad / iz)**2))**2.5)
                    # print("z =", iz, "y =", iy, "x =", ix, "sigz =", sig_z)
        return


# Create GUI root window
root = tk.Tk()
root.title("Traffic Pressures on Pipes")
root.geometry('640x480')

# Add title and description
lbl_title = tk.Label(root, text="Traffic Pressures on Buried Pipes", font=("Arial", 12, "bold"), justify="left", anchor="w")
lbl_title.pack(fill="x", padx=10, pady=10)

lbl_desc = tk.Label(root, text="Calculates traffic pressures using Boussinesq's equation and " \
"wheel loads idealised as point loads as described in Young and Trott's 'Buried Rigid Pipes " \
"Structural Design of Pipelines' (1984). This ")

# Frame for 'Spatial Domain Parameters'
mframe1 = tk.Frame(root, bd=1, relief="solid", padx=10, pady=10)
mframe1.pack(fill="both", expand=True, padx=20, pady=20)
frame1 = tk.Frame(mframe1, bd=1, relief="solid", padx=10, pady=10)
frame1.grid(row=0, column=0, sticky="ew", pady=5)
tk.Label(frame1, text="Input - Spatial Domain Parameters", font=("Arial", 10, "bold")).grid(
    row=0, column=0, sticky="w")
tk.Label(frame1,
         text="Input parameters defining and discretizing spatial domain over which to calculate pressures:",
         wraplength=580, justify="left").grid(row=1, column=0, sticky="w", pady=(5,0))

# Row 1
frame2 = tk.Frame(mframe1, bd=1, relief="solid", padx=10, pady=0)
frame2.grid(row=1, column=0, sticky="ew", pady=0)
tk.Label(frame2, text="Model length along pipe (x direction):").grid(row=0, column=0, sticky="w", padx=(0,10))
entry1 = tk.Entry(frame2, width=15)
entry1.grid(row=0, column=1, sticky="e")
tk.Label(frame2, text="m").grid(row=0, column=2, sticky="w", padx=(5,0))

# Row 2
frame3 = tk.Frame(mframe1, bd=1, relief="solid", padx=10, pady=0)
frame3.grid(row=2, column=0, sticky="ew", pady=0)
tk.Label(frame3, text="Model length across pipe (y direction):").grid(row=0, column=0, sticky="w", padx=(0,10))
entry2 = tk.Entry(frame3, width=15)
entry2.grid(row=0, column=1, sticky="e")
tk.Label(frame3, text="m").grid(row=0, column=2, sticky="w", padx=(5,0))

# Row 3
frame4 = tk.Frame(mframe1, bd=1, relief="solid", padx=10, pady=0)
frame4.grid(row=3, column=0, sticky="ew", pady=0)
#tk.Label(frame4, "To obtain peak")

# Configure alignment
for frame in [frame1, frame2, frame3]:
    frame.grid_columnconfigure(0, weight=1)  # label column stretches
    frame.grid_columnconfigure(1, weight=0)  # entry fixed width
    frame.grid_columnconfigure(2, weight=0)  # units fixed width

root.mainloop()



""" solve = PipePressures()
solve.mesh(1, 0.1, 2, 10, 1 , 16)
solve.load_points("Field", [[-0.45, 0, 60], [0.45, 0, 60]])
solve.boussinesq_pressure("Field") 
# 60kN on 0.4m squares at 0.9m centres
# 45deg 150mm pavement, 30deg thereafter """


