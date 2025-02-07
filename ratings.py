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
        distance_expected = geodesic((coords.y, coords.x), (expected_coords.y, expected_coords.x))
        distance_expected_centroid = geodesic((expected_coords.y, expected_coords.x), (centroid.y, centroid.x))
        distance_actual_centroid = geodesic((coords.y, coords.x), (centroid.y, centroid.x))

        #if distance_actual_centroid.ft < distance_expected.ft and area.get(''):



        distance_yards = distance_expected.ft * 0.333333
        print(distance_yards)

        return max(0, 1 - (distance_yards / 75) ** 2)







