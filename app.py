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
from utils.get_intervals import get_activity_intervals
from constants.dictionaries import activities_color



load_dotenv()

button_style = "flex items-center rounded-md border border-slate-300 py-2 px-4 text-center text-sm transition-all shadow-sm hover:shadow-lg text-slate-600 hover:text-white hover:bg-slate-800 hover:border-slate-800 focus:text-white focus:bg-slate-800 focus:border-slate-800 active:border-slate-800 active:text-white active:bg-slate-800 disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none"
# Initialize Google Cloud Storage client
def gcs_client():
    service_account_info = {
        "type": os.getenv("GCP_TYPE"),
        "project_id": os.getenv("GCP_PROJECT_ID"),
        "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GCP_PRIVATE_KEY"),#.replace('\\n', '\n'),
        "client_email": os.getenv("GCP_CLIENT_EMAIL"),
        "client_id": os.getenv("GCP_CLIENT_ID"),
        "auth_uri": os.getenv("GCP_AUTH_URI"),
        "token_uri": os.getenv("GCP_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GCP_AUTH_PROVIDER_CERT_URL"),
        "client_x509_cert_url": os.getenv("GCP_CLIENT_CERT_URL")
    }
    return storage.Client.from_service_account_info(service_account_info)
client = gcs_client()

external_scripts = [
        "https://cdn.tailwindcss.com"
    ]

# Initialize the Dash app
app = dash.Dash(
    name="Accelerometer Data Visualization",
    external_scripts=external_scripts
    )
server = app.server

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
            html.Button('Add Activity', id='activity-button', n_clicks=0, disabled=True, className=button_style),
        ], className="flex justify-end mb-5 w-full"
    ),
    dcc.Loading(
        id="loading-graph",
        type="default",
        children=dcc.Graph(id='acceleration-plot', className="w-full")
    ),

    html.Div(id='output')
],className="p-10"
)

register_update_file_dropdown_callback(app, client)

@app.callback(
    [Output('acceleration-plot', 'figure'),
     Output('status-message', 'children',allow_duplicate=True)],
    [Input('plot-button', 'n_clicks')],
    [State('file-selection-dropdown', 'value'),
     State('user-id-input', 'value')],
    prevent_initial_call=True
)
def update_plot(n_clicks, selected_file, user_id):
    if not selected_file:
        return go.Figure(), "Please select a file and click 'Plot Data'"
    
    bucket_name = "cardiocareai1.firebasestorage.app"
    
    try:
        client = gcs_client()
        blob = client.bucket(bucket_name).blob(selected_file)
        csv_data = blob.download_as_text()
        df = pd.read_csv(StringIO(csv_data))
        
        # Process the data
        df['time'] = df['t']
        df['t'] = pd.to_numeric(df['t'])
        df['t'] = pd.to_datetime(df['t'], unit='ms')
        
        if df.empty:
            return go.Figure(), "No valid data found in the file"
        
        # Create the plot
        columns = ['x', 'y', 'z']
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                           vertical_spacing=0.05, subplot_titles=columns)

        for i, column in enumerate(columns, start=1):
            fig.add_trace(
                go.Scatter(x=df['t'], y=df[column], mode='lines+markers', name=column),
                row=i, col=1
            )

        fig.update_layout(
            height=800,
            title_text=f"Accelerometer Data from {selected_file}",
            showlegend=False,
            dragmode='select'
        )
        
        for interval in get_activity_intervals(df):
            fig.add_shape(
                type="rect",
                x0=interval["start"],  # Already datetime
                x1=interval["end"],
                xref="x",
                y0=0,
                y1=1,
                yref="paper",
                line=dict(width=0),
                fillcolor=activities_color(interval["activity"]),
                opacity=0.3
            )
        # First subplot: only range selector (buttons)
        fig.update_xaxes(
            row=1, col=1,
            rangeslider_visible=False,
            rangeselector=dict(
                buttons=list([
                    dict(count=10, label="10s", step="second", stepmode="backward"),
                    dict(count=30, label="30s", step="second", stepmode="backward"),
                    dict(count=1, label="1m", step="minute", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )

        # Second subplot: no slider or selector
        fig.update_xaxes(
            row=2, col=1,
            rangeslider_visible=False,
            rangeselector=None
        )

        # Third subplot: only range slider (slider bar)
        fig.update_xaxes(
            row=3, col=1,
            rangeslider_visible=True,
            rangeselector=None
        )
        
        return fig, f"Showing data from file: {selected_file}"
    
    except Exception as e:
        return go.Figure(), f"Error loading data: {str(e)}"
    

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
     Output('activity-input', 'value')],
    [Input('activity-button', 'n_clicks')],
    [State('acceleration-plot', 'selectedData'),
     State('activity-input', 'value')],
    prevent_initial_call=True
)
def handle_activity_button_click(n_clicks, selectedData, activity):
    if n_clicks > 0:
        label_activity(client=client, selected_timestamps=selectedData, activity=activity)
        return True, True, ''
    return dash.no_update, dash.no_update, dash.no_update

if __name__ == '__main__':
    app.run(debug=True)