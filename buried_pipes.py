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
    def __init__(self, widget, text, delay=250):
        self.widget = widget
        self.text = text
        self.delay = delay  # delay in milliseconds
        self.tooltip_window = None
        self.id = None

        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.hide)
        self.widget.bind("<ButtonPress>", self.hide)  # hide on click

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
        tw.wm_overrideredirect(True)  # Remove window decorations
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

# Create GUI root window
root = tk.Tk()
root.title("Traffic Pressures on Pipes")
root.geometry('640x480')

# Add root window title and description
lbl_title = tk.Label(root, text="Traffic Pressures on Buried Pipes", font=("Arial", 12, "bold"),
                      justify="left", anchor="w")
lbl_title.pack(fill="x", padx=10, pady=(10, 0))

lbl_desc = tk.Label(root, text="Calculates traffic pressures using Boussinesq's equation and " \
"wheel loads idealised as point loads as described in Young and Trott's 'Buried Rigid Pipes " \
"Structural Design of Pipelines' (1984). This simplified approach neglects consideration of" \
"pipe diameter, bedding, or tyre contact area.", wraplength=620, justify="left", anchor="w")
lbl_desc.pack(fill="x", padx=10, pady=(0, 10))

# Frame for 'Input - Spatial Domain Parameters'
mframe1 = tk.Frame(root, bd=1, width=60, relief="solid", padx=0, pady=0)
mframe1.pack(fill="x", expand=True, padx=0, pady=0)
frame1 = tk.Frame(mframe1, bd=1, relief="solid", padx=10, pady=10)
frame1.grid(row=0, column=0, sticky="ew", pady=5)
tk.Label(frame1, text="Input - Spatial Domain Parameters", font=("Arial", 10, "bold")).grid(
    row=0, column=0, sticky="w")
tk.Label(frame1, text="Input parameters defining and discretizing spatial domain over which to " \
"calculate pressures:", justify="left").grid(row=1, column=0, sticky="w", 
    pady=(5,0))

# Row 1
frame2 = tk.Frame(mframe1, bd=1, relief="solid", padx=10, pady=0)
frame2.grid(row=1, column=0, sticky="ew", pady=0)
tk.Label(frame2, text="Model length along pipe (x direction):").grid(
    row=0, column=0, sticky="w", padx=(0,10))
entry1 = tk.Entry(frame2, width=15)
entry1.grid(row=0, column=1, sticky="e")
tk.Label(frame2, text="m").grid(row=0, column=2, sticky="w", padx=(5,0))
tooltip1 = Tooltip(entry1, "Should exceed width of applied wheel or axle plus some allowance \n" \
"for load distribution to each side of extreme point load(s)")

# Row 2
frame3 = tk.Frame(mframe1, bd=1, relief="solid", padx=10, pady=0)
frame3.grid(row=2, column=0, sticky="ew", pady=0)
tk.Label(frame3, text="Model length across pipe (y direction):").grid(
    row=0, column=0, sticky="w", padx=(0,10))
entry2 = tk.Entry(frame3, width=15)
entry2.grid(row=0, column=1, sticky="e")
tk.Label(frame3, text="m").grid(row=0, column=2, sticky="w", padx=(5,0))
tooltip2 = Tooltip(entry2, "Should be arbitrarily small number to capture peak pressure at \n" \
"pipe crown, 0.1m is recommended")

# Row 3
frame4 = tk.Frame(mframe1, bd=1, relief="solid", padx=10, pady=0)
frame4.grid(row=3, column=0, sticky="ew", pady=0)
tk.Label(frame4, text="Model depth (z direction):").grid(
    row=0, column=0, sticky="w", padx=(0,10))
entry3 = tk.Entry(frame4, width=15)
entry3.grid(row=0, column=1, sticky="e")
tk.Label(frame4, text="m   to ").grid(row=0, column=2, sticky="w", padx=(5,0))
entry4 = tk.Entry(frame4, width=15)
entry4.grid(row=0, column=3)
tk.Label(frame4, text="m").grid(row=0, column=4, sticky="w", padx=(5,0))
tooltip3 = Tooltip(entry3, "Minimum depth, recommended not less than 0.5m")
tooltip4 = Tooltip(entry4, "Maximum depth")

# Configure alignment
for frame in [frame1, frame2, frame3, frame4]:
    frame.grid_columnconfigure(0, weight=1)  # label column stretches
    frame.grid_columnconfigure(1, weight=0)  # entry fixed width
    frame.grid_columnconfigure(2, weight=0)  # units fixed width
    frame.grid_columnconfigure(3, weight=0)  # units fixed width
    frame.grid_columnconfigure(4, weight=0)  # units fixed width

# Frame for 'Input - Wheel Loads'
mframe2 = tk.Frame(root, bd=1, relief="solid", padx=0, pady=0)
mframe2.pack(fill="x", expand=True, padx=0, pady=0)
frame5 = tk.Frame(mframe2, bd=1, relief="solid", padx=10, pady=10)
frame5.grid(row=0, column=0, sticky="ew", pady=5)
tk.Label(frame5, text="Input - Wheel Loading", font=("Arial", 10, "bold")).grid(
    row=0, column=0, sticky="w")
tk.Label(frame5, text="Input wheel loads as a system of point loads. Patch loading can be " \
"approximated by discretising into a set of point loads.", wraplength=620, justify="left").grid(
    row=1, column=0, sticky="w", pady=(5,0))

frame5 = tk.Frame(mframe2, bd=1, relief="solid", padx=10, pady=0)
frame5.grid(row=1, column=0, sticky="ew", pady=0)
tk.Label(frame5, text="Set of points loads as [x1, y1, P1], [x2, y2, P2], ..., " \
"with coordinates in [m] and wheel loads as dynamic forces in [kN]").grid(
    row=0, column=0, sticky="w", padx=(0,10))
frame6 = tk.Frame(mframe2, bd=1, relief="solid", padx=10, pady=0)
frame6.grid(row=2, column=0, sticky="ew", pady=0)
tk.Label(frame6, text="Note x-y plane assumed centred on origin at (0, 0)").grid(
    row=0, column=0, sticky="w", padx=(0,10))
frame7 = tk.Frame(mframe2, bd=1, relief="solid", padx=10, pady=0)
frame7.grid(row=3, column=0, sticky="ew", pady=0)
entry5 = tk.Entry(frame7, width=100)
entry5.grid(row=0, column=3)


root.mainloop()



""" solve = PipePressures()
solve.mesh(1, 0.1, 2, 10, 1 , 16)
solve.load_points("Field", [[-0.45, 0, 60], [0.45, 0, 60]])
solve.boussinesq_pressure("Field") 
# 60kN on 0.4m squares at 0.9m centres
# 45deg 150mm pavement, 30deg thereafter """


