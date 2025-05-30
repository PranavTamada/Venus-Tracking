import os
import pandas as pd
import json
from datetime import datetime
class DataLogger:
    def __init__(self, output_file="venus_data.csv"):
        self.output_file = output_file
        self.data = []
        self.json_output_file = output_file.replace('.csv', '.json')
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            try:
                self.existing_data = pd.read_csv(output_file)
                print(f"Loaded existing data from {output_file} with {len(self.existing_data)} records")
            except Exception as e:
                print(f"Error loading existing data: {e}")
                self.existing_data = None
        else:
            self.existing_data = None
    
    def log_entry(self, time, position, atmosphere=None):
        entry = {
            'timestamp': time.isoformat(),
            'location_name': position.get('observer_location_name', 'Unknown Location'),
            'observer_latitude': position.get('observer_latitude'),
            'observer_longitude': position.get('observer_longitude'),
            'altitude': position['altitude'],
            'azimuth': position['azimuth'],
            'distance_au': position['distance']['au'] if isinstance(position['distance'], dict) else position['distance'],
            'distance_km': position['distance']['km'] if isinstance(position['distance'], dict) else position['distance'] * 149597870.7,
            'ra': position.get('ra'),
            'dec': position.get('dec'),
            'elongation': position.get('elongation')
        }
        if atmosphere:
            if 'cloud_top_temperature' in atmosphere:
                entry.update({
                    'cloud_temp_k': atmosphere['cloud_top_temperature']['k'],
                    'cloud_temp_c': atmosphere['cloud_top_temperature']['c'],
                    'cloud_pressure_bar': atmosphere['cloud_top_pressure']['bar'],
                    'cloud_pressure_atm': atmosphere['cloud_top_pressure']['atm'],
                    'cloud_pressure_kpa': atmosphere['cloud_top_pressure']['kpa'],
                })
            if 'surface_temperature' in atmosphere:
                entry.update({
                    'surface_temp_k': atmosphere['surface_temperature']['k'],
                    'surface_temp_c': atmosphere['surface_temperature']['c'],
                    'ground_temp_k': atmosphere['ground_temperature']['k'],
                    'ground_temp_c': atmosphere['ground_temperature']['c'],
                    'surface_pressure_bar': atmosphere['surface_pressure']['bar'],
                    'surface_pressure_atm': atmosphere['surface_pressure']['atm'],
                    'surface_pressure_kpa': atmosphere['surface_pressure']['kpa'],
                    'wind_speed_m_s': atmosphere['surface_wind_speed']['m_per_s'],
                    'wind_speed_km_h': atmosphere['surface_wind_speed']['km_per_h'],
                })
            if 'surface_light_intensity' in atmosphere:
                entry.update({
                    'light_intensity_lux': atmosphere['surface_light_intensity']['lux']
                })
            if 'main_compounds' in atmosphere:
                entry.update({
                    'main_compounds': ','.join(atmosphere['main_compounds']),
                })
            if 'phase' in atmosphere:
                entry.update({
                    'phase': atmosphere.get('phase'),
                })
            if 'notes' in atmosphere:
                entry.update({
                    'notes': atmosphere.get('notes', '')
                })
        
        self.data.append(entry)
        raw_entry = {
            'timestamp': time.isoformat(),
            'position': position,
            'atmosphere': atmosphere
        }
        self._write_to_file()
        self._write_to_json(raw_entry)
    
    def _write_to_file(self):
        df = pd.DataFrame(self.data)
        
        if self.existing_data is not None:
            df = pd.concat([self.existing_data, df], ignore_index=True)
        df.to_csv(self.output_file, index=False)
        print(f"Data written to {self.output_file}")
    
    def _write_to_json(self, entry):
        mode = 'w' if not os.path.exists(self.json_output_file) else 'r+'
        
        try:
            if mode == 'r+':
                with open(self.json_output_file, 'r') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {'entries': []}
                
                data['entries'].append(entry)
                
                with open(self.json_output_file, 'w') as f:
                    json.dump(data, f, indent=2)
            else:
                with open(self.json_output_file, 'w') as f:
                    json.dump({'entries': [entry]}, f, indent=2)
            
            print(f"Data written to {self.json_output_file}")
        except Exception as e:
            print(f"Error writing to JSON file: {e}")
    
    def export_data(self, format_type='csv', output_path=None):
        if not self.data:
            print("No data to export")
            return None
        
        df = pd.DataFrame(self.data)
        
        if self.existing_data is not None:
            df = pd.concat([self.existing_data, df], ignore_index=True)
        
        if format_type.lower() == 'csv':
            path = output_path or self.output_file
            df.to_csv(path, index=False)
            return path
        elif format_type.lower() == 'json':
            path = output_path or self.json_output_file
            df.to_json(path, orient='records', indent=2)
            return path
        else:
            print(f"Unsupported export format: {format_type}")
            return None
        
    def get_summary_stats(self):
        if not self.data:
            return {"status": "No data available"}
            
        df = pd.DataFrame(self.data)
        
        stats = {
            "observations": len(df),
            "time_range": {
                "start": df['timestamp'].min(),
                "end": df['timestamp'].max()
            },
            "position": {
                "altitude": {
                    "mean": df['altitude'].mean(),
                    "min": df['altitude'].min(),
                    "max": df['altitude'].max()
                },
                "azimuth": {
                    "mean": df['azimuth'].mean(),
                    "min": df['azimuth'].min(), 
                    "max": df['azimuth'].max()
                },
                "distance_au": {
                    "mean": df['distance_au'].mean(),
                    "min": df['distance_au'].min(),
                    "max": df['distance_au'].max()
                }
            }
        }
        if 'surface_temp_k' in df.columns:
            stats["atmosphere"] = {
                "surface_temperature_k": {
                    "mean": df['surface_temp_k'].mean(),
                    "min": df['surface_temp_k'].min(),
                    "max": df['surface_temp_k'].max()
                },
                "surface_pressure_atm": {
                    "mean": df['surface_pressure_atm'].mean(),
                    "min": df['surface_pressure_atm'].min(),
                    "max": df['surface_pressure_atm'].max()
                }
            }
        
        return stats
