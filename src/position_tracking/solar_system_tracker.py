from skyfield.api import load, wgs84, utc
from astropy import units as u
from astropy.coordinates import solar_system_ephemeris, get_body, get_moon, get_sun, get_body_barycentric
from datetime import datetime, timedelta
import numpy as np
import time
import os

# Constants
AU_TO_KM = 149597870.7  # kilometers per astronomical unit

class SolarSystemTracker:
    def __init__(self, config, location):
        self.config = config
        self.location = location
        self.ephemeris = load('de421.bsp')
        self.planets = {
            'sun': self.ephemeris['sun'],
            'mercury': self.ephemeris['mercury'],
            'venus': self.ephemeris['venus'],
            'earth': self.ephemeris['earth'],
            'mars': self.ephemeris['mars'],
            'jupiter': self.ephemeris['jupiter barycenter'],
            'saturn': self.ephemeris['saturn barycenter'],
            'uranus': self.ephemeris['uranus barycenter'],
            'neptune': self.ephemeris['neptune barycenter'],
        }
        self.moon = self.ephemeris['moon']
        self.observer = self.planets['earth'] + wgs84.latlon(
            latitude_degrees=location['latitude'],
            longitude_degrees=location['longitude'],
            elevation_m=location['elevation']
        )
        self.ts = load.timescale()
        self.last_calculation = None
        self.last_calculation_time = None
        
    def calculate_body_position(self, body_name, target_time):
        t = self.ts.from_datetime(target_time.replace(tzinfo=utc))
        if body_name.lower() == 'moon':
            body = self.moon
        else:
            body = self.planets.get(body_name.lower())
        if not body:
            raise ValueError(f"Unknown celestial body: {body_name}")
        astrometric = self.observer.at(t).observe(body)
        alt, az, distance = astrometric.apparent().altaz()
        ra, dec, _ = astrometric.radec()
        if body_name.lower() != 'sun':
            sun_astrometric = self.observer.at(t).observe(self.planets['sun'])
            elongation = astrometric.separation_from(sun_astrometric).degrees
        else:
            elongation = 0  
            
        return {
            'name': body_name,
            'altitude': alt.degrees,
            'azimuth': az.degrees,            
            'distance': {
                'au': distance.au,
                'km': distance.au * AU_TO_KM
            },            'ra': ra.hours,
            'dec': dec.degrees,
            'elongation': elongation
        }
        
    def calculate_venus_perspective(self, target_time):
        t = self.ts.from_datetime(target_time.replace(tzinfo=utc))
        venus_observer = self.planets['venus']
        earth_astrometric = venus_observer.at(t).observe(self.planets['earth'])
        earth_ra, earth_dec, earth_distance = earth_astrometric.radec()
        sun_astrometric = venus_observer.at(t).observe(self.planets['sun'])
        sun_ra, sun_dec, sun_distance = sun_astrometric.radec()
        earth_sun_angle = earth_astrometric.separation_from(sun_astrometric).degrees
        return {
            'earth_from_venus': {
                'ra': earth_ra.hours,
                'dec': earth_dec.degrees,
                'distance': {
                    'au': earth_distance.au,
                    'km': earth_distance.au * AU_TO_KM
                },
                'angle_from_sun': earth_sun_angle
            },
            'sun_from_venus': {
                'ra': sun_ra.hours,
                'dec': sun_dec.degrees,
                'distance': {
                    'au': sun_distance.au,
                    'km': sun_distance.au * AU_TO_KM
                }
            }
        }
    def calculate_all_planets_positions(self, target_time):
        t = self.ts.from_datetime(target_time.replace(tzinfo=utc))
        positions = {}
        for planet_name, planet in self.planets.items():
            if planet_name != 'earth':  
                astrometric = self.observer.at(t).observe(planet)
                alt, az, distance = astrometric.apparent().altaz()
                ra, dec, _ = astrometric.radec()
                
                positions[planet_name] = {
                    'altitude': alt.degrees,
                    'azimuth': az.degrees,
                    'distance': {
                        'au': distance.au,
                        'km': distance.au * AU_TO_KM
                    },
                    'ra': ra.hours,
                    'dec': dec.degrees
                }
                if planet_name != 'sun':
                    sun_astrometric = self.observer.at(t).observe(self.planets['sun'])
                    positions[planet_name]['elongation'] = astrometric.separation_from(sun_astrometric).degrees
        moon_astrometric = self.observer.at(t).observe(self.moon)
        moon_alt, moon_az, moon_distance = moon_astrometric.apparent().altaz()
        moon_ra, moon_dec, _ = moon_astrometric.radec()
        positions['moon'] = {
            'altitude': moon_alt.degrees,
            'azimuth': moon_az.degrees,
            'distance': {
                'au': moon_distance.au,
                'km': moon_distance.au * AU_TO_KM
            },
            'ra': moon_ra.hours,
            'dec': moon_dec.degrees,
            'elongation': moon_astrometric.separation_from(self.observer.at(t).observe(self.planets['sun'])).degrees
        }
        
        return positions
    
    def calculate_planet_distances(self, target_time):
        t = self.ts.from_datetime(target_time.replace(tzinfo=utc))
        
        distances = {}
        planet_list = list(self.planets.keys())
        for i, planet1 in enumerate(planet_list):
            distances[planet1] = {}
            
            for planet2 in planet_list[i+1:]:
                distance = self.planets[planet1].at(t).observe(self.planets[planet2]).distance()
                
                distances[planet1][planet2] = {
                    'au': distance.au,
                    'km': distance.au * AU_TO_KM
                }
        return distances
    def calculate_orbital_parameters(self, target_time):
        t = self.ts.from_datetime(target_time.replace(tzinfo=utc))
        parameters = {}
        venus = self.planets['venus']
        earth = self.planets['earth']
        sun = self.planets['sun']
        venus_astrometric = self.observer.at(t).observe(venus)
        venus_app = venus_astrometric.apparent()
        _, _, venus_distance = venus_app.altaz()
        sun_astrometric = self.observer.at(t).observe(sun)
        phase_angle = venus_astrometric.separation_from(sun_astrometric).degrees
        phase = (1 + np.cos(np.radians(phase_angle))) / 2
        earth_helio = earth.at(t)
        venus_helio = venus.at(t)
        _, venus_lon, _ = venus_helio.ecliptic_latlon()
        _, earth_lon, _ = earth_helio.ecliptic_latlon()
        venus_longitude = venus_lon.degrees % 360
        earth_longitude = earth_lon.degrees % 360
        
        parameters['venus'] = {
            'distance_from_earth': {
                'au': venus_distance.au,
                'km': venus_distance.au * AU_TO_KM
            },
            'phase_angle': phase_angle,
            'illuminated_fraction': phase,
            'orbital_longitude': venus_longitude,
            'relative_to_earth': (venus_longitude - earth_longitude) % 360
        }
        
        return parameters
    
    def calculate_all_positions(self, target_time):
        if (self.last_calculation_time and 
            (target_time - self.last_calculation_time).total_seconds() < self.config.get('tracking_interval', 60)):
            return self.last_calculation
        
        result = {
            'timestamp': target_time.isoformat(),
            'observer': {
                'location_name': self.location.get('name', 'Unknown Location'),
                'latitude': self.location['latitude'],
                'longitude': self.location['longitude'],
                'elevation': self.location['elevation']
            },
            'celestial_bodies': {
                'venus': self.calculate_body_position('venus', target_time),
                'sun': self.calculate_body_position('sun', target_time),
                'moon': self.calculate_body_position('moon', target_time)
            },
            'venus_perspective': self.calculate_venus_perspective(target_time),
            'orbital_parameters': self.calculate_orbital_parameters(target_time)
        }
        if self.config.get('calculate_all_planets', True):
            result['all_planets'] = self.calculate_all_planets_positions(target_time)
            result['planet_distances'] = self.calculate_planet_distances(target_time)
        
        self.last_calculation = result
        self.last_calculation_time = target_time
        
        return result
    
    def track_real_time(self, duration_seconds=None, callback=None):
        interval_seconds = self.config.get('tracking_interval', 60)
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(seconds=duration_seconds) if duration_seconds else None
        
        print(f"Starting real-time tracking from {start_time} (UTC)")
        print(f"Update interval: {interval_seconds} seconds")
        print(f"Duration: {duration_seconds} seconds" if duration_seconds else "Tracking indefinitely")
        print(f"Observer location: {self.location.get('name', 'Unknown')} ({self.location['latitude']}, {self.location['longitude']}, {self.location['elevation']}m)")
        
        try:
            while True:
                current_time = datetime.utcnow()
                
                if end_time and current_time > end_time:
                    print("Tracking duration completed")
                    break
                
                data = self.calculate_all_positions(current_time)
                
                if callback:
                    callback(current_time, data)
                
                # Calculate time to sleep until next update
                next_update = current_time + timedelta(seconds=interval_seconds)
                sleep_seconds = (next_update - datetime.utcnow()).total_seconds()
                
                if sleep_seconds > 0:
                    time.sleep(sleep_seconds)
                
        except KeyboardInterrupt:
            print("Tracking stopped by user")
        
        print("Tracking complete")
    
    def track_over_time(self, start_time, duration_minutes, data_logger, atmospheric_model=None):
        print(f"Tracking solar system for {duration_minutes} minutes starting at {start_time}")
        interval_seconds = self.config.get('tracking_interval', 60)
        
        end_time = start_time + timedelta(minutes=duration_minutes)
        current_time = start_time
        while current_time <= end_time:
            data = self.calculate_all_positions(current_time)
            atmosphere_data = None
            if atmospheric_model:
                atmosphere_data = atmospheric_model.calculate_parameters(current_time, data['celestial_bodies']['venus'])
            data_logger.log_entry(current_time, data['celestial_bodies']['venus'], atmosphere_data)
            current_time += timedelta(seconds=interval_seconds)
        print(f"Tracking complete. Data logged to {data_logger.output_file}")
