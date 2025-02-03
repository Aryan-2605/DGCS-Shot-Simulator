from geopy.distance import geodesic
from shapely.geometry import Point, Polygon
import ast
from shapely.geometry.linestring import LineString


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

        extension_factor = 5  # Don't mess with lines 73 - 80 unless you know what your doing because I have no clue.
        extended_line = LineString([
            position,
            Point(
                position.x + extension_factor * (centre.x - position.x),
                position.y + extension_factor * (centre.y - position.y)
            )
        ])
        intersection_points = green.exterior.intersection(extended_line)
        if intersection_points.geom_type == 'MultiPoint':
            pass
            #print('Valid')
            #print(intersection_points)
        else:
            print('Invalid')
            print(intersection_points)
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
