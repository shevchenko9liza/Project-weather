from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from flask import Flask
import pandas as pd

def create_dash_app(flask_app):
    dash_app = Dash(__name__, server=flask_app, url_base_pathname='/dash/')
    
    dash_app.layout = html.Div([
        html.H1('Интерактивные графики погоды'),
        
        dcc.Dropdown(
            id='graph-type',
            options=[
                {'label': 'Температура', 'value': 'temp'},
                {'label': 'Влажность', 'value': 'humidity'},
                {'label': 'Скорость ветра', 'value': 'wind'},
                {'label': 'Все параметры', 'value': 'all'}
            ],
            value='all'
        ),
        
        dcc.Graph(id='weather-graph'),
        
        dcc.Slider(
            id='days-slider',
            min=1,
            max=5,
            step=1,
            value=1,
            marks={i: f'{i} день' for i in range(1, 6)}
        )
    ])
    
    @dash_app.callback(
        Output('weather-graph', 'figure'),
        [Input('graph-type', 'value'),
         Input('days-slider', 'value')]
    )
    def update_graph(graph_type, days):
        # Здесь будет логика обновления графика
        pass
    
    return dash_app 