# Venus Atmosphere & Position Tracking System

A Python-based system for tracking the position of Venus and modeling its atmosphere.

## Overview

This project provides tools to:

- Calculate the position of Venus in the sky from any location on Earth
- Model Venus's atmospheric conditions
- Log position and atmospheric data over time
- Generate visualizations of tracking data
- View Venus-centric perspectives of Earth and the Sun

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/PranavTamada/Venus-Tracking.git
   cd Venus-Tracking
   ```

2. Create and activate a virtual environment (optional but recommended):

   ```bash
   # Using conda
   conda create -n venus python=3.9
   conda activate venus
   
   # Or using venv
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Using the Demo Script

The easiest way to explore the functionality is through the enhanced demo script:

```bash
python demo_enhanced.py
```

This will:
- Initialize the application with default settings
- Demonstrate location management
- Show Venus position calculations
- Generate sample data and visualizations
- Provide instructions for real-time tracking

### Using the Main Application

#### Basic Position Tracking

To track Venus's current position from your location:

```bash
python venus_app.py --location "New York City"
```

Or with coordinates:

```bash
python venus_app.py --location "51.4778,-0.0015,0"
```

#### Track Over Time

To track Venus over a period of time:

```bash
python venus_app.py --mode track --location "New York City" --duration 60 --interval 10
```

This will track Venus's position for 60 minutes, taking measurements every 10 seconds.

#### Calculate Position for a Specific Time

To calculate Venus's position at a specific time:

```bash
python venus_app.py --time "2025-06-01 12:00:00" --location "New York City"
```

#### Export Data

All tracking data is automatically saved to CSV and can be exported in various formats:

```bash
python venus_app.py --mode export --format json
```

#### Visualize Data

To generate visualizations from collected data:

```bash
python venus_app.py --mode visualize
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

- `venus_app.py`: Main application entry point
- `demo_enhanced.py`: Interactive demonstration of all features
- `src/position_tracking/`: Venus position calculation
- `src/atmospheric_model/`: Venus atmosphere modeling
- `src/data_logging/`: Data logging and visualization
- `src/config/`: Configuration management
- `config/`: Configuration files
- `data/`: Stored tracking data
- `plots/`: Generated visualizations

## Recent Updates

- Fixed calculation of Venus perspective using Skyfield's proper coordinate system
- Corrected phase angle calculations using `separation_from` instead of deprecated `from_star`
- Improved orbital parameter calculations using ecliptic coordinates
- Enhanced error handling and encoding issue detection

## Requirements

- Python 3.9+
- skyfield
- numpy
- pandas
- matplotlib
- pyyaml
- astropy
- geopy (for location lookups)
- plotly (for interactive visualizations)

The full list of dependencies is available in `requirements.txt`.

## Troubleshooting

### Encoding Issues

If you encounter errors related to null bytes or encoding issues, run the provided fix script:

```bash
python fix_null_bytes.py
```

### Missing Dependencies

If you receive errors about missing modules, ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Coordinate System Errors

When working with celestial coordinates, be aware that:

1. Altitude/azimuth calculations require an observer on a defined celestial body
2. Venus-centric views use right ascension/declination coordinates instead of altitude/azimuth

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The [Skyfield](https://rhodesmill.org/skyfield/) library for astronomical calculations
- NASA JPL for providing the planetary ephemeris data
