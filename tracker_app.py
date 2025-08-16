import dash
from dash import html, dcc, Input, Output, State
import pandas as pd
from datetime import datetime

# Inicializar la app
app = dash.Dash(__name__)

# DataFrame en memoria
data = pd.DataFrame(columns=["actividad", "inicio", "fin"])

app.layout = html.Div([
    html.H1("Registro de Actividades con Timestamps"),

    # Lista de actividades
    html.Div([
        html.Button("Correr", id="btn-correr", n_clicks=0, style={"margin": "5px"}),
        html.Button("Leer", id="btn-leer", n_clicks=0, style={"margin": "5px"}),
        html.Button("Estudiar", id="btn-estudiar", n_clicks=0, style={"margin": "5px"}),
    ], style={"margin": "20px"}),

    html.Button("Finalizar Actividad", id="btn-fin", n_clicks=0, style={"margin": "20px"}),

    html.H2("Registros"),
    html.Div(id="tabla-registros"),

    dcc.Store(id="memoria")  # almacena los datos en memoria del navegador
])


def timestamp_now():
    """Devuelve el timestamp exacto con milisegundos"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


@app.callback(
    Output("memoria", "data"),
    Output("tabla-registros", "children"),
    Input("btn-correr", "n_clicks"),
    Input("btn-leer", "n_clicks"),
    Input("btn-estudiar", "n_clicks"),
    Input("btn-fin", "n_clicks"),
    State("memoria", "data"),
    prevent_initial_call=True
)
def registrar(correr, leer, estudiar, fin, memoria):
    ctx = dash.callback_context
    if not ctx.triggered:
        return memoria, "Sin registros"

    # Inicializar si está vacío
    if memoria is None:
        memoria = []

    btn_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if btn_id in ["btn-correr", "btn-leer", "btn-estudiar"]:
        actividad = btn_id.split("-")[1]  # ejemplo: "correr"
        memoria.append({
            "actividad": actividad,
            "inicio": timestamp_now(),
            "fin": None
        })

    elif btn_id == "btn-fin":
        # Actualiza el último registro sin fin
        for row in reversed(memoria):
            if row["fin"] is None:
                row["fin"] = timestamp_now()
                break

    # Crear tabla en HTML
    df = pd.DataFrame(memoria)
    tabla = html.Table([
        html.Thead(html.Tr([html.Th(col) for col in df.columns])),
        html.Tbody([
            html.Tr([html.Td(str(df.iloc[i][col])) for col in df.columns])
            for i in range(len(df))
        ])
    ])

    return memoria, tabla


#if __name__ == "__main__":
#    app.run(debug=True)
