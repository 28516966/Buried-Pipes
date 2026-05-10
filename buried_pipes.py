# ==============================================================================
# Imports
# ==============================================================================
import csv
import json
import math
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import FixedLocator, FormatStrFormatter, NullFormatter
from matplotlib.widgets import Slider
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

# ==============================================================================
# Class for Model Parameters and Methods
# ==============================================================================

class PipePressures:
    def __init__(self):
        self.lib_load_points = {}
        self.results_pressures = []
        self.results_Ps = []
    def mesh(self, x, y, z, xdivs, ydivs, zdivs, zmin=0.5):
        """Defines parameters for spatial discretisation into a series of nodes for which to solve
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
        self.xdivs = xdivs
        self.ydivs = ydivs
        self.zdivs = zdivs
        self.xinc = x / xdivs
        self.yinc = y / ydivs
        self.zinc = z / zdivs
        xmin = - x/2 + self.xinc/2
        ymin = - y/2 + self.yinc/2
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
        self.lib_load_points[load_name] = wheel_loads
        return

    def boussinesq_pressure(self, load_name="userinput"):
        """Calculate Boussinesq pressures across discretised spatial coordinates for named load
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
    
    def design_pressure_Ps(self, avg_len):
        """Calculates design traffic surcharge pressure, Ps [kPa], by averaging pressures calculated
        for different elements over some length.

        Args:
            avg_len (float): Length over which to take average pressure [m].
        """
        # Identify central y row of concern to perform averaging on
        y_arr_len = len(self.y_arr)
        if y_arr_len % 2 != 0: # if number of points is odd, central y=0
            y_pos = int((y_arr_len - 1) / 2)
        else: # else use nearest row in +y
            y_pos = int(y_arr_len / 2)
        # Determine number of elements along x comprising length to average over
        avg_x_num = round(avg_len / self.xinc) # number of elements comprising average
        x_pos_num = len(self.x_arr) - avg_x_num + 1 # number of positions to take average at
        for i in range(0, len(self.z_arr)): # for each z value
            i_z_ini = i * self.ydivs * self.xdivs
            i_x_ini = i_z_ini + (y_pos * self.xdivs)
            max_p = 0
            for j in range(0, x_pos_num): # for each position to calculate average
                tot_p = 0
                for k in range(0, avg_x_num): # for each node in length to average
                    row_index = i_x_ini + j + k
                    row = self.results_pressures[row_index]
                    tot_p += row[3]
                avg_p = tot_p / avg_x_num
                if max_p < avg_p:
                    max_p = avg_p
            self.results_Ps.append([self.z_arr[i], max_p])
        return

# ==============================================================================
# Functions Called By GUI to Produce & Manipulate Results
# ==============================================================================

def solve():
    """Takes inputs from GUI and creates an instance of class 'PipePressures' to solve"""
    global solution
    try:
        solution.clear()
    except:
        pass
    solution = PipePressures()
    # Read spatial parameters and discretise mesh
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
    solution.design_pressure_Ps(float(row12.get()))
    # Populate drop-box for plotting
    combobox14['values'] = solution.z_arr.tolist()
    combobox17['values'] = solution.y_arr.tolist()
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
        for row in solution.results_Ps:
            writer.writerow(row)
    return

