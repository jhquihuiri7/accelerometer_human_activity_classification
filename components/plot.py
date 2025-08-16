from io import StringIO
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.get_intervals import get_activity_intervals
from constants.dictionaries import activities_color

def main_plot(df, selected_file, show_windows=False):
    """Function to create the main plot with accelerometer data"""
    
    if not selected_file:
        return go.Figure(), "Please select a file and click 'Plot Data'"
    
    try:
        
        # Process the data
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
                go.Scattergl(x=df['t'], y=df[column], mode='lines+markers', name=column),
                row=i, col=1
            )

        fig.update_layout(
            height=800,
            title_text=f"Accelerometer Data from {selected_file}",
            showlegend=False,
            dragmode='select'
        )
        
        # Add activity intervals if they exist
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

        if show_windows and not df.empty:
            # Calculate the time range
            min_time = df['t'].min()
            max_time = df['t'].max()
            total_duration = max_time - min_time
            window_duration = total_duration / 23

            # Add vertical lines for each division
            for i in range(1, 23):
                division_time = min_time + i * window_duration
                fig.add_vline(
                    x=division_time,
                    line=dict(color="red", width=1),
                    row="all",  # Applies to all subplots
                    opacity=0.7
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

        return fig
    
    except Exception as e:
        print(f"Error creating plot: {str(e)}")
        return go.Figure()