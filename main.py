import pandas as pd
from geopy.distance import geodesic
from shapely.geometry import Point, Polygon
import ast
from pprint import pprint


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


#hole_data = create_polygon(hole_data)
#coordinate = (51.60302816132606, -0.2192137342043472)
#point = Point(coordinate)

boolean_location = return_location(Point(51.604104455716836, -0.21924877440459767), create_polygon(hole_data))
pprint(boolean_location)

#DEBUGGING

#arrays = hole_data.loc[hole_data['Area'] == 'TreeLine', 'Coordinates'].values

#This prints all the Polygons for all the zones
#pprint(create_polygon(hole_data))

#This prints the starting entries of the Player_Data
#print(player_data.head())

#This prints a specific players Driver Distance
#print(player_data.loc[player_data['ID'] == 230, 'Driver'].values[0])


#Functions to work on.
def calculate_shot_with_dispersion(player, start_coords, remaining_distance):
    pass
