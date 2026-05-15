"""
====================================================================================================
Technical Basis
====================================================================================================
DMRB loads are taken from CD 533.
Eurocode loads are taken from BS 9295.
Historic loads are taken from Young and O'Reilly (1983).

It should be noted that the charts for construction vehicle loading produced by Young and O'Reilly
(1983) and reproduced in BS 9295 will produce different results than this code. This is because this
code discretises wheel loads over an assumed circular contact area into ten different elements after
Nath (1981). However, Young and O'Reilly pressures appear to be obtained by discretising each wheel
load into quadrants.

====================================================================================================
References
====================================================================================================
British Standards Institution (2023). BS 9295 AMD 1. Guide to the Structural Design of Buried 
    Pipelines.
Nath, P. (1981). Pressures on Buried Pipes Due to Revised HB Loading.
National Highways. (2025). CD 533 V1.2.0 Determination of pipe and bedding combinations for drainage 
    works.
Young, O.C. and O’Reilly, M.P. (1983). A Guide to Design Loadings for Buried Rigid Pipes.
Young, O. and Trott, J. (1984). Buried Rigid Pipes. CRC Press.

====================================================================================================
Build Instructions
====================================================================================================
pyinstaller --onefile --noconsole --name "buried_pipes_traffic_pressure" buried_pipes.py

"""

# ==================================================================================================
# Imports
# ==================================================================================================
import ast
import csv
import json
import math
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import LogNorm
from matplotlib.cm import ScalarMappable
from matplotlib.figure import Figure
from matplotlib.ticker import FixedLocator, FormatStrFormatter, NullFormatter
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# from matplotlib.widgets import Slider

# ==================================================================================================
# Hard Coded Reference Loads
# ==================================================================================================
# L1 prefix denotes wheel loads represented by points
# Otherwise loads have been discretised into 10 point loads per wheel using contact pressure and
# assuming a circular contact area
# 10t = 200kN, 30t = 590kN

