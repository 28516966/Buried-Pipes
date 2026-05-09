import csv
import json
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import tkinter as tk
from tkinter import filedialog

class PipePressures:
    def __init__(self):
        self.lib_load_points = {}
        self.results_pressures = []
        self.results_Ps = []
    def mesh(self, x, y, z, xdivs, ydivs, zdivs, zmin=0.5):
        """Defines parameters for spatial discretization into a series of nodes for which to solve
        Boussinesq earth pressures at.

        Args:
            x (float): Total model length along pipe direction [m]
            y (float): Total model length across pipe direction [m]
            z (float): Total depth [m]
            xdivs (int): Number of divisions in x
            ydivs (int): Number of divisions in y
            zdivs (int): Number of divisions in z
            zmin (float, optional): Minimum depth [m]. Defaults to 0.5.
        """
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

    def wheel_loads(self, wheel_loads, load_name="userinput"):
        """_summary_

        Args:
            wheel_loads: List of lists in format [x, y, P] i.e. coordinates in [m] and point load
                in [kN] describing wheel loads on ground surface at z = 0.
            load_name (str, optional): Name for load case. Defaults to "userinput".
        """
        # define wheel loads along axle as point loads
        self.lib_load_points[load_name] = wheel_loads
        return

    def boussinesq_pressure(self, load_name="userinput"):
        """Calculate Boussinesq pressures across discretized spatial coordinates for named load
        case.

        Args:
            load_name (str, optional): Name for load case. Defaults to "userinput".
        """
        self.results_pressures.clear()
        for iz in self.z_arr:
            for iy in self.y_arr:
                for ix in self.x_arr:
                    sigz = 0
                    for wheel in self.lib_load_points[load_name]:
                        rad = ((ix - wheel[0])**2 + (iy - wheel[1])**2) ** 0.5
                        sigz += (3 * wheel[2] / (2 * math.pi * iz**2) * 
                                  (1 / (1 + (rad / iz)**2))**2.5)
                    self.results_pressures.append([iz, iy, ix, sigz])
                    # print("z =", iz, "y =", iy, "x =", ix, "sigz =", sig_z)
        return
    
    def result_Ps(self, avg_length_over):
        # need to find y value for row of concern
        # need to iterate results array and for each z value calculate average x over given length
        # record maximum and save to results array

        # Identify central y row of concern to perform averaging on
        y_arr_len = len(self.y_arr)
        if y_arr_len % 2 != 0: # if number of points is odd, central y=0
            y_pos = y_arr_len / 2   
        else: # else use nearest row in +y
            y_pos = (y_arr_len + 1) / 2
        y_val = self.y_arr[y_pos]

        # Determine number of elements along x requiring averaging
        


        for iz in self.z_arr:
            #for each depth iterate results 



        return

def solve():
    """Takes inputs from GUI and creates an instance of class 'PipePressures' to solve"""
    global solution
    try:
        solution.clear()
    except:
        print("No existing solution to clear")
    solution = PipePressures()
    # Read spatial parameters and discretize mesh
    x = float(row1.get())
    y = float(row2.get())
    z = float(row3.get())
    zmin = float(row4.get())
    xdivs = int(row5.get())
    ydivs = int(row6.get())
    zdivs = int(row7.get())
    solution.mesh(x, y, z, xdivs, ydivs, zdivs, zmin=zmin)
    # Read and set wheel loads
    loads = json.loads(entry8.get())
    solution.wheel_loads(loads)
    # Solve
    solution.boussinesq_pressure()
    solution.result_Ps()
    return

