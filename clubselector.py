import random


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
        #print(f'Running function bunker(bag, centre)')
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
                        if club != 'Driver':
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

                #print(probabilities)

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

