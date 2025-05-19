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
            'mean_molecular_weight': 43.45,  # g/mol
            'scale_height': 15.9,  # km
            'cloud_top_altitude': 65,  # km
            'troposphere_height': 65,  # km
            'total_atmosphere_height': 250,  # km
        }
    
    def calculate_parameters(self, time, position):
        distance = position['distance']
        
        elongation = position['elongation']
        
        phase = (1 + np.cos(np.radians(elongation))) / 2
        
        cloud_top_temp_day = 230  # K (day side)
        cloud_top_temp_night = 150  # K (night side)
        temperature = phase * cloud_top_temp_day + (1 - phase) * cloud_top_temp_night
        
        pressure = 0.5
        
        main_compounds = sorted(self.composition.items(), key=lambda x: x[1], reverse=True)[:3]
        compounds = [compound[0] for compound in main_compounds]
        
        return {
            'temperature': temperature,  # K
            'pressure': pressure,  # bar
            'compounds': compounds,
            'phase': phase,
            'cloud_top_altitude': self.parameters['cloud_top_altitude'],  # km
            'notes': self._generate_notes(temperature, phase, elongation)
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
        
        return "; ".join(notes) if notes else "Standard conditions"