def save_pressures():
    """Enables saving of comma-delimited results to .txt or .csv file"""
    global solution
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Save results as CSV file"
    )
    if not file_path:
        return
    with open(file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Z [m]", "Y [m]", "X [m]", "SIGMA_Z [kPa]"])
        for row in solution.results_pressures:
            writer.writerow(row)
    return

def save_traffic_surcharge():
    """Enables saving of comma-delimited results to .txt or .csv file"""
    global solution
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Save results as CSV file"
    )
    if not file_path:
        return
    with open(file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Z [m]", "Ps [kPa]"])
        for row in solution.results:
            writer.writerow()
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
# ------------------- Root Window and Main Frames ------------------- #
root = tk.Tk()
root.title("Traffic Pressures on Pipes")
root.geometry("640x480")

mcanvas = tk.Canvas(root)
mcanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=mcanvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
mcanvas.configure(yscrollcommand=scrollbar.set)
scrollframe = tk.Frame(mcanvas)
mcanvas_frame = mcanvas.create_window((0, 0), window=scrollframe, anchor="nw")

def on_frame_configure(event):
    mcanvas.configure(scrollregion=mcanvas.bbox("all"))

scrollframe.bind("<Configure>", on_frame_configure)

def on_canvas_configure(event):
    mcanvas.itemconfig(mcanvas_frame, width=event.width)

mcanvas.bind("<Configure>", on_canvas_configure)

# Title and description
tk.Label(scrollframe, text="Traffic Pressures on Buried Pipes",
         font=("Arial", 12, "bold"), anchor="w", justify="left").pack(
             fill="x", padx=10, pady=(10,0))

tk.Label(scrollframe,
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

    row_entry = tk.Entry(row_frame, width=entry_width)
    row_entry.grid(row=0, column=1, sticky="e")
    if tooltip_text:
        Tooltip(row_entry, tooltip_text)

    if unit_text:
        tk.Label(row_frame, text=unit_text, anchor="w").grid(
            row=0, column=2, sticky="w", padx=(5,0))

    # Make label stretch, entry fixed
    row_frame.grid_columnconfigure(0, weight=1)
    row_frame.grid_columnconfigure(1, weight=0)

    return row_entry

# ------------------- Input - Spatial Domain ------------------- #
mframe1 = create_mframe(scrollframe)
tk.Label(mframe1, text="Input - Spatial Domain Parameters",
         font=("Arial", 10, "bold"), anchor="w", justify="left").pack(fill="x", pady=(0,5))

tk.Label(mframe1, text="Input parameters defining and discretizing spatial domain over which to " \
"calculate pressures:", wraplength=600, anchor="w", justify="left").pack(fill="x", pady=(0,5))

# Rows
row1 = create_row(mframe1,
                    "Model length along pipe (x direction):",
                    "Should exceed width of applied wheel or axle plus some allowance\nfor load " \
                    "distribution to each side of extreme point load(s)",
                    "m")
row2 = create_row(mframe1,
                    "Model length across pipe (y direction):",
                    "Should be arbitrarily small number to capture peak pressure at pipe crown, " \
                    "0.1m is recommended",
                    "m")
row3 = create_row(mframe1,
                    "Minimum depth (z direction):",
                    "Recommended not less than 0.5m",
                    "m")
row4 = create_row(mframe1,
                    "Maximum depth (z direction):",
                    "",
                    "m")
row5 = create_row(mframe1,
                    "Number of x divisions for discretization:",
                    "",
                    "   ")
row6 = create_row(mframe1,
                    "Number of y divisions for discretization:",
                    "Recommended value of 1 since should be small",
                    "   ")
row7 = create_row(mframe1,
                    "Number of z divisions for discretization:",
                    "",
                    "   ")

# ------------------- Input - Wheel Loads ------------------- #
mframe2 = create_mframe(scrollframe)
tk.Label(mframe2, text="Input - Wheel Loading", font=("Arial", 10, "bold"), anchor="w", 
         justify="left").pack(fill="x", pady=(0,5))
tk.Label(mframe2, text="Input wheel loads as a system of dynamic point loads. Patch loading " \
"can be approximated by discretising into a set of point loads.", wraplength=600, anchor="w",
justify="left").pack(fill="x", pady=(0,5))
frame8 = tk.Frame(mframe2)
frame8.pack(fill="x", pady=2)
tk.Label(frame8, text="Set of point loads as [x1, y1, P1], [x2, y2, P2], ...",
         anchor="w", justify="left").grid(row=0, column=0, sticky="w", padx=(0,5))
entry8 = tk.Entry(frame8)
entry8.grid(row=0, column=1, sticky="ew")
frame8.grid_columnconfigure(1, weight=1)
tk.Label(mframe2, text="Note: x-y plane assumed centered on origin at (0,0)").pack(
    anchor="w", pady=(2,2))

# ------------------- Results ------------------- #
mframe3 = create_mframe(scrollframe)
tk.Label(mframe3, text="Output - Results", font=("Arial", 10, "bold"), anchor="w", 
         justify="left").pack(fill="x", pady=(0,5))

frame11 = tk.Frame(mframe3)
frame11.pack(fill="x", pady=2)
tk.Label(frame11, text="Traffic surcharge, Ps, can be obtained by averaging pressures over a " \
"length of pipe (recommended 1m). Here, the greatest average pressure over a given length is " \
"calculated for each depth using the row of elements along x closest to y = 0.", wraplength=600, 
anchor="w", justify="left").pack(fill="x", pady=(0,5))
row12 = create_row(mframe3,
                    "Length of pipe over which to average pressures:",
                    "0.9 - 1.0m is recommended",
                    "m")

frame9 = tk.Frame(mframe3)
frame9.pack(fill="x", pady=2)
button1 = tk.Button(frame9, text="Solve for Pressures & Traffic Surcharge", command=solve)
button1.grid(row=0, column=0, sticky="ew")
frame9.rowconfigure(0, weight=1)
frame9.columnconfigure(0, weight=1)

frame10 = tk.Frame(mframe3)
frame10.pack(fill="x", pady=2)
button2 = tk.Button(frame10, text="Save Pressures to File", command=save_pressures)
button2.grid(row=0, column=0, sticky="ew")
frame10.rowconfigure(0, weight=1)
frame10.columnconfigure(0, weight=1)



# return results in Z, Y, X, pressure


root.mainloop()

print(solution.lib_load_points["userinput"])

""" a = "[[-0.45, 0, 60], [0.45, 0, 60]]"
b = json.loads(a)
print(b) """

""" solve = PipePressures()
solve.mesh(1, 0.1, 2, 10, 1 , 16)
solve.load_points("Field", [[-0.45, 0, 60], [0.45, 0, 60]])
solve.boussinesq_pressure("Field") 
# 60kN on 0.4m squares at 0.9m centres
# 45deg 150mm pavement, 30deg thereafter """


