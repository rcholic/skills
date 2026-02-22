#!/usr/bin/env python3
"""
Yr.no Weather API Client
Fetches weather data from the Norwegian Meteorological Institute (MET)
Documentation: https://developer.yr.no/doc/GettingStarted/
"""

import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

def get_location_forecast(lat, lon, altitude=None):
    """
    Get weather forecast for a specific location using MET's Locationforecast API.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        altitude: Altitude in meters (optional)
    
    Returns:
        Dictionary with weather data
    """
    # Build URL with parameters
    params = {"lat": lat, "lon": lon}
    if altitude:
        params["altitude"] = altitude
    
    query_string = urllib.parse.urlencode(params)
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?{query_string}"
    
    # Set headers with User-Agent (required by MET API)
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

def format_weather(data, hours=24):
    """Format weather data into human-readable output."""
    
    properties = data.get("properties", {})
    timeseries = properties.get("timeseries", [])
    meta = properties.get("meta", {})
    
    if not timeseries:
        print("No weather data available")
        return
    
    # Get location info from first entry
    first_entry = timeseries[0]
    place = meta.get("srid", "").split(":")[-1] if meta.get("srid") else "Unknown location"
    
    print(f"🌤️ Weather Forecast")
    print(f"Coordinates: {meta.get('updated_at', 'N/A')}")
    print("-" * 50)
    
    # Show current weather
    current = timeseries[0]
    current_data = current.get("data", {})
    current_instant = current_data.get("instant", {}).get("details", {})
    
    temp = current_instant.get("air_temperature", "N/A")
    wind = current_instant.get("wind_speed", "N/A")
    humidity = current_instant.get("relative_humidity", "N/A")
    
    print(f"\n📍 Current Conditions:")
    print(f"   Temperature: {temp}°C")
    print(f"   Wind: {wind} m/s")
    print(f"   Humidity: {humidity}%")
    
    # Show next_period symbol code if available
    next_1_hours = current_data.get("next_1_hours", {})
    summary = next_1_hours.get("summary", {})
    symbol = summary.get("symbol_code", "cloudy")
    
    print(f"   Conditions: {get_emoji(symbol)} {symbol.replace('_', ' ').title()}")
    
    # Show upcoming forecasts (every 6 hours)
    print(f"\n📅 Next {hours} Hours:")
    
    shown = 0
    for entry in timeseries[1:]:
        if shown >= 4:  # Show 4 periods
            break
            
        time_str = entry.get("time", "")
        try:
            time_obj = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            time_display = time_obj.strftime("%H:%M")
        except:
            time_display = time_str[:16].replace("T", " ")
        
        data = entry.get("data", {})
        instant = data.get("instant", {}).get("details", {})
        
        next_1h = data.get("next_1_hours", {})
        summary_1h = next_1h.get("summary", {})
        symbol_1h = summary_1h.get("symbol_code", "cloudy")
        
        temp_val = instant.get("air_temperature", "N/A")
        wind_val = instant.get("wind_speed", "N/A")
        
        print(f"   {time_display}: {get_emoji(symbol_1h)} {temp_val}°C, {wind_val} m/s wind")
        shown += 1

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
    
    # Handle variant codes like "rain_day" or "partlycloudy_night"
    base_symbol = symbol_code.split("_")[0]
    return emojis.get(base_symbol, "🌡️")

def main():
    # Default: Cape Town coordinates
    default_lat = -33.9288
    default_lon = 18.4174
    
    # Check for command line arguments
    if len(sys.argv) >= 3:
        try:
            lat = float(sys.argv[1])
            lon = float(sys.argv[2])
        except ValueError:
            print("Usage: weather.py [latitude] [longitude]", file=sys.stderr)
            print(f"Example: weather.py {default_lat} {default_lon}", file=sys.stderr)
            sys.exit(1)
    else:
        lat = default_lat
        lon = default_lon
        print(f"No coordinates provided, using Cape Town ({lat}, {lon})")
    
    altitude = None
    if len(sys.argv) >= 4:
        try:
            altitude = int(sys.argv[3])
        except ValueError:
            pass
    
    data = get_location_forecast(lat, lon, altitude)
    format_weather(data)

if __name__ == "__main__":
    main()
