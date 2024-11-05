"""Make MSPlotly GUI.

License
-------
This file is part of MSPlotly
BSD 3-Clause License
Copyright (c) 2024, Ivan Munoz Gutierrez
"""

import base64
import tempfile
import atexit
from pathlib import Path
from io import BytesIO

import dash
import dash_ag_grid as dag
from dash import html, dcc, Input, Output, State, _dash_renderer
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from plotly.graph_objects import Figure
import plotly.express as px

import plotter as plt
from user_input import UserInput


# TODO: avoid using biopython for blasting.

# ====================================================================================== #
#                                   Global Variables                                     #
# ====================================================================================== #
# Create the tmp directory and ensure it's deleted when the app stops
TMP_DIRECTORY = tempfile.TemporaryDirectory()
atexit.register(TMP_DIRECTORY.cleanup)
USER_INPUT = UserInput()
TMP_PATH = Path(TMP_DIRECTORY.name)


# ====================================================================================== #
#                                   Helper Functions                                     #
# ====================================================================================== #
def save_uploaded_file(file_name, content, temp_folder_path: Path) -> str:
    """Decode the content and write it to a temporary file."""
    # Decode content
    data = content.split(";base64,")[1]
    decoded_data = base64.b64decode(data)

    # Save uploaded file
    output_path = temp_folder_path / file_name
    with open(output_path, "wb") as f:
        f.write(decoded_data)
    # Dash doesn't like Path; hence, we need to cast Path to str.
    return str(output_path)


def list_sequential_color_scales() -> list:
    sequential_color_scales = [
        name for name in dir(px.colors.sequential) if not name.startswith("_")
    ]
    return sequential_color_scales