ref_loads = {
    "L1_DMRBMainRoad1": [[-1.5, -0.9, 112.5], [-0.5, -0.9, 112.5], [0.5, -0.9, 112.5], 
                        [1.5, -0.9, 112.5], [-1.5, 0.9, 112.5], [-0.5, 0.9, 112.5], 
                        [0.5, 0.9, 112.5], [1.5, 0.9, 112.5]],
    "L1_DMRBMainRoad2": [[-1.5, 0, 112.5], [-0.5, 0, 112.5], [0.5, 0, 112.5], 
                        [1.5, 0, 112.5], [-1.5, 1.8, 112.5], [-0.5, 1.8, 112.5], 
                        [0.5, 1.8, 112.5], [1.5, 1.8, 112.5]],
    "L1_DMRBFilter": [[-0.5, 0, 87.5], [0.5, 0, 87.5]],
    "L1_DMRBField": [[-0.5, 0, 60], [0.5, 0, 60]],
    "DMRBMainRoad1": [[-1.462, -0.862, 7.031], [-1.538, -0.862, 7.031], [-1.538, -0.938, 7.031], 
                        [-1.462, -0.938, 7.031], [-1.384, -0.784, 14.062], [-1.5, -0.766, 14.062], 
                        [-1.616, -0.784, 14.062], [-1.616, -1.016, 14.062], [-1.5, -1.034, 14.062], 
                        [-1.384, -1.016, 14.062], [-0.462, -0.862, 7.031], [-0.538, -0.862, 7.031], 
                        [-0.538, -0.938, 7.031], [-0.462, -0.938, 7.031], [-0.384, -0.784, 14.062], 
                        [-0.5, -0.766, 14.062], [-0.616, -0.784, 14.062], [-0.616, -1.016, 14.062], 
                        [-0.5, -1.034, 14.062], [-0.384, -1.016, 14.062], [0.538, -0.862, 7.031], 
                        [0.462, -0.862, 7.031], [0.462, -0.938, 7.031], [0.538, -0.938, 7.031], 
                        [0.616, -0.784, 14.062], [0.5, -0.766, 14.062], [0.384, -0.784, 14.062], 
                        [0.384, -1.016, 14.062], [0.5, -1.034, 14.062], [0.616, -1.016, 14.062], 
                        [1.538, -0.862, 7.031], [1.462, -0.862, 7.031], [1.462, -0.938, 7.031], 
                        [1.538, -0.938, 7.031], [1.616, -0.784, 14.062], [1.5, -0.766, 14.062], 
                        [1.384, -0.784, 14.062], [1.384, -1.016, 14.062], [1.5, -1.034, 14.062], 
                        [1.616, -1.016, 14.062], [-1.462, 0.938, 7.031], [-1.538, 0.938, 7.031], 
                        [-1.538, 0.862, 7.031], [-1.462, 0.862, 7.031], [-1.384, 1.016, 14.062], 
                        [-1.5, 1.034, 14.062], [-1.616, 1.016, 14.062], [-1.616, 0.784, 14.062], 
                        [-1.5, 0.766, 14.062], [-1.384, 0.784, 14.062], [-0.462, 0.938, 7.031], 
                        [-0.538, 0.938, 7.031], [-0.538, 0.862, 7.031], [-0.462, 0.862, 7.031], 
                        [-0.384, 1.016, 14.062], [-0.5, 1.034, 14.062], [-0.616, 1.016, 14.062], 
                        [-0.616, 0.784, 14.062], [-0.5, 0.766, 14.062], [-0.384, 0.784, 14.062], 
                        [0.538, 0.938, 7.031], [0.462, 0.938, 7.031], [0.462, 0.862, 7.031], 
                        [0.538, 0.862, 7.031], [0.616, 1.016, 14.062], [0.5, 1.034, 14.062], 
                        [0.384, 1.016, 14.062], [0.384, 0.784, 14.062], [0.5, 0.766, 14.062], 
                        [0.616, 0.784, 14.062], [1.538, 0.938, 7.031], [1.462, 0.938, 7.031], 
                        [1.462, 0.862, 7.031], [1.538, 0.862, 7.031], [1.616, 1.016, 14.062], 
                        [1.5, 1.034, 14.062], [1.384, 1.016, 14.062], [1.384, 0.784, 14.062], 
                        [1.5, 0.766, 14.062], [1.616, 0.784, 14.062]],
    "DMRBMainRoad2": [[-1.462, 0.038, 7.031], [-1.538, 0.038, 7.031], [-1.538, -0.038, 7.031], 
                      [-1.462, -0.038, 7.031], [-1.384, 0.116, 14.062], [-1.5, 0.134, 14.062], 
                      [-1.616, 0.116, 14.062], [-1.616, -0.116, 14.062], [-1.5, -0.134, 14.062], 
                      [-1.384, -0.116, 14.062], [-0.462, 0.038, 7.031], [-0.538, 0.038, 7.031], 
                      [-0.538, -0.038, 7.031], [-0.462, -0.038, 7.031], [-0.384, 0.116, 14.062], 
                      [-0.5, 0.134, 14.062], [-0.616, 0.116, 14.062], [-0.616, -0.116, 14.062], 
                      [-0.5, -0.134, 14.062], [-0.384, -0.116, 14.062], [0.538, 0.038, 7.031], 
                      [0.462, 0.038, 7.031], [0.462, -0.038, 7.031], [0.538, -0.038, 7.031], 
                      [0.616, 0.116, 14.062], [0.5, 0.134, 14.062], [0.384, 0.116, 14.062], 
                      [0.384, -0.116, 14.062], [0.5, -0.134, 14.062], [0.616, -0.116, 14.062], 
                      [1.538, 0.038, 7.031], [1.462, 0.038, 7.031], [1.462, -0.038, 7.031], 
                      [1.538, -0.038, 7.031], [1.616, 0.116, 14.062], [1.5, 0.134, 14.062], 
                      [1.384, 0.116, 14.062], [1.384, -0.116, 14.062], [1.5, -0.134, 14.062], 
                      [1.616, -0.116, 14.062], [-1.462, 1.838, 7.031], [-1.538, 1.838, 7.031], 
                      [-1.538, 1.762, 7.031], [-1.462, 1.762, 7.031], [-1.384, 1.916, 14.062], 
                      [-1.5, 1.934, 14.062], [-1.616, 1.916, 14.062], [-1.616, 1.684, 14.062], 
                      [-1.5, 1.666, 14.062], [-1.384, 1.684, 14.062], [-0.462, 1.838, 7.031], 
                      [-0.538, 1.838, 7.031], [-0.538, 1.762, 7.031], [-0.462, 1.762, 7.031], 
                      [-0.384, 1.916, 14.062], [-0.5, 1.934, 14.062], [-0.616, 1.916, 14.062], 
                      [-0.616, 1.684, 14.062], [-0.5, 1.666, 14.062], [-0.384, 1.684, 14.062], 
                      [0.538, 1.838, 7.031], [0.462, 1.838, 7.031], [0.462, 1.762, 7.031], 
                      [0.538, 1.762, 7.031], [0.616, 1.916, 14.062], [0.5, 1.934, 14.062], 
                      [0.384, 1.916, 14.062], [0.384, 1.684, 14.062], [0.5, 1.666, 14.062], 
                      [0.616, 1.684, 14.062], [1.538, 1.838, 7.031], [1.462, 1.838, 7.031], 
                      [1.462, 1.762, 7.031], [1.538, 1.762, 7.031], [1.616, 1.916, 14.062], 
                      [1.5, 1.934, 14.062], [1.384, 1.916, 14.062], [1.384, 1.684, 14.062], 
                      [1.5, 1.666, 14.062], [1.616, 1.684, 14.062]],
    "DMRB_Filter": [[-0.472, 0.028, 3.75], [-0.528, 0.028, 3.75], [-0.528, -0.028, 3.75], 
                    [-0.472, -0.028, 3.75], [-0.415, 0.085, 7.5], [-0.5, 0.098, 7.5], 
                    [-0.585, 0.085, 7.5], [-0.585, -0.085, 7.5], [-0.5, -0.098, 7.5], 
                    [-0.415, -0.085, 7.5], [0.528, 0.028, 3.75], [0.472, 0.028, 3.75], 
                    [0.472, -0.028, 3.75], [0.528, -0.028, 3.75], [0.585, 0.085, 7.5], 
                    [0.5, 0.098, 7.5], [0.415, 0.085, 7.5], [0.415, -0.085, 7.5], 
                    [0.5, -0.098, 7.5], [0.585, -0.085, 7.5]],
    "DMRB_Field": [[-0.454, 0.046, 3.75], [-0.546, 0.046, 3.75], [-0.546, -0.046, 3.75], 
                   [-0.454, -0.046, 3.75], [-0.359, 0.141, 7.5], [-0.5, 0.162, 7.5], 
                   [-0.641, 0.141, 7.5], [-0.641, -0.141, 7.5], [-0.5, -0.162, 7.5], 
                   [-0.359, -0.141, 7.5], [0.546, 0.046, 3.75], [0.454, 0.046, 3.75], 
                   [0.454, -0.046, 3.75], [0.546, -0.046, 3.75], [0.641, 0.141, 7.5], 
                   [0.5, 0.162, 7.5], [0.359, 0.141, 7.5], [0.359, -0.141, 7.5], 
                   [0.5, -0.162, 7.5], [0.641, -0.141, 7.5]],
    "10t_2_300": [[0.098, 0.098, 12.5], [-0.098, 0.098, 12.5], [-0.098, -0.098, 12.5], 
                  [0.098, -0.098, 12.5], [0.296, 0.296, 25.0], [0, 0.342, 25.0], 
                  [-0.296, 0.296, 25.0], [-0.296, -0.296, 25.0], [0, -0.342, 25.0], 
                  [0.296, -0.296, 25.0]],
    "10t_2_700": [[0.064, 0.064, 12.5], [-0.064, 0.064, 12.5], [-0.064, -0.064, 12.5], 
                  [0.064, -0.064, 12.5], [0.194, 0.194, 25.0], [0, 0.224, 25.0], 
                  [-0.194, 0.194, 25.0], [-0.194, -0.194, 25.0], [0, -0.224, 25.0], 
                  [0.194, -0.194, 25.0]],
    "30t_2_300": [[0.168, 0.168, 36.875], [-0.168, 0.168, 36.875], [-0.168, -0.168, 36.875], 
                  [0.168, -0.168, 36.875], [0.509, 0.509, 73.75], [0, 0.588, 73.75], 
                  [-0.509, 0.509, 73.75], [-0.509, -0.509, 73.75], [0, -0.588, 73.75], 
                  [0.509, -0.509, 73.75]],
    "30t_2_700": [[0.11, 0.11, 36.875], [-0.11, 0.11, 36.875], [-0.11, -0.11, 36.875], 
                  [0.11, -0.11, 36.875], [0.333, 0.333, 73.75], [0, 0.385, 73.75], 
                  [-0.333, 0.333, 73.75], [-0.333, -0.333, 73.75], [0, -0.385, 73.75], 
                  [0.333, -0.333, 73.75]],
    "Eurocode_LM1": [[-0.952, 0.048, 12.5], [-1.048, 0.048, 12.5], [-1.048, -0.048, 12.5], 
                     [-0.952, -0.048, 12.5], [-0.855, 0.145, 25.0], [-1, 0.168, 25.0], 
                     [-1.145, 0.145, 25.0], [-1.145, -0.145, 25.0], [-1, -0.168, 25.0], 
                     [-0.855, -0.145, 25.0], [1.048, 0.048, 12.5], [0.952, 0.048, 12.5], 
                     [0.952, -0.048, 12.5], [1.048, -0.048, 12.5], [1.145, 0.145, 25.0], 
                     [1, 0.168, 25.0], [0.855, 0.145, 25.0], [0.855, -0.145, 25.0], 
                     [1, -0.168, 25.0], [1.145, -0.145, 25.0]],
    "Eurocode_LM2": [[-0.552, -0.452, 9.375], [-0.648, -0.452, 9.375], [-0.648, -0.548, 9.375], 
                     [-0.552, -0.548, 9.375], [-0.455, -0.355, 18.75], [-0.6, -0.332, 18.75], 
                     [-0.745, -0.355, 18.75], [-0.745, -0.645, 18.75], [-0.6, -0.668, 18.75], 
                     [-0.455, -0.645, 18.75], [0.648, -0.452, 9.375], [0.552, -0.452, 9.375], 
                     [0.552, -0.548, 9.375], [0.648, -0.548, 9.375], [0.745, -0.355, 18.75], 
                     [0.6, -0.332, 18.75], [0.455, -0.355, 18.75], [0.455, -0.645, 18.75], 
                     [0.6, -0.668, 18.75], [0.745, -0.645, 18.75], [-0.552, -2.452, 9.375], 
                     [-0.648, -2.452, 9.375], [-0.648, -2.548, 9.375], [-0.552, -2.548, 9.375], 
                     [-0.455, -2.355, 18.75], [-0.6, -2.332, 18.75], [-0.745, -2.355, 18.75], 
                     [-0.745, -2.645, 18.75], [-0.6, -2.668, 18.75], [-0.455, -2.645, 18.75], 
                     [0.648, -2.452, 9.375], [0.552, -2.452, 9.375], [0.552, -2.548, 9.375], 
                     [0.648, -2.548, 9.375], [0.745, -2.355, 18.75], [0.6, -2.332, 18.75], 
                     [0.455, -2.355, 18.75], [0.455, -2.645, 18.75], [0.6, -2.668, 18.75], 
                     [0.745, -2.645, 18.75],
                     [-0.552, 0.548, 6.25], [-0.648, 0.548, 6.25], [-0.648, 0.452, 6.25], 
                     [-0.552, 0.452, 6.25], [-0.455, 0.645, 12.5], [-0.6, 0.668, 12.5], 
                     [-0.745, 0.645, 12.5], [-0.745, 0.355, 12.5], [-0.6, 0.332, 12.5], 
                     [-0.455, 0.355, 12.5], [0.648, 0.548, 6.25], [0.552, 0.548, 6.25], 
                     [0.552, 0.452, 6.25], [0.648, 0.452, 6.25], [0.745, 0.645, 12.5], 
                     [0.6, 0.668, 12.5], [0.455, 0.645, 12.5], [0.455, 0.355, 12.5], 
                     [0.6, 0.332, 12.5], [0.745, 0.355, 12.5], [-0.552, 2.548, 6.25], 
                     [-0.648, 2.548, 6.25], [-0.648, 2.452, 6.25], [-0.552, 2.452, 6.25], 
                     [-0.455, 2.645, 12.5], [-0.6, 2.668, 12.5], [-0.745, 2.645, 12.5], 
                     [-0.745, 2.355, 12.5], [-0.6, 2.332, 12.5], [-0.455, 2.355, 12.5], 
                     [0.648, 2.548, 6.25], [0.552, 2.548, 6.25], [0.552, 2.452, 6.25], 
                     [0.648, 2.452, 6.25], [0.745, 2.645, 12.5], [0.6, 2.668, 12.5], 
                     [0.455, 2.645, 12.5], [0.455, 2.355, 12.5], [0.6, 2.332, 12.5], 
                     [0.745, 2.355, 12.5]]
}
solutions = {}

