# API ключи
OPENWEATHER_API_KEY = "0ac5319e846074e1bd79ad5838fc45d9"

# URLs
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"
GEOCODING_URL = "http://api.openweathermap.org/geo/1.0/direct"

# Параметры погоды
EXTREME_TEMP_MIN = 0
EXTREME_TEMP_MAX = 35
STRONG_WIND = 50
HIGH_RAIN_PROB = 70
HIGH_HUMIDITY = 85 

# Настройки для прогноза погоды
WEATHER_THRESHOLDS = {
    'temp_min': 0,
    'temp_max': 35,
    'wind_speed_max': 50,
    'rain_probability': 70
}

# Настройки для визуализации
PLOT_CONFIG = {
    'template': 'plotly_white',
    'height': 400
}