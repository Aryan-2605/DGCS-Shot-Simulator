import random

import pandas as pd
from geopy.distance import geodesic
from shapely.geometry import Point, Polygon
import ast
from pprint import pprint
from shapely.geometry.linestring import LineString

player_data = pd.read_csv('player_data.csv')
hole_data = pd.read_csv('Hole_1.csv')


def parse_hole_data(dataframe):
    predefined_areas = ['Fairway', 'TreeLine', 'Green', 'Bunker', 'Zone', 'TeeBox']
    area_coordinates = {}

    for area in predefined_areas:
        arrays = dataframe.loc[dataframe['Area'] == area, 'Coordinates'].values

        converted = [ast.literal_eval(item) for item in arrays]

        area_coordinates[area] = converted

    return area_coordinates


def create_polygon(dataframe):
    area_coordinates = parse_hole_data(dataframe)
    hole_data = {}

    for zone, coordinates in area_coordinates.items():
        #print(f"Zone: {zone}")
        for i, coords in enumerate(coordinates):
            polygon = Polygon(coords)
            hole_data.setdefault(zone, []).append(polygon)
            #print(f"  Polygon {i + 1}: {polygon}")

    return hole_data


def return_location(location, hole_data):
    predefined_areas = ['Fairway', 'TreeLine', 'Green', 'Bunker', 'Zone', 'TeeBox']
    is_inside = {}

    for zone, polygons in hole_data.items():
        if zone in predefined_areas:
            is_inside[zone] = False

            for i, polygon in enumerate(polygons):
                if isinstance(polygon, str):
                    hole_data[zone][i] = Polygon(ast.literal_eval(polygon))
                    polygon = hole_data[zone][i]

                if polygon.contains(location):
                    is_inside[zone] = True
                    break

    #print('Result:')
    #pprint(is_inside)
    return is_inside


def calculate_green_intersections(position, green):
    #+-------------- DEBUGGING --------------+

    #print(f'Position = {position} Green_Polygon = {green}')

    #if green.exterior.coords[0] != green.exterior.coords[-1]:
    #    print("Polygon is not closed!")
    #else:
    #    print("Polygon is properly closed.")

    #+-------------- END OF DEBUG --------------+
    intersections = {}
    #Creates the Point for the middle of the green
    centre = green.centroid

    #line = LineString([position, centre])
    # Apparently the line is not long enough to cut through the green and only gives you one intersection point
    # ALSO there shouldn't be any tangent lines it's impossible since we cut through the polygon's centroid.

    extension_factor = 2  # Dont mess with lines 73 - 80 unless you know what your doing because I have no clue.
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


def calculate_green_distances(position, green):
    distances = {}
    intersections = calculate_green_intersections(position, green)

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


test_hole = create_polygon(hole_data)
#Green = test_hole['Green'][0]
#centre = Green.centroid
#print(centre)

#green_distances = calculate_green_distances(Point(51.60580823146412, -0.22006249113568685), test_hole['Green'][0])
#print(green_distances)

#coordinate = (51.60302816132606, -0.2192137342043472)
#point = Point(coordinate)

boolean_location = return_location(Point(51.604104455716836, -0.21924877440459767), create_polygon(hole_data))


#pprint(boolean_location)

#DEBUGGING

#arrays = hole_data.loc[hole_data['Area'] == 'TreeLine', 'Coordinates'].values

#This prints all the Polygons for all the zones
#pprint(create_polygon(hole_data))

#This prints the starting entries of the Player_Data
#print(player_data.head())

#This prints a specific players Driver Distance
#print(player_data.loc[player_data['ID'] == 230, 'Driver'].values[0])


#Functions to work on.


def organize_bag(data):
    bag = {key: data[key] for key in data.keys() if
           not key.endswith('_Dispersion') and key not in ['ID', 'Age', 'Gender', 'HCP']}

    bag = {
        'Woods': {key: value for key, value in bag.items() if key in ['Driver', '3-Wood', '5-Wood']},
        'Hybrids': {key: value for key, value in bag.items() if key.endswith('Hybrid')},
        'Irons': {key: value for key, value in bag.items() if key.endswith('Iron')},
        'Wedges': {key: value for key, value in bag.items() if key in ['PW', 'GW', 'SW', 'LW']}
    }

    return bag


def extract_row(id, player_data):
    row = player_data.iloc[id]

    row_dict = {col: val for col, val in row.items() if pd.notna(val)}
    for club, item in row_dict.items():
        if not isinstance(item, str):
            row_dict[club] = float(item)

    return row_dict


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

def TeeBox(player_hcp, bag, centre):
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


#print(extract_row(1, player_data))
def club_selection(id, coordinates, player_data, hole_data):
    #Coordinates = tuple
    #player_data = dataframe
    #ID = int

    area = return_location(coordinates, hole_data)
    print(area)
    green_distance = calculate_green_distances(coordinates, hole_data['Green'][0])
    #print(green_distance)
    centre = green_distance['Centre'][0]
    print(centre)
    data = extract_row(id, player_data)
    #print(data['7-Iron'])
    #print(data)
    bag = organize_bag(data)
    player_hcp = data['HCP']
    print(player_hcp)
    print(bag)
    if area.get('TeeBox') is True:
        club = TeeBox(player_hcp, bag, centre)
        return club


    if area.get('Fairway') is True and area.get('Zone') is True and all(
            value is False for key, value in area.items() if key not in ['Fairway', 'Zone']):
        club = fairway(bag, centre)
        return club

    if area.get('Bunker') is True:
        club = bunker(bag, centre)
        return club

    #Add Treeline before Zone
    if area.get('Zone') is True and area.get('TreeLine') is True and all(
            value is False for key, value in area.items() if key not in ['Zone', 'TreeLine']):
        club = treeline(bag, centre)
        return club

    if area.get('Zone') is True and all(value is False for key, value in area.items() if key not in ['Zone']):
        # High HCP players should play conservatively
        club = rough(player_hcp, bag, centre)
        return club


selected_club = club_selection(19, Point(51.60311663745501, -0.21905859961178653), player_data, test_hole)
print(selected_club)


def calculate_shot_with_dispersion(player, start_coords, remaining_distance):
    pass