def plot_results(y, z):
    # Extract results
    global solution
    np_results_Ps = np.asarray(solution.results_Ps)
    np_res_p = np.asarray(solution.results_pressures)

    # Set up fig15
    val_z = np_results_Ps[:, 0]
    val_Ps = np_results_Ps[:, 1]
    val_x = solution.x_arr
    val_y = solution.y_arr
    val_X, val_Y = np.meshgrid(val_x, val_y)
    res = np_res_p[np_res_p[:, 0] == z]
    val_Z = np.zeros_like(val_X, dtype=float)
    for row in range(val_X.shape[0]):
        for col in range(val_X.shape[1]):
            for j in res:
                if (val_X[row, col] == j[2]) and (val_Y[row, col] == j[1]):
                    val_Z[row, col] = j[3]
                    break
    global fig15
    fig15.clear()
    ax1 = fig15.add_subplot(1, 2, 1)
    ax2 = fig15.add_subplot(1, 2, 2, projection='3d')
    ax1.plot(val_Ps, val_z, color="blue", linewidth=2, linestyle="-", marker="*")
    ax1.set_title("Design Surcharge Pressure Ps with Depth")
    ax1.set_xlabel("Surcharge Pressure [kPa], Ps")
    ax1.set_ylabel("Depth [m], z")
    ax1.invert_yaxis()
    ax1.minorticks_on()
    ax1.grid(which='major',
            linestyle='-',
            linewidth=0.8,
            color='gray')
    ax1.grid(which='minor',
            linestyle=':',
            linewidth=0.5,
            color='lightgray')
    ax2.plot_surface(val_X, val_Y, val_Z, cmap="viridis")
    ax2.set_title("Boussinesq Pressures Across X-Y Plane at Specified Depth")
    ax2.set_xlabel("x [m]")
    ax2.set_ylabel("y [m]")
    ax2.set_zlabel("Boussinesq Pressure [kPa]")
    plotcanvas15.draw()

    # Set up fig16
    val_x2 = solution.x_arr
    val_z2 = solution.z_arr
    val_X2, val_Y2 = np.meshgrid(val_x2, val_z2)
    res2 = np_res_p[np_res_p[:, 1] == y]
    val_Z2 = np.zeros_like(val_X2, dtype=float)
    for row in range(val_X2.shape[0]):
        for col in range(val_X2.shape[1]):
            for j in res2: # Z, Y, X, Pressure
                if (val_X2[row, col] == j[2]) and (val_Y2[row, col] == j[0]):
                    val_Z2[row, col] = j[3]
                    break
    global fig16
    fig16.clear()
    ax3 = fig16.add_subplot(1, 2, 1)
    ax4 = fig16.add_subplot(1, 2, 2, projection='3d')
    ax3.plot(val_z, val_Ps, color="blue", linewidth=2, linestyle="-", marker="*")
    ax3.set_title("Design Surcharge Pressure Ps with Depth")
    ax3.set_xscale("log")
    ax3.set_yscale("log")
    ax3.set_xlim(0.5, 10)
    ax3.set_ylim(5, 500)
    x_ticks = [0.5, 1, 2, 3, 4, 5, 10]
    y_ticks = [5, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500]
    ax3.xaxis.set_major_locator(FixedLocator(x_ticks))
    ax3.yaxis.set_major_locator(FixedLocator(y_ticks))
    ax3.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax3.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax3.set_xticks(x_ticks)
    ax3.set_yticks(y_ticks)
    ax3.xaxis.set_minor_locator(FixedLocator(x_ticks))
    ax3.yaxis.set_minor_locator(FixedLocator(y_ticks))
    ax3.xaxis.set_minor_formatter(NullFormatter())
    ax3.yaxis.set_minor_formatter(NullFormatter())
    ax3.set_xticks([0.6, 0.7, 0.8, 0.9, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.2, 2.4, 
                    2.6, 2.8, 3.2, 3.4, 3.6, 3.8, 4.2, 4.4, 4.6, 4.8, 6, 7, 8, 9], minor=True)
    ax3.set_yticks([6, 7, 8, 9, 15, 25, 35, 45, 60, 70, 80, 90, 120, 140, 160, 180, 
                    220, 240, 260, 280, 320, 340, 360, 380, 420, 440, 460, 480], 
                    minor=True)
    ax3.set_xlabel("Cover Depth [m], H")
    ax3.set_ylabel("Surcharge Pressure [kPa], Ps")
    ax3.grid(which='major',
            linestyle='-',
            linewidth=0.8,
            color='gray')
    ax3.grid(which='minor',
            linestyle=':',
            linewidth=0.5,
            color='lightgray')
    ax4.plot_surface(val_X2, val_Y2, val_Z2, cmap="viridis")
    ax4.set_title("Boussinesq Pressures Across X-Z Plane at Specified Y")
    ax4.set_xlabel("x [m]")
    ax4.set_ylabel("z [m]")
    ax4.set_zlabel("Boussinesq Pressure [kPa]")
    ax4.view_init(elev=30, azim=120)
    plotcanvas16.draw()
    # fig_py = plt.figure()
    # ax_py = fig_py.add_subplot(111, projection='3d')
    # ax_py.plot_surface(val_X2, val_Y2, val_Z2, cmap="viridis")
    # ax_py.set_title("Boussinesq Pressures Across X-Z Plane at Y=0")
    # ax_py.set_xlabel("x [m]")
    # ax_py.set_ylabel("z [m]")
    # ax_py.set_zlabel("Boussinesq Pressure [kPa]")
    # plt.show() 
    return


