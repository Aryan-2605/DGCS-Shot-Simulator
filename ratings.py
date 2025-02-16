import math
import random
from shapely.geometry import Point
from geopy.distance import geodesic

class Ratings:
    @staticmethod
    def calculate_dispersion(actual_distance, expected_distance):
        if actual_distance > expected_distance:
            return 1
        else:
            penalty = ((expected_distance - actual_distance) / expected_distance)
            print('Works')
            return max(0, 1 - penalty)

    @staticmethod
    def calculate_expected_area(coords, expected_coords, centroid, area):
        #print(f' Coords {coords}')
        #print(expected_coords)
        #print(area)
        distance_expected = geodesic((coords.y, coords.x), (expected_coords.y, expected_coords.x))
        distance_expected_centroid = geodesic((expected_coords.y, expected_coords.x), (centroid.y, centroid.x))
        distance_actual_centroid = geodesic((coords.y, coords.x), (centroid.y, centroid.x))

        penalty = 1

        if area.get('Fairway') and not area.get('Bunker'):
            penalty = 1
        elif area.get('Bunker'):
            penalty = 0.4
        elif area.get('TreeLine'):
            penalty = 0.5
        elif area.get('Zone'):
            penalty = 0.6

        distance_yards = distance_expected.ft * 0.333333

        return max(0, (1 - (distance_yards / 75) ** 2) * penalty)







