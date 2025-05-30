import os
import yaml


def load_config(config_path="config/default.yml"):

    if not os.path.exists(config_path):
        print(f"Warning: Config file {config_path} not found. Using default configuration.")
        return get_default_config()
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        default_config = get_default_config()
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
        
        return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return get_default_config()


def get_default_config():
    return {
        'location': {
            'name': 'Royal Observatory Greenwich',
            'latitude': 51.4778,
            'longitude': -0.0015,
            'elevation': 0,
        },
        
        'tracking_interval': 60,  
        'real_time': False,
        
        'output_file': 'data/venus_data.csv',
        'create_plots': True,
        
        'atmospheric_model': {
            'enabled': True,
            'complexity': 'basic',  
            'include_cloud_layers': True,
        },
        
        'visualization': {
            'plot_altitude_azimuth': True,
            'plot_temperature': True,
            'plot_3d_position': False,
            'interactive_plots': True,
            'solar_system_map': True,
            'export_formats': ['png', 'csv', 'json'],
        },

        'celestial_bodies': ['sun', 'moon', 'mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune'],
    }


def save_config(config, config_path="config/custom.yml"):
    
    os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
    
    try:
        with open(config_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
        print(f"Configuration saved to {config_path}")
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False
