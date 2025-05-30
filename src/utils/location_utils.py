import geopy
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import numpy as np

# Conversion constants
KM_PER_AU = 149597870.7  # kilometers per astronomical unit
M_PER_KM = 1000.0        # meters per kilometer
ATM_PER_BAR = 0.986923   # atmospheres per bar
KPA_PER_BAR = 100.0      # kilopascals per bar
KM_PER_H_PER_M_PER_S = 3.6  # km/h per m/s


class LocationManager:
    def __init__(self):
        self.geocoder = Nominatim(user_agent="venus_tracking_app")
    
    def lookup_location(self, location_name):
        try:
            location = self.geocoder.geocode(location_name)
            
            if location:
                return {
                    'name': location.address,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'elevation': 0  # Default elevation, can be updated later
                }
            else:
                print(f"Location '{location_name}' not found")
                return None
                
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Geocoding error: {e}")
            return None
    
    def validate_coordinates(self, latitude, longitude, elevation=0):
        if latitude < -90 or latitude > 90:
            print(f"Invalid latitude: {latitude}. Must be between -90 and 90 degrees.")
            return False
        if longitude < -180 or longitude > 180:
            print(f"Invalid longitude: {longitude}. Must be between -180 and 180 degrees.")
            return False
        if elevation < -500 or elevation > 10000:
            print(f"Unusual elevation: {elevation}. Please verify this value.")
        
        return True
    
    def format_location_string(self, location):
        name = location.get('name', 'Unknown Location')
        lat = location.get('latitude', 0)
        lon = location.get('longitude', 0)
        elev = location.get('elevation', 0)
        
        lat_dir = 'N' if lat >= 0 else 'S'
        lon_dir = 'E' if lon >= 0 else 'W'
        
        return f"{name} ({abs(lat):.4f}°{lat_dir}, {abs(lon):.4f}°{lon_dir}, {elev}m)"


class UnitConverter:
    @staticmethod
    def kelvin_to_celsius(kelvin):
        return kelvin - 273.15
    
    @staticmethod
    def celsius_to_kelvin(celsius):
        return celsius + 273.15
    
    @staticmethod
    def au_to_km(au):
        return au * KM_PER_AU
    
    @staticmethod
    def km_to_au(km):
        return km / KM_PER_AU
    
    @staticmethod
    def bar_to_atm(bar):
        return bar * ATM_PER_BAR
    
    @staticmethod
    def bar_to_kpa(bar):
        return bar * KPA_PER_BAR
    
    @staticmethod
    def m_per_s_to_km_per_h(m_per_s):
        return m_per_s * KM_PER_H_PER_M_PER_S
    
    @staticmethod
    def format_with_units(value, unit, precision=2):
        return f"{value:.{precision}f} {unit}"


class FormattingHelper:
    @staticmethod
    def format_timestamp(timestamp, include_timezone=True):
        if isinstance(timestamp, str):
            from datetime import datetime
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except ValueError:
                return timestamp
        
        if include_timezone:
            return timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")
        else:
            return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def format_coordinate(value, is_latitude=True, precision=4):
        if is_latitude:
            direction = 'N' if value >= 0 else 'S'
        else:
            direction = 'E' if value >= 0 else 'W'
        
        return f"{abs(value):.{precision}f}°{direction}"
    
    @staticmethod
    def format_object_data(data, indent=0):
        indent_str = ' ' * indent
        result = []
        
        for key, value in data.items():
            if isinstance(value, dict):
                result.append(f"{indent_str}{key.replace('_', ' ').title()}:")
                result.append(FormattingHelper.format_object_data(value, indent + 2))
            else:
                result.append(f"{indent_str}{key.replace('_', ' ').title()}: {value}")
        
        return '\n'.join(result)
