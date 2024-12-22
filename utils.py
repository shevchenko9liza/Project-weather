from datetime import datetime, timedelta
import requests
from config import *

def get_weather_forecast(location, days=1):
    """Получение прогноза погоды на несколько дней"""
    params = {
        'q': location,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',
        'cnt': days * 8  # 8 измерений в день
    }
    
    try:
        response = requests.get(FORECAST_BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        raise Exception(f"Ошибка при получении прогноза для {location}")

def check_weather_conditions(weather_data):
    """Проверка погодных условий"""
    messages = []
    is_bad = False
    
    temp = weather_data['temp']
    wind_speed = weather_data['wind_speed']
    humidity = weather_data['humidity']
    rain_prob = weather_data.get('rain_prob', 0)
    
    if temp < EXTREME_TEMP_MIN or temp > EXTREME_TEMP_MAX:
        messages.append("Экстремальная температур��")
        is_bad = True
    
    if wind_speed > STRONG_WIND:
        messages.append("Сильный ветер")
        is_bad = True
    
    if rain_prob > HIGH_RAIN_PROB:
        messages.append("Высокая вероятность осадков")
        is_bad = True
        
    if humidity > HIGH_HUMIDITY:
        messages.append("Высокая влажность")
        is_bad = True
    
    return is_bad, ". ".join(messages) if messages else "Погода благоприятная"

def validate_locations(locations):
    """Проверка списка локаций на дубликаты"""
    seen = set()
    duplicates = []
    
    for loc in locations:
        loc_lower = loc.lower()
        if loc_lower in seen:
            duplicates.append(loc)
        seen.add(loc_lower)
    
    if duplicates:
        raise ValueError(f"Обнаружены дублирующиеся города: {', '.join(duplicates)}") 