# ==================================================================================================
# Class for Model Parameters and Methods
# ==================================================================================================

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
        """Associates wheel load with class object and adds to library

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

def clear_plots():
    """Clear results plots"""
    global fig15, fig16, fig28, fig28_state
    fig15.clf()
    fig16.clf()
    fig28.clf()

    keys_to_clear = [
        "label_size", 
        "slider_size", 
        "label_mask_y", 
        "slider_mask_y", 
        "label_mask_z", 
        "slider_mask_z",
    ]

    for key in keys_to_clear:
        if fig28_state[key] is not None:
            fig28_state[key].destroy()

    fig28_state = {
        "fig": fig28,
        "ax": ax5,
        "sc": None,
        "x": None,
        "y": None,
        "z": None,
        "v": None,
        "label_size": None,
        "slider_size": None,
        "label_mask_y": None,
        "slider_mask_y": None,
        "label_mask_z": None,
        "slider_mask_z": None,
        "y_cutoff": 0,
        "z_cutoff": 0
    }
    return

def solve_gui():
    """Takes inputs from GUI and creates an instance of class 'PipePressures' for each input 
    load case to solve.
    """
    global solutions
    # Clear existing solutions and plots
    try:
        solutions.clear()
    except:
        pass
    clear_plots()
    # Read spatial parameters and discretise mesh
    x = float(row1.get())
    y = float(row2.get())
    zmin = float(row3.get())
    z = float(row4.get())
    xdivs = int(row5.get())
    ydivs = int(row6.get())
    zdivs = int(row7.get())
    # Read and set wheel loads
    loadcases = ast.literal_eval(entry8.get())
    for key, value in loadcases.items():
        solution = PipePressures()
        solution.mesh(x, y, z, xdivs, ydivs, zdivs, zmin=zmin)
        solution.wheel_loads(value, load_name=key)
        # Solve
        solution.boussinesq_pressure(load_name=key)
        solution.design_pressure_Ps(float(row12.get()))
        solutions[key] = solution
    # Populate drop-boxes for plotting
    combobox14['values'] = [round(v, 3) for v in solution.z_arr.tolist()]
    combobox17['values'] = [round(v, 3) for v in solution.y_arr.tolist()]
    combobox30['values'] = list(solutions.keys())
    return

def solve_Ps(loads):
    """Create instance of class PipePressures(), solve, and return design construction surcharge
    pressure, Ps. This is distinct from solve_gui() since it avoids invoking global variable
    'solution' and does not update GUI comboboxes."""
    sol_gen = PipePressures()
    x = float(row1.get())
    y = float(row2.get())
    z = float(row3.get())
    zmin = float(row4.get())
    xdivs = int(row5.get())
    ydivs = int(row6.get())
    zdivs = int(row7.get())
    sol_gen.mesh(x, y, z, xdivs, ydivs, zdivs, zmin=zmin)
    sol_gen.wheel_loads(loads)
    sol_gen.boussinesq_pressure()
    sol_gen.design_pressure_Ps(float(row12.get()))
    z_res = [row[0] for row in sol_gen.results_Ps]
    Ps_res = [row[1] for row in sol_gen.results_Ps]
    return z_res, Ps_res

def save_pressures():
    """Enables saving of comma-delimited results to .txt or .csv file"""
    global solutions
    write_res = []
    for key, value in solutions.items():
        # reverse_results = value.results_pressures[]
        for row in value.results_pressures:
            line = [key] + row
            write_res.append(line)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Save results as CSV file"
    )
    if not file_path:
        return
    with open(file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Load Name", "Z [m]", "Y [m]", "X [m]", "SIGMA_Z [kPa]"])
        for row in write_res:
            writer.writerow(row)
    return

def save_traffic_surcharge():
    """Enables saving of comma-delimited results to .txt or .csv file"""
    global solutions
    write_res = []
    for key, value in solutions.items():
        for row in value.results_Ps:
            line = [key] + row
            write_res.append(line)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Save results as CSV file"
    )
    if not file_path:
        return
    with open(file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Load Name", "Z [m]", "Ps [kPa]"])
        for row in write_res:
            writer.writerow(row)
    return

def plot_results_2D():
    """Plots results of design traffic surcharge Ps"""
    # Extract results from GUI inputs
    global solutions
    plot_vals = {}
    for key, value in solutions.items():
        plot_vals[key] = (np.asarray(value.results_Ps)[:, 0], np.asarray(value.results_Ps)[:, 1])

    # Set up fig15
    global fig15
    fig15.clear()
    ax1 = fig15.add_subplot(1, 2, 1)
    ax2 = fig15.add_subplot(1, 2, 2)
    for key, value in plot_vals.items():
        ax1.plot(value[1], value[0], linewidth=1, linestyle="-", marker="o", label=key)
        ax2.plot(value[0], value[1], linewidth=1, linestyle="-", marker="o", label=key)

    ax1.set_title("Design Surcharge Pressure Ps with Depth")
    ax1.set_xlabel("Surcharge Pressure [kPa], Ps")
    ax1.set_ylabel("Cover Depth [m], H")
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
    ax2.set_title("Design Surcharge Pressure Ps with Depth")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlim(0.5, 10)
    ax2.set_ylim(5, 500)
    x_ticks = [0.5, 1, 2, 3, 4, 5, 10]
    y_ticks = [5, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500]
    ax2.xaxis.set_major_locator(FixedLocator(x_ticks))
    ax2.yaxis.set_major_locator(FixedLocator(y_ticks))
    ax2.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax2.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax2.set_xticks(x_ticks)
    ax2.set_yticks(y_ticks)
    ax2.xaxis.set_minor_locator(FixedLocator(x_ticks))
    ax2.yaxis.set_minor_locator(FixedLocator(y_ticks))
    ax2.xaxis.set_minor_formatter(NullFormatter())
    ax2.yaxis.set_minor_formatter(NullFormatter())
    ax2.set_xticks([0.6, 0.7, 0.8, 0.9, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.2, 2.4, 
                    2.6, 2.8, 3.2, 3.4, 3.6, 3.8, 4.2, 4.4, 4.6, 4.8, 6, 7, 8, 9], minor=True)
    ax2.set_yticks([6, 7, 8, 9, 11, 12, 13, 14, 15, 25, 35, 45, 60, 70, 80, 90, 120, 140, 160, 180, 
                    220, 240, 260, 280, 320, 340, 360, 380, 420, 440, 460, 480], 
                    minor=True)
    ax2.set_xlabel("Cover Depth [m], H")
    ax2.set_ylabel("Surcharge Pressure [kPa], Ps")
    ax2.grid(which='major',
            linestyle='-',
            linewidth=0.8,
            color='gray')
    ax2.grid(which='minor',
            linestyle=':',
            linewidth=0.5,
            color='lightgray')
    
    def ref_plot(ax, ref_load, label, cover_on_y=True, style="--", marker="x"):
        """Add results from reference loads to plot"""
        global ref_loads
        if cover_on_y is True:
            y, x = solve_Ps(ref_loads[ref_load])
        else:
            x, y = solve_Ps(ref_loads[ref_load])
        ax.plot(x, y, label=label, linewidth=0.5, linestyle=style, marker=marker)
        return
    
    if var19.get() is True:
        ref_plot(ax1, "DMRBMainRoad1", "DMRB Main Road (straddle)")
        ref_plot(ax1, "DMRBMainRoad2", "DMRB Main Road (axle over crown)")
        ref_plot(ax2, "DMRBMainRoad1", "DMRB Main Road (straddle)", cover_on_y=False)
        ref_plot(ax2, "DMRBMainRoad2", "DMRB Main Road (axle over crown)", cover_on_y=False)
    if var20.get() is True:
        ref_plot(ax1, "DMRB_Filter", "DMRB Filter")
        ref_plot(ax2, "DMRB_Filter", "DMRB Filter", cover_on_y=False)
    if var21.get() is True:
        ref_plot(ax1, "DMRB_Field", "DMRB Field")
        ref_plot(ax2, "DMRB_Field", "DMRB  Field", cover_on_y=False)
    if var22.get() is True:
        ref_plot(ax1, "10t_2_300", "10t wheel, DAF=2, 300kPa")
        ref_plot(ax2, "10t_2_300", "10t wheel, DAF=2, 300kPa", cover_on_y=False)
    if var23.get() is True:
        ref_plot(ax1, "10t_2_700", "10t wheel, DAF=2, 700kPa")
        ref_plot(ax2, "10t_2_700", "10t wheel, DAF=2, 700kPa", cover_on_y=False)
    if var24.get() is True:
        ref_plot(ax1, "30t_2_300", "30t wheel, DAF=2, 300kPa")
        ref_plot(ax2, "30t_2_300", "30t wheel, DAF=2, 300kPa", cover_on_y=False)
    if var25.get() is True:
        ref_plot(ax1, "30t_2_700", "30t wheel, DAF=2, 700kPa")
        ref_plot(ax2, "30t_2_700", "30t wheel, DAF=2, 700kPa", cover_on_y=False)
    if var26.get() is True:
        ref_plot(ax1, "Eurocode_LM1", "Eurocode LM1")
        ref_plot(ax2, "Eurocode_LM1", "Eurocode LM1", cover_on_y=False)
    if var27.get() is True:
        ref_plot(ax1, "Eurocode_LM2", "Eurocode LM2")
        ref_plot(ax2, "Eurocode_LM2", "Eurocode LM2", cover_on_y=False)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), bbox_transform=ax1.transAxes, 
               fontsize="small", ncol=2)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), bbox_transform=ax2.transAxes, 
               fontsize="small", ncol=2)
    fig15.subplots_adjust(wspace=0.2, bottom=0.25)
    plotcanvas15.draw()

    return

def plot_results_3D(y, z, load_name="userinput"):
    """Plots results of Boussinesq pressures

    Args:
        y (float): y coordinate for X-Z slice
        z (float): Z coordinate for X-Y slice
    """
    global solutions
    solution = solutions[load_name]
    np_res_p = np.asarray(solution.results_pressures)

    # Set up fig16
    # Variables for ax3
    val_x0 = solution.x_arr
    val_y0 = solution.y_arr
    val_x, val_y = np.meshgrid(val_x0, val_y0)
    grid_x = val_x.ravel()
    grid_y = val_y.ravel()
    dec = 3
    res = np_res_p[np.round(np_res_p[:, 0], dec) == round(z, dec)]
    res_x = res[:, 2]
    res_y = res[:, 1]
    res_v = res[:, 3]
    grid_keys = np.round(np.c_[grid_x, grid_y], dec)
    res_keys  = np.round(np.c_[res_x, res_y], dec)
    res_dict = {tuple(k): v for k, v in zip(res_keys, res_v)}
    val_v_flat = np.array([res_dict.get(tuple(k), 0.0) for k in grid_keys])
    val_v = val_v_flat.reshape(val_x.shape)
    i_peak = np.argmax(res_v)
    x_peak = res_x[i_peak]
    y_peak = res_y[i_peak]
    v_peak = res_v[i_peak]
    
    # Variables for ax4
    val_z0 = solution.z_arr
    val_x2, val_z2 = np.meshgrid(val_x0, val_z0)
    grid_x2 = val_x2.ravel()
    grid_z2 = val_z2.ravel()
    dec = 3
    res2 = np_res_p[np.round(np_res_p[:, 1], dec) == round(y, dec)]
    res_x2 = res2[:, 2]
    res_z2 = res2[:, 0]
    res_v2 = res2[:, 3]
    grid_keys2 = np.round(np.c_[grid_x2, grid_z2], dec)
    res_keys2  = np.round(np.c_[res_x2, res_z2], dec)
    res_dict2 = {tuple(k): v for k, v in zip(res_keys2, res_v2)}
    val_v2_flat = np.array([res_dict2.get(tuple(k), 0.0) for k in grid_keys2])
    val_v2 = val_v2_flat.reshape(val_x2.shape)
    i_peak2 = np.argmax(res_v2)
    x_peak2 = res_x2[i_peak2]
    z_peak2 = res_z2[i_peak2]
    v_peak2 = res_v2[i_peak2]

    global fig16
    fig16.clear()
    ax3 = fig16.add_subplot(1, 2, 1, projection='3d')
    ax4 = fig16.add_subplot(1, 2, 2, projection='3d')
    ax3.plot_surface(val_x, val_y, val_v, cmap="viridis")
    ax3.set_title("Boussinesq Pressures Across X-Y Plane\n at Specified Depth")
    ax3.set_xlabel("x [m]")
    ax3.set_ylabel("y [m]")
    ax3.set_zlabel("Boussinesq Pressure [kPa]")
    ax3.text(x_peak, y_peak, v_peak, f"{v_peak:.2f}", color="black", fontsize=10)
    ax4.plot_surface(val_x2, val_z2, val_v2, cmap="viridis")
    ax4.set_title("Boussinesq Pressures Across X-Z Plane\n at Specified Y")
    ax4.set_xlabel("x [m]")
    ax4.set_ylabel("Cover Depth [m], H")
    ax4.set_zlabel("Boussinesq Pressure [kPa]")
    ax4.text(x_peak2, z_peak2, v_peak2, f"{v_peak2:.2f}", color="black", fontsize=10)
    ax4.view_init(elev=30, azim=120)
    plotcanvas16.draw()

    # Set up fig28
    global fig28, fig28_state
    fig28.clear()
    ax5 = fig28.add_subplot(111, projection='3d')
    fig28.set_constrained_layout(True)
    dec = 3 
    # Set data and store in persistent dict
    x5_all = np.round(np_res_p[:, 2], 3)
    y5_all = np.round(np_res_p[:, 1], 3)
    z5_all = np.round(np_res_p[:, 0], 3)
    v5_all = np.round(np_res_p[:, 3], 3)
    fig28_state["x"] = x5_all
    fig28_state["y"] = y5_all
    fig28_state["z"] = z5_all
    fig28_state["v"] = v5_all
    # Set axis bounds and initial mask
    mid_x = np.mean([x5_all.min(), x5_all.max()])
    mid_y = np.mean([y5_all.min(), y5_all.max()])
    mid_z = np.mean([z5_all.min(), z5_all.max()])
    max_range = max(np.ptp(x5_all), np.ptp(y5_all), np.ptp(z5_all)) / 2
    ax5.set_xlim(mid_x - max_range, mid_x + max_range)
    ax5.set_ylim(mid_y - max_range, mid_y + max_range)
    ax5.set_zlim(mid_z - max_range, mid_z + max_range)
    initial_y_cutoff = 0
    initial_z_cutoff = z5_all[0]
    mask = (y5_all > initial_y_cutoff) & (z5_all > initial_z_cutoff)
    ax5.set_box_aspect([1,1,1])
    initial_marker_size = 2
    norm=LogNorm(vmin=v5_all.min(), vmax=v5_all.max())
    sc = ax5.scatter(
        x5_all[mask],
        y5_all[mask],
        z5_all[mask],
        c=v5_all[mask],
        s=initial_marker_size,
        cmap='jet',
        norm=norm,
        alpha=0.7
    )
    fig28_state["sc"] = sc
    ax5.set_title("Boussinesq Pressures in 3D Spatial Domain")
    ax5.set_xlabel("x [m]")
    ax5.set_ylabel("y [m]")
    ax5.set_zlabel("Cover Depth [m], H")
    ax5.invert_zaxis()
    # cbar = fig28.colorbar(sc, ax=ax5)
    # cbar.set_label("Boussinesq Pressure [kPa]")
    cbar_ax = fig28.add_axes([0.88, 0.2, 0.03, 0.6])
    sm = ScalarMappable(norm=norm, cmap='jet')
    sm.set_array([])
    cbar = fig28.colorbar(sm, cax=cbar_ax)
    cbar.set_label("Boussinesq Pressure [kPa]")

    # Create callback functions to update plot based on sliders
    def update_marker_size(value):
        """Update marker size of fig28 (3D plot)"""
        sc = fig28_state["sc"]
        v5_all = fig28_state["v"]
        size = float(value)
        sc.set_sizes(np.full(len(v5_all), size))
        plotcanvas28.draw_idle()
        return

    def update_y_mask(value):
        """Update y mask of fig28 (3D plot)"""
        fig28_state["y_cutoff"] = float(value)
        apply_masks()
        return
    
    def update_z_mask(value):
        """Update z mask of fig28 (3D plot)"""
        fig28_state["z_cutoff"] = float(value)
        apply_masks()
        return
    
    def apply_masks():
        """Update masks of fig28 (3D plot)"""
        sc = fig28_state["sc"]
        x5_all = fig28_state["x"]
        y5_all = fig28_state["y"]
        z5_all = fig28_state["z"]
        v5_all = fig28_state["v"]
        y_cutoff = fig28_state["y_cutoff"]
        z_cutoff = fig28_state["z_cutoff"]
        if fig28_state.get("label_mask_y") is not None:
            fig28_state["label_mask_y"].config(text=f"Y Cutoff: {y_cutoff:.2f}")
        if fig28_state.get("label_mask_z") is not None:
            fig28_state["label_mask_z"].config(text=f"Z Cutoff: {z_cutoff:.2f}")
        mask = (y5_all > y_cutoff) & (z5_all > z_cutoff)
        x = x5_all[mask]
        y = y5_all[mask]
        z = z5_all[mask]
        v = v5_all[mask]
        sc._offsets3d = (x, y, z)
        sc.set_array(v)
        plotcanvas28.draw_idle()
        return

    # If no sliders then create them and save to persistent dict for future update on callback
    if fig28_state["slider_size"] is None: # Marker size slider
        fig28_state["label_size"] = ttk.Label(mframe6, text="Marker Size")
        fig28_state["label_size"].pack(fill="x", pady=2)
        fig28_state["slider_size"] = ttk.Scale(
            mframe6,
            from_=1,
            to=100,
            orient="horizontal",
            command=update_marker_size
        )
        fig28_state["slider_size"].pack(fill="x", pady=5)
        fig28_state["slider_size"].set(20)

    if fig28_state["slider_mask_y"] is None: # Mask y slider
        fig28_state["label_mask_y"] = ttk.Label(mframe6, text="Y Cutoff: 0.00")
        fig28_state["label_mask_y"].pack(fill="x", pady=2)
        fig28_state["slider_mask_y"] = ttk.Scale(
            mframe6,
            from_=y5_all.min(),
            to=y5_all.max(),
            orient="horizontal",
            command=update_y_mask
        )
        fig28_state["slider_mask_y"].pack(fill="x", pady=5)
        y_med = 0.5 * (y5_all.min() + y5_all.max())
        fig28_state["y_cutoff"] = y_med
        fig28_state["slider_mask_y"].set(y_med)
        

    if fig28_state["slider_mask_z"] is None: # Mask z slider
        fig28_state["label_mask_z"] = ttk.Label(mframe6, text=f"Z Cutoff: {z5_all[0]:.2f}")
        fig28_state["label_mask_z"].pack(fill="x", pady=2)
        fig28_state["slider_mask_z"] = ttk.Scale(
            mframe6,
            from_=z5_all.min(),
            to=z5_all.max(),
            orient="horizontal",
            command=update_z_mask
        )
        fig28_state["slider_mask_z"].pack(fill="x", pady=5)
        fig28_state["z_cutoff"] = z5_all.min()
        fig28_state["slider_mask_z"].set(z5_all.min())
    return


def discretise_wheel(load, pressure, x=0, y=0, n=10, r1r2=0.5):
    """Converts a point wheel load and contact pressure into a patch load over a circular area, then
    discretises this into a set of n point loads (eitheer 4 quadrants, and 6 annular sectors or just
    4 quadrants)

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
    if n == 4:
        a_quad = 0.25 * math.pi * r2**2
        y_quad = 4 * r2 / (3 * math.pi)
        p_quad = a_quad / area * load
        result = [[x + y_quad, y + y_quad, p_quad], [x - y_quad, y + y_quad, p_quad],
                  [x - y_quad, y - y_quad, p_quad], [x + y_quad, y - y_quad, p_quad]]
    else:
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
        result = [[x + y_quad, y + y_quad, p_quad], [x - y_quad, y + y_quad, p_quad], 
                [x - y_quad, y - y_quad, p_quad], [x + y_quad, y - y_quad, p_quad], 
                [x + x1_sect, y + y1_sect, p_sect], [x, y + y_sect, p_sect],
                [x - x1_sect, y + y1_sect, p_sect], [x - x1_sect, y - y1_sect, p_sect],
                [x, y - y_sect, p_sect], [x + x1_sect, y - y1_sect, p_sect]]
    rounded = [[round(value, 3) for value in row] for row in result]
    return rounded

