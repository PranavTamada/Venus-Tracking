import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta


class DataVisualizer:
    def __init__(self, output_dir="plots"):

        self.output_dir = output_dir
        
        os.makedirs(output_dir, exist_ok=True)
    
    def create_plots(self, data_file, config=None):
        
        try:
            df = pd.read_csv(data_file)
            if len(df) == 0:
                print("No data available for plotting")
                return False
            
            df['datetime'] = pd.to_datetime(df['timestamp'])
            
            self._plot_altitude_azimuth(df)
            
            if 'temperature' in df.columns and 'pressure' in df.columns:
                self._plot_atmospheric_data(df)
            
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
        plot_file = os.path.join(self.output_dir, 'altitude_azimuth.png')
        plt.savefig(plot_file)
        plt.close()
        print(f"Altitude/Azimuth plot saved to {plot_file}")
    
    def _plot_atmospheric_data(self, df):

        plt.figure(figsize=(12, 10))
        
        plt.subplot(2, 1, 1)
        plt.plot(df['datetime'], df['temperature'], 'g-', linewidth=2)
        plt.title('Temperature at Venus Cloud Tops')
        plt.ylabel('Temperature (K)')
        plt.grid(True)
        
        plt.subplot(2, 1, 2)
        plt.plot(df['datetime'], df['pressure'], 'c-', linewidth=2)
        plt.title('Pressure at Venus Cloud Tops')
        plt.xlabel('Date/Time')
        plt.ylabel('Pressure (bar)')
        plt.grid(True)
        
        plt.tight_layout()
        plot_file = os.path.join(self.output_dir, 'atmospheric_data.png')
        plt.savefig(plot_file)
        plt.close()
        print(f"Atmospheric data plot saved to {plot_file}")
    
    def create_polar_plot(self, df):

        plt.figure(figsize=(10, 10))
        ax = plt.subplot(111, projection='polar')
        azimuth_rad = np.radians(90 - df['azimuth'])
        
        zenith = 90 - df['altitude']
        
        zenith_norm = zenith / 90.0
        
        scatter = ax.scatter(azimuth_rad, zenith_norm, c=df.index, cmap='viridis', alpha=0.8)
        
        ax.set_theta_zero_location('N')  
        ax.set_theta_direction(-1)       
        
        ax.set_rlim(0, 1)
        
        ax.set_rticks([0.25, 0.5, 0.75, 1.0])
        ax.set_rticklabels(['65°', '45°', '20°', '0° (horizon)'])
        
        plt.title('Venus Position in the Sky (Polar View)', y=1.08)
        
        cbar = plt.colorbar(scatter, pad=0.1)
        cbar.set_label('Observation Sequence')
        
        plot_file = os.path.join(self.output_dir, 'venus_polar_position.png')
        plt.savefig(plot_file)
        plt.close()
        print(f"Polar plot saved to {plot_file}")
