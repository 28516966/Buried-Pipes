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

class Tooltip:
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.id = None

        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.hide)
        self.widget.bind("<ButtonPress>", self.hide)

    def schedule(self, event=None):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide(self, event=None):
        self.unschedule()
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# ------------------- GUI ------------------- #
root = tk.Tk()
root.title("Traffic Pressures on Pipes")
root.geometry("640x480")

# Title and description
tk.Label(root, text="Traffic Pressures on Buried Pipes",
         font=("Arial", 12, "bold"), anchor="w", justify="left").pack(fill="x", padx=10, pady=(10,0))

tk.Label(root,
         text="Calculates traffic pressures using Boussinesq's equation and wheel loads "
              "idealised as point loads as described in Young and Trott's 'Buried Rigid Pipes "
              "Structural Design of Pipelines' (1984). This simplified approach neglects "
              "consideration of pipe diameter, bedding, or tyre contact area.",
         wraplength=620, justify="left", anchor="w").pack(fill="x", padx=10, pady=(0,10))

# ------------------- Helper Functions ------------------- #
def create_mframe(parent):
    frame = tk.Frame(parent, bd=1, relief="solid", padx=0, pady=0)
    frame.pack(fill="x", padx=10, pady=5)
    return frame

def create_row(frame, label_text, tooltip_text=None, unit_text=None, entry_width=15):
    """Create a row with label, single entry, and optional unit"""
    row_frame = tk.Frame(frame)
    row_frame.pack(fill="x", pady=2)

    label = tk.Label(row_frame, text=label_text, anchor="w", justify="left", width=35)
    label.grid(row=0, column=0, sticky="w")

    entry = tk.Entry(row_frame, width=entry_width)
    entry.grid(row=0, column=1, sticky="e")
    if tooltip_text:
        Tooltip(entry, tooltip_text)

    if unit_text:
        tk.Label(row_frame, text=unit_text, anchor="w").grid(row=0, column=2, sticky="w", padx=(5,0))

    # Make label stretch, entry fixed
    row_frame.grid_columnconfigure(0, weight=1)
    row_frame.grid_columnconfigure(1, weight=0)

    return entry

# ------------------- Spatial Domain ------------------- #
mframe1 = create_mframe(root)
tk.Label(mframe1, text="Input - Spatial Domain Parameters",
         font=("Arial", 10, "bold")).pack(anchor="w", pady=(0,5))

tk.Label(mframe1, text="Input parameters defining and discretizing spatial domain over which to calculate pressures:",
         wraplength=600, justify="left").pack(anchor="w", pady=(0,5))

# Rows
entry1 = create_row(mframe1,
                    "Model length along pipe (x direction):",
                    "Should exceed width of applied wheel or axle plus some allowance\nfor load distribution to each side of extreme point load(s)",
                    "m")
entry2 = create_row(mframe1,
                    "Model length across pipe (y direction):",
                    "Should be arbitrarily small number to capture peak pressure at pipe crown, 0.1m is recommended",
                    "m")
entry3 = create_row(mframe1,
                    "Minimum depth (z direction):",
                    "Recommended not less than 0.5m",
                    "m")
entry4 = create_row(mframe1,
                    "Maximum depth (z direction):",
                    "",
                    "m")
entry5 = create_row(mframe1,
                    "Number of x divisions for discretization:",
                    "",
                    "   ")
entry6 = create_row(mframe1,
                    "Number of y divisions for discretization:",
                    "Recommended value of 1 since should be small",
                    "   ")
entry7 = create_row(mframe1,
                    "Number of z divisions for discretization:",
                    "",
                    "   ")

# ------------------- Wheel Loads ------------------- #
mframe2 = create_mframe(root)
tk.Label(mframe2, text="Input - Wheel Loading", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0,5))
tk.Label(mframe2, text="Input wheel loads as a system of point loads. Patch loading can be approximated by discretising into a set of point loads.",
         wraplength=600, justify="left").pack(anchor="w", pady=(0,5))

# Wide single-row Entry for multiple points
entry8 = tk.Frame(mframe2)
entry8.pack(fill="x", pady=2)
tk.Label(entry8, text="Set of point loads as [x1, y1, P1], [x2, y2, P2], ...",
         anchor="w", justify="left").grid(row=0, column=0, sticky="w", padx=(0,5))
entry5 = tk.Entry(entry8)
entry5.grid(row=0, column=1, sticky="ew")  # expand horizontally
entry8.grid_columnconfigure(1, weight=1)  # make entry expand
tk.Label(mframe2, text="Note: x-y plane assumed centered on origin at (0,0)").pack(anchor="w", pady=(2,2))

root.mainloop()



""" solve = PipePressures()
solve.mesh(1, 0.1, 2, 10, 1 , 16)
solve.load_points("Field", [[-0.45, 0, 60], [0.45, 0, 60]])
solve.boussinesq_pressure("Field") 
# 60kN on 0.4m squares at 0.9m centres
# 45deg 150mm pavement, 30deg thereafter """


