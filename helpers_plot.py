# bokeh basics
from bokeh.plotting import figure, show, output_file, gridplot
from bokeh.models import ColumnDataSource, HoverTool, DataRange1d, Paragraph
from bokeh.models import LinearAxis, Range1d
from bokeh.palettes import Spectral10 as palette
#colors has a list of colors which can be used in plots
import itertools
colors = itertools.cycle(palette)
_tools_to_show = 'box_zoom,pan,save,hover,reset,tap,wheel_zoom'

import plotly.express as px
from plotly.offline import plot
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import numpy as np
import pandas as pd
import re
import scipy.interpolate as interpolate


class DoublePulseViewerBokeh():
    def __init__(self):
        # Create a blank figure with labels
        self.fig_vds = figure(plot_width=600, plot_height=400,
                              title='voltage SW node',
                              x_axis_label='time', y_axis_label='Vds_LS', tools=_tools_to_show)

        self.fig_id = figure(plot_width=600, plot_height=400,
                             title='current LS mos',
                             x_axis_label='time', y_axis_label='Id_LS', tools=_tools_to_show, x_range=self.fig_vds.x_range)

        self.fig_vds.legend.location = "top_left"
        output_file("ltspice.html", title="double_pulse")
        self.p = gridplot(([[self.fig_vds, self.fig_id]]))

    def add_time_wfm(self, time, vds, id, label=None):
        color_step = next(colors)
        self.fig_vds.line(time, vds, legend_label=label, color=color_step)
        self.fig_id.line(time, id, color=color_step)

    def show(self):
        show(self.p)


class DoublePulseViewerPlotly():
    def __init__(self):

        # Initialize figure with 4 subplots
        self.fig_wfm = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'xy'}, {'type': 'xy'}]],
            subplot_titles=("Vds_LS", "Id_LS")
        )

        self.fig_grid = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'scene'}, {'type': 'scene'}]],
            subplot_titles=("Eon", "Eoff")
        )

    def add_time_wfm(self, time, vds, id, label=None):
        # adding surfaces to subplots.
        self.fig_wfm.add_trace(
            go.Scatter(x=time, y=vds, name=label),
            row=1, col=1)

        self.fig_wfm.add_trace(
            go.Scatter(x=time, y=id, name=label),
            row=1, col=2)

    def show(self):
        self.fig_wfm.update_layout(
            title_text='subplots with different colorscales',
            # height=1600,
            # width=1600
        )
        self.fig_wfm.show()


def plot_single_switching_energy_map(switching_map):

    x = switching_map.current
    y = switching_map.voltage
    z_eon = switching_map.eon
    z_eoff = switching_map.eoff

    mesh = np.array([5, 6])

    xGrid = np.reshape(np.array(x), (mesh[0], mesh[1]))
    yGrid = np.reshape(np.array(y), (mesh[0], mesh[1]))

    z = np.reshape(np.array(z_eon), (mesh[0], mesh[1]))
    z_eoff = np.reshape(np.array(z_eoff), (mesh[0], mesh[1]))

    # Creating the plot
    lines = []
    line_marker = dict(color='#FFFAFA', width=3)  # white for grid
    layout = go.Layout(showlegend=False)

    fig = go.Figure(
        data=[go.Surface(z=z, x=xGrid, y=yGrid, colorscale='Viridis')],
        layout=layout)

    for i, j, k in zip(xGrid, yGrid, z):
            fig.add_trace(go.Scatter3d(
                x=i, y=j, z=k, mode='lines', line=line_marker))

    for i, j, k in zip(np.transpose(xGrid), np.transpose(yGrid), np.transpose(z)):
        fig.add_trace(go.Scatter3d(
            x=i, y=j, z=k, mode='lines', line=line_marker))

    fig.update_layout(title='Hackermans superplot', scene=dict(xaxis_title="Current [A]", yaxis_title="Voltage [V]", zaxis_title="Energy [J]"),
                      scene_camera=dict(up=dict(x=0, y=0, z=15), center=dict(x=0, y=0, z=0), eye=dict(x=-2.5, y=-2.5, z=1.25)))
    fig.show()




