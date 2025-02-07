import csv
import math
import os
import random
import folium
import numpy as np
import pandas as pd
from geopy.distance import *
from shapely import LineString
from shapely.geometry import Point, Polygon
from clubselector import ClubSelector
from hole import Hole
from player import Player
from angle_dispersion import AngleDispersion
from geopy.distance import great_circle
from mid_point import MidPoint
from ratings import Ratings

class GolfSimulator:
    def __init__(self, player_data, hole_data, starting_point, hole_id):
        self.player_data = player_data
        self.player_id = None
        self.hole_data = hole_data
        self.starting_point = starting_point
        self.latest_point = starting_point
        self.clubs = []
        self.positions = []
        self.hole_id = hole_id
        self.score = 0
        self.csv_initialized = False
        self.expected_area = []
        self.shot_distances = []

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
        # Select a club based on the player's location

        club = self.club_selection(player_id, coordinates)
        player = Player(player_id, self.player_data)

        hole = Hole(self.hole_data)
        area = hole.return_location(coordinates)

        # Fetch club distance and dispersion from player data
        club_distance = player.data.get(club, 0)
        self.expected_area.append(self.calculate_expected_area(self.latest_point, club_distance))



        for item in self.expected_area:
            print(f'Expected area: {item}')
        dispersion = player.data.get(f'{club}_Dispersion', 0)


        green_distances = hole.calculate_green_distances(coordinates, hole.polygons['Green'][0])

        if club_distance > green_distances['Centre'][0]:
            club_distance = green_distances['Centre'][0]

        if area.get('Bunker'):
            mean_factor = 0.1 + (1 - 0.1) * (36 - min(player.hcp, 36)) / 36

            scaling_factor = np.random.normal(loc=mean_factor, scale=0.3)
            scaling_factor = max(0.1, min(1, scaling_factor))
            #print(f'Scaling factor for bunker: {scaling_factor}')

            club_distance = club_distance * scaling_factor

        if area.get('Zone') == True and area.get('Bunker') == False:
            mean_factor = 0.7 + (1 - 0.7) * (36 - min(player.hcp, 36)) / 36
            scaling_factor = min(np.random.normal(loc=mean_factor, scale=0.3), 1)

           # print(f'Scaling factor for rough:  {scaling_factor}')

            club_distance = club_distance * scaling_factor



        valid = False
        while not valid:
            # Randomize shot distance with Gaussian variation (realistic)
            #mean_factor = 0.2 + (1 - 0.2) * (36 - min(player.hcp, 36)) / 36
            actual_distance = min(random.gauss(club_distance, dispersion), club_distance+10)

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

                print(f'The Zone is Invalid {Point(new_lon, new_lat)} \n New trajectory is being calculated.')

        # Print debugging info
        print(f"\nClub: {club}")
        self.clubs.append(club)
        print(f"Original Position: {coordinates}")
        print(f"Green Centre: {green_centre}")
        print(f"Dispersion: {dispersion}")
        print(f"Shot Distance (yards): {actual_distance}")
        self.shot_distances.append(actual_distance)
        print(f"Angle Dispersion (degrees): {angle_dispersion}")
        print(f"New Position: {Point(new_lon, new_lat)}\n")
        self.latest_point = Point(new_lon, new_lat)
        self.positions.append(Point(new_lon, new_lat))

        return Point(new_lon, new_lat)

    def simulateShot(self, last_id):
        for player_id in range(1, last_id+1):
            print(f'--------------------[PLAYER : {player_id}]--------------------')
            print('Itteration happens')
            simulator = GolfSimulator(self.player_data, self.hole_data, self.starting_point, self.hole_id)

            simulator.player_id = player_id
            hole = Hole(simulator.hole_data)
            area = hole.return_location(simulator.latest_point)
            while area.get('Green') is False:
                coordinates = simulator.calculate_shot_with_dispersion(simulator.player_id, simulator.latest_point)
                simulator.score += 1
                area = hole.return_location(coordinates)
                if player_id != 1:
                    simulator.csv_initialized = True
            simulator.plotShot()
            simulator.write_to_csv()
            print()
            print(f'--------------------[FINSHIED: {player_id}]--------------------')
            print()


    def calculate_expected_area(self, position, club_distance):
        hole = Hole(self.hole_data)
        area = hole.return_location(position)
        green_distances = hole.calculate_green_distances(position, hole.polygons['Green'][0])
        centroid = hole.polygons['Green'][0].centroid
        bearing = MidPoint.calculate_bearing(position, centroid)

        print(f'Player Position {position} \n Green Centroid: {centroid}')
        print(f'Angle towards the centroid: {bearing}')

        if club_distance > green_distances['Centre'][0]:
            print('Centroid is the most suitable expected area.')
            return centroid

        club_distance = club_distance * 0.000568182 #Convert distance to miles

        end_coords = geodesic(miles=club_distance).destination((position.y, position.x), bearing)
        expected_area = Point(end_coords.longitude, end_coords.latitude)
        print(f'Expected area: {expected_area}')
        fairway_MP = MidPoint.find_fairway_intersections(expected_area, hole.polygons['Fairway'][0])
        print(f'Fairway intersections: {fairway_MP}')

        return fairway_MP



    def shotRating(self):
        shotRatings = []
        dispersionRatings = []
        areaRatings = []
        player = Player(self.player_id, self.player_data)
        hole = Hole(self.hole_data)
        centroid = hole.polygons['Green'][0].centroid

        for item in self.positions:
            index = self.positions.index(item)
            expected_area = self.expected_area[index]
            area = hole.return_location(item)
            expected_distance = player.data.get(self.clubs[index], 0)
            real_distance = self.shot_distances[index]

            areaRatings.append(Ratings.calculate_expected_area(item, expected_area, centroid, area))
            dispersionRatings.append(Ratings.calculate_dispersion(real_distance, expected_distance))
            #print(Ratings.calculate_dispersion(real_distance, expected_distance))


    def plotShot(self):
        print(f'Printing in plot shot: {self.expected_area}')
        m = folium.Map(location=[self.starting_point.x, self.starting_point.y], zoom_start=18)
        folium.TileLayer('Esri.WorldImagery').add_to(m)
        folium.LayerControl().add_to(m)
        color_scheme = {
            'Driver' : 'Red',
            '5-Wood' : 'Blue',
            '3-Wood' : 'Purple',
            '3-Hybrid' : 'Orange',
            '4-Hybrid' : 'Darkred',
            '5-Hybrid' : 'Darkblue',
            '4-Iron' : 'Lightred',
            '5-Iron' : 'Beige',
            '6-Iron' : 'Darkblue',
            '7-Iron' : 'Lightblue',
            '8-Iron' : 'Pink',
            '9-Iron' : 'Cadetblue',
            'PW' : 'Lightgray',
            'SW' : 'Yellow',
            'GW' : 'White',
            'LW' : 'Lightgray'

        }

        current_x, current_y = self.starting_point.x, self.starting_point.y
        print(current_x, current_y)
        for position in self.positions:
            x, y = position.x, position.y
          #  print(current_x, current_y)
           # print()
           # print(x,y)
            color = color_scheme[self.clubs[self.positions.index(position)]]
            folium.PolyLine([(current_x, current_y), (x,y)], color=color, weight=4.5, opacity=0.8).add_to(m)
            folium.Marker([current_x, current_y], color = color,
                          popup=self.clubs[self.positions.index(position)]).add_to(m)
            current_x, current_y = position.x, position.y

        m.save(f'Dataset/Maps/{self.player_id}.html')

    def write_to_csv(self):

        self.shotRating()

        fieldnames = ['player_id', 'hole_id','shot_id','start_coords', 'end_coords', 'club']

        if self.csv_initialized is False:
            with open('Dataset/Output.csv', 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            self.csv_initialized = True

        start_coords = (self.starting_point.x, self.starting_point.y)
        score = []
        for i in range(1,self.score+1):
            score.append(i)

        for position in self.positions:
            index = self.positions.index(position)

            data_entry = {'player_id': self.player_id,
                          'hole_id': self.hole_id,
                          'shot_id': score[index]
                          }
            end_coords = (position.x, position.y)
            club = self.clubs[index]
            data_entry['start_coords'] = start_coords
            data_entry['end_coords'] = end_coords
            data_entry['club'] = club
            start_coords = end_coords

            with open('Dataset/Output.csv', 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writerow(data_entry)



if __name__ == '__main__':

    player_data = pd.read_csv('player_data.csv')
    hole_data = pd.read_csv('Hole_1.csv')


    simulator = GolfSimulator(player_data, hole_data, Point(51.60576426300037, -0.22007174187974488), 1)
    simulator.simulateShot(1)
    #print(simulator.expected_area)



    hole = Hole(hole_data)
    #simulator.calculate_expected_area(Point(51.60427449727718, -0.21965515431456822), 97)
    #print(simulator.expected_area)
    #print(hole.polygons['Fairway'][0])
    #test = MidPoint.find_fairway_intersections(Point(51.603567730737126, -0.21886414640818094), hole.polygons['Fairway'][0])
    #print(test)

   # bearing = MidPoint.calculate_bearing(Point(51.60431819609354, -0.22023722309929555),
   #                                      Point(51.60301799505365, -0.21922544942785488))


    #print(bearing)

    #dispersion_score = Ratings.calculate_dispersion(130, 150)
    #print(dispersion_score)

    distance = Ratings.calculate_expected_area(Point(51.60350114052477, -0.2192771469886219), Point(51.60297470685016, -0.2193307911662193), hole.polygons['Green'][0].centroid)
    #print(distance)




