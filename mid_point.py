from shapely.geometry import Point, LineString, Polygon
import numpy as np


class MidPoint:
    @staticmethod
    def get_fairway_orientation(area):
        coords = list(area.exterior.coords)

        max_length = 0
        best_angle = 0
        for i in range(len(coords) - 1):
            p1, p2 = Point(coords[i]), Point(coords[i + 1])
            length = p1.distance(p2)
            if length > max_length:
                max_length = length
                best_angle = np.degrees(np.arctan2(p2.y - p1.y, p2.x - p1.x))  # Angle in degrees

        return best_angle

    @staticmethod
    def find_fairway_intersections(player_position, fairway_polygon, extend_distance=0.001):
        """
        Create a lateral line perpendicular to the fairway's orientation and find intersections.
        :param player_position: (lon, lat) tuple of the player's position
        :param fairway_polygon: Shapely Polygon representing the fairway
        :param extend_distance: Distance to extend left/right
        :return: List of intersection points
        """
        x, y = player_position.x, player_position.y  # long and lat,

        # Get fairway orientation
        fairway_angle = MidPoint.get_fairway_orientation(fairway_polygon)

        # Calculate perpendicular direction (fairway_angle ± 90°)
        perp_angle_rad = np.radians(fairway_angle + 90)  # Convert to radians

        # extends the line left and right
        left_x = x + extend_distance * np.cos(perp_angle_rad)
        left_y = y + extend_distance * np.sin(perp_angle_rad)

        right_x = x - extend_distance * np.cos(perp_angle_rad)
        right_y = y - extend_distance * np.sin(perp_angle_rad)

        # Create a properly oriented lateral line
        lateral_line = LineString([(left_x, left_y), (right_x, right_y)])

        # Fidns the intersections
        intersection = fairway_polygon.exterior.intersection(lateral_line)

        # Return intersection points
        if intersection.is_empty:
            print("Error can't find intersection")
            return []
        elif intersection.geom_type == "Point":
            print('Error: Line is not long enough')
            return [intersection]
        elif intersection.geom_type == "MultiPoint":
            points = list(intersection.geoms)
            intersections = []
            for point in points:
                print(f"Intersection at: ({point.x:.13f}, {point.y:.13f})")
                intersections.append(Point(f'{point.x:.13f}', f'{point.y:.13f}'))

            return MidPoint.mid_point_calc(intersections)

    @staticmethod
    def mid_point_calc(points):
        # ((x1 + x2)/2, (y1 + y2)/2). (MP formula)
        LHS = round((points[0].x + points[1].x) / 2, 13)
        RHS = round((points[0].y + points[1].y) / 2, 13)

        return Point(LHS, RHS)


