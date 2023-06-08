import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import os


def k_means(X):
    # create kmeans model and choose appropriate parameters
    # By looking at the plot, I would say the right amount of clusters are 4-5

    model = KMeans(n_clusters=365, random_state=0, n_init=10).fit(X)
    Y = model.labels_
    cluster_centers = model.cluster_centers_
    int_list = []
    for lst in cluster_centers:
        int_sublist = []
        for num in lst:
            int_sublist.append(int(num))
        int_list.append(int_sublist)
    timeAndCons = sorted(int_list, key=lambda x: x[0])
    time = [sublist[0] for sublist in timeAndCons]
    cons = [sublist[1] for sublist in timeAndCons]
    # print(Y)
    for t in np.unique(Y):
        plt.scatter(X[Y == t, 0], X[Y == t, 1], s=5, label=t)
    plt.xlabel('Time')
    plt.ylabel('Consumption [MW]')
    plt.legend()
    # plt.show()
    return cons, time


def get_wind_values(wind_rows, country_code):
    # Read the CSV file into a pandas dataframe
    df = pd.read_csv('/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/timeseries_and_consumers/DE_time_series/wind_series_raw_.csv')

    wind_column = 'wind_' + country_code

    # Get the values
    wind_values = df.loc[wind_rows, wind_column].tolist()

    return wind_values


def get_hydro_values(hydro_rows):
    # Read the CSV file into a pandas dataframe
    df = pd.read_csv('/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/timeseries_and_consumers/DE_time_series/hydro_series_raw.csv', sep=';')

    hydro_column = 'Production'

    # Get the values
    hydro_values = df.loc[hydro_rows, hydro_column].tolist()

    max_hydro = max(hydro_values)

    hydro_values = [round(i / max_hydro, 4) for i in hydro_values]

    return hydro_values


def make_list(number):
    fuel = []
    for i in range(365):
        fuel.append(number)
    return fuel


def combined_arrays(*arrays):
    combined_array = np.column_stack(arrays)
    indices = combined_array[:, 0]
    values = np.sum(combined_array[:, 1:], axis=1)
    result = np.column_stack((indices, values))

    return result


def find_max_value(array):
    indices = array[:, 0]
    values = np.sum(array[:, 1:], axis=1)
    result = np.column_stack((indices, values))
    max_value = np.max(result[:, 1])
    return max_value


