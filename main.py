import math
import random

import numpy as np
import pandas as pd
from geopy.distance import geodesic
from shapely.geometry import Point, Polygon
import ast
from pprint import pprint
from shapely.geometry.linestring import LineString
from angle_dispersion import AngleDispersion

class Player:
    def __init__(self, player_id, player_data):
        self.player_id = player_id - 1
        self.data = self.extract_row(player_data)
        self.hcp = self.data['HCP']
        self.bag = self.organize_bag()

    def extract_row(self, player_data):
        row = player_data.iloc[self.player_id]

        row_dict = {col: val for col, val in row.items() if pd.notna(val)}
        for club, item in row_dict.items():
            if not isinstance(item, str):
                row_dict[club] = float(item)

        return row_dict

    def organize_bag(self):
        bag = {key: self.data[key] for key in self.data.keys() if
               not key.endswith('_Dispersion') and key not in ['ID', 'Age', 'Gender', 'HCP']}

        bag = {
            'Woods': {key: value for key, value in bag.items() if key in ['Driver', '3-Wood', '5-Wood']},
            'Hybrids': {key: value for key, value in bag.items() if key.endswith('Hybrid')},
            'Irons': {key: value for key, value in bag.items() if key.endswith('Iron')},
            'Wedges': {key: value for key, value in bag.items() if key in ['PW', 'GW', 'SW', 'LW']}
        }

        return bag


class Hole:
    def __init__(self, hole_data):
        self.hole_data = hole_data
        self.polygons = self.create_polygon()

    def parse_hole_data(self):
        predefined_areas = ['Fairway', 'TreeLine', 'Green', 'Bunker', 'Zone', 'TeeBox']
        area_coordinates = {}

        for area in predefined_areas:
            arrays = self.hole_data.loc[self.hole_data['Area'] == area, 'Coordinates'].values

            converted = [ast.literal_eval(item) for item in arrays]

            area_coordinates[area] = converted

        return area_coordinates

    def create_polygon(self):
        area_coordinates = self.parse_hole_data()
        hole_polygons = {}

        for zone, coordinates in area_coordinates.items():
            #print(f"Zone: {zone}")
            for i, coords in enumerate(coordinates):
                polygon = Polygon(coords)
                hole_polygons.setdefault(zone, []).append(polygon)
                #print(f"  Polygon {i + 1}: {polygon}")

        return hole_polygons

    def return_location(self, location):
        predefined_areas = ['Fairway', 'TreeLine', 'Green', 'Bunker', 'Zone', 'TeeBox']
        is_inside = {}

        for zone, polygons in self.polygons.items():
            if zone in predefined_areas:
                is_inside[zone] = False

                for i, polygon in enumerate(polygons):
                    if isinstance(polygon, str):
                        self.polygons[zone][i] = Polygon(ast.literal_eval(polygon))
                        polygon = self.polygons[zone][i]

                    if polygon.contains(location):
                        is_inside[zone] = True
                        break

        return is_inside

    def calculate_green_intersections(self, position, green):
        #+-------------- DEBUGGING --------------+

        #print(f'Position = {position} Green_Polygon = {green}')

        #if green.exterior.coords[0] != green.exterior.coords[-1]:
        #    print("Polygon is not closed!")
        #else:
        #    print("Polygon is properly closed.")

        #+-------------- END OF DEBUG --------------+
        intersections = {}  #Creates the Point for the middle of the green
        centre = green.centroid

        #line = LineString([position, centre])
        # Apparently the line is not long enough to cut through the green and only gives you one intersection point
        # ALSO there shouldn't be any tangent lines it's impossible since we cut through the polygon's centroid.

        extension_factor = 2  # Don't mess with lines 73 - 80 unless you know what your doing because I have no clue.
        extended_line = LineString([
            position,
            Point(
                position.x + extension_factor * (centre.x - position.x),
                position.y + extension_factor * (centre.y - position.y)
            )
        ])

        intersection_points = green.exterior.intersection(extended_line)

        points_list = list(intersection_points.geoms)
        #print(points_list[0])  #Front of green
        #print(points_list[1])  #back on green

        intersections.setdefault("Back", []).append(points_list[0])
        intersections.setdefault("Centre", []).append(centre)
        intersections.setdefault("Front", []).append(points_list[1])
        #pprint(intersections)

        return intersections

    def calculate_green_distances(self, position, green):
        distances = {}
        intersections = self.calculate_green_intersections(position, green)

        position = (position.y, position.x)
        front = (intersections['Front'][0].y, intersections['Front'][0].x)
        back = (intersections['Back'][0].y, intersections['Back'][0].x)
        centre = (intersections['Centre'][0].y, intersections['Centre'][0].x)

        distance_front = round(geodesic(position, front).meters * 1.09361, 1)
        distance_centre = round(geodesic(position, centre).meters * 1.09361, 1)
        distance_back = round(geodesic(position, back).meters * 1.09361, 1)

        distances.setdefault("Front", []).append(distance_front)
        #print(f'Distance to front = {distance_front}')

        distances.setdefault("Centre", []).append(distance_centre)
        #print(f'Distance to centre = {distance_centre}')

        distances.setdefault("Back", []).append(distance_back)
        #print(f'Distance to back = {distance_back}')

        #pprint(distances)
        return distances


