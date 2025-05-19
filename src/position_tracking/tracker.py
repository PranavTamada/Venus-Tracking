from skyfield.api import load, wgs84, utc
from datetime import datetime, timedelta
import time


class VenusTracker:
    def __init__(self, config, location):
        self.config = config
        self.location = location
        
        self.ephemeris = load('de421.bsp')  
        self.earth = self.ephemeris['earth']
        self.venus = self.ephemeris['venus']
        
        self.observer = self.earth + wgs84.latlon(
            latitude_degrees=location['latitude'],
            longitude_degrees=location['longitude'],
            elevation_m=location['elevation']
        )
        
        self.ts = load.timescale()
    
    def calculate_position(self, target_time):
        t = self.ts.from_datetime(target_time.replace(tzinfo=utc))
        
        astrometric = self.observer.at(t).observe(self.venus)
        
        alt, az, distance = astrometric.apparent().altaz()
        
        return {
            'altitude': alt.degrees,
            'azimuth': az.degrees,
            'distance': astrometric.distance().au,  # in astronomical units
            'ra': astrometric.radec()[0].hours,     # right ascension
            'dec': astrometric.radec()[1].degrees,  # declination
            'elongation': astrometric.from_star(self.ephemeris['sun']).degrees
        }
    
    def track_over_time(self, start_time, duration_minutes, data_logger, atmospheric_model=None):
        
        print(f"Tracking Venus for {duration_minutes} minutes starting at {start_time}")
        
        interval_seconds = self.config.get('tracking_interval', 60)  
        
        end_time = start_time + timedelta(minutes=duration_minutes)
        current_time = start_time
        
        while current_time <= end_time:
            position = self.calculate_position(current_time)
            
            if atmospheric_model:
                atmosphere = atmospheric_model.calculate_parameters(current_time, position)
            else:
                atmosphere = None
            
            data_logger.log_entry(current_time, position, atmosphere)
            
            print(f"Time: {current_time} | Alt: {position['altitude']:.2f}° | Az: {position['azimuth']:.2f}°")
            
            if self.config.get('real_time', False) and current_time < end_time:
                time.sleep(interval_seconds)
                current_time = datetime.now()
            else:
                current_time += timedelta(seconds=interval_seconds)
                
        print(f"Tracking complete. Data logged to {data_logger.output_file}")
