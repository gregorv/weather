#!/usr/bin/env python
"""
   Copyright 2013 Gregor Vollmer

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import json
import urllib.request
import datetime
import argparse
import traceback
import sys

#U+263C ☼   e2 98 bc    WHITE SUN WITH RAYS
#U+2600  ☀   e2 98 80    BLACK SUN WITH RAYS
#U+2601  ☁   e2 98 81    CLOUD
#U+2602  ☂   e2 98 82    UMBRELLA
#U+2603  ☃   e2 98 83    SNOWMAN
#U+2607  ☇   e2 98 87    LIGHTNING
#U+2608  ☈   e2 98 88    THUNDERSTORM
#U+2614  ☔   e2 98 94    UMBRELLA WITH RAIN DROP
#U+2604  ☄   e2 98 84    COMET
#U+2606 ☆   e2 98 86    WHITE STAR
#U+2652 ♒   e2 99 92    AQUARIUS

icon_codes = {
    "clear": 0x2600,
    "clouds": 0x2601,
    "drizzle": 0x2602,
    "ice": 0x2603,
    "rain": 0x2614,
    "snow": 0x2603,
    "lightning": 0x2607,
    "heavy_lightning": 0x2608,
    "extreme": 0x2604,
}

severeness_colors = {
    "normal": 0xffffff,
    "light": 0xaaaaaa,
    "heavy": 0x888888,
}

verbose_weather_codes = {
    200: "thunderstorm with light rain",
    201: "thunderstorm with rain",
    202: "thunderstorm with heavy rain",
    210: "light thunderstorm",
    211: "thunderstorm",
    212: "heavy thunderstorm",
    221: "ragged thunderstorm",
    230: "thunderstorm with light drizzle",
    231: "thunderstorm with drizzle",
    232: "thunderstorm with heavy drizzle",
    300: "light intensity drizzle",
    301: "drizzle",
    302: "heavy intensity drizzle",
    310: "light intensity drizzle rain",
    311: "drizzle rain",
    312: "heavy intensity drizzle rain",
    321: "shower drizzle",
    500: "light rain",
    501: "moderate rain",
    502: "heavy intensity rain",
    503: "very heavy rain",
    504: "extreme rain",
    511: "freezing rain",
    520: "light intensity shower rain",
    521: "shower rain",
    522: "heavy intensity shower rain",
    600: "light snow",
    601: "snow",
    602: "heavy snow",
    611: "sleet",
    621: "shower snow",
    701: "mist",
    711: "smoke",
    721: "haze",
    731: "Sand/Dust Whirls",
    741: "Fog",
    800: "sky is clear",
    801: "few clouds",
    802: "scattered clouds",
    803: "broken clouds",
    804: "overcast clouds",
    900: "tornado",
    901: "tropical storm",
    902: "hurricane",
    903: "cold",
    904: "hot",
    905: "windy",
    906: "hail"
}

def getWeatherStatusIcon(weather_code_numeric):
    # http://openweathermap.org/wiki/API/Weather_Condition_Codes
    weather_code = list(map(int, str(weather_code_numeric)))
    icon = "clear"
    severeness = "normal"

    if weather_code[0] == 2:
        if weather_code[2] == 0:
            icon = "lightning"
            severeness = "light"
        elif weather_code[2] == 1:
            icon = "heavy_lightning"
            severeness = "light"
        elif weather_code[2] == 2:
            icon = "heavy_lightning"
            severeness = "heavy"
    elif weather_code[0] == 3:
        icon = "drizzle"
        if weather_code[1] == 0:
            severeness = "normal"
        elif weather_code[1] == 1:
            severeness = "light"
        elif weather_code[1] == 1:
            severeness = "heavy"
    elif weather_code[0] == 5:
        icon = "rain"
        if weather_code[0] == 0:
            severeness = "normal"
        elif weather_code[0] >= 2:
            severeness = "light"
        elif weather_code_numeric == 504:
            icon = "extreme"
            severeness = "heavy"
        elif weather_code_numeric == 511:
            icon = "ice"
            severness = "heavy"
        else:
            severeness = "heavy"
    elif weather_code[0] == 6:
        pass
    elif weather_code[0] == 7:
        pass
    elif weather_code[0] == 8:
        if weather_code[2] == 0:
            icon = "clear"
        else:
            icon = "clouds"
            if weather_code[2] == 2:
                severeness = "light"
            elif weather_code[2] > 2:
                severeness = "heavy"
    elif weather_code[0] == 9:
        icon, severeness = "extreme", "heavy"
    return icon, severeness

def temperatureToColor(temperature):
    "accepts a temperature in degree celcius"
    if temperature < -10.0:
        return 0x1E40FF
    elif temperature < 0.0:
        return 0x5367FF
    elif temperature < 5.0:
        return 0x5B9FAD
    elif temperature < 10.0:
        return 0x74DFDF
    elif temperature < 15.0:
        return 0x9FDFDB
    elif temperature < 18.0:
        return 0xE1EB81
    elif temperature < 22.0:
        return 0xD9EB4E
    elif temperature < 26.0:
        return 0xFFD940
    elif temperature < 32.0:
        return 0xFFAD31
    elif temperature < 36.0:
        return 0xFF4A09
    elif temperature > 36.0:
        return 0xFF0000

def generateAwesomeReports(data, file_suffix):
    icon, severeness = getWeatherStatusIcon(data["weather"][0]["id"])
    temperature_color = temperatureToColor(max(data["temperatures"]))

    with open("/tmp/.weather_icon_{0}".format(file_suffix), "w") as f:
        f.write("<span background='#%x' color='#%x' font-size='18000'>&#x%x;</span>" % (temperature_color, severeness_colors[severeness], icon_codes[icon]))

def generateCmdlineDailyReport(data):
    day = data["dt"].strftime("%a, %d.%b")
    weather = verbose_weather_codes[data["weather"][0]["id"]]
    icon, severeness = getWeatherStatusIcon(data["weather"][0]["id"])
    min_temp, max_temp = min(data["temperatures"]), max(data["temperatures"])
    icon = chr(icon_codes[icon])
    
    print("{0}: min/max {1: > 5.1f}°C {2: = 5.1f}°C {3} {4}".format(day, min_temp, max_temp, icon, weather))
    
def owmQuery(*args, **kwargs):
    request_url = "/".join(map(urllib.parse.quote_plus, map(str, args)))
    params = urllib.parse.urlencode(kwargs)
    data_url = "http://api.openweathermap.org/data/2.1/{0}?{1}".format(request_url, params)
    response = urllib.request.urlopen(data_url)
    data = {}
    try:
        raw_json = response.readall()
        data = json.loads(raw_json.decode("utf-8"))
    except ValueError as e:
        if raw_json:
            traceback.print_exc()
            print(raw_json)
        else:
            print("Server did not return data. Maybe simply nothing was found, maybe the server was lazy. Try again and find out.")
        sys.exit(-1)
    return data

def loadData(city, compact=True):
    if isinstance(city, int):
        data = owmQuery("forecast", "city", city, mode = ("daily_compact" if compact else ""))
    else:
        data = owmQuery("forecast", "city", q = city, mode = ("daily_compact" if compact else ""))
    for day in data["list"]:
        day["dt"] = datetime.datetime.fromtimestamp(day["dt"])
        day["temperatures"] = list(
            map(lambda x: x-273.15,
                [day["morn"], day["temp"], day["eve"], day["night"]]
            )
        )
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch weather information and prepare it for consumation')
    parser.add_argument("-c, --city", type=str, default="karlsruhe", metavar="CITY", dest="city", help="Name of the city do display forecast from")
    parser.add_argument("-i, --cityid", type=int, metavar="CITY", dest="city", help="OWM Id of the city to display forecast from")
    parser.add_argument("-a, --awesome", action="store_const", const="awesome", dest="mode", help="Write files in /tmp for consumation by awesome widgets")
    parser.add_argument("-d, --num-days", type=int, default=3, metavar="CITY", dest="num_days", help="Number of days in forecast, set to 0 for maximum available")
    parser.add_argument("-q, --q", type=str, default=None, metavar="CITY", dest="query", help="Query city names and display informations about matches. Does not display weather data.")
    args = vars(parser.parse_args())
    
    if "query" in args and args["query"]:
        data = owmQuery("find", "name", q = args["query"], type = "like")
        for city in data["list"]:
            print("{name},{sys[country]}; OWM-ID {id}, population {sys[population]}, lon".format(**city))
    else:
        data = loadData(args["city"])
        if args["mode"] is None:
            print("{city[name]}, {city[country]}; lat {city[coord][lat]}, lon {city[coord][lon]}, population {city[population]}, OWM ID {city[id]}".format(**data))
        for i, day in enumerate(data["list"]):
            if args["num_days"] != 0 and i >= args["num_days"]:
                break
            
            if args["mode"] == "awesome":
                generateAwesomeReports(day, i)
            else:
                generateCmdlineDailyReport(day)
