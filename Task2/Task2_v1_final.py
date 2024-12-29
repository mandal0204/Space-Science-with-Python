import csv  
from sgp4.api import Satrec  
from sgp4.api import jday  
import numpy as np  
from datetime import datetime, timedelta  
import matplotlib.pyplot as plt  
from mpl_toolkits.mplot3d import Axes3D  
import os

# Check if the file exists and delete it
file_name = "satellite_positions.csv"  # Replace with your file name
if os.path.exists(file_name):
    os.remove(file_name)
with open(file_name, mode="a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Satellite name", "Time", "X Coordinate", "Y Coordinate", "Z Coordinate"])

# Sample Data
tle_data1 = {
"ISS": [
"1 25544U 98067A   22325.59167824  .00016717  00000+0  30729-3 0  9993",
"2 25544  51.6431 226.7758 0005941 113.7952 246.3823 15.50087640370124",
]
}

tle_data = {
"ISS": [
"1 25544U 98067A   22325.59167824  .00016717  00000+0  30729-3 0  9993",
"2 25544  51.6431 226.7758 0005941 113.7952 246.3823 15.50087640370124",
],
"Hubble": [
"1 20580U 90037B   22326.14821306  .00001264  00000+0  60660-4 0  9991",
"2 20580  28.4692 341.3025 0002725 99.7240 260.4518 15.09257816345634",
],
"Landsat 8": [
"1 39084U 13008A   22326.29217208  .00000068  00000+0  18063-4 0  9991",
"2 39084  98.2083 322.0110 0001335 90.0123 270.0100 14.57190296322473",
],
"StarLink-32637": [
"1 62032U 24216A   24355.91667824  .00004160  00000+0  10686-3 0  9994",
"2 62032  42.9978 264.4632 0001924 273.7191 58.1736 15.40684592 5668"
]
}

# Function to save positions to a CSV file
def save_to_csv(satellite_name, satellite_positions, file_name="satellite_positions.csv"):
    with open(file_name, mode="a", newline="") as file:
        write = csv.writer(file)
        for position in satellite_positions:
            write.writerow([satellite_name, position[0], position[1], position[2], position[3]])

# Function to predict satellite positions over time and returns a list of tuples containing timestamps and positions (x, y, z)
def predict_positions(satellite_name, tle, start_time, duration_minutes, interval_seconds=60):
    
     # Parsing TLE data and creating a satellite object
    line1, line2 = tle
    satellite = Satrec.twoline2rv(line1, line2)

    # List of timestamps at specified intervals
    timestamps = [
        start_time + timedelta(seconds=i)
        for i in range(0, duration_minutes * 60, interval_seconds)
    ]
    positions = []  # List to store calculated positions

    # Loop for caluculating satellite position at each timestamp
    for ts in timestamps:
        year, month, day, hour, minute, second = ts.timetuple()[:6] # Extracting the specified variables from each timestamp
        jd, fr = jday(year, month, day, hour, minute, second)  # Convert to Julian date
        e, r, _ = satellite.sgp4(jd, fr)  # Calculate position using SGP4 model
        if e == 0:  # Check if the calculation was successful
            positions.append((ts, r[0], r[1], r[2]))  # Append timestamp and position
        else:
            print(f"Error with {satellite_name} at timestamp {ts}")  # Print error message if failed
    save_to_csv(satellite_name, positions) # Save the predicted positions of the current satellite in a csv file
    return positions


# Visualizing multiple satellite orbits
def visualize_multiple_orbits(tle_data, start_time, duration_minutes, interval_seconds=60):
    
    fig = plt.figure(figsize=(12, 9))  # New figure of specified size
    ax = fig.add_subplot(111, projection="3d") # Create a 3D plot

    # Plot Earth as a sphere
    u, v = np.linspace(0, 2 * np.pi, 360), np.linspace(0, np.pi, 360) # Linspace to generate list of angle values
    radius_earth = 6378.137  # Earth's radius in km
    x_earth = radius_earth * np.outer(np.cos(u), np.sin(v)) # analogous to arc_length = radius * angle for x-axis
    y_earth = radius_earth * np.outer(np.sin(u), np.sin(v)) # similar for y-axis
    z_earth = radius_earth * np.outer(np.ones(np.size(u)), np.cos(v)) # similar for z-axis
    ax.plot_surface(x_earth, y_earth, z_earth, color="blue", alpha=0.2) # 0.3 looks good with other colors for satellite orbits

    # Different colors for different satellite orbits
    colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan']
    color_iter = iter(colors) # Itering colors list
    
    # Plotting different satellite orbits
    for satellite_name, tle in tle_data.items():
        # Variable is a list containing the positions of the current satellite(satellite_name)
        positions = predict_positions(satellite_name, tle, start_time, duration_minutes, interval_seconds)
        print(f"Plotting orbit for {satellite_name} satellite....")
        if not positions:
            print(f"No positions calculated for {satellite_name}.")
            continue
        
        # x, y, z are tuples containg position values respectively
        x, y, z = zip(*[(pos[1], pos[2], pos[3]) for pos in positions])

        # Creating 3D plot
        ax.plot(x, y, z, label=satellite_name, color=next(color_iter))

    # Set plot labels and legend
    ax.set_xlabel("X (km)")
    ax.set_ylabel("Y (km)")
    ax.set_zlabel("Z (km)")
    ax.set_title("Satellite Orbital Trajectories")
    ax.legend()
    plt.show()


# Parameters for visualization
start_time = datetime.now()  # Start time: current UTC time
duration_minutes = 100  # Predict for 60 minutes

# Initializing visualize_multiple_orbits function
visualize_multiple_orbits(tle_data, start_time, duration_minutes)
print(f"Plotted orbits for {len(tle_data)} satellites succesfully.")