def convert_patch_loads(widget, wheel_loads, contact_pressure, n):
    """Runs input wheel loads through discretise_wheel() function and adds results to GUI window
    for user to copy

    Args:
        widget: text widget to edit with output
        wheel_loads: list of lists, see discretise_wheel() for more information
        contact_pressure (kPa): contact pressure for determination of patch load
    """
    output = []
    for wheel in wheel_loads:
        output.extend(discretise_wheel(wheel[2], contact_pressure, x=wheel[0], 
                                       y=wheel[1], n=n))
    widget.delete("1.0", "end")
    widget.insert("1.0", str(output))
    return

def show_load_dialog():
    """Create popup window enabling further discretisation of wheel loads and giving information
    on different traffic loading
    """
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
    "Main road loading - 45 units HB loading: static wheel of 112.5kN including impact factor of "\
    "1.25, contact pressure 1100kPa. Comprises eight wheels spread across two axles with wheel " \
    "spacing 1.0m, axle spacing 1.8m. \n\nPosition #1 - Axles Straddling Origin:\n"
    "[[-1.5, -0.9, 112.5], [-0.5, -0.9, 112.5], [0.5, -0.9, 112.5], [1.5, -0.9, 112.5], " \
    "[-1.5, 0.9, 112.5], [-0.5, 0.9, 112.5], [0.5, 0.9, 112.5], [1.5, 0.9, 112.5]]\n" \
    "Position #2 - One Axle Directly Over Origin:\n"
    "[[-1.5, 0, 112.5], [-0.5, 0, 112.5], [0.5, 0, 112.5], [1.5, 0, 112.5], " \
    "[-1.5, 1.8, 112.5], [-0.5, 1.8, 112.5], [0.5, 1.8, 112.5], [1.5, 1.8, 112.5]]\n\n" \
    "Filter drain loading - 30 units HB loading (62.5kN wheel load), however, considering only " \
    "two wheels with an increased dynamic factor for total wheel load 87.5kN (1100kPa):\n"
    "[[-0.5, 0, 87.5], [0.5, 0, 87.5]]\n\n" \
    "Field loading - two wheels 1.0m apart, static weight 30kN, impact factor of 2 giving " \
    "dynamic wheel load of 60kN, (contact pressure assumed 400kPa):\n" \
    "[[-0.5, 0, 60], [0.5, 0, 60]]\n\n", "normal")
    p_text1.insert("end", "Construction Loading (Young and O'Reilly (1983))\n", "bold")
    p_text1.insert("end", 
    "Static wheel 10t, dynamic factor 2.0, contact pressure 300-700kPa\n" \
    "[[0, 0, 200]]\n\n" \
    "Static wheel 30t, dynamic factor 2.0, contact pressure 300-700kPa\n" \
    "[[0, 0, 590]]\n\n", "normal")
    p_text1.insert("end", "Eurocode Loading\n", "bold")
    p_text1.insert("end", 
    "Load model 2 - two wheels 2m apart with wheel load 200kN, contact pressure 1250 kPa with " \
    "contact area being a 0.4m square area:\n" \
    "[[-1, 0, 200], [1, 0, 200]]\n\n", "normal")
    p_text1.insert("end", "Historic Loading (Young and O'Reilly (1983), BS 5400-2:1978)\n", "bold")
    p_text1.insert("end", 
    "Main road loading - 45 units HB loading: static wheel of 112.5kN including impact factor of "\
    "1.25, contact pressure 1100kPa. Comprises eight wheels spread across two axles with wheel " \
    "spacing 1.0m, axle spacing 1.8m. \n\nPosition #1 - Axles Straddling Origin:\n"
    "[[-1.5, -0.9, 112.5], [-0.5, -0.9, 112.5], [0.5, -0.9, 112.5], [1.5, -0.9, 112.5], " \
    "[-1.5, 0.9, 112.5], [-0.5, 0.9, 112.5], [0.5, 0.9, 112.5], [1.5, 0.9, 112.5]]\n" \
    "Position #2 - One Axle Directly Over Origin:\n"
    "[[-1.5, 0, 112.5], [-0.5, 0, 112.5], [0.5, 0, 112.5], [1.5, 0, 112.5], " \
    "[-1.5, 1.8, 112.5], [-0.5, 1.8, 112.5], [0.5, 1.8, 112.5], [1.5, 1.8, 112.5]]\n\n" \
    "Light road loading - two wheels 0.9m apart, static weight 70kN, impact factor of 1.5 " \
    "giving dynamic weight 105kN, contact pressure 700kPa:\n" \
    "[[-0.45, 0, 105], [0.45, 0, 105]]\n\n" 
    "Field loading - two wheels 0.9m apart, static weight 30kN, impact factor of 2 giving " \
    "dynamic wheel load of 60kN, contact pressure 400kPa:\n" \
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

    p_frame6 = tk.Frame(popup)
    p_frame6.pack(fill="x", padx=10, pady=(5,10))
    p_frame6a = tk.Frame(p_frame6)
    p_frame6a.pack(side="left", fill="x")
    p_frame6b = tk.Frame(p_frame6, width=15)
    p_frame6b.pack(side="right", fill="x")
    tk.Label(p_frame6a, text="Number of points to discretise to\neither 4 total = 4 quadrants\n" \
    "or 10 total = 4 inner quadrants + 6 outer annular sectors", justify="left").pack(side="left")
    n = tk.IntVar()
    p_rbutton6a = ttk.Radiobutton(p_frame6b, text="4", variable=n, value=4)
    p_rbutton6a.pack(side="left", fill="x")
    p_rbutton6b = ttk.Radiobutton(p_frame6b, text="10", variable=n, value=10)
    p_rbutton6b.pack(side="right", fill="x")
    # p_entry6 = tk.Entry(p_frame6, width=15)
    # p_entry6.pack(side="right", padx=5)

    p_frame4 = tk.Frame(popup)
    p_frame4.pack(fill="x", pady=2)
    p_button4 = tk.Button(p_frame4, text="Discretize wheel patch loading into set of n point " \
    "loads (assuming circular contact patch)", command=lambda: convert_patch_loads(
        p_text5, json.loads(p_entry2.get()), float(p_entry3.get()), n=n.get()))
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

# ==================================================================================================
# GUI
# ==================================================================================================

# ==================================================================================================
# Root Window and Main Frames
# ==================================================================================================

root = tk.Tk()
root.title("Traffic Pressures on Pipes")
root.geometry("1280x720")

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

# ==================================================================================================
# Helper Functions for GUI Elements
# ==================================================================================================

def create_mframe(parent, pady_ext=5):
    """Create a frame"""
    frame = tk.Frame(parent, bd=1, relief="solid", padx=0, pady=0)
    frame.pack(fill="x", padx=10, pady=pady_ext)
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

def create_row_check(frame, label_text, variable=None):
    """Create a row with a label and checkbutton"""
    if variable is None:
        variable = tk.BooleanVar(value=False)
    row_frame = tk.Frame(frame)
    row_frame.pack(fill="x", padx=(10,2), pady=2)
    label = tk.Label(row_frame, text=label_text, anchor="w", justify="left")
    label.grid(row=0, column=0, sticky="w")
    checkbutton = tk.Checkbutton(row_frame, variable=variable)
    checkbutton.grid(row=0, column=1, sticky="e")
    # Make label stretch, checkbutton fixed
    row_frame.grid_columnconfigure(0, weight=1)
    row_frame.grid_columnconfigure(1, weight=0)
    return checkbutton, variable

# ==================================================================================================
# GUI Inputs - Spatial Domain Parameters
# ==================================================================================================

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
                    "Should be arbitrarily small number to capture peak pressure at \npipe " \
                    "crown, 0.3m is recommended (3 number 0.1m elements)",
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
                    "3 elements is recommended to enable pressure surface plotting, \nnote only " \
                    "central row of elements is used to calculate Ps",
                    "   ")
