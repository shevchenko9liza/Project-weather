from flask import Flask, request, render_template, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# OpenWeatherMap API Key
API_KEY = "0ac5319e846074e1bd79ad5838fc45d9"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Проверка плохой погоды
def check_bad_weather(temp, wind_speed, rain_prob):
    if temp < 0 or temp > 35:
        return True, "Экстремальная температура."
    elif wind_speed > 50:
        return True, "Сильный ветер."
    elif rain_prob > 70:
        return True, "Высокая вероятность дождя."
    return False, "Погода благоприятная."

# Главная страница
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        start_location = request.form.get('start_location')
        end_location = request.form.get('end_location')

        if not start_location or not end_location:
            flash("Пожалуйста, введите оба города.", "error")
            return redirect(url_for('home'))

        try:
            start_weather = get_weather_data(start_location)
            end_weather = get_weather_data(end_location)
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for('home'))

        start_bad_weather, start_msg = check_bad_weather(start_weather['temp'], start_weather['wind_speed'], start_weather['rain_prob'])
        end_bad_weather, end_msg = check_bad_weather(end_weather['temp'], end_weather['wind_speed'], end_weather['rain_prob'])

        return render_template('results.html', start_location=start_location, end_location=end_location,
                               start_weather=start_weather, end_weather=end_weather,
                               start_bad_weather=start_bad_weather, end_bad_weather=end_bad_weather,
                               start_msg=start_msg, end_msg=end_msg)

    return render_template('home.html')

# Получение данных о погоде
def get_weather_data(location):
    params = {
        'q': location,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        raise Exception(f"Не удалось получить данные для {location}. Проверьте название города.")

    data = response.json()
    return {
        'temp': data['main']['temp'],
        'humidity': data['main']['humidity'],
        'wind_speed': data['wind']['speed'],
        'rain_prob': data.get('rain', {}).get('1h', 0) * 100
    }

# Страница ошибки
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
