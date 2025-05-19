import os
import sys
from datetime import datetime, timedelta

current_dir = os.path.dirname(os.path.abspath(__file__))

os.makedirs(os.path.join(current_dir, "data"), exist_ok=True)
os.makedirs(os.path.join(current_dir, "plots"), exist_ok=True)

class MockVenusTracker:
    def __init__(self, config, location):
        self.config = config
        self.location = location
        print(f"Venus tracker initialized with location: {location}")
    
    def calculate_position(self, time):
        return {
            'altitude': 45.2,
            'azimuth': 225.7,
            'distance': 0.72,
            'elongation': 36.5,
            'ra': 12.5,
            'dec': -5.2
        }

class MockAtmosphericModel:
    def __init__(self, config):
        self.config = config
        print("Atmospheric model initialized")
    
    def calculate_parameters(self, time, position):
        return {
            'temperature': 230.5,
            'pressure': 0.92,
            'compounds': ['CO2', 'N2', 'SO2'],
            'notes': 'Standard conditions'
        }

class MockDataLogger:
    def __init__(self, output_file):
        self.output_file = output_file
        print(f"Data logger initialized with output file: {output_file}")
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write("timestamp,altitude,azimuth,distance,ra,dec,elongation,temperature,pressure,main_compounds,notes\n")
    
    def log_entry(self, time, position, atmosphere):
        print(f"Logging entry for time: {time}")
        compounds = ','.join(atmosphere['compounds']) if 'compounds' in atmosphere else ''
        
        with open(self.output_file, 'a') as f:
            f.write(f"{time.isoformat()},{position['altitude']},{position['azimuth']},{position['distance']},{position.get('ra', '')},{position.get('dec', '')},{position.get('elongation', '')},{atmosphere.get('temperature', '')},{atmosphere.get('pressure', '')},{compounds},{atmosphere.get('notes', '')}\n")

class MockDataVisualizer:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        print(f"Data visualizer initialized with output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    
    def create_plots(self, data_file):
        print(f"Creating plots from data file: {data_file}")
        with open(os.path.join(self.output_dir, 'altitude_azimuth.png'), 'w') as f:
            f.write("Placeholder for altitude/azimuth plot")
        
        with open(os.path.join(self.output_dir, 'atmospheric_data.png'), 'w') as f:
            f.write("Placeholder for atmospheric data plot")
    
    def create_polar_plot(self, df):
        print("Creating polar plot")
        with open(os.path.join(self.output_dir, 'venus_polar_position.png'), 'w') as f:
            f.write("Placeholder for polar position plot")

def mock_load_config(path):
    print(f"Loading configuration from: {path}")
    return {
        'location': {
            'latitude': 51.4778,
            'longitude': -0.0015,
            'elevation': 0
        },
        'tracking_interval': 60,
        'real_time': False,
        'atmospheric_model': {
            'enabled': True
        }
    }

def run_demo():
    print("Venus Tracking System - Demo")
    print("-" * 40)
    
    config = mock_load_config("config/default.yml")
    
    location = config.get('location', {'latitude': 51.4778, 'longitude': -0.0015, 'elevation': 0})
    
    print("\nInitializing Venus tracker...")
    tracker = MockVenusTracker(config, location)
    
    print("Initializing atmospheric model...")
    atmospheric_model = MockAtmosphericModel(config)
    
    print("Initializing data logger...")
    data_logger = MockDataLogger("data/demo_venus_data.csv")
    
    print("\nCalculating current position of Venus...")
    now = datetime.now()
    position = tracker.calculate_position(now)
    
    atmosphere = atmospheric_model.calculate_parameters(now, position)
    
    data_logger.log_entry(now, position, atmosphere)
    
    print("\nCurrent Venus Position:")
    print(f"Altitude: {position['altitude']:.2f}°")
    print(f"Azimuth: {position['azimuth']:.2f}°")
    print(f"Distance: {position['distance']:.2f} AU")
    print("\nAtmospheric Conditions at Cloud Tops:")
    print(f"Temperature: {atmosphere['temperature']:.2f} K")
    print(f"Pressure: {atmosphere['pressure']:.2f} bar")
    print(f"Main compounds: {', '.join(atmosphere['compounds'])}")
    print(f"Notes: {atmosphere['notes']}")
    
    print("\nTracking Venus over the next 24 hours (one reading per hour)...")
    for hour in range(1, 25):
        time_point = now + timedelta(hours=hour)
        position = tracker.calculate_position(time_point)
        atmosphere = atmospheric_model.calculate_parameters(time_point, position)
        data_logger.log_entry(time_point, position, atmosphere)
        
        if hour % 6 == 0:
            print(f"Hour {hour}: Alt={position['altitude']:.2f}°, Az={position['azimuth']:.2f}°")
    
    print("\nTracking complete. Creating visualizations...")
    
    visualizer = MockDataVisualizer("plots")
    visualizer.create_plots("data/demo_venus_data.csv")
    
    class MockDataFrame:
        def __init__(self):
            pass
    
    df = MockDataFrame()
    visualizer.create_polar_plot(df)
    
    print("\nDemo completed. Data saved to 'data/demo_venus_data.csv'.")
    print("Visualizations saved to the 'plots' directory.")
    print("\nTry running the main script with your own parameters:")
    print("python main.py --location \"YOUR_LAT,YOUR_LON,YOUR_ELEVATION\" --duration 120")


if __name__ == "__main__":
    run_demo()
