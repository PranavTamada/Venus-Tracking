import os
import pandas as pd
from datetime import datetime


class DataLogger:
    def __init__(self, output_file="venus_data.csv"):
        
        self.output_file = output_file
        self.data = []
        
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            try:
                # Load existing data
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
            'altitude': position['altitude'],
            'azimuth': position['azimuth'],
            'distance': position['distance'],
            'ra': position.get('ra'),
            'dec': position.get('dec'),
            'elongation': position.get('elongation')
        }
        
        if atmosphere:
            entry.update({
                'temperature': atmosphere['temperature'],
                'pressure': atmosphere['pressure'],
                'main_compounds': ','.join(atmosphere['compounds']),
                'phase': atmosphere.get('phase'),
                'notes': atmosphere.get('notes', '')
            })
        
        
        self.data.append(entry)
        
        self._write_to_file()
    
    def _write_to_file(self):
        """Write collected data to the output file."""
        df = pd.DataFrame(self.data)
        
        if self.existing_data is not None:
            df = pd.concat([self.existing_data, df], ignore_index=True)
        
        
        df.to_csv(self.output_file, index=False)
        
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
                "distance": {
                    "mean": df['distance'].mean(),
                    "min": df['distance'].min(),
                    "max": df['distance'].max()
                }
            }
        }
        
        if 'temperature' in df.columns:
            stats["atmosphere"] = {
                "temperature": {
                    "mean": df['temperature'].mean(),
                    "min": df['temperature'].min(),
                    "max": df['temperature'].max()
                },
                "pressure": {
                    "mean": df['pressure'].mean(),
                    "min": df['pressure'].min(),
                    "max": df['pressure'].max()
                }
            }
        
        return stats
