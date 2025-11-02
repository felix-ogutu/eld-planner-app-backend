import requests
import os
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2


class RouteCalculator:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTE_API_KEY', 'YOUR_API_KEY_HERE')
        self.base_url = "https://api.openrouteservice.org/v2"

    def geocode_location(self, location):
        """Convert location string to coordinates"""
        url = f"{self.base_url}/geocode/search"
        params = {
            'api_key': self.api_key,
            'text': location,
            'size': 1
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data['features']:
                coords = data['features'][0]['geometry']['coordinates']
                return {'lon': coords[0], 'lat': coords[1]}
            else:
                return self._get_fallback_coords(location)
        except:
            return self._get_fallback_coords(location)

    def _get_fallback_coords(self, location):
        """Fallback coordinates for common cities"""
        fallback = {
            'los angeles': {'lon': -118.2437, 'lat': 34.0522},
            'phoenix': {'lon': -112.0740, 'lat': 33.4484},
            'dallas': {'lon': -96.7970, 'lat': 32.7767},
            'chicago': {'lon': -87.6298, 'lat': 41.8781},
            'new york': {'lon': -74.0060, 'lat': 40.7128},
            'houston': {'lon': -95.3698, 'lat': 29.7604},
            'atlanta': {'lon': -84.3880, 'lat': 33.7490},
        }

        location_key = location.lower().split(',')[0].strip()
        return fallback.get(location_key, {'lon': -95.7129, 'lat': 37.0902})

    def calculate_route(self, current_loc, pickup_loc, dropoff_loc):
        """Calculate route with all waypoints"""
        current_coords = self.geocode_location(current_loc)
        pickup_coords = self.geocode_location(pickup_loc)
        dropoff_coords = self.geocode_location(dropoff_loc)

        leg1_distance = self._calculate_distance(current_coords, pickup_coords)
        leg2_distance = self._calculate_distance(pickup_coords, dropoff_coords)
        total_distance = leg1_distance + leg2_distance

        driving_time = total_distance / 60.0
        fuel_stops = int(total_distance / 1000)
        total_trip_time = driving_time + 2.0 + (fuel_stops * 0.5)

        map_url = self._generate_map_url(current_coords, pickup_coords, dropoff_coords)

        stops = self._generate_stops(
            current_coords, pickup_coords, dropoff_coords,
            total_distance, fuel_stops
        )

        return {
            'total_distance': total_distance,
            'driving_time': driving_time,
            'total_trip_time': total_trip_time,
            'fuel_stops': fuel_stops,
            'map_url': map_url,
            'trip_id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'stops': stops
        }

    def _calculate_distance(self, coord1, coord2):
        """Calculate distance using Haversine formula"""
        lat1, lon1 = radians(coord1['lat']), radians(coord1['lon'])
        lat2, lon2 = radians(coord2['lat']), radians(coord2['lon'])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        radius = 3958.8  # Earth radius in miles
        distance = radius * c

        return distance

    def _generate_map_url(self, current, pickup, dropoff):
        """Generate OpenStreetMap URL"""
        return f"https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route={current['lat']},{current['lon']};{pickup['lat']},{pickup['lon']};{dropoff['lat']},{dropoff['lon']}"

    def _generate_stops(self, current, pickup, dropoff, total_distance, fuel_stops):
        """Generate list of stops"""
        stops = [
            {'type': 'start', 'location': 'Current Location', 'coords': current},
            {'type': 'pickup', 'location': 'Pickup Location', 'coords': pickup, 'duration': 1.0},
        ]

        for i in range(fuel_stops):
            stops.append({
                'type': 'fuel',
                'location': f'Fuel Stop #{i + 1}',
                'duration': 0.5
            })

        stops.append({
            'type': 'dropoff',
            'location': 'Dropoff Location',
            'coords': dropoff,
            'duration': 1.0
        })

        return stops