def discretise_wheel(load, pressure, x=0, y=0, r1r2=0.5):
    """Converts a point wheel load and contact pressure into a patch load over a circular area, then
    discretises this into a set of 10 point loads (4 quadrants, and 6 annular sectors)

    Args:
        load (float): Overall point load of wheel [kN]
        pressure (float): Contact pressure [kPa]
        x (float, optional): Position of centre of wheel [m]. Defaults to 0.
        y (float, optional): Position of centre of wheel [m]. Defaults to 0.
        r1r2 (float, optional): Ratio of inner quadrant radius to total radius. Defaults to 0.5.

    Returns:
        list of lists in format [x, y, P]
    """
    area = load / pressure
    r2 = (area / math.pi) ** 0.5
    r1 = r1r2 * r2
    a_quad = 0.25 * math.pi * r1**2
    y_quad = 4 * r1 / (3 * math.pi)
    p_quad = a_quad / area * load
    alpha = 2 * math.pi / 12
    a_sect = alpha * (r2**2 - r1**2)
    y_sect = 2 * math.sin(alpha) * (r2**3 - r1**3) / (3 * alpha * (r2**2 - r1**2))
    x1_sect = y_sect * math.cos(alpha)
    y1_sect = y_sect * math.cos(alpha)
    p_sect = a_sect / area * load
    return [[x + y_quad, y + y_quad, p_quad], [x - y_quad, y + y_quad, p_quad], 
            [x - y_quad, y - y_quad, p_quad], [x + y_quad, y - y_quad, p_quad], 
            [x + x1_sect, y + y1_sect, p_sect], [x, y + y_sect, p_sect],
            [x - x1_sect, y + y1_sect, p_sect], [x - x1_sect, y - y1_sect, p_sect],
            [x, y - y_sect, p_sect], [x + x1_sect, y - y1_sect, p_sect]]

def convert_patch_loads(widget, wheel_loads, contact_pressure):
    output = []
    print("wheelloads", wheel_loads)
    for wheel in wheel_loads:
        output.extend(discretise_wheel(wheel[2], contact_pressure, x=wheel[0], 
                                       y=wheel[1]))
    widget.delete("1.0", "end")
    widget.insert("1.0", str(output))
    return

