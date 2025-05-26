import streamlit as st
from streamlit_bokeh import streamlit_bokeh
from bokeh.plotting import figure
from bokeh.palettes import Dark2
import requests
from datetime import datetime, timezone, timedelta

# get stored openweather api key
api_key = st.secrets["weather_api_key"]


# WEATHER AS TEXT
def get_location(city, api_key=api_key):
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={
        city}&limit=3&appid={api_key}'
    r = requests.get(url)
    lat = r.json()[0]['lat']
    lon = r.json()[0]['lon']
    country = r.json()[0]['country']
    return lat, lon, country


def weather_in(city, api_key=api_key):
    lat, lon, country = get_location(city=city)
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={
        lat}&lon={lon}&appid={api_key}'
    r = requests.get(url)
    res = r.json()
    # human perceived temperature in °C
    tmp = round(res['main']['feels_like'] - 273, 1)
    wind_speed = round(res['wind']['speed'] * 3.6, 1)  # in m/s
    sky = res['weather'][0]['description']
    output = (f"If you look up in {city} ({country}), you'll see {sky}. "
              f"The temperature feels like {str(tmp)} °C, "
              f"and the wind blows with {wind_speed} km/h.")
    return output


# INTERACTIVE BOKEH PLOT
@st.cache_data
def temperature_in_last_days(city, api_key=api_key):
    lat, lon, country = get_location(city=city)
    # define start and end date
    # now = datetime.now(timezone.utc)
    # start = (now - timedelta(days=7)).timestamp() # seven days ago
    # end = now.timestamp() # current utc time in unix time
    # HISTORICAL AND 16-DAY FORECAST ARE BY PURCHASE ONLY!
    url = (f"https://api.openweathermap.org/data/2.5/"
           f"forecast?lat={lat}&lon={lon}&appid={api_key}")
    r = requests.get(url)
    res = r.json()
    # extract time and temperature
    time = []
    temp = []
    for i in range(res['cnt']):
        unix_time = res['list'][i]['dt']
        time.append(datetime.fromtimestamp(unix_time))
        temp.append(res['list'][i]['main']['temp'] - 273.15)
    return time, temp


def bokeh_plot(cities, colors):
    p = figure(title='Temperature Forecast',
               y_axis_label='temperature [°C]',
               x_axis_type="datetime")
    for city, color in zip(cities, colors):
        time, temp = temperature_in_last_days(city=city)
        if city == city_sel:
            line_width = 5
            size = 10
            alpha = 1
        else:
            line_width = 2
            size = 5
            alpha = 0.8
        p.line(time, temp, color=color, legend_label=city,
               line_width=line_width, alpha=alpha)
        p.circle(time, temp, color=color, size=size, alpha=alpha)
    # render in streamlit
    streamlit_bokeh(p, use_container_width=True, theme="streamlit")


# MAIN
st.title("🎈 Small WDigital eather Station!")
cities = ['Berlin', 'Heidelberg', 'Madrid', 'Salamanca']

# selection box showing printed temperature
city_sel = st.selectbox(label='Choose a city.', options=cities)
st.write(weather_in(city_sel))

st.write("And now let's compare the forecast for all cities:")
# Dark 2 hcl color scheme
# colors = ['#C87A8A', '#AC8C4E', '#6B9D59', '#00A396']
bokeh_plot(cities, colors=Dark2[len(cities)])
