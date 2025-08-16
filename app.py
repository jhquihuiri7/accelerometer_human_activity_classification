# -*- coding: utf-8 -*-
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google.cloud import storage
from google.api_core.exceptions import NotFound
import pandas as pd
from io import StringIO
from datetime import datetime
import os
from dotenv import load_dotenv
from callbacks.update_file_dropdown import register_update_file_dropdown_callback
from utils.label_data import label_activity
from utils.auth import gcs_client
from components.plot import main_plot
from components.legend_boxes import plot_legend_boxes
import dash_daq as daq

def create_label_app(server):

    button_style = "flex items-center rounded-md border border-slate-300 py-2 px-4 text-center text-sm transition-all shadow-sm hover:shadow-lg text-slate-600 hover:text-white hover:bg-slate-800 hover:border-slate-800 focus:text-white focus:bg-slate-800 focus:border-slate-800 active:border-slate-800 active:text-white active:bg-slate-800 disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none"
    # Initialize Google Cloud Storage client

    client = gcs_client()

    external_scripts = [
            "https://cdn.tailwindcss.com"
        ]

    # Initialize the Dash app
    app = dash.Dash(
        server=server,
        name="Accelerometer Data Visualization",
        title="Accelerometer Data Visualization",
        external_scripts=external_scripts
        )

    # App layout
    app.layout = html.Div([
        html.H1("Accelerometer Data Visualization", style={'textAlign': 'center'}),
        
        html.Div([
            html.Label("Select User:"),
            dcc.Dropdown(
                id='user-id-input',
                options=[
                    {'label': 'Teddy', 'value': 'lDeSLxsFy1XLxOWJz9Ce9BhTgwY2'},
                    {'label': 'Jhonatan', 'value': '6NX2wXNm0tbodQE5xi83jsv3R4e2'},
                    {'label': 'Raj', 'value': 'dib7IxzzzJRrOlZYMcXJvQltkVb2'}
                ],
                value='lDeSLxsFy1XLxOWJz9Ce9BhTgwY2',
                className="w-[200px] mx-10"
            ),
            dcc.Loading(
                id="loading-files",
                type="default",
                children=html.Button('Load Files', id='load-files-button', n_clicks=0, className=button_style),
            ),
        ], className="flex items-start mb-5"),
        
        html.Div(id='file-selection-div', children=[
            html.Label("Select File to Analyze:"),
            dcc.Dropdown(
                id='file-selection-dropdown',
                options=[],
                className="w-[300px] mx-10"
            ),
            dcc.Loading(
                id="loading-plot",
                type="default",
                children=html.Button('Plot Data', id='plot-button', n_clicks=0, disabled=True, className=button_style),
            ),
        ], className="flex items-start"),
        
        html.Div(id='status-message', style={'margin': '20px', 'textAlign': 'center'}),
        html.Div(
            children=[
                plot_legend_boxes(),
                html.Div(
                    children=[
                        daq.ToggleSwitch(
                            id='show-windows-toggle',
                            value=False,
                            color="#00cc96",
                            style={"color": "#00cc96"},
                        ),
                        dcc.Dropdown(
                        id='activity-input',
                        options=[
                            {'label': 'Running', 'value': 'running'},
                            {'label': 'Sitting', 'value': 'sitting'},
                            {'label': 'Jogging', 'value': 'jogging'},
                            {'label': 'Walking', 'value': 'walking'},
                            {'label': 'Standing', 'value': 'standing'},
                            {'label': 'Lying down', 'value': 'lying down'},
                            {'label': 'Going upstairs', 'value': 'going upstairs'},
                            {'label': 'Going downstairs', 'value': 'going downstairs'}
                        ],
                        value='',
                        className="w-[200px] mx-10",
                        disabled=True
                        ),
                        html.Button('Add Activity', id='activity-button', n_clicks=0, disabled=True, className=button_style)
                    ], className="flex flex-row"
                ),
            ], className="flex flex-row justify-between items-center mb-5 w-full"
        ),
        dcc.Loading(
            id="loading-graph",
            type="default",
            children=dcc.Graph(id='acceleration-plot', className="w-full")
        ),
        html.Div(id='output'),
        dcc.Store(id='data-store'),
        dcc.Store(id='file-store')
    ],className="p-10"
    )

    register_update_file_dropdown_callback(app, client)

    @app.callback(
        [Output('acceleration-plot', 'figure'),
        Output('status-message', 'children',allow_duplicate=True),
        Output('data-store', 'data'),
        Output('file-store', 'data')],
        [Input('plot-button', 'n_clicks')],
        [State('file-selection-dropdown', 'value'),
        State('user-id-input', 'value')],
        prevent_initial_call=True
    )
    def update_plot(n_clicks, selected_file, user_id):
        print("UPDATE PLOT CALLBACK TRIGGERED")
        if not selected_file:
            return go.Figure(), "Please select a file and click 'Plot Data'"
        
        bucket_name = "cardiocareai1.firebasestorage.app"
        
        try:
            client = gcs_client()
            blob = client.bucket(bucket_name).blob(selected_file)
            csv_data = blob.download_as_text()
            df = pd.read_csv(StringIO(csv_data))
            data = df.to_dict()
            return main_plot(df,selected_file, show_windows=False), f"Showing data from file: {selected_file}",data, selected_file
        except Exception as e:
            return go.Figure(), f"Error loading data: {str(e)}", None, None
        

    @app.callback(
        Output('output', 'children'),
        Input('acceleration-plot', 'selectedData')
    )
    def mostrar_seleccion(selectedData):
        if not selectedData:
            return "Selecciona puntos con el mouse."
        x_vals = [p['x'] for p in selectedData['points']]
        return f"Valores X seleccionados: {x_vals}"

    @app.callback(
        [Output('activity-button', 'disabled'),
        Output('activity-input', 'disabled')],
        [Input('acceleration-plot', 'selectedData')],
        prevent_initial_call=True
    )
    def enable_activity_button(selectedData):
        if selectedData is None:
            return True, True  # Disable both button and dropdown when no selection
        return False, False  # Enable both when there's a selection

    @app.callback(
        [Output('activity-button', 'disabled',allow_duplicate=True),
        Output('activity-input', 'disabled', allow_duplicate=True),
        Output('activity-input', 'value'),
        Output('data-store', 'data', allow_duplicate=True),
        Output('acceleration-plot', 'figure', allow_duplicate=True)],
        [Input('activity-button', 'n_clicks')],
        [State('acceleration-plot', 'selectedData'),
        State('activity-input', 'value'),
        State('file-store', 'data'),
        State('show-windows-toggle', 'value')],
        prevent_initial_call=True
    )
    def handle_activity_button_click(n_clicks, selectedData, activity, selected_file, value):
        if n_clicks > 0:
            df = label_activity(client=client, selected_timestamps=selectedData, activity=activity, selected_file=selected_file)
            data =df.to_dict()
            fig = main_plot(df, selected_file=selected_file, show_windows=value > 0)
            return True, True, '', data, fig
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output('acceleration-plot', 'figure', allow_duplicate=True),
        [Input('show-windows-toggle', 'value')],
        [State('file-selection-dropdown', 'value'),
        State('data-store', 'data')],
        prevent_initial_call=True
    )
    def handle_toggle_window(value, selected_file,data):
        print("TOGGLE WINDOW CALLBACK TRIGGERED")
        df = pd.DataFrame(data)
        return main_plot(df, selected_file=selected_file, show_windows=value > 0)

    return app
#if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))