def show_load_dialog():
    popup = tk.Toplevel()
    popup.title("Wheel Load Calculator")
    
    # Make the window modal - comment out to enable clicking back to root window
    # popup.grab_set()
    
    # Text widget (read-only)
    p_frame1 = tk.Frame(popup)
    p_frame1.pack(fill="both", expand=True, padx=10, pady=(10,5))
    p_text1 = tk.Text(p_frame1, wrap="word", width=60, height=10)
    p_text1.tag_configure("bold", font=("Arial", 10, "bold"))
    p_text1.tag_configure("normal", font=("Arial", 10))
    p_text1.insert("1.0", "DMRB CD 533 Loading\n", "bold")
    p_text1.insert("end", 
    "Main road loading - 45 units HB loading: static wheel of 112.5 kN including impact factor of "\
    "1.25, contact pressure 1100 kPa. Comprises eight wheels spread across two axles with wheel " \
    "spacing 1.0m, axle spacing 1.8m. \nPosition #1 - Axles Straddling Origin:\n"
    "[[-1.5, -0.9, 112.5], [-0.5, -0.9, 112.5], [0.5, -0.9, 112.5], [1.5, -0.9, 112.5], " \
    "[-1.5, 0.9, 112.5], [-0.5, 0.9, 112.5], [0.5, 0.9, 112.5], [1.5, 0.9, 112.5]]\n" \
    "Position #2 - One Axle Directly Over Origin:\n"
    "[[-1.5, 0, 112.5], [-0.5, 0, 112.5], [0.5, 0, 112.5], [1.5, 0, 112.5], " \
    "[-1.5, 1.8, 112.5], [-0.5, 1.8, 112.5], [0.5, 1.8, 112.5], [1.5, 1.8, 112.5]]\n\n" \
    "Field loading - two wheels 1.0 m apart, static weight 30 kN, impact factor of 2 giving " \
    "dynamic wheel load of 60 kN, (contact pressure assumed 400 kPa):\n" \
    "[[-0.5, 0, 60], [0.5, 0, 60]]\n\n" \
    "Filter drain loading - 30 units HB loading (62.5 kN wheel load), however, considering only " \
    "two wheels with an increased dynamic factor for total wheel load 87.5 kN:\n"
    "[[-0.5, 0, 87.5], [0.5, 0, 87.5]]\n\n", "normal")
    p_text1.insert("end", "Eurocode Loading\n", "bold")
    p_text1.insert("end", 
    "Load model 2 - two wheels 2m apart with wheel load 200kN, contact pressure 1250 kPa with" \
    "contact area being a 0.4m square area:\n" \
    "[[-1, 0, 200], [1, 0, 200]]\n\n", "normal")
    p_text1.insert("end", "Historic Loading (Young and O'Reilly (1983), BS 5400-2:1978)\n", "bold")
    p_text1.insert("end", 
    "Main road loading - 45 units HB loading: static wheel of 112.5 kN including impact factor of "\
    "1.25, contact pressure 1100 kPa. Comprises eight wheels spread across two axles with wheel " \
    "spacing 1.0m, axle spacing 1.8m. \nPosition #1 - Axles Straddling Origin:\n"
    "[[-1.5, -0.9, 112.5], [-0.5, -0.9, 112.5], [0.5, -0.9, 112.5], [1.5, -0.9, 112.5], " \
    "[-1.5, 0.9, 112.5], [-0.5, 0.9, 112.5], [0.5, 0.9, 112.5], [1.5, 0.9, 112.5]]\n" \
    "Position #2 - One Axle Directly Over Origin:\n"
    "[[-1.5, 0, 112.5], [-0.5, 0, 112.5], [0.5, 0, 112.5], [1.5, 0, 112.5], " \
    "[-1.5, 1.8, 112.5], [-0.5, 1.8, 112.5], [0.5, 1.8, 112.5], [1.5, 1.8, 112.5]]\n\n" \
    "Light road loading - two wheels 0.9 m apart, static weight 70 kN, impact factor of 1.5 " \
    "giving dynamic weight 105 kN, contact pressure 700 kPa:\n" \
    "[[-0.45, 0, 105], [0.45, 0, 105]]\n\n" 
    "Field loading - two wheels 0.9 m apart, static weight 30 kN, impact factor of 2 giving " \
    "dynamic wheel load of 60 kN, contact pressure 400 kPa:\n" \
    "[[-0.45, 0, 60], [0.45, 0, 60]]\n\n", "normal")
    p_text1.config(state="disabled")  # make read-only but still selectable
    p_text1.pack(padx=10, pady=10, side="left", fill="both", expand=True)
    
    # Add a scrollbar
    p_scrollbar1 = ttk.Scrollbar(p_frame1, orient="vertical", command=p_text1.yview)
    p_text1.config(yscrollcommand=p_scrollbar1.set)
    p_scrollbar1.pack(side="right", fill="y")
    
    # Add inputs
    p_frame2 = tk.Frame(popup)
    p_frame2.pack(fill="x", padx=10, pady=(5,10))
    tk.Label(p_frame2, text="Wheel loading to discretise:").pack(side="left")
    p_entry2 = tk.Entry(p_frame2)
    p_entry2.pack(side="right", fill="x", expand=True, padx=5)
    
    p_frame3 = tk.Frame(popup)
    p_frame3.pack(fill="x", padx=10, pady=(5,10))
    tk.Label(p_frame3, text="Contact pressure for wheels [kPa]").pack(side="left")
    p_entry3 = tk.Entry(p_frame3, width=15)
    p_entry3.pack(side="right", padx=5)

    p_frame4 = tk.Frame(popup)
    p_frame4.pack(fill="x", pady=2)
    p_button4 = tk.Button(p_frame4, text="Discretize wheel patch loading into set of 10 point " \
    "loads", command=lambda: convert_patch_loads(
        p_text5, json.loads(p_entry2.get()), float(p_entry3.get())))
    p_button4.grid(row=0, column=0, sticky="ew")
    p_frame4.rowconfigure(0, weight=1)
    p_frame4.columnconfigure(0, weight=1)

    p_frame5 = tk.Frame(popup)
    p_frame5.pack(fill="both", expand=True, padx=10, pady=(10,5))
    p_text5 = tk.Text(p_frame5, wrap="word", width=60, height=10)
    p_text5.tag_configure("normal", font=("Arial", 10))
    p_text5.insert("1.0", "Results Will Display Here", "normal")
    p_text5.pack(padx=10, pady=10, side="left", fill="both", expand=True)

    # Close button
    btn = ttk.Button(popup, text="Close", command=popup.destroy)
    btn.pack(pady=(0,10))
    
    # Center the popup over root
    popup.update_idletasks()
    w = popup.winfo_width()
    h = popup.winfo_height()
    ws = popup.winfo_screenwidth()
    hs = popup.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    popup.geometry(f"{w}x{h}+{x}+{y}")
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
        """Starts delayed tooltip appearance"""
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show)

    def unschedule(self):
        """Cancels any pending tooltip timer"""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show(self, event=None):
        """Displays tooltip"""
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
        """Hides tooltip"""
        self.unschedule()
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# ==============================================================================
# GUI
# ==============================================================================

