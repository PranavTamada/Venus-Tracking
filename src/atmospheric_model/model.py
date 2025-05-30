import numpy as np
from datetime import datetime
class AtmosphericModel:
    def __init__(self, config):
        self.config = config
        self.composition = {
            'CO2': 96.5,
            'N2': 3.5,
            'SO2': 0.015,
            'Ar': 0.007,
            'CO': 0.0017,
            'H2O': 0.002,
            'He': 0.0012,
            'Ne': 0.0007
        }
        
        self.parameters = {
            'surface_pressure': 92,  # bar
            'surface_temperature': 737,  # K (464°C)
            'ground_temperature': 737,  # K (464°C)
            'mean_molecular_weight': 43.45,  # g/mol
            'scale_height': 15.9,  # km
            'cloud_top_altitude': 65,  # km
            'troposphere_height': 65,  # km
            'total_atmosphere_height': 250,  # km
            'surface_wind_speed': 0.5,  # m/s
            'surface_light_intensity': 10000,  # lux (very rough estimate)
        }
        self.conversions = {
            'bar_to_atm': 0.986923,  # 1 bar = 0.986923 atm
            'bar_to_kpa': 100,       # 1 bar = 100 kPa
            'k_to_c': lambda k: k - 273.15,  # Kelvin to Celsius
            'm_per_s_to_km_per_h': 3.6,  # 1 m/s = 3.6 km/h
        }
    
    def kelvin_to_celsius(self, kelvin):
        """Convert temperature from Kelvin to Celsius."""
        return kelvin - 273.15
    
    def bar_to_atm(self, bar):
        """Convert pressure from bar to atmospheres."""
        return bar * self.conversions['bar_to_atm']
    
    def bar_to_kpa(self, bar):
        """Convert pressure from bar to kilopascals."""
        return bar * self.conversions['bar_to_kpa']
    
    def m_per_s_to_km_per_h(self, m_per_s):
        """Convert speed from meters per second to kilometers per hour."""
        return m_per_s * self.conversions['m_per_s_to_km_per_h']
    
    def calculate_parameters(self, time, position):
        distance = position['distance']['au']
        elongation = position['elongation']
        
        # Calculate illuminated fraction (phase)
        phase = (1 + np.cos(np.radians(elongation))) / 2
        
        # Cloud top temperatures vary between day and night sides
        cloud_top_temp_day = 230  # K (day side)
        cloud_top_temp_night = 150  # K (night side)
        cloud_top_temperature = phase * cloud_top_temp_day + (1 - phase) * cloud_top_temp_night
        
        # Surface values remain nearly constant
        surface_temperature = self.parameters['surface_temperature']
        ground_temperature = self.parameters['ground_temperature']
        
        # Surface pressure with minor variations
        pressure_variation = np.sin(np.radians(elongation)) * 0.5  # Small variation
        surface_pressure = self.parameters['surface_pressure'] + pressure_variation
        
        # Wind speed varies with solar heating
        base_wind_speed = self.parameters['surface_wind_speed']
        wind_speed_variation = phase * 2  # Higher winds on day side
        surface_wind_speed = base_wind_speed + wind_speed_variation
        
        # Light intensity varies with phase
        base_light = self.parameters['surface_light_intensity']
        light_intensity = base_light * (phase ** 2)  # Quadratic falloff with phase
        
        # Top three compounds by percentage
        main_compounds = sorted(self.composition.items(), key=lambda x: x[1], reverse=True)[:3]
        compounds = [compound[0] for compound in main_compounds]
        
        return {
            # Cloud top parameters
            'cloud_top_temperature': {
                'k': cloud_top_temperature,
                'c': self.kelvin_to_celsius(cloud_top_temperature)
            },
            'cloud_top_pressure': {
                'bar': 0.5,
                'atm': self.bar_to_atm(0.5),
                'kpa': self.bar_to_kpa(0.5)
            },
            
            # Surface parameters
            'surface_temperature': {
                'k': surface_temperature,
                'c': self.kelvin_to_celsius(surface_temperature)
            },
            'ground_temperature': {
                'k': ground_temperature,
                'c': self.kelvin_to_celsius(ground_temperature)
            },
            'surface_pressure': {
                'bar': surface_pressure,
                'atm': self.bar_to_atm(surface_pressure),
                'kpa': self.bar_to_kpa(surface_pressure)
            },
            'surface_wind_speed': {
                'm_per_s': surface_wind_speed,
                'km_per_h': self.m_per_s_to_km_per_h(surface_wind_speed)
            },
            'surface_light_intensity': {
                'lux': light_intensity
            },
            
            # Other parameters
            'composition': self.composition,
            'main_compounds': compounds,
            'phase': phase,
            'notes': self._generate_notes(cloud_top_temperature, phase, elongation)
        }
    
    def _generate_notes(self, temperature, phase, elongation):
        notes = []
        
        if elongation < 10:
            notes.append("Venus near superior conjunction (behind the Sun)")
        elif elongation > 160:
            notes.append("Venus near inferior conjunction (between Earth and Sun)")
        
        if phase > 0.8:
            notes.append("Full Venus phase - mostly day side visible")
        elif phase < 0.2:
            notes.append("Crescent phase - mostly night side visible")
        
        if temperature > 220:
            notes.append("Upper cloud temperature higher than average")
        elif temperature < 160:
            notes.append("Upper cloud temperature lower than average")
        
        notes.append(f"Surface temperature: {self.kelvin_to_celsius(self.parameters['surface_temperature']):.1f}°C")
        notes.append(f"Surface pressure: {self.bar_to_atm(self.parameters['surface_pressure']):.1f} atm")
        
        return "; ".join(notes) if notes else "Standard conditions"
