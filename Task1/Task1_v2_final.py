# Before running the python file, kindly install the following libraries - numpy, pandas, astropy, scikit-image
# Before running the python file, set the folder path of the folder containing the fits files

import os
import numpy as np
import pandas as pd
from astropy.io import fits
from skimage.measure import label, regionprops
from skimage.filters import threshold_otsu

# Step 1: Data Ingestion
# This function takes the image as a parameter and returns the image (top layer) of the fits file in the form of a 2D numpy array
def read_fits_file(file_path):
    with fits.open(file_path) as image:
        image_data = image[0].data
    return image_data

# Step 2: Image Processing and Detecting Objects
# This function takes the 2D array from step 1 as a parameter and returns a 2D array having values 0,1,2,3.... depending on the pixel intensity using otsu filter
def detect_objects(image_data):
    # Setting the threshold value of pixel intensity using Otsu method
    threshold = threshold_otsu(image_data) 
    binary_image = image_data > threshold # 2D array of image with values True or False
    labeled_image = label(binary_image) # 2D array of image with values 0,1,2,3......
    return labeled_image

# Step 3: Feature Extraction
# This function takes labeled_image, image_data as main parameters and creates a list of the specified properties 
def extract_features(labeled_image, image_data, fits_file_name, file_index):

    # Creating a empty list to contain the properties specified below
    results = [] 

    # Creating a list named properties to store the properties extracted from the labeled_image using the image_data as reference
    properties = regionprops(labeled_image, intensity_image=image_data) 

    # Using enumerate function to iterate each region detected and append its priperties to the results list
    for i, prop in enumerate(properties):
        object_id = i + 1
        centroid_y, centroid_x = prop.centroid
        size = prop.area
        luminosity = prop.mean_intensity * prop.area
        results.append({
            'File_no.': file_index,
            'File_name': fits_file_name,
            'Object_ID': object_id,
            'X Coordinate': centroid_x,
            'Y Coordinate': centroid_y,
            'Size (pixels^2)': size,
            'Luminosity (pixel intensity * pixels)': luminosity
        })
        # Properties and results dono alag alag list hai
        # regionprops function se properties nikal ke properties wale list me dal rahe
        # Properties wale list me se elements nikal ke results wale list me identification ke sath order me dal rahe 
    return results

# Step 4: Data Output
def save_to_csv(output_results, output_results_csv):
    # Using pandas to create a data frame from the extracted results and saving it to a csv file (handling csv files)
    dataframe = pd.DataFrame(output_results)
    dataframe.to_csv(output_results_csv, index=False) # Exporting without index

# Pipeline Execution
def run_pipeline(fits_files_folder, output_results_csv): # Taking inputs of fits_files_folder-path and output_results_csv-path
    # Creating a empty list to contain the properties specified below
    output_results = []

    # Creating a counter for fits files
    fits_file_index=1

    # Processing each fits file through the for loop
    # Joining each fits file name with its folder path to create file path of each file that ends with the name '.fits'
    for fits_file in os.listdir(fits_files_folder):
        if fits_file.endswith('.fits'):
            file_path = os.path.join(fits_files_folder, fits_file)
            print(f"Processing file {fits_file_index}: {fits_file}...")

            # Step 1: Data Ingestion
            image_data = read_fits_file(file_path)

            # Step 2: Image Processing and Detecting Objects
            labeled_image = detect_objects(image_data)

            # Step 3: Feature Extraction
            features = extract_features(labeled_image, image_data, fits_file, fits_file_index)

            # Using extend() function to add the elements of the feature list to output_results list
            # If append() is used isntead of extent(), the the entire list of features will be added as a element of output_results insted of the elements 
            output_results.extend(features)

            # Updating the counter value for the next fits file
            fits_file_index += 1
    
    # Step 4: Data Output - Craeting csv file 
    save_to_csv(output_results, output_results_csv)

    print(f"Pipeline executed succesfully.\nResults saved to {output_results_csv}")

# Define the paths
fits_files_folder = "Sample Files" # Place the relative path of the folder containing fits files
output_results_csv = "output_results.csv" # The output file will be created in the current working directory or inside the same folder in which this python file is running

# Executing the pipeline
run_pipeline(fits_files_folder, output_results_csv)