# ==============================================================================
# Root Window and Main Frames
# ==============================================================================

root = tk.Tk()
root.title("Traffic Pressures on Pipes")
root.geometry("1080x1080")

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

# ==============================================================================
# Helper Functions for GUI Elements
# ==============================================================================

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

# ==============================================================================
# GUI Inputs - Spatial Domain Parameters
# ==============================================================================

mframe1 = create_mframe(scrollframe)
tk.Label(mframe1, text="Input - Spatial Domain Parameters",
         font=("Arial", 10, "bold"), anchor="w", justify="left").pack(fill="x", pady=(0,5))

tk.Label(mframe1, text="Input parameters defining and discretising spatial domain over which to " \
"calculate pressures:", wraplength=600, anchor="w", justify="left").pack(fill="x", pady=(0,5))

# Rows
row1 = create_row(mframe1,
                    "Model length along pipe (x direction):",
                    "Should exceed width of applied wheel or axle plus some allowance\nfor load " \
                    "distribution to each side of extreme point load(s)",
                    "m")
row2 = create_row(mframe1,
                    "Model length across pipe (y direction):",
                    "Should be arbitrarily small number to capture peak pressure at \npipe crown, " \
                    "0.3m is recommended (3 number 0.1m elements)",
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
                    "Number of x divisions for discretisation:",
                    "At least 10 elements per metre is recommended",
                    "   ")
row6 = create_row(mframe1,
                    "Number of y divisions for discretisation:",
                    "3 elements is recommended to enable pressure surface plotting, \nnote only central " \
                    "row of elements is used to calculate Ps",
                    "   ")
row7 = create_row(mframe1,
                    "Number of z divisions for discretisation:",
                    "",
                    "   ")

# ==============================================================================
# GUI Inputs - Wheel Loading
# ==============================================================================

mframe2 = create_mframe(scrollframe)
tk.Label(mframe2, text="Input - Wheel Loading", font=("Arial", 10, "bold"), anchor="w", 
         justify="left").pack(fill="x", pady=(0,5))
tk.Label(mframe2, text="Input wheel loads as a system of dynamic point loads. Patch loading " \
"can be approximated by discretising into a set of point loads.", wraplength=600, anchor="w",
justify="left").pack(fill="x", pady=(0,5))

frame16 = tk.Frame(mframe2)
frame16.pack(fill="x", pady=2)
button16 = tk.Button(frame16, text="Reference Wheel Loads and Patch Load Conversion Calculator", 
                     command=show_load_dialog)
button16.grid(row=0, column=0, sticky="ew")
frame16.rowconfigure(0, weight=1)
frame16.columnconfigure(0, weight=1)

frame8 = tk.Frame(mframe2)
frame8.pack(fill="x", pady=2)
tk.Label(frame8, text="Set of point loads as [x1, y1, P1], [x2, y2, P2], ...",
         anchor="w", justify="left").grid(row=0, column=0, sticky="w", padx=(0,5))