# ====================================================================================== #
#                               App Layout Functions                                     #
# ====================================================================================== #
def make_tab_main() -> dbc.Tab:
    """Make tab Main."""
    tab_main = dbc.Tab(
        label="Main",
        tab_id="tab-main",
        children=[
            dbc.Row(  # = UPLOAD FILES SECTION = #
                [
                    dmc.Divider(
                        label=html.Span(
                            dmc.Text("Files", style={"fontSize": "25px"}),
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        labelPosition="center",
                    ),
                    html.Div(
                        [
                            dcc.Upload(
                                id="upload",
                                children=dmc.Button(
                                    "Upload",
                                    color="#3a7ebf",
                                    leftSection=DashIconify(
                                        icon="bytesize:upload",
                                        width=40,
                                    ),
                                    variant="outline",
                                    size="xl",
                                    style={
                                        "fontSize": "20px",
                                        "borderStyle": "dashed",
                                        "borderWidth": "3px",
                                        "width": "240px",
                                    },
                                ),
                                multiple=True,
                                accept=".gb, .gbk",
                            ),
                            dmc.Button(
                                "Delete Selected",
                                id="delete-selected-files-button",
                                leftSection=DashIconify(
                                    icon="material-symbols-light:delete-outline-rounded",
                                    width=35,
                                ),
                                color="#3a7ebf",
                                size="xl",
                                style={"fontSize": "20px", "width": "240px"},
                            ),
                        ],
                        className="d-flex justify-content-evenly my-2",
                    ),
                    html.Div(  # Div to center AgGrid
                        [
                            dag.AgGrid(  # Table to display file names and paths
                                id="files-table",
                                columnDefs=[
                                    {
                                        "headerName": "File Name",
                                        "field": "filename",
                                        "rowDrag": True,
                                        "sortable": True,
                                        "editable": False,
                                        "checkboxSelection": True,
                                        "headerCheckboxSelection": True,
                                        "cellStyle": {"fontSize": "20px"},
                                    },
                                ],
                                defaultColDef={"resizable": True},
                                dashGridOptions={
                                    "rowDragManaged": True,
                                    "localeText": {"noRowsToShow": "No Uploaded Files"},
                                    "rowSelection": "multiple",
                                },
                                rowData=[],  # Empty at start
                                columnSize="sizeToFit",
                                style={
                                    "height": "300px",
                                    "width": "100%",
                                    "fontSize": "20px",
                                },
                                className="ag-theme-alpine-dark",
                            ),
                        ],
                        style={"margin": "10px"},
                        className="d-flex justify-content-center",
                    ),
                ],
                className="d-flex justify-content-center mt-3",
                style={
                    "margin": "5px",
                },
            ),
            dbc.Row(  # = ALIGN AND PLOT SECTION = #
                [
                    dmc.Divider(
                        label=html.Span(
                            [
                                dmc.Text("Plot", style={"fontSize": "25px"}),
                            ],
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        labelPosition="center",
                    ),
                    dbc.Row(
                        [
                            dmc.Button(
                                "Reset",
                                id="reset-button",
                                leftSection=DashIconify(
                                    icon="material-symbols-light:reset-settings-rounded",
                                    width=40,
                                ),
                                color="#3a7ebf",
                                size="xl",
                                style={"fontSize": "20px", "width": "150px"},
                            ),
                            dmc.Button(
                                "Erase",
                                id="erase-button",
                                leftSection=DashIconify(
                                    icon="clarity:eraser-line",
                                    width=30,
                                ),
                                color="#3a7ebf",
                                size="xl",
                                style={"fontSize": "20px", "width": "150px"},
                            ),
                            dmc.Button(
                                "Draw",
                                id="draw-button",
                                leftSection=DashIconify(
                                    icon="stash:pencil-writing-light",
                                    width=40,
                                ),
                                color="#b303b3",
                                size="xl",
                                style={"fontSize": "20px", "width": "150px"},
                            ),
                        ],
                        className="d-flex justify-content-evenly mt-3 mb-1",
                    ),
                    dbc.Row(  # Genes info and align sequences
                        [
                            dmc.Select(
                                id="use-genes-info-from",
                                label="Use Genes Info from",
                                value="product",
                                data=[
                                    {"value": "gene", "label": "CDS Gene"},
                                    {"value": "product", "label": "CDS Product"},
                                ],
                                w=250,
                                size="xl",
                            ),
                            dmc.Select(
                                id="align-plot",
                                label="Align Sequences",
                                value="left",
                                data=[
                                    {"value": "left", "label": "Left"},
                                    {"value": "center", "label": "Center"},
                                    {"value": "right", "label": "Right"},
                                ],
                                w=250,
                                size="xl",
                            ),
                        ],
                        className="d-flex justify-content-evenly my-3",
                        style={"textAlign": "center"},
                    ),
                    dbc.Row(  # homology length and homology lines styles
                        [
                            dmc.NumberInput(
                                label="Min Homology Length",
                                id="minimum-homology-length",
                                value=0,
                                min=0,
                                step=50,
                                w=250,
                                suffix=" bp",
                                size="xl",
                            ),
                            dmc.Select(
                                id="homology-lines",
                                label="Homology Lines",
                                value="straight",
                                data=[
                                    {"value": "bezier", "label": "Bezier"},
                                    {"value": "straight", "label": "Straight"},
                                ],
                                w=250,
                                size="xl",
                            ),
                        ],
                        className="d-flex justify-content-evenly my-3",
                        style={"textAlign": "center"},
                    ),
                ],
                className="d-flex justify-content-center mt-2",
                style={"margin": "5px"},
            ),
        ],
        style={"margin": "5px"},
    )
    return tab_main


def make_tab_annotate() -> dbc.Tab:
    """Make tab Annotate."""
    tab_annotate = dbc.Tab(
        label="Annotate",
        tab_id="tab-annotate",
        children=[
            dbc.Row(
                [
                    dmc.Divider(
                        label=html.Span(
                            [
                                dmc.Text(
                                    "Annotate Sequences", style={"fontSize": "25px"}
                                ),
                            ],
                            className="d-flex align-items-center justify-content-evenly",
                        ),
                        labelPosition="center",
                        className="my-2",
                    ),
                    dbc.Row(
                        [
                            dmc.Select(
                                id="annotate-sequences",
                                value="no",
                                data=[
                                    {"value": "no", "label": "No"},
                                    {"value": "accession", "label": "Accession"},
                                    {"value": "name", "label": "Sequence name"},
                                    {"value": "fname", "label": "File name"},
                                ],
                                w=250,
                                size="xl",
                            ),
                            dmc.Button(
                                "Update",
                                id="update-annotate-sequences-button",
                                leftSection=DashIconify(
                                    icon="radix-icons:update",
                                    width=30,
                                ),
                                color="#3a7ebf",
                                size="xl",
                                style={"fontSize": "20px", "width": "150px"},
                            ),
                        ],
                        className="d-flex justify-content-evenly my-2",
                        style={"textAlign": "center"},
                    ),
                    dmc.Divider(
                        label=html.Span(
                            [
                                dmc.Text("Annotate Genes", style={"fontSize": "25px"}),
                            ],
                            className="d-flex align-items-center justify-content-evenly",
                        ),
                        labelPosition="center",
                        className="my-2",
                    ),
                    dbc.Row(
                        [
                            dmc.Select(
                                id="annotate-genes",
                                value="no",
                                data=[
                                    {"value": "no", "label": "No"},
                                    {"value": "top", "label": "Top genes"},
                                    {"value": "bottom", "label": "Bottom genes"},
                                    {
                                        "value": "top-bottom",
                                        "label": "Top and bottom genes",
                                    },
                                ],
                                w=250,
                                size="xl",
                            ),
                            dmc.Button(
                                "Update",
                                id="update-annotate-genes-button",
                                leftSection=DashIconify(
                                    icon="radix-icons:update",
                                    width=30,
                                ),
                                color="#3a7ebf",
                                size="xl",
                                style={"fontSize": "20px", "width": "150px"},
                            ),
                        ],
                        className="d-flex justify-content-evenly my-2",
                        style={"textAlign": "center"},
                    ),
                    dmc.Divider(
                        label=html.Span(
                            [
                                dmc.Text("Scale Bar", style={"fontSize": "25px"}),
                            ],
                            className="d-flex align-items-center justify-content-evenly",
                        ),
                        labelPosition="center",
                        className="my-2",
                    ),
                    dbc.Row(
                        [
                            dmc.Select(
                                id="scale-bar",
                                value="yes",
                                data=[
                                    {"value": "no", "label": "No"},
                                    {"value": "yes", "label": "Yes"},
                                ],
                                w=250,
                                size="xl",
                            ),
                            dmc.Button(
                                "Update",
                                id="update-scale-bar-button",
                                leftSection=DashIconify(
                                    icon="radix-icons:update",
                                    width=30,
                                ),
                                color="#3a7ebf",
                                size="xl",
                                style={"fontSize": "20px", "width": "150px"},
                            ),
                        ],
                        className="d-flex justify-content-evenly mt-1",
                        style={"textAlign": "center"},
                    ),
                ],
                className="d-flex justify-content-center mt-2",
                style={"margin": "5px"},
            ),
        ],
        style={"margin": "5px"},
    )
    return tab_annotate


def make_tab_edit() -> dbc.Tab:
    """Make tab edit."""
    tab_edit = dbc.Tab(
        label="Edit",
        tab_id="tab-edit",
        children=[
            dbc.Row(  # = GENES COLOR SECTION = #
                [
                    dmc.Divider(
                        label=html.Span(
                            dmc.Text("Colors", style={"fontSize": "25px"}),
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        labelPosition="center",
                        className="my-3",
                    ),
                    dbc.Row(
                        [
                            dmc.Button(
                                "Change",
                                id="change-gene-color-button",
                                leftSection=DashIconify(
                                    icon="oui:color",
                                    width=30,
                                ),
                                color="#3a7ebf",
                                size="xl",
                                style={"fontSize": "20px", "width": "160px"},
                            ),
                            dmc.ColorInput(
                                id="color-input",
                                value="rgb(0, 255, 255)",
                                w=300,
                                format="rgb",
                                swatches=[
                                    "rgb(255,0,255)",
                                    "rgb(0,255,255)",
                                    "rgb(255,26,0)",
                                    "rgb(255,116,0)",
                                    "rgb(255,255,0)",
                                    "rgb(0,255,0)",
                                    "rgb(151,59,255)",
                                    "rgb(0,0,0)",
                                ],
                                size="xl",
                            ),
                        ],
                        className="d-flex justify-content-evenly my-2",
                    ),
                    dbc.Row(
                        [
                            dmc.Button(
                                "Select",
                                id="select-change-color-button",
                                leftSection=DashIconify(
                                    icon="material-symbols-light:arrow-selector-tool-outline",
                                    width=40,
                                ),
                                color="#3a7ebf",
                                size="xl",
                                variant="outline",
                                disabled=True,
                                style={"fontSize": "20px", "width": "160px"},
                            ),
                            dcc.Store(id="select-button-state-store", data=False),
                        ],
                        className="d-flex justify-content-evenly my-2",
                    ),
                ],
                className="d-flex justify-content-center my-1",
                style={"margin": "5px"},
            ),
            dbc.Row(  # Color input for homology regions
                [
                    dmc.Divider(
                        label=html.Span(
                            dmc.Text(
                                "Homology Regions Colorscale",
                                style={"fontSize": "25px"},
                            ),
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        labelPosition="center",
                        className="mt-5 mb-2",
                    ),
                    dbc.Row(
                        [
                            dmc.Button(
                                "Update",
                                id="change-homology-color-button",
                                leftSection=DashIconify(
                                    icon="radix-icons:update",
                                    width=30,
                                ),
                                color="#3a7ebf",
                                size="xl",
                                style={"fontSize": "20px", "width": "160px"},
                            ),
                            dmc.Select(
                                id="color-scale",
                                value="Greys",
                                data=list_sequential_color_scales(),
                                w=300,
                                radius=10,
                                size="xl",
                            ),
                        ],
                        className="d-flex justify-content-evenly mt-3 mb-2",
                    ),
                    dbc.Row(
                        "Set Colorscale Range",
                        className="d-flex justify-content-evenly mt-3 mb-0",
                        style={"fontSize": "22px"},
                    ),
                    dbc.Row(
                        dmc.ButtonGroup(
                            [
                                dmc.Button(
                                    "Extreme Homologies",
                                    id="extreme-homologies-button",
                                    variant="subtle",
                                    size="xl",
                                    style={
                                        "width": "280px",
                                        "padding": "5px",
                                    },
                                ),
                                dmc.Button(
                                    "Truncate",
                                    id="truncate-colorscale-button",
                                    variant="filled",
                                    size="xl",
                                    style={
                                        "width": "280px",
                                        "padding": "5px",
                                        "pointer-events": "none",
                                    },
                                ),
                                dcc.Store(
                                    id="is_set_to_extreme_homologies",
                                    data=False,
                                ),
                            ],
                            style={"padding": "0px"},
                        ),
                        className="""
                                d-flex align-items-center justify-content-center my-1
                                rounded-1
                            """,
                        style={
                            "height": "75px",
                            "width": "90%",
                            "backgroundColor": "#2e2e2e",
                        },
                    ),
                    dbc.Row(
                        html.Div(
                            dcc.Graph(
                                id="color-scale-display",
                                config={"displayModeBar": False, "staticPlot": True},
                                style={"width": "100%"},
                                className="border",
                            ),
                            style={"width": "90%"},
                        ),
                        className="d-flex justify-content-center mt-2 mb-1",
                    ),
                    dbc.Row(
                        html.Div(
                            dmc.RangeSlider(
                                id="range-slider",
                                value=[0, 75],
                                marks=[
                                    {"value": 25, "label": "25%"},
                                    {"value": 50, "label": "50%"},
                                    {"value": 75, "label": "75%"},
                                ],
                                size="xl",
                                style={"width": "90%", "fontSize": "20px"},
                            ),
                            className="d-flex justify-content-center my-1",
                        ),
                    ),
                ],
                className="d-flex justify-content-center mt-2",
                style={"margin": "5px"},
            ),
        ],
        style={"margin": "15px"},
    )
    return tab_edit


def make_tab_save() -> dbc.Tab:
    """Make tab save."""
    tab_save = dbc.Tab(
        label="Save",
        tab_id="tab-save",
        children=[
            dbc.Row(
                [
                    dmc.Select(
                        label="Format",
                        id="figure-format",
                        value="png",
                        data=[
                            {"value": "png", "label": "png"},
                            {"value": "jpg", "label": "jpg"},
                            {"value": "pdf", "label": "pdf"},
                            {"value": "svg", "label": "svg"},
                        ],
                        w=170,
                        size="xl",
                    ),
                    dmc.Button(
                        "Download",
                        id="download-plot-button",
                        leftSection=DashIconify(
                            icon="bytesize:download",
                            width=35,
                        ),
                        variant="outline",
                        color="#3a7ebf",
                        size="xl",
                        style={
                            "fontSize": "20px",
                            "borderWidth": "3px",
                            "width": "240px",
                        },
                    ),
                    dcc.Download(id="download-plot-component"),
                ],
                className="d-flex align-items-end justify-content-evenly mt-4 mb-2",
                style={"margin": "5px"},
            ),
            dbc.Row(
                [
                    dmc.NumberInput(
                        label="Width",
                        id="figure-width",
                        value=1200,
                        step=10,
                        w=190,
                        size="xl",
                        suffix=" px",
                    ),
                    dmc.NumberInput(
                        label="Height",
                        id="figure-height",
                        value=1000,
                        step=10,
                        w=190,
                        size="xl",
                        suffix=" px",
                    ),
                    dmc.NumberInput(
                        label="Scale",
                        id="figure-scale",
                        value=1,
                        step=0.2,
                        min=1,
                        max=10,
                        w=140,
                        size="xl",
                    ),
                ],
                className="d-flex align-items-end justify-content-evenly mt-4 mb-2",
                style={"margin": "5px"},
            ),
        ],
        style={"margin": "5px"},
    )
    return tab_save


def create_dash_app() -> dash.Dash:
    """Make the app layout"""
    _dash_renderer._set_react_version("18.2.0")

    # Initialize the Dash app with a Bootstrap theme
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

    app.layout = dmc.MantineProvider(
        dbc.Container(
            [
                dcc.Location(id="url", refresh=True),  # Allows refreshing app
                dbc.Row(
                    [
                        dbc.Col(  # PLOT CONTROL
                            children=[
                                html.Div(
                                    "MSPlotter",
                                    className="text-white fw-bold text-center my-2",
                                    style={"fontSize": "30px"},
                                ),
                                html.Div(
                                    [
                                        html.Div(  # TABS MENU
                                            dbc.Tabs(
                                                [
                                                    make_tab_main(),
                                                    make_tab_annotate(),
                                                    make_tab_edit(),
                                                    make_tab_save(),
                                                ],
                                                id="tabs",
                                            ),
                                            className="mt-1",
                                            style={
                                                "height": "950px",
                                                "width": "100%",
                                                "overflow": "auto",
                                            },
                                        ),
                                    ],
                                ),
                            ],
                            className="col-5 mx-3",
                            style={
                                "width": "580px",
                                "font-size": "20px",
                                "backgroundColor": "#242424",
                                "border-radius": "8px",
                                "height": "100vh",
                                "overflow": "auto",
                            },
                        ),
                        dbc.Col(  # GRAPH SECTION
                            [
                                html.Div(
                                    dcc.Graph(
                                        id="plot",
                                        style={"height": "100%"},
                                    ),
                                    style={
                                        "border": "1px solid black",
                                        "height": "1000px",
                                        "display": "flex",
                                        "flex-direction": "column",
                                        "justify-content": "flex-start",
                                    },
                                ),
                                dcc.Store(id="selected-trace-store", data=[]),
                                dcc.Store(id="extreme-homologies-store", data=[]),
                            ],
                            class_name="col",
                            style={"padding-top": "0px"},
                        ),
                    ],
                    className="align-items-start mb-2 mt-0",
                ),
            ],
            fluid=True,
            style={
                "padding": "20px",
            },
        ),
        forceColorScheme="dark",
    )

    # ==== Callback files-table ================================================+======= #
    @app.callback(
        Output("files-table", "rowData"),
        [
            Input("upload", "filename"),
            Input("upload", "contents"),
            Input("delete-selected-files-button", "n_clicks"),
        ],
        [State("files-table", "rowData"), State("files-table", "selectedRows")],
    )
    def update_file_table(
        filenames, contents, n_clicks, current_row_data, selected_rows
    ):
        ctx = dash.callback_context
        ctx_id = ctx.triggered[0]["prop_id"].split(".")[0]
        # Update table with uploaded files.
        if (ctx_id == "upload") and filenames and contents:
            new_rows = []
            # Simulate saving each file and creating a temporary file path
            for name, content in zip(filenames, contents):
                file_path = save_uploaded_file(name, content, TMP_PATH)
                new_rows.append({"filename": name, "filepath": file_path})

            # Append new filenames and file paths to the table data
            return current_row_data + new_rows if current_row_data else new_rows

        # Delete selected rows
        if ctx_id == "delete-selected-files-button":
            updated = [row for row in current_row_data if row not in selected_rows]
            return updated

        return current_row_data if current_row_data else []

    # ==== Callback to plot the alignments -> MAIN FUNCTION ============================ #
    @app.callback(
        [
            Output("plot", "figure"),
            Output("selected-trace-store", "data"),
            Output("plot", "clickData"),
            Output("extreme-homologies-store", "data"),
        ],
        [
            Input("draw-button", "n_clicks"),
            Input("erase-button", "n_clicks"),
            Input("plot", "clickData"),
            Input("change-homology-color-button", "n_clicks"),
            Input("change-gene-color-button", "n_clicks"),
            Input("update-annotate-sequences-button", "n_clicks"),
            Input("update-annotate-genes-button", "n_clicks"),
            Input("update-scale-bar-button", "n_clicks"),
        ],
        [
            State("files-table", "virtualRowData"),
            State("tabs", "active_tab"),
            State("plot", "figure"),
            State("color-input", "value"),
            State("selected-trace-store", "data"),
            State("select-button-state-store", "data"),
            State("color-scale", "value"),
            State("range-slider", "value"),
            State("align-plot", "value"),
            State("homology-lines", "value"),
            State("minimum-homology-length", "value"),
            State("extreme-homologies-store", "data"),
            State("is_set_to_extreme_homologies", "data"),
            State("annotate-sequences", "value"),
            State("annotate-genes", "value"),
            State("scale-bar", "value"),
            State("use-genes-info-from", "value"),
        ],
        prevent_initial_call=True,
    )
    def main_plot(
        plot_button_clicks,  # input plot button click
        clear_button_clicks,  # input clear button click
        click_data,  # input click data form plot
        change_homology_color_button_clicks,  # input selected color scale value
        change_gene_color_button_clicks,  # input selected color value
        annotate_sequences_button_clicks,  # input to update annotate sequences
        annotate_genes_button_clicks,  # input to update annotate sequences
        scale_bar_button_clicks,  # input to update scale bar
        virtual,  # state of table with path to GenBank files
        active_tab,  # state activet tab
        figure_state,  # state output Figure object
        color_input_state,  # state color input
        selected_trace_store_state,  # state selected trace store
        select_button_state,  # state select button state store
        color_scale_state,  # state color scale
        range_slider_state,  # state range slider for color scale
        align_plot_state,  # state align plot
        homology_lines_state,  # state homology lines
        minimum_homology_length,  # state miminum homology length
        extreme_homologies_values_state,  # state of extreme homologies values.
        is_set_to_extreme_homologies,  # state button colorscale range
        annotate_sequences_state,  # state annotate sequences
        annotate_genes_state,  # state annotate sequences
        scale_bar_state,  # state scale bar
        use_genes_info_from_state,  # state genes info
    ) -> Figure:
        # Use context to find button that triggered the callback.
        ctx = dash.callback_context
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Print for debugging
        print()
        print(f"button id: {button_id}")
        print(f"slider range: {range_slider_state}")
        print(f"align_plot: {align_plot_state}")
        print(f"is_set_to_extreme_homologies: {is_set_to_extreme_homologies}")

        # ============================================================================== #
        #                             MAIN TAB -> Plot                                   #
        # ============================================================================== #
        # ==== Plot Sequences ========================================================== #
        if (button_id == "draw-button") and virtual:
            # Fill USER_INPUT for plotting
            USER_INPUT.input_files = [Path(row["filepath"]) for row in virtual]
            USER_INPUT.output_folder = TMP_PATH
            USER_INPUT.alignments_position = align_plot_state
            USER_INPUT.identity_color = color_scale_state
            USER_INPUT.colorscale_vmin = range_slider_state[0] / 100
            USER_INPUT.colorscale_vmax = range_slider_state[1] / 100
            USER_INPUT.set_colorscale_to_extreme_homologies = (
                is_set_to_extreme_homologies
            )
            USER_INPUT.annotate_sequences = annotate_sequences_state
            USER_INPUT.annotate_genes = annotate_genes_state
            USER_INPUT.annotate_genes_with = use_genes_info_from_state
            USER_INPUT.straight_homology_regions = homology_lines_state
            USER_INPUT.minimum_homology_length = minimum_homology_length
            USER_INPUT.add_scale_bar = True if scale_bar_state == "yes" else False

            fig, lowest_identity, highest_identity = plt.make_figure_gui(USER_INPUT)
            fig.update_layout(clickmode="event+select")
            print("figure is displayed")
            return (
                fig,
                selected_trace_store_state,
                None,
                [lowest_identity, highest_identity],
            )

        # ==== Erase plot ============================================================== #
        if button_id == "erase-button":
            return ({}, [], None, [])

        # ============================================================================== #
        #                           EDIT TAB -> colors                                   #
        # ============================================================================== #
        # = Change homology color and colorscale bar legend = #
        if button_id == "change-homology-color-button":
            # Change homlogy color traces
            fig = plt.change_homoloy_color_traces(
                figure=figure_state,
                colorscale_name=color_scale_state,
                vmin_truncate=range_slider_state[0] / 100,
                vmax_truncate=range_slider_state[1] / 100,
                set_colorscale_to_extreme_homologies=is_set_to_extreme_homologies,
                lowest_homology=extreme_homologies_values_state[0],
                highest_homology=extreme_homologies_values_state[1],
            )
            # Remove old colorscale bar legend
            fig = plt.remove_traces_by_name(fig, "colorbar legend")
            # convert the fig dictionary return by remove_traces_by_name into a Figure object
            fig = Figure(data=fig["data"], layout=fig["layout"])
            # Make new colorscale bar legend
            fig = plt.plot_colorbar_legend(
                fig=fig,
                colorscale=plt.get_truncated_colorscale(
                    colorscale_name=color_scale_state,
                    vmin=range_slider_state[0] / 100,
                    vmax=range_slider_state[1] / 100,
                ),
                min_value=extreme_homologies_values_state[0],
                max_value=extreme_homologies_values_state[1],
                set_colorscale_to_extreme_homologies=is_set_to_extreme_homologies,
            )
            return (
                fig,
                selected_trace_store_state,
                None,
                extreme_homologies_values_state,
            )

        # = Change color of selected traces = #
        if button_id == "change-gene-color-button":
            curve_numbers = set(selected_trace_store_state)
            # Iterate over selected curve numbers and change color
            for curve_number in curve_numbers:
                figure_state["data"][curve_number]["fillcolor"] = color_input_state
                figure_state["data"][curve_number]["line"]["color"] = color_input_state
                figure_state["data"][curve_number]["line"]["width"] = 1
            # Return figure and empty the list of stored curve numbers.
            return (figure_state, [], None, extreme_homologies_values_state)

        # = Select traces for changing color = #
        if (
            (active_tab == "tab-edit")
            and (click_data is not None)
            and select_button_state
        ):
            stored = selected_trace_store_state
            # Get curve_number
            curve_number = click_data["points"][0]["curveNumber"]
            # if curve_number already in stored, remove it from the list and restore trace
            if curve_number in stored:
                selected_trace_store_state.remove(curve_number)
                fillcolor = figure_state["data"][curve_number]["fillcolor"]
                figure_state["data"][curve_number]["line"]["color"] = fillcolor
                figure_state["data"][curve_number]["line"]["width"] = 1
                return (
                    figure_state,
                    selected_trace_store_state,
                    None,
                    extreme_homologies_values_state,
                )
            # Save the curve number in stored for future modification
            stored.append(curve_number)
            # Make selection effect by changing line color
            fig = plt.make_selection_effect(figure_state, curve_number)
            return (fig, stored, None, extreme_homologies_values_state)

        # ============================================================================== #
        #                                ANNOTATE TAB                                    #
        # ============================================================================== #
        # ==== Change annotation to DNA sequences ====================================== #
        if figure_state and button_id == "update-annotate-sequences-button":
            # Convert the figure_state dictionary into a Figure object
            fig = Figure(data=figure_state["data"], layout=figure_state["layout"])
            # Remove any dna sequence annotations
            fig = plt.remove_annotations_by_name(fig, "Sequence annotation:")
            # If annotate_sequences_state is not no add annotations.
            if annotate_sequences_state != "no":
                return (
                    plt.annotate_dna_sequences_using_trace_customdata(
                        fig, annotate_sequences_state
                    ),
                    selected_trace_store_state,
                    None,
                    extreme_homologies_values_state,
                )
            # Otherwise, return figure without any annotation.
            return (
                fig,
                selected_trace_store_state,
                None,
                extreme_homologies_values_state,
            )

        # ==== Toggle scale bar ======================================================== #
        if figure_state and button_id == "update-scale-bar-button":
            # Convert the figure_state dictionary into a Figure object
            fig = Figure(data=figure_state["data"], layout=figure_state["layout"])
            show = True if scale_bar_state == "yes" else False
            # toggle scale bar
            fig = plt.toggle_scale_bar(fig, show)
            return (
                fig,
                selected_trace_store_state,
                None,
                extreme_homologies_values_state,
            )

        # ==== Change annotation to genes ============================================== #
        if figure_state and (button_id == "update-annotate-genes-button"):
            # convert the figure_state dictionary into a Figure object
            fig = Figure(data=figure_state["data"], layout=figure_state["layout"])
            # Remove any gene annotations
            fig = plt.remove_annotations_by_name(fig, "Gene annotation:")

            if annotate_genes_state == "top":
                return (
                    plt.annotate_genes_top_using_trace_customdata(fig),
                    selected_trace_store_state,
                    None,
                    extreme_homologies_values_state,
                )
            if annotate_genes_state == "bottom":
                return (
                    plt.annotate_genes_bottom_using_trace_customdata(fig),
                    selected_trace_store_state,
                    None,
                    extreme_homologies_values_state,
                )
            if annotate_genes_state == "top-bottom":
                fig = plt.annotate_genes_top_using_trace_customdata(fig)
                fig = plt.annotate_genes_bottom_using_trace_customdata(fig)
                return (
                    fig,
                    selected_trace_store_state,
                    None,
                    extreme_homologies_values_state,
                )

            return (
                fig,
                selected_trace_store_state,
                None,
                extreme_homologies_values_state,
            )

        return (
            figure_state,
            selected_trace_store_state,
            None,
            extreme_homologies_values_state,
        )

    # ==== Callbacks to activate update buttons only when there is a figure ============ #
    @app.callback(
        [
            Output("erase-button", "disabled"),
            Output("update-annotate-sequences-button", "disabled"),
            Output("update-annotate-genes-button", "disabled"),
            Output("update-scale-bar-button", "disabled"),
            Output("change-gene-color-button", "disabled"),
            Output("change-homology-color-button", "disabled"),
            Output("select-change-color-button", "disabled"),
        ],
        Input("plot", "figure"),
    )
    def toggle_update_buttons(figure) -> bool:
        if figure and figure.get("data", []):
            return [False] * 7
        return [True] * 7

    # ==== Callback to activate Draw button when files in upload table ================= #
    @app.callback(
        Output("draw-button", "disabled"),
        Input("files-table", "rowData"),
    )
    def toggle_draw_button(row_data) -> bool:
        return False if row_data else True

    # ==== Callback to activate Select buttons ========================================= #
    @app.callback(
        [
            Output("select-change-color-button", "variant"),
            Output("select-button-state-store", "data"),
        ],
        Input("select-change-color-button", "n_clicks"),
        State("select-button-state-store", "data"),
    )
    def toggle_select_button(n_clicks, is_active):
        if n_clicks:
            # Toggle the active state on click
            is_active = not is_active

        # Set button style based on the active state
        if is_active:
            button_style = "filled"
        else:
            button_style = "outline"
        return button_style, is_active

    # ==== Callback to toggle between set colorscale buttons =========================== #
    @app.callback(
        [
            Output("extreme-homologies-button", "variant"),
            Output("extreme-homologies-button", "style"),
            Output("truncate-colorscale-button", "variant"),
            Output("truncate-colorscale-button", "style"),
            Output("is_set_to_extreme_homologies", "data"),
        ],
        [
            Input("extreme-homologies-button", "n_clicks"),
            Input("truncate-colorscale-button", "n_clicks"),
        ],
    )
    def toggle_colorscale_buttons(extreme_clicks, truncate_clicks):
        ctx = dash.callback_context

        option1 = (
            "subtle",
            {"width": "280px", "padding": "5px"},
            "filled",
            {"width": "280px", "padding": "5px", "pointer-events": "none"},
            False,
        )
        option2 = (
            "filled",
            {"width": "280px", "padding": "5px", "pointer-events": "none"},
            "subtle",
            {"width": "280px", "padding": "5px"},
            True,
        )

        if not ctx.triggered:
            return option1

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == "extreme-homologies-button":
            return option2
        elif triggered_id == "truncate-colorscale-button":
            return option1

        return option1

    # ==== Callback to update the color scale display ================================== #
    @app.callback(
        Output("color-scale-display", "figure"),
        Input("color-scale", "value"),
    )
    def update_color_scale(value):
        return plt.create_color_line(value.capitalize())

    # ==== Callback to reset page ====================================================== #
    @app.callback(
        Output("url", "href"),
        Input("reset-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_page(n_clicks):
        if n_clicks:
            # Return the current URL to trigger a reload
            return "/"

    # ==== Callback to save file ======================================================= #
    @app.callback(
        Output("download-plot-component", "data"),
        Input("download-plot-button", "n_clicks"),
        [
            State("plot", "figure"),
            State("figure-format", "value"),
            State("figure-scale", "value"),
            State("figure-width", "value"),
            State("figure-height", "value"),
        ],
        prevent_initial_call=True,
    )
    def download_plot(
        n_clicks,
        figure,
        figure_format,
        scale,
        width,
        height,
    ):
        # Create an in-memory bytes buffer
        buffer = BytesIO()

        # Convert figure to an image in the chosen format and DPI
        fig = Figure(data=figure["data"], layout=figure["layout"])

        fig.write_image(
            buffer,
            format=figure_format,
            width=width,
            height=height,
            scale=scale,
            engine="kaleido",
        )

        # Encode the buffer as a base64 string
        encoded = base64.b64encode(buffer.getvalue()).decode()
        figure_name = f"plot.{figure_format}"

        # Return data for dmc.Download to promto a download
        return dict(
            base64=True, content=encoded, filename=figure_name, type=figure_format
        )

    return app


def main() -> None:
    app = create_dash_app()
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
