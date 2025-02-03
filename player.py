
import pandas as pd

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