entry8 = tk.Entry(frame8)
entry8.grid(row=0, column=1, sticky="ew")
frame8.grid_columnconfigure(1, weight=1)
tk.Label(mframe2, text="Note: x-y plane assumed centered on origin at (0,0)").pack(
    anchor="w", pady=(2,2))

# ==============================================================================
# GUI Outputs - Results
# ==============================================================================

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
button9 = tk.Button(frame9, text="Solve for Pressures & Traffic Surcharge", command=solve)
button9.grid(row=0, column=0, sticky="ew")
frame9.rowconfigure(0, weight=1)
frame9.columnconfigure(0, weight=1)

frame10 = tk.Frame(mframe3)
frame10.pack(fill="x", pady=2)
button10 = tk.Button(frame10, text="Save Pressures to File", command=save_pressures)
button10.grid(row=0, column=0, sticky="ew")
frame10.rowconfigure(0, weight=1)
frame10.columnconfigure(0, weight=1)

frame13 = tk.Frame(mframe3)
frame13.pack(fill="x", pady=2)
button13 = tk.Button(frame13, text="Save Traffic Surcharge Ps to File", command=save_traffic_surcharge)
button13.grid(row=0, column=0, sticky="ew")
frame13.rowconfigure(0, weight=1)
frame13.columnconfigure(0, weight=1)

frame14 = tk.Frame(mframe3)
frame14.pack(fill="x", pady=2)
label14 = tk.Label(frame14, text="Plot pressures on x-y plane at depth, z:", anchor="w", 
                   justify="left", width=35)
label14.grid(row=0, column=0, sticky="w")
combobox14 = ttk.Combobox(frame14)
combobox14.grid(row=0, column=1, sticky="e")
tk.Label(frame14, text="m", anchor="w").grid(row=0, column=2, sticky="w", padx=(5,0))
frame14.grid_columnconfigure(0, weight=1)
frame14.grid_columnconfigure(1, weight=0)

frame17 = tk.Frame(mframe3)
frame17.pack(fill="x", pady=2)
label17 = tk.Label(frame17, text="Plot pressures on x-z plane at y:", anchor="w", 
                   justify="left", width=35)
label17.grid(row=0, column=0, sticky="w")
combobox17 = ttk.Combobox(frame17)
combobox17.grid(row=0, column=1, sticky="e")
tk.Label(frame17, text="m", anchor="w").grid(row=0, column=2, sticky="w", padx=(5,0))
frame17.grid_columnconfigure(0, weight=1)
frame17.grid_columnconfigure(1, weight=0)


def on_plot():
    y_value = combobox17.get()
    z_value = combobox14.get()
    if not (y_value and z_value):
        return
    plot_results(float(y_value), float(z_value))

frame15 = tk.Frame(mframe3)
frame15.pack(fill="x", pady=2)
button15 = tk.Button(frame15, text="Generate Results Plots", 
                     command=on_plot)
button15.grid(row=0, column=0, sticky="ew")
frame15.rowconfigure(0, weight=1)
frame15.columnconfigure(0, weight=1)

fig15 = Figure(figsize=(8, 8))
ax1 = fig15.add_subplot(111)
plotcanvas15 = FigureCanvasTkAgg(fig15, master=mframe3)
plotcanvas15.draw()
plotcanvas15.get_tk_widget().pack(fill="both", expand=True)

fig16 = Figure(figsize=(8, 8))
ax3 = fig16.add_subplot(111)
plotcanvas16 = FigureCanvasTkAgg(fig16, master=mframe3)
plotcanvas16.draw()
plotcanvas16.get_tk_widget().pack(fill="both", expand=True)


# Default values
row1.insert(0, "2")
row2.insert(0, "0.3")
row3.insert(0, "0.5")
row4.insert(0, "2")
row5.insert(0, "20")
row6.insert(0, "3")
row7.insert(0, "16")
entry8.insert(0, "[[-0.45, 0, 60], [0.45, 0, 60]]")
row12.insert(0, "1")
root.mainloop()
# to do: add other plots, log plot of Ps, surface pressures in x-z plane
