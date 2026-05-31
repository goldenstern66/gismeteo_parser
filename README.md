# gismeteo_parser
Weather parser for After Effects (Gismeteo + Open-Meteo)
Python 3.13 selenium webdriver-manager requests
The parser collects the weather forecast for tomorrow.
You can add/remove a city by adding the name and link to the city on Gismeteo, the name and coordinates for coastal cities from Open_Meteo.
The data is taken from Gismeteo (night and day temperature, wind speed, clouds and precipitation) and Open-Meteo (water temperature for coastal cities).
The result is saved in the parsed_data.json, which is then used in After Effects to automatically update the graphics.
The config.json is needed for communication between JSON data and layers in After Effects.
"kld_name" is the name of the text layer in After Effects. "cities[0].name" is the path to the data in parsed_data.json (first city, name field)
The ScriptAE.jsx reads this config, finds the layers in the composition and substitutes the necessary values in them. If there is no layer with that name, the script simply skips it without error.