def make_DE_demand_time_series():
    sheet_names = ['UK00', 'DE00', 'NOM1', 'NON1', 'NOS0', 'DKE1', 'DKW1', 'NL00', 'BE00']

    node_dfs = {}
    folder_path = 'demand_per_country'

    for sheet_name in sheet_names:
        file_path = os.path.join(folder_path, sheet_name + '_demand_data_2030_DE.csv')
        df = pd.read_csv(file_path, sep=';')
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y %H:%M')
        # Store the dataframe in the node_dfs dictionary
        node_dfs[sheet_name] = df

    # Create an empty dictionary to store the consumer data for each node
    consumer_data = {}

    # Loop through the dictionary of node names and their corresponding dataframes
    for node, df in node_dfs.items():
        consumer_data_list = []
        for i in range(8760):
            new_list = [i, df.iloc[i, 6]]
            consumer_data_list.append(new_list)
        consumer_data[node] = np.array(consumer_data_list)

    A = []
    for i in range(365):
        A.append(1)

    # Combine the arrays of Norway and Denmark
    consumer_data['NO00'] = combined_arrays(consumer_data['NOM1'], consumer_data['NON1'], consumer_data['NOS0'])
    consumer_data['DK00'] = combined_arrays(consumer_data['DKE1'], consumer_data['DKW1'])

    # Specify the scenario
    scenario = 'DE'

    if scenario == 'DE' or scenario == 'GA':
        # Set the price for all fuel types
        fuel_bio = make_list(51.42853029)
        fuel_gas = make_list(41.34853835)
        fuel_hard_coal = make_list(20.26284093)
        fuel_hydro = make_list(20)
        fuel_lignite = make_list(18.5142709)
        fuel_nuclear = make_list(4.834281847)
        fuel_oil = make_list(95.58939721)
        fuel_solar = make_list(0)
        fuel_onshore_wind = make_list(0)
        fuel_wind = make_list(0)
        fuel_other_non_res = make_list(100)
        fuel_other_res = make_list(0)
    elif scenario == 'NT':
        # Set the price for all fuel types
        fuel_bio = make_list(51.42853029)
        fuel_gas = make_list(64.07994874)
        fuel_hard_coal = make_list(25.50855102)
        fuel_hydro = make_list(30)
        fuel_lignite = make_list(18.5142709)
        fuel_nuclear = make_list(4.834281847)
        fuel_oil = make_list(130.547264)
        fuel_solar = make_list(0)
        fuel_onshore_wind = make_list(0)
        fuel_wind = make_list(0)
        fuel_other_non_res = make_list(100)
        fuel_other_res = make_list(0)
    else:
        print('Please provide scenario')

    # Make solar values for each country
    solar_UK = make_list(0.1085)
    solar_DE = make_list(0.1270)
    solar_NO = make_list(0.0978)
    solar_DK = make_list(0.1157)
    solar_NL = make_list(0.1268)
    solar_BE = make_list(0.1266)

    # Define the regions and their related codes
    regions = {
        'UK': ['UK00'],
        'DE': ['DE00'],
        'NO': ['NO00'],
        'DK': ['DK00'],
        'NL': ['NL00'],
        'BE': ['BE00']
    }

    # Initialize dictionaries to hold results
    max_values = {}
    times = {}
    demand_values = {}
    wind_values = {}
    solar_values = {}

    # Loop over regions
    for region, codes in regions.items():
        # Calculate max value for each region
        max_values[region] = find_max_value(*(consumer_data[code] for code in codes))

        # Get timestamps for sampling and demand_functions at these timestep
        data = sum(consumer_data[code] for code in codes)
        demand_values[region], times[region] = k_means(data)

        # Normalize the data
        demand_values[region] = [round(x / max_values[region], 6) for x in demand_values[region]]

        # Get the wind series
        wind_values[region] = get_wind_values(times[region], region)

    # Find hydro inflow for 'NO' region
    hydro_values = get_hydro_values(times['NO'])


    data_dict = {
        'const': A,
        'demand_UK': demand_values['UK'],
        'demand_DE': demand_values['DE'],
        'demand_NO': demand_values['NO'],
        'demand_DK': demand_values['DK'],
        'demand_NL': demand_values['NL'],
        'demand_BE': demand_values['BE'],
        'wind_UK': wind_values['UK'],
        'wind_DE': wind_values['DE'],
        'wind_NO': wind_values['NO'],
        'wind_DK': wind_values['DK'],
        'wind_NL': wind_values['NL'],
        'wind_BE': wind_values['BE'],
        'inflow_hydro': hydro_values,
        'solar_UK': solar_UK,
        'solar_DE': solar_DE,
        'solar_NO': solar_NO,
        'solar_DK': solar_DK,
        'solar_NL': solar_NL,
        'solar_BE': solar_BE,
        'fuel_bio': fuel_bio,
        'fuel_gas': fuel_gas,
        'fuel_hard_coal': fuel_hard_coal,
        'fuel_hydro': fuel_hydro,
        'fuel_lignite': fuel_lignite,
        'fuel_nuclear': fuel_nuclear,
        'fuel_oil': fuel_oil,
        'fuel_solar': fuel_solar,
        'fuel_onshore_wind': fuel_onshore_wind,
        'fuel_wind': fuel_wind,
        'fuel_other_non_res': fuel_other_non_res,
        'fuel_other_res': fuel_other_res,
    }

    # Convert the dictionary to a pandas dataframe
    df = pd.DataFrame(data_dict)
    # Write the dataframe to a CSV file
    df.to_csv('time_series_sample_DE.csv', index=False)

    # Create a list of lists with the data
    data = [
        ['NO_main', max_values['NO'], 'demand_NO', 1.00E+09, ''],
        ['DK_main', max_values['DK'], 'demand_DK', 1.00E+09, ''],
        ['DE_main', max_values['DE'], 'demand_DE', 1.00E+09, ''],
        ['NL_main', max_values['NL'], 'demand_NL', 1.00E+09, ''],
        ['BE_main', max_values['BE'], 'demand_BE', 1.00E+09, ''],
        ['UK_main', max_values['UK'], 'demand_UK', 1.00E+09, ''],
    ]

    # Create the pandas DataFrame
    df_con = pd.DataFrame(data, columns=['node', 'demand_avg', 'demand_ref', 'emission_cap', 'comment'])
    # Save the DataFrame to a CSV file
    df_con.to_csv('consumers_DE_new.csv', index=False)

    return df


if __name__ == "__main__":
    make_DE_demand_time_series()
