import time
import json
import re
import requests
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# города
city = [
    ("Калининград", "https://www.gismeteo.ru/weather-kaliningrad-4225/tomorrow/"),
    ("Светлогорск", "https://www.gismeteo.ru/weather-svetlogorsk-11615/tomorrow/"),
    ("Зеленоградск", "https://www.gismeteo.ru/weather-zelenogradsk-11291/tomorrow/"),
    ("Пионерский", "https://www.gismeteo.ru/weather-pionersky-4199/tomorrow/"),
    ("Балтийск", "https://www.gismeteo.ru/weather-baltysk-4224/tomorrow/"),
    ("Черняховск", "https://www.gismeteo.ru/weather-chernyakhovsk-4228/tomorrow/"),
    ("Советск", "https://www.gismeteo.ru/weather-sovetsk-4200/tomorrow/"),
    ("Гусев", "https://www.gismeteo.ru/weather-gusev-12531/tomorrow/"),
    ("Гвардейск", "https://www.gismeteo.ru/weather-gvardeysk-4226/tomorrow/"),
    ("Янтарный", "https://www.gismeteo.ru/weather-yantarny-14702/tomorrow/"),
    ("Правдинск", "https://www.gismeteo.ru/weather-pravdinsk-11618/tomorrow/"),
    ("Багратионовск", "https://www.gismeteo.ru/weather-bagrationovsk-145881/tomorrow/"),
    ("Нестеров", "https://www.gismeteo.ru/weather-nesterov-146418/tomorrow/"),
    ("Краснознаменск", "https://www.gismeteo.ru/weather-krasnoznamensk-146303/tomorrow/"),
    ("Полесск", "https://www.gismeteo.ru/weather-polessk-11617/tomorrow/"),
]

# к-ты прибрежных городов ля Open-Meteo
water_coords = {
    "Светлогорск": {"lat": 54.9444, "lon": 20.1593},
    "Зеленоградск": {"lat": 54.9583, "lon": 20.4732},
    "Пионерский": {"lat": 54.9444, "lon": 20.1593},
    "Балтийск": {"lat": 54.6518, "lon": 19.9083},
    "Янтарный": {"lat": 54.8708, "lon": 19.9669},
}

output_json = "parsed_data.json"

id_condition = {
    "d_c0": "Ясно", "n_c0": "Ясно",
    "d_c1": "Малооблачно", "n_c1": "Малооблачно",   
    "d_c2": "Облачно", "n_c2": "Облачно",
    "d_c3": "Пасмурно", "n_c3": "Пасмурно",
    "d_c4": "Небольшой дождь", "n_c4": "Небольшой дождь",
    "d_c5": "Дождь", "n_c5": "Дождь",
    "d_c6": "Сильный дождь", "n_c6": "Сильный дождь",
    "d_c7": "Гроза", "n_c7": "Гроза",
    "d_c8": "Небольшой снег", "n_c8": "Небольшой снег",
    "d_c9": "Снег", "n_c9": "Снег",
    "d_c10": "Сильный снег", "n_c10": "Сильный снег",
    "d_c11": "Туман", "n_c11": "Туман",
}

id2_condition = {
    "r0": "", "s0": "",
    "r1": "небольшой дождь", "s1": "небольшой снег",
    "r2": "дождь", "s2": "снег",
    "r3": "сильный дождь", "s3": "сильный снег",
    "t0": "гроза", "t1": "гроза с дождём",
}

# настройки браузера для Gismeteo
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

weather_data = {
    "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    "forecast_date": None,
    "cities": []
}

for idx, (city_name, url) in enumerate(city, 1):
    max_retries = 3
    success = False
    
    for attempt in range(max_retries):
        try:
            driver.get(url)
            time.sleep(random.uniform(3, 5))
            active_tab = driver.find_element(By.CSS_SELECTOR, "div.weathertab.is-active")
            success = True
            break
        except Exception:
            if attempt == max_retries - 1:
                raise
            time.sleep(random.uniform(2, 4))
    
    if not success:
        city_data = {
            "name": city_name,
            "night_temp": None,
            "day_temp": None,
            "condition": None,
            "wind_speed": None,
            "water_temp": None,
            "unit": "celsius"
        }
        weather_data["cities"].append(city_data)
        continue
    
    try:
        temp_elements = active_tab.find_elements(By.CSS_SELECTOR, "temperature-value[value]")
        temps = []
        for elem in temp_elements:
            value = elem.get_attribute("value")
            if value and value.lstrip('-').isdigit():
                temps.append(int(value))
        
        night_temp = temps[0] if len(temps) >= 2 else None
        day_temp = temps[1] if len(temps) >= 2 else None
        
        weather_parts = []
        try:
            top_icon = active_tab.find_element(By.CSS_SELECTOR, ".top-layer use")
            top_href = top_icon.get_attribute("href")
            if top_href:
                top_match = re.search(r'#([a-z]_c\d+)', top_href)
                if top_match:
                    icon_id = top_match.group(1)
                    condition = id_condition.get(icon_id)
                    if condition:
                        weather_parts.append(condition)
        except:
            pass
        
        try:
            bottom_icon = active_tab.find_element(By.CSS_SELECTOR, ".bottom-layer use")
            bottom_href = bottom_icon.get_attribute("href")
            if bottom_href:
                bottom_match = re.search(r'#([a-z]\d+)', bottom_href)
                if bottom_match:
                    precip_code = bottom_match.group(1)
                    precip_text = id2_condition.get(precip_code)
                    if precip_text:
                        weather_parts.append(precip_text)
        except:
            pass
        
        condition = ", ".join(weather_parts) if weather_parts else "неизвестно"
        
        max_wind_speed = 0
        try:
            wind_rows = driver.find_elements(By.CSS_SELECTOR, ".widget-row-wind .row-item")
            for row in wind_rows:
                try:
                    speed_elem = row.find_element(By.CSS_SELECTOR, "speed-value")
                    speed_value = int(speed_elem.get_attribute("value"))
                    if speed_value > max_wind_speed:
                        max_wind_speed = speed_value
                except:
                    pass
                try:
                    gust_elem = row.find_element(By.CSS_SELECTOR, ".wind-gust speed-value")
                    gust_value = int(gust_elem.get_attribute("value"))
                    if gust_value > max_wind_speed:
                        max_wind_speed = gust_value
                except:
                    pass
        except:
            pass
        
        water_temp = None
        if city_name in water_coords:
            try:
                lat = water_coords[city_name]["lat"]
                lon = water_coords[city_name]["lon"]
                api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m&timezone=Europe/Moscow&forecast_days=1"
                
                response = requests.get(api_url, timeout=10)
                data = response.json()
                
                temps_list = data['hourly']['temperature_2m'][:24]
                if temps_list:
                    water_temp = int(round(sum(temps_list) / len(temps_list)))
            except Exception:
                pass
        
        city_data = {
            "name": city_name,
            "night_temp": night_temp,
            "day_temp": day_temp,
            "condition": condition,
            "wind_speed": max_wind_speed if max_wind_speed > 0 else None,
            "water_temp": water_temp,
            "unit": "celsius"
        }
        
    except Exception:
        city_data = {
            "name": city_name,
            "night_temp": None,
            "day_temp": None,
            "condition": None,
            "wind_speed": None,
            "water_temp": None,
            "unit": "celsius"
        }
    
    weather_data["cities"].append(city_data)
    time.sleep(random.uniform(2, 4))

driver.quit()

with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(weather_data, f, ensure_ascii=False, indent=4)