class ClubSelector:
    @staticmethod
    def fairway(bag, centre):
        club_selected = None
        current_distance = 0
        shortest_club = None
        shortest_distance = float('inf')
        #print('Running function Fairway(bag, centre)')
        for category, clubs in bag.items():
            for club, club_distance in clubs.items():
                if club_distance < shortest_distance:
                    shortest_distance = club_distance
                    shortest_club = club

        for category, clubs in bag.items():
            for item, distance in clubs.items():
                if distance < centre and item != 'Driver':
                    if current_distance < distance:
                        club_selected = item
                        current_distance = distance

        if club_selected is None:
            club_selected = shortest_club

        return club_selected

    @staticmethod
    def bunker(bag, centre):
        club_selected = None
        current_distance = 0
        print(f'Running function bunker(bag, centre)')
        for category, clubs in bag.items():
            for item, distance in clubs.items():
                # prioritize Wedges
                if centre <= 100 and category == 'Wedges':
                    if distance < centre and (club_selected is None or distance > current_distance):
                        club_selected = item
                        current_distance = distance
                # Long-distance bunker logic: use other appropriate clubs
                elif centre > 100 and category == 'Irons':
                    centre += 10
                    if distance < centre and (club_selected is None or distance > current_distance):
                        club_selected = item
                        current_distance = distance
                else:
                    return 'SW'
        return club_selected

    @staticmethod
    def rough(player_hcp, bag, centre):
        club_selected = None
        current_distance = 0
        shortest_club = None
        shortest_distance = float('inf')  # Start with an infinitely large number

        #print(f'Running function rough(player_hcp, bag, centre)')
        #print(f'Distance to target: {centre}')

        for category, clubs in bag.items():
            for club, club_distance in clubs.items():
                if club_distance < shortest_distance:
                    shortest_distance = club_distance
                    shortest_club = club

        # Logic for club selection
        if player_hcp >= 15:
            for category, clubs in bag.items():
                for club, club_distance in clubs.items():
                    # High HCP: Choose a safe, controlled shot with short irons or hybrids
                    if category in ['Irons', 'Hybrids'] and club_distance < centre:
                        if club_selected is None or club_distance > current_distance:
                            club_selected = club
                            current_distance = club_distance
        else:  # Low HCP players can take more aggressive shots
            for category, clubs in bag.items():
                for club, club_distance in clubs.items():
                    # Low HCP: Allow longer irons, hybrids, or woods for longer distances
                    #print(f'Checking club: {club} (distance: {club_distance})')
                    if category in ['Woods', 'Hybrids', 'Irons'] and club_distance < centre:
                        #print(f'Selecting club: {club}')
                        if club_selected is None or club_distance > current_distance:
                            club_selected = club
                            current_distance = club_distance

        # Fallback: Select the shortest club if no suitable club was found
        if club_selected is None:
            #print("No club suitable for the target distance. Using shortest club as fallback.")
            club_selected = shortest_club

        return club_selected

    @staticmethod
    def tee_box(player_hcp, bag, centre):
        current_distance = 0
        club_selected = None

        for category, clubs in bag.items():
            if category == 'Woods':
                probabilities = {}
                for club, club_distance in clubs.items():

                    if club == 'Driver':
                        if player_hcp <= 10:
                            probabilities[club] = 0.9
                        elif player_hcp <= 20:
                            probabilities[club] = 0.7
                        else:  # High HCP: Lower chance for Driver
                            probabilities[club] = 0.5
                    else:  # Safer clubs like 3-Wood and 5-Wood
                        probabilities[club] = 1 - probabilities.get('Driver', 0)

                print(probabilities)

                # Normalize probabilities to ensure they sum to 1
                total_weight = sum(probabilities.values())
                normalized_probabilities = {club: prob / total_weight for club, prob in probabilities.items()}

                selected_club = random.choices(
                    list(normalized_probabilities.keys()),
                    weights=normalized_probabilities.values(),
                    k=1
                )[0]

                # Track the selected club and its distance
                if clubs[selected_club] > current_distance:
                    club_selected = selected_club
                    current_distance = clubs[selected_club]

        return club_selected

    @staticmethod
    def treeline(bag, centre):
        club_selected = None
        current_distance = 0

        # Iterate over bag for suitable clubs
        for category, clubs in bag.items():
            for club, club_distance in clubs.items():
                if category in ['Hybrids', 'Irons'] and club_distance <= centre:
                    # Prefer low-lofted clubs for control
                    if club_selected is None or club_distance > current_distance:
                        club_selected = club
                        current_distance = club_distance

        if club_selected is None:
            club_selected = 'SW'

        return club_selected


