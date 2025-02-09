# The Dynamic Golf Caddy System Shot Simulator 

## Overview  
The **Golf Shot Simulator** is a Python-based tool that simulates golf shots using **player attributes**, **golf course data**, and **realistic dispersion mechanics**. It calculates shot distances, dispersion, and expected landing areas while tracking club selection and shot outcomes.  

## Features  
- **Club Selection**: Selects the best club based on player stats and shot distance.  
- **Shot Simulation**: Applies realistic dispersion and random variations for accuracy.  
- **Expected Landing Area**: Predicts shot landing positions based on shot type.  
- **Zone Detection**: Determines if the shot lands in Fairway, Rough, Bunker, or Green.  
- **Shot Rating System**: Scores each shot based on accuracy, zone, and dispersion.  
- **Data Export**: Saves shot data to CSV for analysis.  
- **Visualization**: Uses `folium` to generate interactive maps of shot paths.  

## Installation  

### Clone the Repository  
```bash
git clone https://github.com/Aryan-2605/DGCS-Simulator.git  
cd DGCS-Simulator
```
### Required libraries include:

- **geopy**: for distance calculations.
-  **shapely**: for polygon and geometry processing
-  **pandas**: for data handling
-  **folium**: for shot visualizatio

## Usage

### Run the Simulator

```python
from shapely.geometry import Point  
import pandas as pd  
from golf_simulator import GolfSimulator  

# Load player and course data  
player_data = pd.read_csv('player_data.csv')  
hole_data = pd.read_csv('Hole_1.csv')  

# Set starting position  
start_position = Point(51.60576426300037, -0.22007174187974488)  

# Create simulator instance  
simulator = GolfSimulator(player_data, hole_data, start_position, hole_id=1)  

# Run simulation for 10 players  
simulator.simulateShot(10)  

# Generate shot ratings  
simulator.shotRating()  
```
## Shot Rating System
Each shot is evaluated based on:
| Metric            | Description                                      |
|------------------|------------------------------------------------|
| Accuracy Score   | Measures distance to expected landing zone.    |
| Zone Score      | Rates if the shot lands in Fairway, Green, or Bunker. |
| Dispersion Score | Evaluates shot deviation from target.          |


## Data Output
### CSV output
| Player_ID | Hole_ID | Shot_ID | Start_Coords       | End_Coords         | Club   | Rating |
|-----------|--------|---------|--------------------|--------------------|--------|--------|
| 1         | 1      | 1       | (51.605, -0.220)  | (51.604, -0.219)  | Driver | 0.85   |
| 1         | 1      | 2       | (51.604, -0.219)  | (51.603, -0.218)  | 7-Iron | 0.92   |

### Visualization Output
- This code also generates an interactive map showing shot paths in
  ```Dataset/Maps/{player_id}.html```
![Github](https://github.com/user-attachments/assets/a469445d-7d5d-4704-b59c-a72a777af986)

## Customization
- Modify **weights** in ```shotRating()``` to tweak the ratings.
- Adjust ```ClubSelector``` logic for different playing styles
- Add new features such as **weather, elevation, or win effects.**
- Refer to the DGCS Dataset repository for the inital dataset generation

## Credits and how to Contribute
All work has been done by me. If you are intrested in contributing:

```bash
1. Fork the repository
2. Create a feature branch
3. Mark your chances and submit a pull request 
```

## License
This project is licensed under the MIT license 
