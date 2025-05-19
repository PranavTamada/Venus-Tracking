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

   ```bash
   git clone https://github.com/PranavTamada/Venus-Tracking.git
   cd venus-tracking
   ```

2. Create and activate a conda environment(optional but recommended):

   ```bash
   conda create -n venus python=3.9
   conda activate venus
   ```

3. Install required packages:

   ```bash
    pip install -r requirements.txt
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