row7 = create_row(mframe1,
                    "Number of z divisions for discretisation:",
                    "",
                    "   ")

# ==================================================================================================
# GUI Inputs - Wheel Loading
# ==================================================================================================

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
tk.Label(frame8, text='Set of point loads as {"Load Name": [[x1, y1, P1], [x2, y2, P2], ...]}',
         anchor="w", justify="left").grid(row=0, column=0, sticky="w", padx=(0,5))
entry8 = tk.Entry(frame8)
entry8.grid(row=0, column=1, sticky="ew")
frame8.grid_columnconfigure(1, weight=1)
tk.Label(mframe2, text="Note: x-y plane assumed centered on origin at (0,0)").pack(
    anchor="w", pady=(2,2))

# ==================================================================================================
# GUI Outputs - Results
# ==================================================================================================

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
button9 = tk.Button(frame9, text="Solve for Pressures & Traffic Surcharge", command=solve_gui)
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
button13 = tk.Button(frame13, text="Save Traffic Surcharge Ps to File", 
                     command=save_traffic_surcharge)
button13.grid(row=0, column=0, sticky="ew")
frame13.rowconfigure(0, weight=1)
frame13.columnconfigure(0, weight=1)

tk.Label(mframe3, 
         text="2D Plot Settings",
         font=("Arial", 10, "bold"), 
         anchor="w", 
         justify="left"
    ).pack(fill="x", padx=0, pady=(10,0))

