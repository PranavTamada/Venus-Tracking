import os
import sys
import yaml
import shutil
from datetime import datetime

DIRECTORIES = [
    'config',
    'data',
    'plots',
    'plots/static',
    'plots/interactive',
    'src/utils',
]

DEFAULT_CONFIG = {
    'location': {
        'name': 'Royal Observatory Greenwich',
        'latitude': 51.4778,
        'longitude': -0.0015,
        'elevation': 0,
    },
    'tracking_interval': 60,
    'real_time': True,
    'output_file': 'data/venus_data.csv',
    'create_plots': True,
    'calculate_all_planets': True,
    'atmospheric_model': {
        'enabled': True,
        'complexity': 'full',
        'include_cloud_layers': True,
    },
    'visualization': {
        'plot_altitude_azimuth': True,
        'plot_temperature': True,
        'plot_3d_position': True,
        'interactive_plots': True,
        'solar_system_map': True,
        'export_formats': ['png', 'csv', 'json'],
    },
    'celestial_bodies': [
        'sun', 'moon', 'mercury', 'venus', 'earth', 
        'mars', 'jupiter', 'saturn', 'uranus', 'neptune'
    ],
}

def create_directories():
    print("Creating directories...")
    
    for directory in DIRECTORIES:
        os.makedirs(directory, exist_ok=True)
        print(f"  Created: {directory}/")
    
    print("All directories created successfully.")


def create_config_file():
    config_path = 'config/default.yml'
    if not os.path.exists(config_path) or os.path.getsize(config_path) == 0:
        print(f"Creating default configuration file: {config_path}")
        
        with open(config_path, 'w') as file:
            yaml.dump(DEFAULT_CONFIG, file, default_flow_style=False)
        
        print("Default configuration file created.")
    else:
        print(f"Configuration file already exists: {config_path}")


def create_init_files():
    """Create __init__.py files in all src directories."""
    print("Creating __init__.py files...")
    for root, dirs, files in os.walk('src'):
        for dir_name in dirs:
            init_path = os.path.join(root, dir_name, '__init__.py')
            os.makedirs(os.path.dirname(init_path), exist_ok=True)
            if not os.path.exists(init_path):
                with open(init_path, 'w') as file:
                    file.write(f"# {init_path} - Created by setup.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                print(f"  Created: {init_path}")


def main():
    print("Venus Tracking Application - Setup Utility")
    print("=" * 50)
    create_directories()
    create_config_file()
    create_init_files()
    
    print("\nSetup completed successfully!")
    print("You can now run the application with: python venus_app.py")
    print("Or try the demo with: python demo_enhanced.py")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)
