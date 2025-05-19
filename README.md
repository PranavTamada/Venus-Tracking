<<<<<<< HEAD
# Venus Atmosphere & Position Tracking System

A Python-based system for tracking the position of Venus and modeling its atmosphere.

## Overview

This project provides tools to:

- Calculate the position of Venus in the sky from any location on Earth
- Model Venus's atmospheric conditions
- Log position and atmospheric data over time
- Generate visualizations of tracking data

## Installation

1. Clone this repository:

   ```git clone https://github.com/PranavTamada/Venus-Tracking.git
   cd venus-tracking
   ```

2. Create and activate a conda environment(optional but recommended):

   ```bash

   ```conda create -n venus python=3.9
   conda activate venus
   ```

3. Install required packages:

   ```pip install -r requirements.txt
   ```

## Usage

### Basic Position Tracking

To track Venus's current position from your location:

```bash
python main.py --location "51.4778,-0.0015,0"
```

### Track Over Time

To track Venus over a period of time:

```bash
python main.py --location "51.4778,-0.0015,0" --duration 60
```

This will track Venus's position for 60 minutes, taking measurements at the interval specified in the configuration.

### Calculate Position for a Specific Time

To calculate Venus's position at a specific time:

```bash
python main.py --location "51.4778,-0.0015,0" --time "2025-06-01 12:00:00"
```

### Export Data to CSV

All tracking data is automatically saved to CSV. You can specify a custom output file:

```bash
python main.py --location "51.4778,-0.0015,0" --output "my_venus_data.csv"
```

### Using Custom Configuration

You can create your own configuration file and use it:

```bash
python main.py --config "path/to/your/config.yml"
```

## Configuration

The default configuration is in `config/default.yml`. You can create custom config files based on this template.

Key configuration options:

- `location`: Observer's location (latitude, longitude, elevation)
- `tracking_interval`: Time between position calculations in seconds
- `real_time`: Whether to track in real-time or as fast as possible
- `atmospheric_model`: Settings for the atmospheric model
- `visualization`: Options for data visualization

## Project Structure

- `src/position_tracking/`: Venus position calculation
- `src/atmospheric_model/`: Venus atmosphere modeling
- `src/data_logging/`: Data logging and visualization
- `src/config/`: Configuration management
- `config/`: Configuration files
- `main.py`: Main entry point

## Requirements

- Python 3.9+
- skyfield
- numpy
- pandas
- matplotlib
- pyyaml
=======
# Real-Time Venus Atmosphere + Sky Position Tracker
This Python project provides a lightweight, terminal-based tool to track the real-time position of Venus (azimuth and altitude) from a specified Earth location and display a simulated model of Venus' atmospheric conditions. Built using the skyfield library, it updates every 5 seconds and is designed for easy expansion (e.g., GUI or database logging).
Features

## Real-Time Sky Position: Tracks Venus' altitude and azimuth from a user-defined Earth location (default: Hyderabad, India).
Atmospheric Model: Displays a simulated real-time model of Venus' atmosphere, including temperature, pressure, gas composition, wind speed, clouds, visibility, and sky appearance.
Lightweight: Runs in the terminal with minimal dependencies.
Extensible: Code is modular for future enhancements like GUI integration or data logging.

## Prerequisites

Python 3.6+
skyfield library

## Installation

### Clone this repository:
git clone https://github.com/your-username/venus-realtime-tracker.git
cd venus-realtime-tracker

Install the required dependency:
pip install skyfield



Usage

Save the main script as venus_realtime_tracker.py (or use the provided file in the repository).
Run the script:python venus_realtime_tracker.py


The terminal will display Venus' position and atmospheric data, updating every 5 seconds.
Press Ctrl+C to stop the tracker.

## Sample Output
--- Real-Time Venus Tracker (Atmosphere + Position) ---

Time: 2025-04-05 14:25:12 UTC
Venus Position → Altitude: 51.40°, Azimuth: 213.25°

Current Venus Atmosphere (Simulated Real-Time):
 - Surface Temperature: 464°C
 - Pressure: 92 atm
 - Gas Composition: 96.5% CO₂, 3.5% N₂
 - Wind Speed (Cloud Tops): 360 km/h
 - Clouds: Sulfuric Acid, opaque
 - Visibility: Zero (optically thick clouds)
 - Sky Appearance: Bright yellow-white due to reflection

============================================================

## Customization

Change Location: Modify the observer's coordinates in the script by updating the wgs84.latlon(17.385, 78.4867) line to your desired latitude and longitude.
Update Interval: Adjust the time.sleep(5) value to change the refresh rate (in seconds).
Atmospheric Model: Enhance the get_venus_atmosphere_model() function to include more parameters or dynamic data.

## Future Enhancements

Add a GUI using tkinter or PyQt for a visual interface.
Implement database logging (e.g., SQLite) to store position and atmospheric data over time.
Integrate real-time atmospheric data from scientific APIs (if available).
Add support for tracking other celestial bodies.

## Dependencies

Skyfield: For accurate astronomical calculations.
Python's built-in time module.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
Contributing
Contributions are welcome! Please fork the repository, create a new branch, and submit a pull request with your changes.
Acknowledgments

Built with Skyfield for precise planetary position calculations.
Atmospheric data based on scientific models from Venus exploration missions.


>>>>>>> 30eff81640e3d1aa12046f0430f3b105d04e1b20
