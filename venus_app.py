import os
import sys
import argparse
import yaml
import time
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.position_tracking.solar_system_tracker import SolarSystemTracker
from src.atmospheric_model.model import AtmosphericModel
from src.data_logging.logger import DataLogger
from src.data_logging.enhanced_visualizer import EnhancedDataVisualizer
from src.config.settings import load_config, save_config
from src.utils.location_utils import LocationManager, UnitConverter, FormattingHelper

class VenusApp:
    def __init__(self, config_path=None):
        self.config = load_config(config_path) if config_path else load_config()
        self.location_manager = LocationManager()
        self.tracker = None
        self.atmospheric_model = None
        self.data_logger = None
        self.visualizer = None
        os.makedirs('data', exist_ok=True)
        os.makedirs('plots', exist_ok=True)
        
        print(f"Venus Tracking App initialized with configuration from: {config_path or 'default'}")
    
    def setup_location(self, location_name=None, latitude=None, longitude=None, elevation=None):
        if location_name:
            location = self.location_manager.lookup_location(location_name)
            if location:
                if latitude is not None:
                    location['latitude'] = latitude
                if longitude is not None:
                    location['longitude'] = longitude
                if elevation is not None:
                    location['elevation'] = elevation
                self.config['location'] = location
                return location
            elif latitude is not None and longitude is not None:
                print(f"Could not geocode '{location_name}', using provided coordinates")
        if latitude is not None and longitude is not None:
            location = {
                'name': location_name or 'Custom Location',
                'latitude': latitude,
                'longitude': longitude,
                'elevation': elevation or 0
            }
            if not self.location_manager.validate_coordinates(latitude, longitude, elevation or 0):
                print("Warning: Invalid coordinates, using anyway")
            self.config['location'] = location
            return location
        print("Using default location from configuration")
        if 'name' not in self.config['location']:
            self.config['location']['name'] = 'Greenwich, London' 
        return self.config['location']
    
    def initialize_components(self):
        try:
            self.tracker = SolarSystemTracker(self.config, self.config['location'])
            if self.config.get('atmospheric_model', {}).get('enabled', True):
                self.atmospheric_model = AtmosphericModel(self.config)
            output_file = self.config.get('output_file', 'data/venus_data.csv')
            self.data_logger = DataLogger(output_file)
            self.visualizer = EnhancedDataVisualizer('plots')
            return True
        except Exception as e:
            print(f"Error initializing components: {e}")
            return False
    
    def run_single_calculation(self, time=None):
        if not self.tracker:
            self.initialize_components()
        if time is None:
            time = datetime.utcnow()
        print(f"Calculating for {time} UTC")
        print(f"Observer location: {self.location_manager.format_location_string(self.config['location'])}")
        
        results = self.tracker.calculate_all_positions(time)
        if self.atmospheric_model:
            atmosphere = self.atmospheric_model.calculate_parameters(time, results['celestial_bodies']['venus'])
            results['venus_atmosphere'] = atmosphere
            if self.data_logger:
                self.data_logger.log_entry(time, results['celestial_bodies']['venus'], atmosphere)
        return results
    
    def display_results(self, results):
        timestamp = results.get('timestamp')
        if timestamp:
            print(f"\nResults for: {FormattingHelper.format_timestamp(timestamp)}")
        observer = results.get('observer', {})
        print(f"\nObserver: {observer.get('location_name', 'Unknown')}")
        print(f"Coordinates: {FormattingHelper.format_coordinate(observer.get('latitude', 0), True)}, " +
                f"{FormattingHelper.format_coordinate(observer.get('longitude', 0), False)}, " +
                f"{observer.get('elevation', 0)}m")
        venus = results.get('celestial_bodies', {}).get('venus', {})
        if venus:
            print("\nVenus Position (from Earth):")
            print(f"  Altitude: {venus.get('altitude', 0):.2f}°")
            print(f"  Azimuth: {venus.get('azimuth', 0):.2f}Â°")
            print(f"  Distance: {venus.get('distance', {}).get('au', 0):.6f} AU " +
                    f"({venus.get('distance', {}).get('km', 0):.0f} km)")
            print(f"  Right Ascension: {venus.get('ra', 0):.4f} hours")
            print(f"  Declination: {venus.get('dec', 0):.4f}Â°")
            print(f"  Elongation from Sun: {venus.get('elongation', 0):.2f}Â°")
        sun = results.get('celestial_bodies', {}).get('sun', {})
        if sun:
            print("\nSun Position:")
            print(f"  Altitude: {sun.get('altitude', 0):.2f}Â°")
            print(f"  Azimuth: {sun.get('azimuth', 0):.2f}Â°")
        
        moon = results.get('celestial_bodies', {}).get('moon', {})
        if moon:
            print("\nMoon Position:")
            print(f"  Altitude: {moon.get('altitude', 0):.2f}Â°")
            print(f"  Azimuth: {moon.get('azimuth', 0):.2f}Â°")
            print(f"  Distance: {moon.get('distance', {}).get('au', 0):.6f} AU " +
                    f"({moon.get('distance', {}).get('km', 0):.0f} km)")
        venus_perspective = results.get('venus_perspective', {})
        if venus_perspective:
            earth_from_venus = venus_perspective.get('earth_from_venus', {})
            if earth_from_venus:
                print("\nEarth Position (from Venus):")
                print(f"  Altitude: {earth_from_venus.get('altitude', 0):.2f}Â°")
                print(f"  Azimuth: {earth_from_venus.get('azimuth', 0):.2f}Â°")
                print(f"  Distance: {earth_from_venus.get('distance', {}).get('au', 0):.6f} AU " +
                        f"({earth_from_venus.get('distance', {}).get('km', 0):.0f} km)")
        atmosphere = results.get('venus_atmosphere', {})
        if atmosphere:
            print("\nVenus Atmospheric Data:")
            surface_temp = atmosphere.get('surface_temperature', {})
            if surface_temp:
                print(f"  Surface Temperature: {surface_temp.get('k', 0):.1f} K " +
                        f"({surface_temp.get('c', 0):.1f}Â°C)")
            ground_temp = atmosphere.get('ground_temperature', {})
            if ground_temp:
                print(f"  Ground Temperature: {ground_temp.get('k', 0):.1f} K " +
                        f"({ground_temp.get('c', 0):.1f}Â°C)")
            surface_pressure = atmosphere.get('surface_pressure', {})
            if surface_pressure:
                print(f"  Surface Pressure: {surface_pressure.get('bar', 0):.2f} bar " +
                        f"({surface_pressure.get('atm', 0):.2f} atm, " +
                        f"{surface_pressure.get('kpa', 0):.1f} kPa)")
            wind_speed = atmosphere.get('surface_wind_speed', {})
            if wind_speed:
                print(f"  Surface Wind Speed: {wind_speed.get('m_per_s', 0):.1f} m/s " +
                        f"({wind_speed.get('km_per_h', 0):.1f} km/h)")
            light = atmosphere.get('surface_light_intensity', {})
            if light:
                print(f"  Surface Light Intensity: {light.get('lux', 0):.0f} lux")
            composition = atmosphere.get('composition', {})
            if composition:
                print("\n  Atmospheric Composition:")
                for compound, percentage in sorted(composition.items(), key=lambda x: x[1], reverse=True):
                    print(f"    {compound}: {percentage:.4f}%")
            notes = atmosphere.get('notes')
            if notes:
                print(f"\n  Notes: {notes}")
        orbital = results.get('orbital_parameters', {}).get('venus', {})
        if orbital:
            print("\nVenus Orbital Parameters:")
            print(f"  Distance from Earth: {orbital.get('distance_from_earth', {}).get('au', 0):.6f} AU " +
                    f"({orbital.get('distance_from_earth', {}).get('km', 0):.0f} km)")
            print(f"  Phase Angle: {orbital.get('phase_angle', 0):.2f}Â°")
            print(f"  Illuminated Fraction: {orbital.get('illuminated_fraction', 0):.4f}")
            print(f"  Orbital Longitude: {orbital.get('orbital_longitude', 0):.2f}Â°")
            print(f"  Relative to Earth: {orbital.get('relative_to_earth', 0):.2f}Â°")
    
    def run_tracking_session(self, duration_minutes=60, interval_seconds=None):
        if not self.tracker:
            if not self.initialize_components():
                return False
        if interval_seconds is None:
            interval_seconds = self.config.get('tracking_interval', 60)
        self.config['tracking_interval'] = interval_seconds
        
        start_time = datetime.utcnow()
        print(f"\nStarting tracking session at {start_time} UTC")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Update interval: {interval_seconds} seconds")
        print(f"Observer: {self.location_manager.format_location_string(self.config['location'])}")
        try:
            self.tracker.track_real_time(
                duration_seconds=duration_minutes * 60, 
                callback=self._tracking_callback
            )
            return True
        except KeyboardInterrupt:
            print("\nTracking session interrupted by user")
            return False
        except Exception as e:
            print(f"\nError during tracking session: {e}")
            return False
    
    def _tracking_callback(self, time, data):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Venus Tracking - {FormattingHelper.format_timestamp(time)}")
        print(f"Observer: {self.location_manager.format_location_string(self.config['location'])}")
        print("-" * 60)
        venus = data.get('celestial_bodies', {}).get('venus', {})
        if venus:
            print(f"Venus: Alt={venus.get('altitude', 0):.1f}Â°, Az={venus.get('azimuth', 0):.1f}Â°, " +
                    f"Dist={venus.get('distance', {}).get('au', 0):.4f} AU")
        sun = data.get('celestial_bodies', {}).get('sun', {})
        if sun:
            print(f"Sun: Alt={sun.get('altitude', 0):.1f}Â°, Az={sun.get('azimuth', 0):.1f}Â°")
        moon = data.get('celestial_bodies', {}).get('moon', {})
        if moon:
            print(f"Moon: Alt={moon.get('altitude', 0):.1f}Â°, Az={moon.get('azimuth', 0):.1f}Â°")
        venus_perspective = data.get('venus_perspective', {})
        if venus_perspective and 'earth_from_venus' in venus_perspective:
            earth = venus_perspective['earth_from_venus']
            print(f"Earth (from Venus): Alt={earth.get('altitude', 0):.1f}Â°, Az={earth.get('azimuth', 0):.1f}Â°")
        if 'venus_atmosphere' in data:
            atmosphere = data['venus_atmosphere']
            surface_temp = atmosphere.get('surface_temperature', {})
            surface_pressure = atmosphere.get('surface_pressure', {})
            
            if surface_temp and surface_pressure:
                print(f"\nVenus Surface: Temp={surface_temp.get('k', 0):.1f} K ({surface_temp.get('c', 0):.1f}Â°C), " +
                        f"Pressure={surface_pressure.get('bar', 0):.1f} bar ({surface_pressure.get('atm', 0):.1f} atm)")
            wind = atmosphere.get('surface_wind_speed', {})
            if wind:
                print(f"Wind: {wind.get('m_per_s', 0):.1f} m/s ({wind.get('km_per_h', 0):.1f} km/h)")
            notes = atmosphere.get('notes')
            if notes:
                print(f"\nNotes: {notes}")
        if self.data_logger and self.atmospheric_model:
            atmosphere = self.atmospheric_model.calculate_parameters(time, venus)
            self.data_logger.log_entry(time, venus, atmosphere)
    
    def create_visualizations(self, data_file=None):
        if not self.visualizer:
            self.visualizer = EnhancedDataVisualizer('plots')
        if data_file is None:
            data_file = self.config.get('output_file', 'data/venus_data.csv')
        print(f"\nCreating visualizations from {data_file}")
        success = self.visualizer.create_plots(data_file, self.config)
        if success:
            dashboard = self.visualizer.create_dashboard(data_file)
            print(f"Dashboard created: {dashboard}")
            return True
        else:
            print("Failed to create visualizations")
            return False
    
    def export_data(self, format_type='csv', output_path=None):
        if not self.data_logger:
            print("Data logger not initialized")
            return None
        print(f"\nExporting data to {format_type.upper()} format")
        path = self.data_logger.export_data(format_type, output_path)
        if path:
            print(f"Data exported to {path}")
            return path
        else:
            print("Failed to export data")
            return None
    
    def save_configuration(self, config_path=None):
        if config_path is None:
            config_path = "config/custom.yml"
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        try:
            with open(config_path, 'w') as file:
                yaml.dump(self.config, file, default_flow_style=False)
            
            print(f"Configuration saved to {config_path}")
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Venus Application - Astronomical Data Visualization and Analysis")
    parser.add_argument("-c", "--config", help="Path to configuration file")
    parser.add_argument("-l", "--location", help="Observer location name")
    parser.add_argument("--lat", type=float, help="Observer latitude in degrees")
    parser.add_argument("--lon", type=float, help="Observer longitude in degrees")
    parser.add_argument("--elev", type=float, help="Observer elevation in meters")
    parser.add_argument("-m", "--mode", choices=["single", "track", "visualize"], default="single",
                        help="Operation mode: single calculation, tracking, or visualization")
    parser.add_argument("-t", "--time", help="Specific time for calculation (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("-d", "--duration", type=int, default=60, help="Duration to track in minutes")
    parser.add_argument("-i", "--interval", type=int, help="Update interval in seconds")
    parser.add_argument("-o", "--output", help="Output file for data")
    parser.add_argument("-f", "--format", choices=["csv", "json"], help="Export format")

    args = parser.parse_args()
    app = VenusApp(args.config)
    app.setup_location(args.location, args.lat, args.lon, args.elev)
    
    if args.output:
        app.config['output_file'] = args.output
    if args.mode == "single":
        if args.time:
            try:
                time = datetime.fromisoformat(args.time.replace(" ", "T"))
            except ValueError:
                print(f"Invalid time format: {args.time}. Using current time.")
                time = None
        else:
            time = None
        
        results = app.run_single_calculation(time)
        app.display_results(results)
        if args.format:
            app.export_data(args.format)
    
    elif args.mode == "track":
        app.run_tracking_session(args.duration, args.interval)
        app.create_visualizations()
        if args.format:
            app.export_data(args.format)
    elif args.mode == "visualize":
        app.create_visualizations(args.output)
    app.save_configuration()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
