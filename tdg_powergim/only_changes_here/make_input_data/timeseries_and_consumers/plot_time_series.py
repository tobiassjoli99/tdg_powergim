import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def extract_desired_columns(input_file1):
    # Load the input CSV files
    df = pd.read_csv(input_file1)

    # Extract the '2009' column and overwrite the original CSV files
    df[['wind_UK', 'wind_DE', 'wind_NO', 'wind_DK', 'wind_NL', 'wind_BE', 'inflow_hydro', 'solar_UK', 'solar_DE', 'solar_NO', 'solar_DK', 'solar_NL', 'solar_BE']].to_csv(input_file1, index=False)

# Call the function with the input filenames
# extract_desired_columns('time_series_sample_for_plotting.csv')


def plot_wind_values(csv_file):
    df = pd.read_csv(csv_file)
    countries = ['UK', 'DE', 'NO', 'DK', 'NL', 'BE']
    colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown']

    plt.figure(figsize=(10, 6))

    for i, country in enumerate(countries):
        plt.plot(df.index, df[f'wind_{country.upper()}'], label=country, color=colors[i])

    plt.title('Wind Values for Each Country')
    plt.xlabel('Day of Year')
    plt.ylabel('Capacity factor')
    plt.legend()
    plt.show()


def plot_hydro_values(csv_file):
    df = pd.read_csv(csv_file)

    plt.figure(figsize=(10, 5))

    plt.plot(df.index, df[f'inflow_hydro'])

    plt.title('Hydro timeseries')
    plt.xlabel('Time')
    plt.ylabel('Capacity factor')
    plt.show()


plot_hydro_values('/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/timeseries_and_consumers/DE_time_series/time_series_sample_DE.csv')