import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def make_wind_series():
    # Define the list of country codes to read data for
    countries = ['BE', 'DE', 'DK', 'NL', 'NO', 'UK']

    # Define the year to filter by
    year = '2009'

    # Create an empty dictionary to store the data for each country
    country_data = {}

    folder_path = 'case1/wind_data_all_countries'
    # Loop over the countries and read the data from the corresponding file
    for country in countries:
        # Define the filename for the current country
        filename = f"{folder_path}/ninja_wind_country_{country}.csv"

        # Load the CSV file into a DataFrame
        df = pd.read_csv(filename)

        # Filter the DataFrame to only include rows from the specified year
        df_filtered = df[df['time'].str[:4] == year]

        # Select only the 'offshore' column
        offshore = df_filtered['offshore']

        # Add the offshore data to the country_data dictionary with the country code as key
        country_data[f'wind_{country}'] = offshore.values

    # Combine the data for all countries into a single DataFrame
    df_output = pd.DataFrame(country_data)

    # Add a new column with row numbers
    df_output.reset_index(inplace=True)
    df_output.index += 1

    # Save the combined data to a new CSV file
    wind_series_raw = df_output.to_csv('wind_series_raw_.csv', index=False)

    return wind_series_raw


def plot_wind_series():

    # Read the CSV file into pandas DataFrame
    df = pd.read_csv('/only_changes_here/make_input_data/timeseries_and_consumers/GA_time_series/hydro_series_raw.csv', sep=';')

    # Create a figure and a set of subplots
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot each column
    ax.plot(df['Production'])

    # Add labels and title
    ax.set_xlabel('Time [h]')
    ax.set_ylabel('Generation [MW]')
    ax.set_title('Hydro series')

    # Add a legend
    ax.legend()

    # Show the plot
    plt.show()


if __name__ == "__main__":
    plot_wind_series()


