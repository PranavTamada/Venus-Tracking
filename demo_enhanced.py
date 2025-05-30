import os
import sys
import time
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_file_encoding(file_path):
    """Check if a file has encoding issues and return True if it does."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        if b'\x00' in content:
            print(f"Warning: Null bytes detected in {file_path}")
            return True
        try:
            content.decode('utf-8')
        except UnicodeDecodeError:
            print(f"Warning: Invalid UTF-8 characters detected in {file_path}")
            return True
    except Exception as e:
        print(f"Error checking file {file_path}: {e}")
    return False

def safe_import():
    try:
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venus_app.py')
        if check_file_encoding(app_path):
            print("Please run the fix_null_bytes.py script to fix encoding issues")
            print("python fix_null_bytes.py")
            sys.exit(1)
        src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
        if os.path.exists(src_path):
            for root, dirs, files in os.walk(src_path):
                for file in files:
                    if file == "__init__.py":
                        file_path = os.path.join(root, file)
                        if check_file_encoding(file_path):
                            print(f"Found encoding issues in {file_path}")
                            print("Please run the fix_null_bytes.py script to fix encoding issues")
                            print("python fix_null_bytes.py")
                            sys.exit(1)
        from venus_app import VenusApp
        return VenusApp
    except ValueError as e:
        if "null bytes" in str(e):
            print("\nERROR: Null bytes detected in imported module.")
            print("Please run the fix_null_bytes.py script to fix encoding issues:")
            print("python fix_null_bytes.py")
            sys.exit(1)
        else:
            raise
    except SyntaxError as e:
        if "unicode error" in str(e):
            print("\nERROR: Unicode decoding error in imported module.")
            print("Please run the fix_null_bytes.py script to fix encoding issues:")
            print("python fix_null_bytes.py")
            sys.exit(1)
        else:
            raise
    except ImportError as e:
        print(f"\nERROR: Could not import VenusApp: {e}")
        print("This could be due to encoding issues or missing modules.")
        print("Please run the fix_null_bytes.py script to fix encoding issues:")
        print("python fix_null_bytes.py")
        sys.exit(1)
VenusApp = safe_import()

def run_demo():
    """Run a demonstration of the Venus Tracking Application."""
    print("Venus Tracking Application - Interactive Demo")
    print("=" * 60)
    print("\nThis demo will showcase the main features of the application.")
    app = VenusApp()
    print("\n1. Application initialized with default configuration")
    print("\n2. Location Management Demo")
    print("-" * 40)
    default_location = app.config['location'].copy()
    default_location.setdefault('name', 'Greenwich, London')
    print(f"Default location: {default_location['name']} "
            f"({default_location['latitude']}, {default_location['longitude']}, {default_location['elevation']}m)")
    new_location = app.setup_location("New York City")
    print(f"Changed location to: {new_location['name']} "
            f"({new_location['latitude']}, {new_location['longitude']}, {new_location['elevation']}m)")
    app.setup_location(default_location.get('name', 'Greenwich, London'), 
                        default_location['latitude'], 
                        default_location['longitude'], 
                        default_location['elevation'])
    print("\n3. Single Calculation Demo")
    print("-" * 40)
    results = app.run_single_calculation()
    venus = results['celestial_bodies']['venus']
    print(f"\nVenus position summary:")
    print(f"  Altitude: {venus['altitude']:.2f}°")
    print(f"  Azimuth: {venus['azimuth']:.2f}°")
    print(f"  Distance: {venus['distance']['au']:.6f} AU ({venus['distance']['km']:.0f} km)")
    if 'venus_atmosphere' in results:
        atm = results['venus_atmosphere']
        temp = atm.get('surface_temperature', {})
        pressure = atm.get('surface_pressure', {})
        
        print("\nVenus environmental data summary:")
        if temp:
            print(f"  Surface Temperature: {temp.get('k', 0):.1f} K ({temp.get('c', 0):.1f}°C)")
        if pressure:
            print(f"  Surface Pressure: {pressure.get('bar', 0):.1f} bar ({pressure.get('atm', 0):.1f} atm)")
    print("\n4. Data Visualization Demo")
    print("-" * 40)
    print("Creating visualizations... (this may take a moment)")
    if not app.initialize_components():
        print("Failed to initialize components")
        return
    print("Generating sample data...")
    current_time = datetime.utcnow()
    for i in range(10):
        time_point = current_time + timedelta(minutes=i*10)
        data = app.tracker.calculate_all_positions(time_point)
        
        if app.atmospheric_model:
            atmosphere = app.atmospheric_model.calculate_parameters(
                time_point, data['celestial_bodies']['venus'])
            app.data_logger.log_entry(time_point, data['celestial_bodies']['venus'], atmosphere)
    app.create_visualizations()
    csv_path = app.export_data('csv')
    json_path = app.export_data('json')
    
    print("\nDemo data files created:")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")
    
    print("\nVisualization files created in 'plots' directory:")
    print("  Static plots: plots/static/")
    print("  Interactive plots: plots/interactive/")
    print("  Dashboard: plots/venus_dashboard.html")

    print("\n5. Real-time Tracking")
    print("-" * 40)
    print("To run real-time tracking, use the following command:")
    print("  python venus_app.py --mode track --duration 60 --interval 10")
    print("This will track Venus and other celestial bodies for 60 minutes with updates every 10 seconds.")
    
    print("\nDemo Completed!")
    print("=" * 60)
    print("Explore the generated files and try running the application with different parameters.")
    print("For more information, see the README.md file.")


if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()
