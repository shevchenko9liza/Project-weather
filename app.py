from flask import (
    Flask, 
    request, 
    render_template, 
    jsonify, 
    session, 
    redirect, 
    url_for,
    flash
)
import requests
from dash_app import create_dash_app
from utils import get_weather_forecast, check_weather_conditions, validate_locations

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Инициализация Dash
dash_app = create_dash_app(app)

# OpenWeatherMap API Key
API_KEY = "0ac5319e846074e1bd79ad5838fc45d9"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Проверка плохой погоды
def check_bad_weather(temp, wind_speed, rain_prob, humidity):
    messages = []
    is_bad = False
    
    if temp < 0 or temp > 35:
        messages.append("Экстремальная температура")
        is_bad = True
    if wind_speed > 50:
        messages.append("Сильный ветер")
        is_bad = True
    if rain_prob > 70:
        messages.append("Высокая вероятность дождя")
        is_bad = True
    if humidity > 85:
        messages.append("Высокая влажность")
        is_bad = True
        
    return is_bad, ". ".join(messages) if messages else "Погода благоприятная."

# Главная страница
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        locations = request.form.getlist('locations[]')
        forecast_days = int(request.form.get('forecast-days', 1))

        if not locations:
            flash("Пожалуйста, введите хотя бы один город.", "error")
            return redirect(url_for('home'))

        try:
            validate_locations(locations)
            weather_data = []
            
            for location in locations:
                try:
                    coordinates = get_coordinates(location)
                    current_weather = get_weather_data(location)
                    forecast = get_weather_forecast(location, forecast_days)
                    
                    weather_info = {
                        'location': location,
                        'coordinates': coordinates,
                        'weather': current_weather,
                        'forecast': forecast
                    }
                    
                    is_bad, message = check_bad_weather(
                        current_weather['temp'],
                        current_weather['wind_speed'],
                        current_weather['rain_prob'],
                        current_weather['humidity']
                    )
                    
                    weather_info['weather']['is_bad'] = is_bad
                    weather_info['weather']['message'] = message
                    weather_data.append(weather_info)
                    
                except Exception as e:
                    flash(f"Ошибка при получении данных для {location}: {str(e)}", "error")
                    return redirect(url_for('home'))

            if weather_data:
                # Сохраняем данные в сессии для использования в Dash
                session['weather_data'] = weather_data
                session['forecast_days'] = forecast_days

            return render_template('results.html',
                                 locations=weather_data,
                                 forecast_days=forecast_days)

        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for('home'))

    return render_template('home.html')

# Получение данных о погоде
def get_weather_data(location):
    params = {
        'q': location,
        'appid': API_KEY,
        'units': 'metric'
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        return {
            'temp': round(data['main']['temp'], 1),
            'humidity': data['main']['humidity'],
            'wind_speed': round(data['wind']['speed'] * 3.6, 1),  # конвертация в км/ч
            'rain_prob': data.get('rain', {}).get('1h', 0) * 100,
            'description': data['weather'][0]['description']
        }
    except requests.exceptions.RequestException:
        raise Exception(f"Ошибка при получении данных о погоде для {location}")
    except KeyError:
        raise Exception(f"Город {location} не найден")
    except requests.exceptions.ConnectionError:
        raise Exception(f"Не удалось подключиться к серверу погоды. Проверьте подключение к интернету.")
    except requests.exceptions.Timeout:
        raise Exception(f"Превышено время ожидания ответа от сервера. Попробуйте позже.")

# Страница ошибки
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# Добавим новую функцию для получения координат
def get_coordinates(location):
    """
    Получает координаты для заданного местоположения через OpenWeatherMap Geocoding API
    """
    geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        'q': location,
        'limit': 1,
        'appid': API_KEY
    }
    
    try:
        response = requests.get(geocoding_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if not data:
            raise ValueError(f"Местоположение не найдено: {location}")
            
        return {
            'lat': data[0]['lat'],
            'lon': data[0]['lon']
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при получении координат для {location}: {str(e)}")

# Маршрут для обработки точек маршрута
@app.route('/route', methods=['GET', 'POST'])
def route():
    if request.method == 'POST':
        city = request.form.get('city')
        
        if 'cities' not in session:
            session['cities'] = []
        
        if city and city not in session['cities']:
            try:
                coordinates = get_coordinates(city)
                weather_data = get_weather_data(city)
                
                session['cities'].append(city)
                session.modified = True
                
                return jsonify({
                    'success': True,
                    'city': city,
                    'coordinates': coordinates,
                    'weather': weather_data
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 400
        
        return jsonify({
            'success': False,
            'error': 'Город уже добавлен или не указан'
        }), 400
    
    return redirect(url_for('home'))

# Добавить валидацию формы
@app.route('/', methods=['POST'])
def validate_form():
    if not request.form.get('locations[]'):
        flash('Пожалуйста, введите хотя бы один город', 'error')
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
