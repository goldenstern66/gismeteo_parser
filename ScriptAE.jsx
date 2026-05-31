(function() {
    var scriptPath = new File($.fileName).path;
    var configFile = new File(scriptPath + "/config.json");
    
    if (!configFile.exists) {
        alert("Ошибка: Файл config.json не найден!\nПуть: " + scriptPath);
        return;
    }
    
    configFile.open("r");
    var configText = configFile.read();
    configFile.close();
    var config = JSON.parse(configText);
    
    var dataFile = new File(scriptPath + "/" + config.json_file);
    if (!dataFile.exists) {
        alert("Ошибка: Файл " + config.json_file + " не найден!\nЗапустите сначала parser.py");
        return;
    }
    
    dataFile.open("r");
    var dataText = dataFile.read();
    dataFile.close();
    var weatherData = JSON.parse(dataText);
    
    function getValueByPath(obj, path) {
        var parts = path.split('.');
        var current = obj;
        for (var i = 0; i < parts.length; i++) {
            var part = parts[i];
            var arrayMatch = part.match(/(\w+)\[(\d+)\]/);
            if (arrayMatch) {
                current = current[arrayMatch[1]][parseInt(arrayMatch[2])];
            } else {
                current = current[part];
            }
            if (current === undefined) return undefined;
        }
        return current;
    }
    
    function formatTemperature(temp) {
        if (temp === null || temp === undefined) return "?";
        var num = parseInt(temp);
        if (num > 0) return "+" + num;
        if (num < 0) return num.toString();
        return "0";
    }
    
    var comp = app.project.activeItem;
    if (!comp || !(comp instanceof CompItem)) {
        alert("Ошибка: Откройте композицию и выделите её в панели Project!");
        return;
    }
    
    var updatedCount = 0;
    var notFoundLayers = [];
    
    for (var layerName in config.layers) {
        if (config.layers.hasOwnProperty(layerName)) {
            var path = config.layers[layerName];
            var value = getValueByPath(weatherData, path);
            
            if (value === undefined) {
                notFoundLayers.push(layerName + " (путь: " + path + ")");
                continue;
            }
            
            var layer = null;
            for (var i = 1; i <= comp.layers.length; i++) {
                if (comp.layers[i].name === layerName) {
                    layer = comp.layers[i];
                    break;
                }
            }
            
            if (!layer) {
                notFoundLayers.push(layerName);
                continue;
            }
            
            if (layer instanceof TextLayer) {
                var displayValue = value.toString();
                
                // Форматируем температуру воздуха (ночь/день)
                if (layerName.indexOf("night") !== -1 || layerName.indexOf("day") !== -1) {
                    displayValue = formatTemperature(value);
                } 
                // Форматируем температуру воды
                else if (layerName.indexOf("water") !== -1 && value !== null) {
                    displayValue = value + "°C";
                }
                // Форматируем ветер
                else if (layerName.indexOf("wind") !== -1 && value !== null) {
                    displayValue = value + " м/с";
                }
                // Остальное (название города, описание погоды) оставляем как есть
                
                layer.text.sourceText.setValue(displayValue);
                updatedCount++;
            }
        }
    }
    
    var message = "Обновление завершено!\n";
    message += "Обновлено слоёв: " + updatedCount + "\n";
    message += "Данные от: " + weatherData.last_update;
    
    if (notFoundLayers.length > 0) {
        message += "\n\n⚠️ Не найдены слои:\n" + notFoundLayers.join("\n");
    }
    
    alert(message);
})();