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

    distance_front = round(geodesic(position, front).meters * 1.09361,1)
    distance_centre = round(geodesic(position, centre).meters * 1.09361,1)
    distance_back = round(geodesic(position, back).meters * 1.09361,1)


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

green_distances = calculate_green_distances(Point(51.60580823146412, -0.22006249113568685), test_hole['Green'][0])
print(green_distances)

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

def club_selection(coordinates, player_data, hole_data):
    area = return_location(coordinates, hole_data)
    green_distance = calculate_green_distances(coordinates, hole_data['Green'][0])
    



def calculate_shot_with_dispersion(player, start_coords, remaining_distance):
    pass