frame18 = tk.Frame(mframe3)
frame18.pack(fill="x", pady=(0, 2))
label18 = tk.Label(frame18, text="In addition to user wheel loads, also plot:", anchor="w",
                   justify="left")
label18.pack(fill="x", pady=2)

row19, var19 = create_row_check(mframe3, "DMRB Main Road Loading")
row20, var20 = create_row_check(mframe3, "DMRB Filter Drain Loading")
row21, var21 = create_row_check(mframe3, "DMRB Field Loading")
row22, var22 = create_row_check(mframe3, "BS 9295 10t static wheel, dynamic factor 2.0, 300kPa " \
"contact pressure")
row23, var23 = create_row_check(mframe3, "BS 9295 10t static wheel, dynamic factor 2.0, 700kPa " \
"contact pressure")
row24, var24 = create_row_check(mframe3, "BS 9295 30t static wheel, dynamic factor 2.0, 300kPa " \
"contact pressure")
row25, var25 = create_row_check(mframe3, "BS 9295 30t static wheel, dynamic factor 2.0, 700kPa " \
"contact pressure")
row26, var26 = create_row_check(mframe3, "Eurocode Load Model 1")
row27, var27 = create_row_check(mframe3, "Eurocode Load Model 2")

tk.Label(mframe3, 
         text="3D Plot Settings",
         font=("Arial", 10, "bold"), 
         anchor="w", 
         justify="left"
    ).pack(fill="x", padx=0, pady=(10,0))

