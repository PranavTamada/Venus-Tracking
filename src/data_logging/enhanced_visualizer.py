import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

class EnhancedDataVisualizer:
    def __init__(self, output_dir="plots"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "static"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "interactive"), exist_ok=True)
    
    def create_plots(self, data_file, config=None):
        try:
            df = pd.read_csv(data_file)
            if len(df) == 0:
                print("No data available for plotting")
                return False
            df['datetime'] = pd.to_datetime(df['timestamp'])
            self._plot_altitude_azimuth(df)
            if 'cloud_temp_k' in df.columns and 'surface_pressure_bar' in df.columns:
                self._plot_atmospheric_data(df)
            self.create_polar_plot(df)
            self._create_interactive_altitude_azimuth(df)
            if 'cloud_temp_k' in df.columns:
                self._create_interactive_atmospheric_data(df)
            if 'distance_au' in df.columns:
                self._create_solar_system_map(df)
            return True
        except Exception as e:
            print(f"Error creating plots: {e}")
            return False
    def _plot_altitude_azimuth(self, df):
        plt.figure(figsize=(12, 10))
        
        plt.subplot(2, 1, 1)
        plt.plot(df['datetime'], df['altitude'], 'b-', linewidth=2)
        plt.title('Venus Altitude Over Time')
        plt.ylabel('Altitude (degrees)')
        plt.grid(True)

        plt.subplot(2, 1, 2)
        plt.plot(df['datetime'], df['azimuth'], 'r-', linewidth=2)
        plt.title('Venus Azimuth Over Time')
        plt.xlabel('Date/Time')
        plt.ylabel('Azimuth (degrees)')
        plt.grid(True)
        
        plt.tight_layout()
        plot_file = os.path.join(self.output_dir, 'static', 'altitude_azimuth.png')
        plt.savefig(plot_file)
        plt.close()
        print(f"Altitude/Azimuth plot saved to {plot_file}")
    
    def _plot_atmospheric_data(self, df):
        plt.figure(figsize=(12, 15))
        plt.subplot(3, 1, 1)
        if 'cloud_temp_k' in df.columns:
            plt.plot(df['datetime'], df['cloud_temp_k'], 'g-', linewidth=2, label='Cloud Top')
        if 'surface_temp_k' in df.columns:
            plt.plot(df['datetime'], df['surface_temp_k'], 'r-', linewidth=2, label='Surface')
        if 'ground_temp_k' in df.columns:
            plt.plot(df['datetime'], df['ground_temp_k'], 'b--', linewidth=2, label='Ground')
        plt.title('Venus Temperatures')
        plt.ylabel('Temperature (K)')
        plt.legend()
        plt.grid(True)
        plt.subplot(3, 1, 2)
        if 'cloud_pressure_bar' in df.columns:
            plt.plot(df['datetime'], df['cloud_pressure_bar'], 'c-', linewidth=2, label='Cloud Top')
        if 'surface_pressure_bar' in df.columns:
            plt.plot(df['datetime'], df['surface_pressure_bar'], 'm-', linewidth=2, label='Surface')
        plt.title('Venus Atmospheric Pressure')
        plt.ylabel('Pressure (bar)')
        plt.legend()
        plt.grid(True)
        plt.subplot(3, 1, 3)
        if 'wind_speed_m_s' in df.columns:
            plt.plot(df['datetime'], df['wind_speed_m_s'], 'k-', linewidth=2)
            plt.title('Venus Surface Wind Speed')
            plt.xlabel('Date/Time')
            plt.ylabel('Wind Speed (m/s)')
            plt.grid(True)
        plt.tight_layout()
        plot_file = os.path.join(self.output_dir, 'static', 'atmospheric_data.png')
        plt.savefig(plot_file)
        plt.close()
        print(f"Atmospheric data plot saved to {plot_file}")
    def create_polar_plot(self, df):
        plt.figure(figsize=(10, 10))
        ax = plt.subplot(111, projection='polar')
        azimuth_rad = np.radians(90 - df['azimuth'])
        zenith = 90 - df['altitude']
        zenith_norm = zenith / 90.0
        
        # Create scatter plot with color representing observation sequence
        scatter = ax.scatter(azimuth_rad, zenith_norm, c=df.index, cmap='viridis', alpha=0.8)
        
        # Set plot orientation
        ax.set_theta_zero_location('N')  # 0 degrees at North
        ax.set_theta_direction(-1)       # Clockwise
        
        # Set radial limits
        ax.set_rlim(0, 1)
        
        # Set custom radial ticks and labels
        ax.set_rticks([0.25, 0.5, 0.75, 1.0])
        ax.set_rticklabels(['65°', '45°', '20°', '0° (horizon)'])
        
        # Add title
        plt.title('Venus Position in the Sky (Polar View)', y=1.08)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, pad=0.1)
        cbar.set_label('Observation Sequence')
        
        # Save plot
        plot_file = os.path.join(self.output_dir, 'static', 'venus_polar_position.png')
        plt.savefig(plot_file)
        plt.close()
        print(f"Polar plot saved to {plot_file}")
    
    def _create_interactive_altitude_azimuth(self, df):
        """
        Create interactive plotly plot of altitude and azimuth over time.
        
        Args:
            df (DataFrame): Pandas DataFrame with observation data
        """
        # Create subplot with 2 rows
        fig = make_subplots(rows=2, cols=1, 
                           subplot_titles=("Venus Altitude Over Time", "Venus Azimuth Over Time"))
        
        # Add altitude trace
        fig.add_trace(
            go.Scatter(x=df['datetime'], y=df['altitude'], mode='lines', 
                      name='Altitude', line=dict(color='blue', width=2)),
            row=1, col=1
        )
        
        # Add azimuth trace
        fig.add_trace(
            go.Scatter(x=df['datetime'], y=df['azimuth'], mode='lines', 
                      name='Azimuth', line=dict(color='red', width=2)),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            title_text="Venus Position Over Time",
            hovermode="closest"
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="Altitude (degrees)", row=1, col=1)
        fig.update_yaxes(title_text="Azimuth (degrees)", row=2, col=1)
        
        # Update x-axis labels
        fig.update_xaxes(title_text="Date/Time", row=2, col=1)
        
        # Save as HTML file
        plot_file = os.path.join(self.output_dir, 'interactive', 'altitude_azimuth.html')
        fig.write_html(plot_file, include_plotlyjs='cdn')
        print(f"Interactive altitude/azimuth plot saved to {plot_file}")
    
    def _create_interactive_atmospheric_data(self, df):
        """
        Create interactive plotly plot of atmospheric data over time.
        
        Args:
            df (DataFrame): Pandas DataFrame with observation data
        """
        # Create subplot with 3 rows
        fig = make_subplots(rows=3, cols=1, 
                           subplot_titles=("Venus Temperatures", "Venus Atmospheric Pressure", "Venus Surface Wind Speed"))
        
        # Add temperature traces
        if 'cloud_temp_k' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['datetime'], y=df['cloud_temp_k'], mode='lines', 
                          name='Cloud Top Temperature (K)', line=dict(color='green', width=2)),
                row=1, col=1
            )
        
        if 'surface_temp_k' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['datetime'], y=df['surface_temp_k'], mode='lines', 
                          name='Surface Temperature (K)', line=dict(color='red', width=2)),
                row=1, col=1
            )
            
            # Add temperature in Celsius on secondary y-axis
            fig.add_trace(
                go.Scatter(x=df['datetime'], y=df['surface_temp_c'], mode='lines', 
                          name='Surface Temperature (°C)', line=dict(color='orange', width=2, dash='dash')),
                row=1, col=1
            )
        
        # Add pressure traces
        if 'cloud_pressure_bar' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['datetime'], y=df['cloud_pressure_bar'], mode='lines', 
                          name='Cloud Top Pressure (bar)', line=dict(color='cyan', width=2)),
                row=2, col=1
            )
        
        if 'surface_pressure_bar' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['datetime'], y=df['surface_pressure_bar'], mode='lines', 
                          name='Surface Pressure (bar)', line=dict(color='magenta', width=2)),
                row=2, col=1
            )
            
            # Add pressure in atm on secondary y-axis
            fig.add_trace(
                go.Scatter(x=df['datetime'], y=df['surface_pressure_atm'], mode='lines', 
                          name='Surface Pressure (atm)', line=dict(color='purple', width=2, dash='dash')),
                row=2, col=1
            )
        
        # Add wind speed trace
        if 'wind_speed_m_s' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['datetime'], y=df['wind_speed_m_s'], mode='lines', 
                          name='Surface Wind Speed (m/s)', line=dict(color='black', width=2)),
                row=3, col=1
            )
            
            # Add wind speed in km/h on secondary y-axis
            fig.add_trace(
                go.Scatter(x=df['datetime'], y=df['wind_speed_km_h'], mode='lines', 
                          name='Surface Wind Speed (km/h)', line=dict(color='gray', width=2, dash='dash')),
                row=3, col=1
            )
        
        # Update layout
        fig.update_layout(
            height=1000,
            title_text="Venus Atmospheric Data",
            hovermode="closest"
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="Temperature (K / °C)", row=1, col=1)
        fig.update_yaxes(title_text="Pressure (bar / atm)", row=2, col=1)
        fig.update_yaxes(title_text="Wind Speed (m/s / km/h)", row=3, col=1)
        
        # Update x-axis labels
        fig.update_xaxes(title_text="Date/Time", row=3, col=1)
        
        # Save as HTML file
        plot_file = os.path.join(self.output_dir, 'interactive', 'atmospheric_data.html')
        fig.write_html(plot_file, include_plotlyjs='cdn')
        print(f"Interactive atmospheric data plot saved to {plot_file}")
    
    def _create_solar_system_map(self, df):
        """
        Create interactive solar system map.
        
        Args:
            df (DataFrame): Pandas DataFrame with observation data
        """
        # Use the latest data point
        latest_data = df.iloc[-1]
        
        # Create figure
        fig = go.Figure()
        
        # Add Sun at the center
        fig.add_trace(go.Scatter(
            x=[0],
            y=[0],
            mode='markers',
            name='Sun',
            marker=dict(
                size=20,
                color='yellow',
                line=dict(color='orange', width=2)
            )
        ))
        
        # Get last data row for planet positions
        # In a real implementation, this would use the planet positions data
        # For demonstration, we'll use dummy orbital positions
        
        # Mercury orbit
        mercury_orbit_x = np.cos(np.linspace(0, 2*np.pi, 100)) * 0.4
        mercury_orbit_y = np.sin(np.linspace(0, 2*np.pi, 100)) * 0.4
        fig.add_trace(go.Scatter(
            x=mercury_orbit_x,
            y=mercury_orbit_y,
            mode='lines',
            line=dict(color='gray', width=1),
            hoverinfo='skip',
            showlegend=False
        ))
        
        # Venus orbit
        venus_orbit_x = np.cos(np.linspace(0, 2*np.pi, 100)) * 0.7
        venus_orbit_y = np.sin(np.linspace(0, 2*np.pi, 100)) * 0.7
        fig.add_trace(go.Scatter(
            x=venus_orbit_x,
            y=venus_orbit_y,
            mode='lines',
            line=dict(color='gray', width=1),
            hoverinfo='skip',
            showlegend=False
        ))
        
        # Earth orbit
        earth_orbit_x = np.cos(np.linspace(0, 2*np.pi, 100)) * 1.0
        earth_orbit_y = np.sin(np.linspace(0, 2*np.pi, 100)) * 1.0
        fig.add_trace(go.Scatter(
            x=earth_orbit_x,
            y=earth_orbit_y,
            mode='lines',
            line=dict(color='gray', width=1),
            hoverinfo='skip',
            showlegend=False
        ))
        
        # Mars orbit
        mars_orbit_x = np.cos(np.linspace(0, 2*np.pi, 100)) * 1.5
        mars_orbit_y = np.sin(np.linspace(0, 2*np.pi, 100)) * 1.5
        fig.add_trace(go.Scatter(
            x=mars_orbit_x,
            y=mars_orbit_y,
            mode='lines',
            line=dict(color='gray', width=1),
            hoverinfo='skip',
            showlegend=False
        ))
        
        # Planet positions (example positions)
        # For a full implementation, these would come from the planet tracking data
        mercury_pos = 0.8  # position in orbit (0-1)
        venus_pos = 0.3
        earth_pos = 0.6
        mars_pos = 0.2
        
        # Add planets
        # Mercury
        mercury_x = np.cos(mercury_pos * 2 * np.pi) * 0.4
        mercury_y = np.sin(mercury_pos * 2 * np.pi) * 0.4
        fig.add_trace(go.Scatter(
            x=[mercury_x],
            y=[mercury_y],
            mode='markers',
            name='Mercury',
            marker=dict(
                size=8,
                color='gray',
                line=dict(color='darkgray', width=1)
            )
        ))
        
        # Venus
        venus_x = np.cos(venus_pos * 2 * np.pi) * 0.7
        venus_y = np.sin(venus_pos * 2 * np.pi) * 0.7
        fig.add_trace(go.Scatter(
            x=[venus_x],
            y=[venus_y],
            mode='markers',
            name='Venus',
            marker=dict(
                size=15,
                color='orange',
                line=dict(color='brown', width=1)
            )
        ))
        
        # Earth
        earth_x = np.cos(earth_pos * 2 * np.pi) * 1.0
        earth_y = np.sin(earth_pos * 2 * np.pi) * 1.0
        fig.add_trace(go.Scatter(
            x=[earth_x],
            y=[earth_y],
            mode='markers',
            name='Earth',
            marker=dict(
                size=15,
                color='blue',
                line=dict(color='darkblue', width=1)
            )
        ))
        
        # Mars
        mars_x = np.cos(mars_pos * 2 * np.pi) * 1.5
        mars_y = np.sin(mars_pos * 2 * np.pi) * 1.5
        fig.add_trace(go.Scatter(
            x=[mars_x],
            y=[mars_y],
            mode='markers',
            name='Mars',
            marker=dict(
                size=12,
                color='red',
                line=dict(color='darkred', width=1)
            )
        ))
        
        # Add Earth-Venus line
        fig.add_trace(go.Scatter(
            x=[earth_x, venus_x],
            y=[earth_y, venus_y],
            mode='lines',
            name='Earth-Venus',
            line=dict(color='cyan', width=2, dash='dash')
        ))
        
        # Update layout
        fig.update_layout(
            title="Solar System Map",
            xaxis_title="X (AU)",
            yaxis_title="Y (AU)",
            legend_title="Celestial Bodies",
            hovermode="closest",
            xaxis=dict(
                scaleanchor="y",
                scaleratio=1,
                range=[-2, 2]
            ),
            yaxis=dict(
                scaleanchor="x",
                scaleratio=1,
                range=[-2, 2]
            )
        )
        
        # Add annotations
        fig.add_annotation(
            x=0, y=0,
            text="Sun",
            showarrow=True,
            arrowhead=1,
            ax=30, ay=30
        )
        
        # Save as HTML file
        plot_file = os.path.join(self.output_dir, 'interactive', 'solar_system_map.html')
        fig.write_html(plot_file, include_plotlyjs='cdn')
        print(f"Interactive solar system map saved to {plot_file}")
        
        # Also create a distance comparison graph
        self._create_distance_comparison()
    
    def _create_distance_comparison(self):
        """Create interactive distance comparison graph between planets."""
        # Example distance data (would come from actual tracking data)
        distances = {
            'Mercury-Venus': 0.34,
            'Mercury-Earth': 0.61,
            'Mercury-Mars': 1.14,
            'Venus-Earth': 0.28,
            'Venus-Mars': 0.83,
            'Earth-Mars': 0.52
        }
        
        # Convert to AU and km
        distances_km = {k: v * 149597870.7 for k, v in distances.items()}
        
        # Create figure
        fig = make_subplots(rows=1, cols=2, 
                           subplot_titles=("Planet Distances (AU)", "Planet Distances (Million km)"),
                           specs=[[{"type": "bar"}, {"type": "bar"}]])
        
        # Add AU data
        fig.add_trace(
            go.Bar(
                x=list(distances.keys()),
                y=list(distances.values()),
                name='Distance (AU)',
                marker_color='blue'
            ),
            row=1, col=1
        )
        
        # Add km data
        fig.add_trace(
            go.Bar(
                x=list(distances_km.keys()),
                y=[v/1000000 for v in distances_km.values()],  # Convert to millions
                name='Distance (Million km)',
                marker_color='green'
            ),
            row=1, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="Interplanetary Distances",
            height=500,
            showlegend=False
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="Distance (AU)", row=1, col=1)
        fig.update_yaxes(title_text="Distance (Million km)", row=1, col=2)
        
        # Save as HTML file
        plot_file = os.path.join(self.output_dir, 'interactive', 'distance_comparison.html')
        fig.write_html(plot_file, include_plotlyjs='cdn')
        print(f"Interactive distance comparison plot saved to {plot_file}")
    
    def create_dashboard(self, data_file):
        dashboard_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Venus Tracking Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        .dashboard {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .section {{
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .plots {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .plot-link {{
            display: block;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            padding: 10px 15px;
            border-radius: 4px;
            margin: 5px 0;
        }}
        .plot-link:hover {{
            background-color: #45a049;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="section">
            <h1>Venus Tracking Dashboard</h1>
            <p>Data source: {data_file}</p>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>Interactive Visualizations</h2>
            <div class="plots">
                <div>
                    <h3>Position Tracking</h3>
                    <a class="plot-link" href="interactive/altitude_azimuth.html" target="_blank">Altitude & Azimuth</a>
                    <a class="plot-link" href="interactive/solar_system_map.html" target="_blank">Solar System Map</a>
                    <a class="plot-link" href="interactive/distance_comparison.html" target="_blank">Planet Distances</a>
                </div>
                <div>
                    <h3>Venus Environmental Data</h3>
                    <a class="plot-link" href="interactive/atmospheric_data.html" target="_blank">Atmospheric Parameters</a>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Static Visualizations</h2>
            <div class="plots">
                <div>
                    <h3>Position Tracking</h3>
                    <a class="plot-link" href="static/altitude_azimuth.png" target="_blank">Altitude & Azimuth</a>
                    <a class="plot-link" href="static/venus_polar_position.png" target="_blank">Polar Position</a>
                </div>
                <div>
                    <h3>Venus Environmental Data</h3>
                    <a class="plot-link" href="static/atmospheric_data.png" target="_blank">Atmospheric Parameters</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        # Save dashboard HTML
        dashboard_file = os.path.join(self.output_dir, 'venus_dashboard.html')
        with open(dashboard_file, 'w') as f:
            f.write(dashboard_html)
        
        print(f"Dashboard created at {dashboard_file}")
        return dashboard_file
