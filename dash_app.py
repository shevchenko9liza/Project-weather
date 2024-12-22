from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from flask import session

def create_dash_app(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dashboard/',
        assets_folder='static'
    )

    dash_app.server = flask_app

    dash_app.layout = html.Div([
        html.H2('Прогноз погоды', className='dash-title'),
        
        html.Div([
            dcc.Dropdown(
                id='location-selector',
                options=[],
                placeholder='Выберите город',
                className='dropdown'
            ),
            
            dcc.Dropdown(
                id='time-interval',
                options=[
                    {'label': '1 день', 'value': '1'},
                    {'label': '3 дня', 'value': '3'},
                    {'label': '5 дней', 'value': '5'}
                ],
                value='1',
                className='dropdown'
            )
        ], className='controls'),
        
        html.Div([
            dcc.Graph(id='temperature-graph'),
            dcc.Graph(id='wind-graph'),
            dcc.Graph(id='precipitation-graph')
        ], className='graphs-container')
    ])

    @dash_app.callback(
        Output('location-selector', 'options'),
        [Input('location-selector', 'id')]
    )
    def update_locations(_):
        if 'weather_data' in session:
            locations = [{'label': loc['location'], 'value': loc['location']} 
                        for loc in session['weather_data']]
            return locations
        return []

    @dash_app.callback(
        [Output('temperature-graph', 'figure'),
         Output('wind-graph', 'figure'),
         Output('precipitation-graph', 'figure')],
        [Input('location-selector', 'value'),
         Input('time-interval', 'value')]
    )
    def update_graphs(location, interval):
        if not location or 'weather_data' not in session:
            return create_empty_figures()
            
        weather_data = next(
            (item for item in session['weather_data'] if item['location'] == location),
            None
        )
        
        if not weather_data:
            return create_empty_figures()

        # Создаем временные метки с часами
        dates = []
        for day in range(int(interval)):
            for hour in [6, 12, 18, 0]:  # Основные временные точки дня
                dates.append(datetime.now() + timedelta(days=day, hours=hour))
        
        # Генерируем реалистичные данные на основе текущих значений
        def generate_hourly_data(base_value, variation=0.2):
            return [base_value * (1 + ((-1)**hour) * variation * (hour/24)) 
                   for hour in range(len(dates))]

        # Температура
        temp_data = generate_hourly_data(weather_data['weather']['temp'])
        temp_fig = go.Figure()
        temp_fig.add_trace(go.Scatter(
            x=dates,
            y=temp_data,
            name='Температура',
            line=dict(
                color='#1E90FF',  # Голубой цвет
                width=3,
                shape='spline'  # Сглаженная линия
            ),
            fill='tonexty',  # Добавляем заливку под графиком
            fillcolor='rgba(30, 144, 255, 0.1)',
            hovertemplate='<b>%{x|%d.%m %H:00}</b><br>' +
                         'Температура: %{y:.1f}°C<extra></extra>'
        ))

        # Добавляем зоны температур с улучшенными подписями
        annotations = []
        zones = [
            {'y0': -float('inf'), 'y1': 0, 'color': 'rgba(0, 0, 255, 0.1)', 'text': 'Холодно'},
            {'y0': 0, 'y1': 15, 'color': 'rgba(135, 206, 235, 0.1)', 'text': 'Прохладно'},
            {'y0': 15, 'y1': 25, 'color': 'rgba(0, 255, 0, 0.1)', 'text': 'Комфортно'},
            {'y0': 25, 'y1': 35, 'color': 'rgba(255, 165, 0, 0.1)', 'text': 'Тепло'},
            {'y0': 35, 'y1': float('inf'), 'color': 'rgba(255, 0, 0, 0.1)', 'text': 'Жарко'}
        ]

        for zone in zones:
            temp_fig.add_hrect(
                y0=zone['y0'],
                y1=zone['y1'],
                fillcolor=zone['color'],
                layer='below',
                line_width=0
            )
            annotations.append(dict(
                x=1.02,
                y=(zone['y0'] + zone['y1'])/2 if not isinstance(zone['y0'], str) and not isinstance(zone['y1'], str) else 0,
                text=zone['text'],
                showarrow=False,
                xref='paper',
                yref='y',
                font=dict(size=12)
            ))

        # Ветер
        wind_data = generate_hourly_data(weather_data['weather']['wind_speed'])
        wind_fig = go.Figure()
        wind_fig.add_trace(go.Scatter(
            x=dates,
            y=wind_data,
            name='Скорость ветра',
            line=dict(
                color='#20B2AA',  # Бирюзовый цвет
                width=3,
                shape='spline'
            ),
            fill='tonexty',
            fillcolor='rgba(32, 178, 170, 0.1)'
        ))
        # Добавляем индикаторы силы ветра
        wind_fig.add_hrect(
            y0=0, y1=15,
            fillcolor="green", opacity=0.1,
            layer="below", line_width=0,
            annotation_text="Слабый ветер"
        )
        wind_fig.add_hrect(
            y0=15, y1=30,
            fillcolor="yellow", opacity=0.1,
            layer="below", line_width=0,
            annotation_text="Умеренный ветер"
        )
        wind_fig.add_hrect(
            y0=30, y1=50,
            fillcolor="orange", opacity=0.1,
            layer="below", line_width=0,
            annotation_text="Сильный ветер"
        )
        wind_fig.update_layout(
            title={
                'text': f'Скорость ветра в {location}',
                'font': {'size': 24}
            },
            yaxis_title='Скорость ветра, км/ч',
            xaxis_title='Время',
            hovermode='x unified',
            template='plotly_white'
        )

        # Добавляем индикатор опасности
        wind_fig.add_shape(
            type="line",
            x0=min(dates),
            x1=max(dates),
            y0=50,  # ��ороговое значение сильного ветра
            y1=50,
            line=dict(
                color="Red",
                width=2,
                dash="dash",
            )
        )

        # Осадки
        rain_data = generate_hourly_data(weather_data['weather']['rain_prob'], variation=0.4)
        precip_fig = go.Figure()
        precip_fig.add_trace(go.Bar(
            x=dates,
            y=rain_data,
            name='Вероятность осадков',
            marker_color='#636EFA',
            hovertemplate='%{y:.1f}%<br>%{x|%d.%m %H:00}<extra></extra>'
        ))
        # Добавляем индикаторы вероятности осадков
        precip_fig.add_hrect(
            y0=0, y1=30,
            fillcolor="green", opacity=0.1,
            layer="below", line_width=0,
            annotation_text="Низкая вероятность"
        )
        precip_fig.add_hrect(
            y0=30, y1=70,
            fillcolor="yellow", opacity=0.1,
            layer="below", line_width=0,
            annotation_text="Средняя вероятность"
        )
        precip_fig.add_hrect(
            y0=70, y1=100,
            fillcolor="red", opacity=0.1,
            layer="below", line_width=0,
            annotation_text="Высокая вероятность"
        )
        precip_fig.update_layout(
            title={
                'text': f'Вероятность осадков в {location}',
                'font': {'size': 24}
            },
            yaxis_title='Вероятность осадков, %',
            xaxis_title='Время',
            hovermode='x unified',
            template='plotly_white',
            yaxis_range=[0, 100]
        )

        # Добавляем градиент вероятности
        precip_fig.update_traces(
            marker=dict(
                color=rain_data,
                colorscale=[
                    [0, '#87CEEB'],    # Светло-голубой
                    [0.3, '#4169E1'],  # Синий
                    [0.7, '#0000CD'],  # Темно-синий
                    [1, '#191970']     # Полночно-синий
                ],
                opacity=0.7,
                showscale=True,
                colorbar=dict(
                    title='Вероятность',
                    ticksuffix='%',
                    tickfont=dict(size=12),
                    titlefont=dict(size=14)
                )
            )
        )

        # Общие улучшения для всех графиков
        for fig in [temp_fig, wind_fig, precip_fig]:
            fig.update_layout(
                plot_bgcolor='rgba(240, 248, 255, 0.5)',  # Светло-голубой фон
                paper_bgcolor='white',
                font=dict(
                    family='Arial',
                    size=14,
                    color='#003366'
                ),
                title=dict(
                    font=dict(size=24, color='#003366'),
                    x=0.5,
                    xanchor='center'
                ),
                legend=dict(
                    bgcolor='rgba(255, 255, 255, 0.8)',
                    bordercolor='#1E90FF',
                    borderwidth=1
                ),
                hoverlabel=dict(
                    bgcolor='white',
                    font_size=14,
                    font_family='Arial'
                ),
                margin=dict(l=50, r=50, t=80, b=50),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(30, 144, 255, 0.1)',
                    tickformat='%H:00\n%d.%m',
                    tickangle=0
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(30, 144, 255, 0.1)',
                    zeroline=True,
                    zerolinecolor='rgba(30, 144, 255, 0.5)',
                    zerolinewidth=1
                )
            )

        temp_fig.update_traces(
            hovertemplate="<b>Температура:</b> %{y:.1f}°C<br>" +
                          "<b>Время:</b> %{x|%d.%m %H:00}<extra></extra>"
        )

        return temp_fig, wind_fig, precip_fig

    def create_empty_figures():
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title={
                'text': 'Выберите город для отображения данных',
                'font': {'size': 24, 'color': '#003366'}
            },
            template='plotly_white',
            xaxis={'visible': False},
            yaxis={'visible': False},
            annotations=[{
                'text': 'Нет данных для отображения',
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 20, 'color': '#003366'}
            }]
        )
        return empty_fig, empty_fig, empty_fig

    return dash_app