#!/usr/bin/env python3
"""
Yr.no Weather - Tomorrow's Forecast
Shows weather forecast for tomorrow using MET's API.
"""

import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

def get_tomorrow_forecast(lat, lon):
    """Get tomorrow's weather forecast."""
    
    params = {"lat": lat, "lon": lon}
    query_string = urllib.parse.urlencode(params)
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?{query_string}"
    
    headers = {
        "User-Agent": "OpenClawYrWeather/1.0 github.com/openclaw/openclaw"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data
    except Exception as e:
        print(f"Error fetching weather: {e}", file=sys.stderr)
        sys.exit(1)

def get_emoji(symbol_code):
    """Convert MET symbol code to emoji."""
    emojis = {
        "clearsky": "☀️",
        "fair": "🌤️",
        "partlycloudy": "⛅",
        "cloudy": "☁️",
        "rain": "🌧️",
        "rainshowers": "🌦️",
        "sleet": "🌨️",
        "snow": "❄️",
        "snowshowers": "🌨️",
        "fog": "🌫️",
        "lightrain": "🌦️",
        "heavyrain": "⛈️",
        "lightsnow": "🌨️",
        "heavysnow": "❄️",
    }
    base_symbol = symbol_code.split("_")[0]
    return emojis.get(base_symbol, "🌡️")

def format_tomorrow(data, lat, lon):
    """Format tomorrow's weather forecast."""
    
    properties = data.get("properties", {})
    timeseries = properties.get("timeseries", [])
    
    if not timeseries:
        print("No weather data available")
        return
    
    # Calculate tomorrow's date
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    tomorrow_date = tomorrow.strftime("%Y-%m-%d")
    tomorrow_display = tomorrow.strftime("%A, %d %B")
    
    # Filter for tomorrow's forecasts
    tomorrow_entries = []
    for entry in timeseries:
        time_str = entry.get("time", "")
        if tomorrow_date in time_str:
            tomorrow_entries.append(entry)
    
    if not tomorrow_entries:
        print(f"No forecast data available for tomorrow ({tomorrow_display})")
        return
    
    print(f"🌤️ Tomorrow's Weather - {tomorrow_display}")
    print(f"📍 Location: {lat:.4f}, {lon:.4f}")
    print("-" * 50)
    
    # Group by time of day
    times_of_day = {
        "morning": [],    # 06:00 - 12:00
        "afternoon": [],  # 12:00 - 18:00
        "evening": [],    # 18:00 - 00:00
        "night": []       # 00:00 - 06:00
    }
    
    for entry in tomorrow_entries:
        time_str = entry.get("time", "")
        try:
            time_obj = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            hour = time_obj.hour
        except:
            continue
        
        data_entry = entry.get("data", {})
        instant = data_entry.get("instant", {}).get("details", {})
        
        # Get symbol for the period
        next_1h = data_entry.get("next_1_hours", {})
        summary_1h = next_1h.get("summary", {})
        symbol_1h = summary_1h.get("symbol_code", "cloudy")
        
        temp = instant.get("air_temperature")
        wind = instant.get("wind_speed")
        humidity = instant.get("relative_humidity")
        
        entry_data = {
            "hour": hour,
            "time": time_obj.strftime("%H:%M"),
            "temp": temp,
            "wind": wind,
            "humidity": humidity,
            "symbol": symbol_1h
        }
        
        if 6 <= hour < 12:
            times_of_day["morning"].append(entry_data)
        elif 12 <= hour < 18:
            times_of_day["afternoon"].append(entry_data)
        elif 18 <= hour < 24:
            times_of_day["evening"].append(entry_data)
        else:
            times_of_day["night"].append(entry_data)
    
    # Display each time period
    for period, entries in times_of_day.items():
        if entries:
            # Get average/midpoint values
            mid = len(entries) // 2
            mid_entry = entries[mid]
            
            emoji = get_emoji(mid_entry["symbol"])
            temp = mid_entry["temp"]
            wind = mid_entry["wind"]
            symbol_display = mid_entry["symbol"].replace("_", " ").title().split()[0]
            
            print(f"\n🕐 {period.capitalize()}:")
            print(f"   {emoji} {symbol_display}")
            print(f"   Temperature: {temp}°C")
            print(f"   Wind: {wind} m/s")
    
    # Summary
    all_temps = [e.get("temp") for e in tomorrow_entries if e.get("temp") is not None]
    if all_temps:
        min_temp = min(all_temps)
        max_temp = max(all_temps)
        print(f"\n📊 Daily Range: {min_temp}°C - {max_temp}°C")

def main():
    # Default: Cape Town coordinates
    default_lat = -33.9288
    default_lon = 18.4174
    
    if len(sys.argv) >= 3:
        try:
            lat = float(sys.argv[1])
            lon = float(sys.argv[2])
        except ValueError:
            print("Usage: tomorrow.py [latitude] [longitude]", file=sys.stderr)
            print(f"Example: tomorrow.py {default_lat} {default_lon}", file=sys.stderr)
            sys.exit(1)
    else:
        lat = default_lat
        lon = default_lon
        print(f"Using Cape Town coordinates ({lat}, {lon})\n")
    
    data = get_tomorrow_forecast(lat, lon)
    format_tomorrow(data, lat, lon)

if __name__ == "__main__":
    main()
