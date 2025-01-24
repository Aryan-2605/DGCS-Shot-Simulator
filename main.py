import pandas as pd
from geopy.distance import geodesic
from shapely.geometry import Polygon
import ast
from pprint import pprint


player_data = pd.read_csv('player_data.csv')
hole_data = pd.read_csv('Hole_1.csv')

arrays = hole_data.loc[hole_data['Area'] == 'TreeLine', 'Coordinates'].values
tree_lines = []


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

    
    for zone, polygons in hole_data.items():
            for i, polygon in enumerate(polygons):
                pass


hole_data = create_polygon(hole_data)
print(hole_data['Fairway'][0])
test = list(hole_data.keys())
print(len(hole_data['TreeLine']))
print(test[0])


print(player_data.head())

print(player_data.loc[player_data['ID'] == 230, 'Driver'].values[0])

def calculate_shot_with_dispersion(player, start_coords, remaining_distance):
    pass