frame30 = tk.Frame(mframe3)
frame30.pack(fill="x", pady=2)
label30 = tk.Label(frame30, text="Plot pressures from load case", anchor="w", 
                   justify="left", width=35)
label30.grid(row=0, column=0, sticky="w")
combobox30 = ttk.Combobox(frame30)
combobox30.grid(row=0, column=1, sticky="e")
tk.Label(frame30, text="m", anchor="w").grid(row=0, column=2, sticky="w", padx=(5,0))
frame30.grid_columnconfigure(0, weight=1)
frame30.grid_columnconfigure(1, weight=0)

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

def on_plot_3D():
    """Obtains inputs from GUI and calls plot_results() for 3D plots"""
    y_value = combobox17.get()
    z_value = combobox14.get()
    load_name = combobox30.get()
    if not (y_value and z_value):
        return
    if not (load_name):
        load_name = "userinput"
    plot_results_3D(float(y_value), float(z_value), load_name=load_name)
    return

frame15 = tk.Frame(mframe3)
frame15.pack(fill="x", pady=2)
button15 = tk.Button(frame15, text="Generate 2D Results Plots", command=plot_results_2D)
button15.grid(row=0, column=0, sticky="ew")
frame15.rowconfigure(0, weight=1)
frame15.columnconfigure(0, weight=1)