# FIXME: this code is not working if multiple plot is required
def plot_switching_energy_map(switching_map):
    # Initialize figure with 4 3D subplots
    fig = make_subplots(rows=2, cols=2, specs=[[{'type': 'scene'}, {
                        'type': 'scene'}], [{'type': 'scene'}, {'type': 'scene'}]])

    x = switching_map.current
    y = switching_map.voltage
    z_eon = switching_map.eon
    z_eoff = switching_map.eoff

    mesh = np.array([5, 6])

    xGrid = np.reshape(np.array(x), (mesh[0], mesh[1]))
    yGrid = np.reshape(np.array(y), (mesh[0], mesh[1]))

    z_eon = np.reshape(np.array(z_eon), (mesh[0], mesh[1]))
    z_eoff = np.reshape(np.array(z_eoff), (mesh[0], mesh[1]))

    # Creating the plot
    lines = []
    line_marker = dict(color='#FFFAFA', width=3)  # white for grid
    layout = go.Layout(showlegend=False)

    # fig.add_trace(go.Figure(
    #     data=[go.Surface(z=z_eon, x=xGrid, y=yGrid, colorscale='Viridis')],
    #     layout=layout), row=1, col=1)

    for i, j, k in zip(xGrid, yGrid, z_eon):
        fig.add_trace(go.Scatter3d(
            x=i, y=j, z=k, mode='lines', line=line_marker), row=1, col=1)
    for i, j, k in zip(np.transpose(xGrid), np.transpose(yGrid), np.transpose(z_eon)):
        fig.add_trace(go.Scatter3d(
            x=i, y=j, z=k, mode='lines', line=line_marker), row = 1, col = 1)

    fig.add_trace(go.Figure(
        data=[go.Surface(z=z_eoff, x=xGrid, y=yGrid,
                            colorscale='Viridis')],
        layout=layout), row=1, col=2)

    for i, j, k in zip(xGrid, yGrid, z_eoff):
        fig.add_trace(go.Scatter3d(
            x=i, y=j, z=k, mode='lines', line=line_marker), row=1, col=2)

    for i, j, k in zip(np.transpose(xGrid), np.transpose(yGrid), np.transpose(z_eoff)):
        fig.add_trace(go.Scatter3d(
            x=i, y=j, z=k, mode='lines', line=line_marker), row=1, col=2)

    fig.update_layout(title='Hackermans superplot', scene=dict(xaxis_title="Current [A]", yaxis_title="Voltage [V]", zaxis_title="Energy [J]"),
                      scene_camera=dict(up=dict(x=0, y=0, z=15), center=dict(x=0, y=0, z=0), eye=dict(x=-2.5, y=-2.5, z=1.25)))
    fig.show()


def plot_switching_energy_map_scatter(switching_map):

    # Initialize figure with 4 3D subplots
    fig = make_subplots(rows=2, cols=2, specs=[[{'type': 'scene'}, {
                        'type': 'scene'}], [{'type': 'scene'}, {'type': 'scene'}]])

    current_grid, voltage_grid = np.meshgrid(
        switching_map.voltage, switching_map.current)
    eon_grid = interpolate.griddata((switching_map.current, switching_map.voltage),
                                    switching_map.eon, (current_grid, voltage_grid), method='cubic', fill_value=0)

    Eon_surf = fig.add_trace(go.Surface(x=current_grid, y=voltage_grid, z=eon_grid,
                                        colorscale='Viridis',
                                        name='Eon',
                                        showscale=True,
                                        ), row=1, col=1)

    Eon_fig = fig.add_trace(go.Scatter3d(x=switching_map.current, y=switching_map.voltage, z=switching_map.eon,
                                         mode='markers',
                                         name='Eon',
                                         marker=dict(
                                             size=3,
                                             # set color to an array/list of desired values
                                             color=switching_map.eoff,
                                             colorscale='Viridis',   # choose a colorscale
                                             opacity=0.8
                                         ),
                                         ), row=1, col=1)

    Eoff_fig = fig.add_trace(go.Scatter3d(x=switching_map.current, y=switching_map.voltage, z=switching_map.eoff,
                                          mode='markers',
                                          name='Eoff',
                                          marker=dict(
                                              size=3,
                                              # set color to an array/list of desired values
                                              color=switching_map.eoff,
                                              colorscale='Viridis',   # choose a colorscale
                                              opacity=0.8
                                          ),
                                          ), row=1, col=2)

    # Update xaxis properties
    fig.update_xaxes(title_text="current [A]", row=1, col=1)
    fig.update_yaxes(title_text="voltage [V]", row=1, col=1)
    # fig.update_zaxes(title_text="energy [J]", row=1, col=1)

    fig.update_xaxes(title_text="current [A]", row=1, col=2)
    fig.update_yaxes(title_text="voltage [V]", row=1, col=2)
    # fig.update_zaxes(title_text="energy [J]", row=1, col=2)

    fig.update_layout(height=1000, showlegend=True)
    fig.show()