class GolfSimulator:
    def __init__(self, player_data, hole_data):
        self.player_data = player_data
        self.hole_data = hole_data

    def club_selection(self, player_id, coordinates):
        hole = Hole(self.hole_data)
        area = hole.return_location(coordinates)
        #print('Location the ball is in: ')
        #print(area)
        green_distance = hole.calculate_green_distances(coordinates, hole.polygons['Green'][0])
        centre = green_distance['Centre'][0]
        #print(green_distance)
        #print('Distance to the centre:')
        #print(str(centre) + " Yards")
        player = Player(player_id, self.player_data)
        #print('Players Bag:')
        #print(player.bag)
        #print(data['7-Iron'])
        #print(data)
        if area.get('TeeBox') is True:
            return ClubSelector.tee_box(player.hcp, player.bag, centre)

        if area.get('Fairway') is True and area.get('Zone') is True and all(
                value is False for key, value in area.items() if key not in ['Fairway', 'Zone']):
            return ClubSelector.fairway(player.bag, centre)

        if area.get('Bunker') is True:
            return ClubSelector.bunker(player.bag, centre)

        if area.get('Zone') is True and area.get('TreeLine') is True and all(
                value is False for key, value in area.items() if key not in ['Zone', 'TreeLine']):
            return ClubSelector.treeline(player.bag, centre)

        if area.get('Zone') is True and all(value is False for key, value in area.items() if key not in ['Zone']):
            return ClubSelector.rough(player.hcp, player.bag, centre)

    def calculate_shot_with_dispersion(self, player_id, coordinates):
        """
        Simulate a golf shot considering dispersion and aiming towards the center of the green.

        Args:
            player_id (int): The player's ID.
            coordinates (shapely.geometry.Point): The starting coordinates of the shot.

        Returns:
            shapely.geometry.Point: The new coordinates of the shot after dispersion.
        """

        # Select a club based on the player's location
        club = self.club_selection(player_id, coordinates)
        player = Player(player_id, self.player_data)

        # Fetch club distance and dispersion from player data
        club_distance = player.data.get(club, 0)
        dispersion = player.data.get(f'{club}_Dispersion', 0)

        hole = Hole(self.hole_data)
        area = hole.return_location(coordinates)
        green_distances = hole.calculate_green_distances(coordinates, hole.polygons['Green'][0])

        if club_distance > green_distances['Centre'][0]:
            club_distance = green_distances['Centre'][0]

        if area.get('Bunker'):
            mean_factor = 0.1 + (1 - 0.1) * (36 - min(player.hcp, 36)) / 36

            scaling_factor = np.random.normal(loc=mean_factor, scale=0.3)
            scaling_factor = max(0.1, min(1, scaling_factor))
            print(f'Scaling factor: {scaling_factor}')

            club_distance = club_distance * scaling_factor

            

        valid = False
        while not valid:
            # Randomize shot distance with Gaussian variation (realistic)
            actual_distance = random.gauss(club_distance, dispersion)

            # Ensure the ball doesn’t exceed the remaining distance
            green_centre = hole.polygons['Green'][0].centroid  # Aim for the green center

            # Calculate direction from current position to green center
            dx = green_centre.x - coordinates.x
            dy = green_centre.y - coordinates.y
            magnitude = math.sqrt(dx**2 + dy**2)

            # Normalize the direction vector
            dx /= magnitude
            dy /= magnitude

            # Angle dispersion for shot randomness
            angle_dispersion = AngleDispersion.get_random_value_float(player.hcp,
                                                                      False if area.get('Bunker') is True else False)
            angle_radians = math.radians(angle_dispersion)

            # Rotate the direction vector by dispersion angle
            new_dx = dx * math.cos(angle_radians) - dy * math.sin(angle_radians)
            new_dy = dx * math.sin(angle_radians) + dy * math.cos(angle_radians)

            # Convert distance from yards to meters (1 yard = 0.9144 meters)
            meters_distance = actual_distance * 0.9144

            # Apply distance movement to coordinates
            new_lat = coordinates.y + (meters_distance * new_dy) / 111139  # Approx. meters to latitude
            new_lon = coordinates.x + (meters_distance * new_dx) / (111139 * math.cos(math.radians(coordinates.y)))

            new_area = hole.return_location(Point(new_lon, new_lat))

            if(new_area.get('Zone') is True):
                valid = True
            else:
                print('Invalid Zone')
                print(Point(new_lon, new_lat))

        # Print debugging info
        print(f"\nClub: {club}")
        print(f"Original Position: {coordinates}")
        print(f"Green Centre: {green_centre}")
        print(f"Dispersion: {dispersion}")
        print(f"Shot Distance (yards): {actual_distance}")
        print(f"Angle Dispersion (degrees): {angle_dispersion}")
        print(f"New Position: {Point(new_lon, new_lat)}\n")

        return Point(new_lon, new_lat)








player_data = pd.read_csv('player_data.csv')
hole_data = pd.read_csv('Hole_1.csv')
print(random.gauss(304, 18))

simulator = GolfSimulator(player_data, hole_data)
simulator.calculate_shot_with_dispersion(5, Point(51.60411884325774, -0.2200671400154587))
selected_club = simulator.club_selection(19, Point(51.60405860120144, -0.2195491439693001))
print(f"Selected Club: {selected_club}")