frame29 = tk.Frame(mframe3)
frame29.pack(fill="x", pady=2)
button29 = tk.Button(frame29, text="Generate 3D Results Plots", command=on_plot_3D)
button29.grid(row=0, column=0, sticky="ew")
frame29.rowconfigure(0, weight=1)
frame29.columnconfigure(0, weight=1)

mframe4 = create_mframe(scrollframe, pady_ext=0)
fig15 = Figure(figsize=(8, 12))
ax1 = fig15.add_subplot(111)
plotcanvas15 = FigureCanvasTkAgg(fig15, master=mframe4)
plotcanvas15.draw()
plotcanvas15.get_tk_widget().pack(fill="both", expand=True)

mframe5 = create_mframe(scrollframe, pady_ext=0)
fig16 = Figure(figsize=(16, 8))
ax3 = fig16.add_subplot(111)
plotcanvas16 = FigureCanvasTkAgg(fig16, master=mframe5)
plotcanvas16.draw()
plotcanvas16.get_tk_widget().pack(fill="both", expand=True)

mframe6 = create_mframe(scrollframe, pady_ext=0)
fig28 = Figure(figsize=(8,8))
ax5 = fig28.add_subplot(111)
fig28_state = {
    "fig": fig28,
    "ax": ax5,
    "sc": None,
    "x": None,
    "y": None,
    "z": None,
    "v": None,
    "label_size": None,
    "slider_size": None,
    "label_mask_y": None,
    "slider_mask_y": None,
    "label_mask_z": None,
    "slider_mask_z": None,
    "y_cutoff": 0,
    "z_cutoff": 0
}
plotcanvas28 = FigureCanvasTkAgg(fig28, master=mframe6)
plotcanvas28.draw()
plotcanvas28.get_tk_widget().pack(fill="both", expand=True)

# Default values
row1.insert(0, "3")
row2.insert(0, "2.1")
row3.insert(0, "0.5")
row4.insert(0, "2")
row5.insert(0, "30")
row6.insert(0, "21")
row7.insert(0, "32")
entry8.insert(0, '{"Field 1": [[-0.5, 0, 60], [0.5, 0, 60]], "Filter 1": [[-0.5, 0, 87.5], [0.5, 0, 87.5]]}')
row12.insert(0, "1")

# Create root window
root.mainloop()